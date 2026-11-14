"""Generate the original EN curriculum against a strictly read-only corpus.

All generation history belongs to a separate private staging SQLite database.
This command never ingests, backfills or migrates the source corpus. It does
not promote documents just because generation completed.
"""
from __future__ import annotations

import argparse
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import sys
from types import SimpleNamespace

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from pricinglibrary_rag.api import _COURSE_REFERENCE_ALLOWLIST, _reference_match_text
from pricinglibrary_rag.calculators import PracticeCalculator
from pricinglibrary_rag.course_english_content import COURSES
from pricinglibrary_rag.embeddings import LocalHashingEmbedding
from pricinglibrary_rag.generation import MaterialGenerator
from pricinglibrary_rag.llm import TemplateLLM
from pricinglibrary_rag.retrieval import build_retriever
from pricinglibrary_rag.schemas import CourseRequest, SourceRef
from pricinglibrary_rag.storage import LocalStore


class ReadOnlyCorpus(LocalStore):
    def __init__(self, path):
        self.db_path = Path(path).resolve(strict=True)

    def connect(self):
        db = sqlite3.connect(self.db_path.as_uri() + "?mode=ro", uri=True)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA query_only=ON")
        return db


def verified_pinned_sources(corpus, slug):
    """Reuse only the reviewed bibliography, never the French lesson prose."""
    legacy = BACKEND / "pricinglibrary_rag" / "course_scripts" / f"{slug}.md"
    text = legacy.read_text(encoding="utf-8") if legacy.is_file() else ""
    section = re.search(r"(?ms)^## Sources RAG a citer\s*\n(.*?)(?=^## |\Z)", text)
    entries = re.findall(r"(?ms)^- \*(.*?)\*\s*—\s*«(.*?)»", section[1] if section else "")
    sources = []
    with corpus.connect() as db:
        for anchor, document, index in _COURSE_REFERENCE_ALLOWLIST.get(slug, ()):
            row = db.execute("SELECT c.id,c.content,d.title FROM chunks c JOIN documents d ON d.id=c.document_id WHERE c.document_id=? AND c.chunk_index=?", (document, index)).fetchone()
            if row is None or anchor not in _reference_match_text(row["content"]):
                raise ValueError(f"Reviewed source anchor unavailable for {slug}: {document}/{index}")
            quote = next((quote for _, quote in entries if anchor in _reference_match_text(quote)
                          and _reference_match_text(quote) in _reference_match_text(row["content"])), "")
            if not quote:
                # Use actual contiguous corpus windows; never reconstruct a
                # cleaned equation or compose a quote from noncontiguous words.
                words = row["content"].split()
                quote = next((" ".join(words[i:i+32]) for i in range(max(1,len(words)-31))
                              if anchor in _reference_match_text(" ".join(words[i:i+32]))), "")
            if quote and MaterialGenerator._presentable_source_snippet(quote):
                sources.append(SourceRef(document_id=document,chunk_id=row["id"],title=row["title"],source=None,
                    chunk_index=index,score=1,vector_score=0,lexical_score=1,snippet=re.sub(r"\s+", " ", quote).strip()))
    return sources


