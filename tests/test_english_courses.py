"""Original EN course authoring, independent numeric controls and strict gate.

Source fixtures in unit tests are synthetic original prose, not claims that a
real textbook endorsed the course. Release generation uses the real RO corpus.
"""
from dataclasses import asdict, replace
import json
import math
from pathlib import Path
import re
import sqlite3
from statistics import NormalDist
import sys
from types import SimpleNamespace

import pytest

from pricinglibrary_rag.calculators import PracticeCalculator
from pricinglibrary_rag.course_english import _pack, build_english_course, calculator_ticket
from pricinglibrary_rag.course_english_content import COURSES
from pricinglibrary_rag.generation import GenerationContext, MaterialGenerator
from pricinglibrary_rag.llm import TemplateLLM
from pricinglibrary_rag.schemas import CourseRequest, SourceRef
from test_exercise_generation import services,auth

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))


def context(sources=()):
    return GenerationContext("English authoring test",[],list(sources),[],[],{}, {}, [])


class EmptyRetriever:
    def retrieve(self,*args,**kwargs): return []
    def to_source_ref(self,item): raise AssertionError("No source was retrieved")


@pytest.mark.parametrize("key",list(COURSES))
def test_generate_course_english_is_authored_and_keeps_exact_module_quiz_contract(key):
    course=COURSES[key]
    generator=MaterialGenerator(EmptyRetriever(),TemplateLLM())
    result=generator.generate_course(CourseRequest(topic=course.title,product=course.product,concepts=[key],
        language="en",module_count=len(course.lessons)))
    assert result.metadata["language"]=="en" and result.metadata["topic_key"]==key
    assert result.metadata["llm_used"] is False and result.metadata["release_eligible"] is False
    assert len(re.findall(r"^### Lesson \d+ -",result.content,re.M))==len(course.lessons)
    assert len(re.findall(r"^### Module \d+ -",result.content,re.M))==len(course.lessons)
    assert "## Written course" in result.content and "## Cours redige" not in result.content
    assert "No readable source quotation is available" in result.content
    assert len(re.findall(r"^\*\*Q\d+\.",result.content,re.M))==5
    assert set(re.findall(r"^Answer: \*\*([A-E])\*\*",result.content,re.M))==set("ABCDE")
    assert len(re.findall(r"^[A-E]\. ",result.content,re.M))==25
    assert result.metadata["calculation_pack"]["steps"]
    assert not any(re.search(r"\b(?:frequence|annuelle)\b",str(step)) for step in result.metadata["calculation_pack"]["steps"])
    assert re.findall(r"\d+(?:\.\d+)?",result.metadata["authored_ticket"])==re.findall(r"\d+(?:\.\d+)?",result.metadata["calculator_ticket"])
    if course.tool is None: assert "tpl tools example None" not in result.content


def test_french_generation_contract_remains_french():
    result=MaterialGenerator(EmptyRetriever(),TemplateLLM()).generate_course(CourseRequest(topic="Black-Scholes",module_count=8,language="fr"))
    assert "## Cours redige" in result.content and "## Exemple numerique resolu" in result.content
    assert "## Written course" not in result.content and result.metadata["language"]=="fr"


def test_unknown_english_topic_is_honestly_unsupported_without_french_fallback():
    result=MaterialGenerator(EmptyRetriever(),TemplateLLM()).generate_course(CourseRequest(topic="Unspecified unrelated curriculum",language="en"))
    assert result.metadata["authoring_status"]=="unsupported_topic"
    assert result.metadata["release_eligible"] is False and "No French substitute" in result.content


def test_english_course_never_calls_a_configured_external_writer():
    class ForbiddenWriter:
        name="external-provider-configured-but-not-used"
        def generate(self,*args,**kwargs): raise AssertionError("External writer must not be called")
    result=MaterialGenerator(EmptyRetriever(),ForbiddenWriter()).generate_course(CourseRequest(topic="Black-Scholes",language="en"))
    assert result.metadata["llm"]=="template" and result.metadata["llm_used"] is False


def test_sixty_course_specific_quiz_stems_are_distinct():
    stems=[question[0] for course in COURSES.values() for question in course.quiz]
    assert len(stems)==60 and len(set(stems))==60


def test_every_wrong_answer_has_an_authored_specific_explanation():
    from pricinglibrary_rag.course_english_feedback import FEEDBACK
    assert set(FEEDBACK)==set(COURSES)
    all_reasons=[]
    for key,course in COURSES.items():
        assert len(FEEDBACK[key])==len(course.quiz)==5
        for question,reasons in zip(course.quiz,FEEDBACK[key]):
            assert len(reasons)==len(question[2])==4 and len(set(reasons))==4
            assert all(len(reason.split())>=12 for reason in reasons)
            assert not any("The alternative does not follow" in reason for reason in reasons)
            all_reasons.extend(reasons)
    assert len(all_reasons)==len(set(all_reasons))==240
    from pricinglibrary_rag.course_english import _quiz
    rendered=_quiz(COURSES["swap"])
    question=rendered.split("**Q2.")[1].split("**Q3.")[0]
    assert "B. Annuity is always quoted in currency per basis point." in question
    assert "- B: With accruals measured in years, the annuity has year units." in question
    assert FEEDBACK["swap"][1][1] in question


def test_english_serialization_never_appends_french_formula_sections():
    from generate_course_scripts import CourseSpec,_course_markdown
    response=MaterialGenerator(EmptyRetriever(),TemplateLLM()).generate_course(CourseRequest(topic="Black-Scholes",language="en"))
    markdown=_course_markdown(CourseSpec("vanilla-options-quote","Black-Scholes",None),response)
    assert "language: en" in markdown
    assert "## Written course" in markdown and "## Formules de desk" not in markdown


def test_real_http_course_generation_uses_english_and_server_entitlements(services):
    from fastapi.testclient import TestClient
    from pricinglibrary_rag.api import create_app
    client=TestClient(create_app(services))
    services.store.upsert_entitlement("student@test.invalid","student",user_id="student")
    services.store.upsert_entitlement("starter@test.invalid","starter",user_id="starter")
    request={"topic":"Black-Scholes","language":"en","module_count":8}
    for route in ("/generate/course","/agent/course"):
        assert client.post(route,json=request).status_code==401
        assert client.post(route,headers=auth(services,"starter"),json=request).status_code==403
        response=client.post(route,headers=auth(services,"student"),json=request)
        assert response.status_code==200,response.text[:500]
        body=response.json()
        assert body["metadata"]["language"]=="en" and body["metadata"]["llm_used"] is False
        assert "## Written course" in body["content"] and "## Cours redige" not in body["content"]
        assert body["metadata"]["calculation_pack"]["steps"][1]["result"]=="10.4506"
        assert body["metadata"]["release_eligible"] is False


def test_course_results_match_independent_elementary_oracles():
    packs={key:_pack(course,PracticeCalculator()) for key,course in COURSES.items()}
    steps=lambda key:{s.label:s.result for s in packs[key].steps}
    N=NormalDist().cdf
    d1=(.05+.5*.2**2)/.2
    call=100*N(d1)-100*math.exp(-.05)*N(d1-.2)
    assert steps("vanilla_bs")["Call price"]==f"{call:.4f}"
    assert steps("stochastic")["Call price"]==steps("vanilla_bs")["Call price"]
    assert steps("greeks")["Total P&L"]==f"{250000*(-2)+.5*(-80000)*(-2)**2+120000*3-15000:,.0f} EUR"
    assert steps("swap")["DV01"]==f"{100e6*4.55*1e-4:,.0f} EUR/bp"
    assert steps("swap")["Rate-shock P&L"]==f"{100e6*4.55*10e-4:,.0f} EUR"
    assert steps("bond")["Rate-shock P&L"]==f"{-50e6*6.2*25e-4:,.0f} EUR"
    assert steps("cds")["Protection-buyer spread-shock P&L"]==f"{50e6*4.2*25e-4:,.0f} EUR"
    assert steps("barrier")["Scenario spot 1.2"]==f"{10e6*max(1.2-1.1,0):,.0f} USD"
    assert steps("autocall")["Total investor cash receipts"]==f"{1e6*(1+2*.06):,.0f} EUR"
    z=NormalDist().inv_cdf(.95)
    assert steps("var")["VaR"]==f"{20e6*.02*z:,.0f}"
    assert steps("var")["Expected Shortfall"]==f"{20e6*.02*math.exp(-z*z/2)/math.sqrt(2*math.pi)/.05:,.0f}"
    d1=1/1.03
    d2=(1-.032*d1)/1.032
    d3=(1-.0335*(d1+d2))/1.0335
    for n,df in enumerate((d1,d2,d3),1):
        row=next(s.result for s in packs["yield_curve"].steps if s.label.startswith(f"DF {n}y"))
        assert f"DF={df:.10f}" in row
    assert "20.0001%" in steps("vol_smile")["Bounded implied-volatility inversion"]
    mc=steps("monte_carlo")
    assert mc["Black-Scholes benchmark"]==f"{call:.4f}" and "20,000" in mc["Simulation S_T"]