class CourseRetriever:
    """Add reviewed course locators to real lexical retrieval, with no writes."""
    def __init__(self, base, corpus):
        self.base, self.corpus, self.slug, self.pinned = base, corpus, "", []
        self.course=None
        self.snippets={}

    def retrieve(self, *args, **kwargs):
        retrieved = self.base.retrieve(*args, **kwargs)
        if self.course:
            # Broad whole-course queries are poor coverage for distinct lesson
            # mechanisms. Retrieve each actual module subject, preserving real
            # source locators and rejecting tables/indexes/OCR instead of
            # filling the evidence count with unrelated generic paragraphs.
            keywords=MaterialGenerator._FAMILY_KEYWORDS.get(self.course.family,())
            for lesson in self.course.lessons:
                retrieved += self.base.retrieve(self.course.title+" "+lesson.title,top_k=12,usable_only=True,min_quality=45)
            unique={}
            self.snippets={}
            for item in retrieved:
                locator=(item.chunk.document_id,item.chunk.chunk_index)
                if locator in unique: continue
                compact=re.sub(r"\s+"," ",item.chunk.content).strip()
                candidates=re.split(r"(?<=[.!?])\s+(?=[A-Z])",compact)
                candidates=[candidate for candidate in candidates if 60<=len(candidate)<=700
                    and MaterialGenerator._presentable_source_snippet(candidate)
                    and not re.search(r"\b(?:journal of|university press|bibliograph|isbn|doi\.org)\b",candidate,re.I)
                    and (not keywords or any(word in candidate.lower() for word in keywords))]
                if not candidates: continue
                quote=max(candidates,key=MaterialGenerator._source_prose_score)
                self.snippets[locator]=quote
                unique[locator]=item
            retrieved=list(unique.values())[:max(kwargs.get("top_k",64),64)]
        return [*[SimpleNamespace(chunk=SimpleNamespace(content=s.snippet,metadata={},section_title=None),
                score=s.score,vector_score=0,lexical_score=1,_pinned=s) for s in self.pinned], *retrieved]

    def to_source_ref(self, item):
        if getattr(item,"_pinned",None): return item._pinned
        source=self.base.to_source_ref(item)
        quote=self.snippets.get((source.document_id,source.chunk_index))
        return source.model_copy(update={"snippet":quote}) if quote else source


def validate_release_review(index,review):
    if review.get("verdict") != "PASS" or review.get("reviewer_role") != "business_client_mystere":
        raise RuntimeError("Independent business review is not PASS")
    entries=review.get("courses",[])
    reviewed={item["slug"]:item["sha256"] for item in entries}
    if len(reviewed)!=len(entries): raise RuntimeError("Duplicate course in independent review")
    if any(reviewed.get(item["slug"]) != item["sha256"] for item in index["courses"]):
        raise RuntimeError("Business review does not match exact course hashes")


def promote_reviewed_courses(output,served,index,review):
    """Commit private variants with raw hashes, then replace the index atomically."""
    validate_release_review(index,review)
    destination=served/"en"
    destination.mkdir(exist_ok=True)
    for item in index["courses"]:
        source=(output/item["path"]).resolve()
        if not source.is_relative_to(output.resolve()): raise RuntimeError("Course path escapes staging")
        if hashlib.sha256(source.read_bytes()).hexdigest()!=item["sha256"]:
            raise RuntimeError("Staged course changed after its content review")
        target=destination/source.name
        shutil.copy2(source,target)
        if hashlib.sha256(target.read_bytes()).hexdigest()!=item["sha256"]:
            raise RuntimeError("Promoted course bytes differ from the reviewed artifact")
        if item.get("evidence"):
            evidence=(output/item["evidence"]).resolve()
            if not evidence.is_relative_to(output.resolve()): raise RuntimeError("Evidence path escapes staging")
            shutil.copy2(evidence,destination/evidence.name)
        item["status"]="accepted_98_and_independent_review"
    index["schema_version"]="tpl.course.language-index.v1"
    index.pop("schema",None)
    index["status"]="accepted_98_and_independent_review"
    index["review"]={"reviewer_role":"business_client_mystere","kind":"independent_agent_content_review",
                     "technical_threshold":98,"human_certification_claimed":False}
    pending=destination/"_index.pending.json"
    pending.write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding="utf-8")
    os.replace(pending,destination/"_index.json")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", default=str(BACKEND / "data" / "pricinglibrary_rag.sqlite3"))
    parser.add_argument("--output-dir", default=str(BACKEND / "generated_english_courses"))
    parser.add_argument("--slug", action="append", default=[])
    parser.add_argument("--review-report", help="Independent business review JSON required for promotion")
    parser.add_argument("--promote", action="store_true")
    args = parser.parse_args()
    output = Path(args.output_dir).resolve()
    corpus = ReadOnlyCorpus(args.corpus)
    if corpus.db_path == (output/"authoring.sqlite3").resolve():
        parser.error("Corpus and authoring databases must be different")
    # Refuse staging in the served path: file-exists language discovery must not
    # advertise drafts before both gates have accepted their exact content hash.
    served = (BACKEND / "pricinglibrary_rag" / "course_scripts").resolve()
    if output.is_relative_to(served):
        parser.error("Use private staging outside the served course_scripts tree")
    output.mkdir(parents=True, exist_ok=True)
    before = {"size": corpus.db_path.stat().st_size,"mtime_ns":corpus.db_path.stat().st_mtime_ns}
    stats = corpus.pedagogy_stats()
    with corpus.connect() as db:
        row=db.execute("SELECT embedding_blob,embedding_json FROM chunks LIMIT 1").fetchone()
    if row is None: raise RuntimeError("Source corpus is empty")
    dim=len(row["embedding_blob"])//4 if row["embedding_blob"] is not None else len(json.loads(row["embedding_json"]))
    base=build_retriever("lexical",corpus,LocalHashingEmbedding(dim=dim))
    retriever=CourseRetriever(base,corpus)
    generator=MaterialGenerator(retriever,TemplateLLM(),LocalStore(output/"authoring.sqlite3"))
    index={"schema_version":"tpl.course.language-index.v1","language":"en","status":"draft_pending_review",
        "corpus_mode":"SQLite mode=ro; PRAGMA query_only=ON","corpus_stats":stats,"courses":[]}
    requested=set(args.slug)
    if requested-set(c.slug for c in COURSES.values()): parser.error("Unknown course slug")
    for course in COURSES.values():
        if requested and course.slug not in requested: continue
        retriever.slug=course.slug
        retriever.course=course
        retriever.pinned=verified_pinned_sources(corpus,course.slug)
        response=generator.generate_course(CourseRequest(topic=course.title,product=course.product,concepts=[course.key],
            language="en",module_count=len(course.lessons),duration_minutes=240,level="advanced",top_k=64))
        # Topic routing must not silently send e.g. a Greeks/volatility course
        # to a generic vanilla family because of an incidental title keyword.
        if response.metadata.get("topic_key") != course.key: raise RuntimeError(f"Wrong family for {course.slug}: {response.metadata.get('topic_key')}")
        content=f"---\nslug: {course.slug}\nlanguage: en\nsource_count: {len(response.sources)}\n---\n\n{response.content}\n"
        path=output/f"{course.slug}.md"
        path.write_text(content,encoding="utf-8")
        sha=hashlib.sha256(path.read_bytes()).hexdigest()
        evidence=output/f"_{course.slug}.evidence.json"
        evidence.write_text(json.dumps(response.model_dump(),ensure_ascii=False,indent=2),encoding="utf-8")
        index["courses"].append({"slug":course.slug,"language":"en","modules":len(course.lessons),"sha256":sha,
            "path":path.name,"evidence":evidence.name,"sources":len(response.metadata.get("source_ledger",[])),"status":"draft_pending_review"})
        print(json.dumps({"step":"generate","slug":course.slug,"modules":len(course.lessons),"sources":index["courses"][-1]["sources"]}))
    after={"size":corpus.db_path.stat().st_size,"mtime_ns":corpus.db_path.stat().st_mtime_ns}
    if before != after: raise RuntimeError("Source corpus changed during generation; investigate before publication")
    index["source_corpus_unchanged"]=True
    (output/"_index.json").write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding="utf-8")
    if args.promote:
        import audit_course_quality
        audit_course_quality.DEFAULT_CORPUS_DB=corpus.db_path
        gate=audit_course_quality.audit_dir(output,98)
        if gate.get("courses_passing_gate") != len(index["courses"]): raise RuntimeError("Strict 98 gate not satisfied")
        if not args.review_report: raise RuntimeError("Independent business content review required before promotion")
        review=json.loads(Path(args.review_report).read_text(encoding="utf-8"))
        promote_reviewed_courses(output,served,index,review)
    print(json.dumps({"status":index["status"],"courses":len(index["courses"]),"corpus":stats,"source_corpus_unchanged":True}))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