@pytest.mark.parametrize("key,changed,expected",[
    ("bond","Bond market value 12m modified duration 4.5, yield rises 10bp.","-54,000 EUR"),
    ("barrier","FX down-and-out call spot 1.0800 strike 1.1000 barrier 1.0000 notional EUR 1m. Terminal spot 1.3000.","200,000 USD"),
    ("autocall","Autocall Athena initial level 100, autocall barrier 100%, coupon barrier 70%, protection barrier 60%, coupon 4% per observation with memory, notional 2m. Observed levels: 65, 102.","2,160,000 EUR"),
])
def test_legacy_keyword_adapter_preserves_nondefault_numbers_without_fallback(key,changed,expected):
    course=replace(COURSES[key],ticket=changed)
    assert re.findall(r"\d+(?:\.\d+)?",calculator_ticket(course))==re.findall(r"\d+(?:\.\d+)?",changed)
    assert _pack(course,PracticeCalculator()).steps[-1].result==expected


def test_strict_english_gate_rejects_cosmetic_labels_bad_quiz_and_changed_results(tmp_path,monkeypatch):
    import audit_course_quality as gate
    from pricinglibrary_rag.api import _COURSE_REFERENCE_ALLOWLIST
    from pricinglibrary_rag.course_english import _sources
    db_path=tmp_path/"synthetic-original-sources.sqlite3"
    source_text="European option teaching uses a declared contract and consistent discounting. This synthetic original source describes a reproducible valuation exercise and its assumptions, with explicit limits rather than an executable market quote."
    sources=[]
    with sqlite3.connect(db_path) as db:
        db.execute("CREATE TABLE chunks(document_id TEXT,chunk_index INTEGER,content TEXT)")
        for n in range(16):
            identifier=f"{n:024x}"
            db.execute("INSERT INTO chunks VALUES(?,?,?)",(identifier,0,source_text))
            sources.append(SourceRef(document_id=identifier,chunk_id=f"chunk-{n}",title=f"Original synthetic fixture {n}",
                source=None,chunk_index=0,score=1,vector_score=0,lexical_score=1,snippet=source_text))
    monkeypatch.setattr(gate,"DEFAULT_CORPUS_DB",db_path)
    monkeypatch.setitem(_COURSE_REFERENCE_ALLOWLIST,COURSES["vanilla_bs"].slug,(("european option teaching uses a declared contract",sources[0].document_id,0),))
    request=CourseRequest(topic="Black-Scholes",language="en",module_count=8)
    body,metadata=build_english_course(request,context(sources),PracticeCalculator())
    path=tmp_path/(COURSES["vanilla_bs"].slug+".md")
    original=f"---\nslug: {path.stem}\nlanguage: en\n---\n\n{body}\n"
    path.write_text(original,encoding="utf-8")
    path.with_name("_"+path.stem+".evidence.json").write_text(json.dumps({"content":body,"metadata":metadata}),encoding="utf-8")
    assert gate.audit_one(path,98)["gate"]=="PASS"
    (tmp_path/"README.md").write_text("Repository confidentiality documentation, not a course.",encoding="utf-8")
    assert gate.audit_dir(tmp_path,98)["courses_audited"]==1
    path.write_text(original.replace("E. ","F. ",1),encoding="utf-8")
    assert not gate.audit_one(path,98)["criticals"]["quiz_five_options"]
    path.write_text(re.sub(r"Answer: \*\*[B-E]\*\*","Answer: **A**",original),encoding="utf-8")
    assert not gate.audit_one(path,98)["criticals"]["quiz_varied_correct_positions"]
    path.write_text(original.replace("10.4506","10.4507"),encoding="utf-8")
    assert not gate.audit_one(path,98)["criticals"]["numerical_evidence_recomputed"]
    path.write_text(original.replace("**Concept.**","**Concept.** notionnel cours redige exercice corrige ",1),encoding="utf-8")
    assert not gate.audit_one(path,98)["criticals"]["original_english_no_french_instruction"]
    path.write_text(original.replace("**Concept.**","**Concept.** Interest rates must be positive. ",1),encoding="utf-8")
    assert not gate.audit_one(path,98)["criticals"]["quant_truth_claims"]
    dirty=sources+[sources[0].model_copy(update={"document_id":"ocr","snippet":source_text+"\x03"}),
                   sources[0].model_copy(update={"document_id":"bibliography","snippet":"Journal of Applied Probability. University Press. "+source_text})]
    ledger,_=_sources(context(dirty),COURSES["vanilla_bs"])
    assert len(ledger)==16


def test_original_corpus_connection_is_read_only_and_review_is_hash_bound(tmp_path):
    from generate_english_courses import ReadOnlyCorpus,validate_release_review
    path=tmp_path/"source.sqlite3"
    with sqlite3.connect(path) as db: db.execute("CREATE TABLE immutable_test(value TEXT)")
    before=(path.stat().st_size,path.stat().st_mtime_ns)
    with ReadOnlyCorpus(path).connect() as db:
        assert db.execute("PRAGMA query_only").fetchone()[0]==1
        with pytest.raises(sqlite3.OperationalError): db.execute("INSERT INTO immutable_test VALUES('forbidden')")
    assert (path.stat().st_size,path.stat().st_mtime_ns)==before
    index={"courses":[{"slug":"one","sha256":"a"*64}]}
    good={"verdict":"PASS","reviewer_role":"business_client_mystere","courses":[{"slug":"one","sha256":"a"*64}]}
    validate_release_review(index,good)
    for bad in ({**good,"verdict":"FAIL"},{**good,"reviewer_role":"technical_rl"},
                {**good,"courses":[{"slug":"one","sha256":"b"*64}]},
                {**good,"courses":good["courses"]*2}):
        with pytest.raises(RuntimeError): validate_release_review(index,bad)
    from audit_english_course_quality import _verify_source_locators
    absent=tmp_path/"missing-corpus.sqlite3"
    assert _verify_source_locators(absent,[],[])[0] is False
    assert not absent.exists()


def test_private_promotion_keeps_raw_bytes_and_commits_accepted_index_last(tmp_path):
    import hashlib
    from generate_english_courses import promote_reviewed_courses
    stage=tmp_path/"drafts";stage.mkdir()
    served=tmp_path/"private-course-root";served.mkdir()
    raw="# Synthetic technical course fixture — not real teaching evidence\r\n".encode("utf-8")
    (stage/"fixture.md").write_bytes(raw)
    (stage/"_fixture.evidence.json").write_text("{}",encoding="utf-8")
    sha=hashlib.sha256(raw).hexdigest()
    index={"courses":[{"slug":"fixture","path":"fixture.md","sha256":sha,"evidence":"_fixture.evidence.json"}]}
    review={"verdict":"PASS","reviewer_role":"business_client_mystere","courses":[{"slug":"fixture","sha256":sha}]}
    promote_reviewed_courses(stage,served,index,review)
    assert (served/"en/fixture.md").read_bytes()==raw
    manifest=json.loads((served/"en/_index.json").read_text(encoding="utf-8"))
    assert manifest["schema_version"]=="tpl.course.language-index.v1"
    assert manifest["courses"][0]["status"]=="accepted_98_and_independent_review"
    assert manifest["review"]["human_certification_claimed"] is False
    assert not (served/"en/_index.pending.json").exists()
    (stage/"fixture.md").write_bytes(raw+b"changed")
    with pytest.raises(RuntimeError,match="changed after"):
        promote_reviewed_courses(stage,served,index,review)
    assert (served/"en/fixture.md").read_bytes()==raw
