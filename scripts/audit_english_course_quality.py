"""English extension of the strict 98 course gate, with unchanged depth floors.

This is an automated artifact gate. Its two persona-oriented scores are not
human user studies or a commercial validation. Publication also requires an
independent content review of the exact document hashes.
"""
from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import re
import sqlite3

from pricinglibrary_rag.api import _public_course_markdown, _COURSE_REFERENCE_ALLOWLIST, _reference_match_text
from pricinglibrary_rag.calculators import PracticeCalculator
from pricinglibrary_rag.course_english_content import COURSES
from pricinglibrary_rag.course_english import _pack

FORBIDDEN_ENGLISH_CLAIMS={
    "rates_must_be_positive":r"interest rates? (?:must|have to) (?:always )?be positive",
    "negative_rates_invalidate_curve":r"negative (?:rates|forwards) (?:prove|imply|mean) (?:an? )?(?:invalid curve|bad interpolation)",
    "inverted_curve_is_invalid":r"an? inverted (?:yield )?curve is (?:always |necessarily )?invalid",
    "fixed_seed_biases_estimator":r"(?:a |the )?fixed seed (?:makes|causes|introduces) (?:an? |the )?(?:estimator )?bias",
    "small_sample_biases_estimator":r"(?:a )?small sample (?:size )?(?:necessarily )?biases (?:the )?estimator",
    "monte_carlo_predicts_future":r"monte carlo (?:can )?predicts? (?:the )?future (?:stock |spot )?prices",
    "risk_neutral_means_indifferent_investors":r"risk.neutral valuation means (?:that )?investors are indifferent to risk",
    "q_drift_uses_historical_return":r"risk.neutral drift (?:depends on|equals|is determined by) (?:the )?(?:historical|physical) (?:expected )?return",
    "volatility_predicts_spot_direction":r"higher volatility (?:means|predicts|guarantees) (?:that )?(?:the )?(?:stock|spot) (?:price )?(?:rises|increases)",
    "buyer_loses_on_widening":r"(?:a |the )?protection buyer (?:always )?loses (?:value |money )?(?:when|on|from) (?:a )?spread widening",
    "cs01_positive_always_loss":r"positive cs01 (?:always )?means (?:a )?loss",
    "buyer_receives_running_premium":r"(?:a |the )?protection buyer receives (?:the )?running premium",
    "duration_understates_positive_convexity_loss":r"duration.only understates (?:the )?loss (?:from|for) (?:a )?yield rise (?:for|with) (?:a )?positive.convexity",
    "delta_always_percentage":r"delta (?:is always|must be) (?:expressed as )?(?:a )?percentage",
    "gamma_always_percentage_squared":r"gamma (?:is always|must be) (?:expressed as )?(?:a )?squared percentage",
    "positive_delta_means_itm":r"positive delta (?:means|implies|proves) (?:that )?the option is in.the.money",
    "positive_delta_buy_hedge":r"positive delta (?:must be hedged by|requires) buying (?:the )?underlying",
    "delta_hedge_cannot_lose":r"delta.hedging (?:guarantees no loss|eliminates all risks|cannot lose)",
    "receipts_equal_profit":r"total (?:cash )?receipts (?:are|equal) (?:the )?(?:net )?profit",
    "var_is_maximum_loss":r"var (?:is|defines) (?:a |the )?(?:guaranteed |absolute )?maximum (?:possible )?loss",
    "ci_covers_model_error":r"(?:a |the )?confidence interval (?:covers|includes) all (?:model|specification|discretisation) errors",
}


def _verify_source_locators(database,source_lines,rules):
    if not database.is_file(): return False,["source_corpus_unavailable"],False
    failures=[]
    pinned=bool(rules)
    try:
        with sqlite3.connect(database.resolve().as_uri()+"?mode=ro",uri=True) as db:
            db.execute("PRAGMA query_only=ON")
            for entry in source_lines:
                match=re.search(r"\(document ([a-z0-9]+), chunk (\d+)\): (.+)$",entry)
                if not match:
                    failures.append("invalid_locator");continue
                row=db.execute("SELECT content FROM chunks WHERE document_id=? AND chunk_index=?",(match[1],int(match[2]))).fetchone()
                if row is None or _reference_match_text(match[3]) not in _reference_match_text(row[0]):
                    failures.append(f"{match[1]}:{match[2]}")
            for anchor,document,index in rules:
                row=db.execute("SELECT content FROM chunks WHERE document_id=? AND chunk_index=?",(document,index)).fetchone()
                pinned &= row is not None and anchor in _reference_match_text(row[0])
    except sqlite3.Error:
        return False,["source_corpus_unreadable_or_schema_unavailable"],False
    return bool(source_lines) and not failures,failures,pinned


def audit_english_one(path: Path, threshold=98):
    from audit_course_quality import _word_count, _scale, _weighted, _bool_score, _section, DEFAULT_CORPUS_DB
    text=path.read_text(encoding="utf-8")
    public=_public_course_markdown(text)
    # Prose depth must not be manufactured by raw sources or JSON widget rows.
    prose=re.sub(r"```[\s\S]*?```", "", public)
    written=_section(text,"Written course")
    written_prose=re.sub(r"```[\s\S]*?```", "", written)
    lesson_parts=re.split(r"(?m)^### Lesson \d+ - .+$",written_prose)[1:]
    counts=[_word_count(value) for value in lesson_parts]
    modules=len(re.findall(r"(?m)^### Module \d+ -",text))
    lessons=len(counts)
    full_words=_word_count(prose)
    course_words=_word_count(written_prose)
    average=round(sum(counts)/max(1,len(counts)))
    minimum=min(counts,default=0)
    sections=len(re.findall(r"(?m)^## ",text))
    types=re.findall(r"(?m)^type: ([a-z_]+)",text)
    type_set=set(types)
    ui_count=len(re.findall(r"(?m)^```uiblock\s*$",text))
    formulas=len(re.findall(r"\$\$[\s\S]*?\$\$",text))+types.count("equation")
    required={"equation","scenario_table"}.issubset(type_set)
    practical=bool(type_set & {"payoff","greeks_scenario","vol_smile","monte_carlo","corr_matrix"})
    source_lines=re.findall(r"(?m)^- \[S\d+\] (.+)$",text)
    references=re.findall(r"(?m)^- \*.+?\* — «(.+)»\s*$",_section(public,"References"))
    rules=_COURSE_REFERENCE_ALLOWLIST.get(path.stem,())
    reviewed=sum(any(anchor in _reference_match_text(quote) for anchor,_,_ in rules) for quote in references)
    source_valid,source_failures,pinned_valid=_verify_source_locators(DEFAULT_CORPUS_DB,source_lines,rules)
    quiz=_section(text,"Course-specific quiz")
    questions=re.findall(r"(?m)^\*\*Q\d+\. (.+?)\*\*$",quiz)
    answers=re.findall(r"(?m)^Answer: \*\*([A-E])\*\*",quiz)
    question_blocks=re.split(r"(?m)^\*\*Q\d+\.",quiz)[1:]
    options=[re.findall(r"(?m)^([A-E])\. (.+)$",value) for value in question_blocks]
    five_options=bool(options) and all([letter for letter,_ in row]==list("ABCDE") for row in options)
    unique_options=all(len({value for _,value in row})==5 for row in options)
    solved=bool(_section(text,"Worked numerical example")) and bool(re.search(r"\bResult:\s*\*\*",text))
    corrected=bool(_section(text,"Corrected exercises")) and "**Correction.**" in text
    synthesis=bool(_section(text,"Synthesis desk case"))
    checkpoint=bool(_section(text,"Student and junior-professional checkpoint"))
    provenance="Content provenance:" in text and all(t in text for t in ("[extrait]","[reformule]","[genere]"))
    decision=len(re.findall(r"\b(?:quote|hedge|monitor|reduce|reject|escalate|decision|trader|sales|risk)\b",prose,re.I))
    market=len(re.findall(r"\b(?:price|pricing|P&L|sensitivity|DV01|delta|gamma|vega|spread|volatility|stress|scenario)\b",prose,re.I))
    french=re.findall(r"\b(?:frequence|annuelle|notionnel|hypotheses controlees|cours redige|exercice corrige|reponse|calculs a respecter|lecture desk|valeur actuelle)\b",written_prose,re.I)
    truth_violations=[name for name,pattern in FORBIDDEN_ENGLISH_CLAIMS.items() if re.search(pattern,written_prose,re.I)]
    # Verify the exact deterministic source of displayed numbers independently
    # of word counts or presence of a 'verified' label in the Markdown.
    evidence_file=path.with_name("_"+path.stem+".evidence.json")
    numerical=False
    if evidence_file.is_file():
        evidence=json.loads(evidence_file.read_text(encoding="utf-8"))
        metadata=evidence.get("metadata",{})
        profile=COURSES.get(metadata.get("topic_key"))
        if profile:
            expected=asdict(_pack(profile,PracticeCalculator()))
            numerical=(metadata.get("calculation_pack")==expected and evidence.get("content","").strip()==text.split("---",2)[-1].strip())
    structure=_weighted([(_scale(modules,8),2),(_scale(lessons,max(8,modules)),2),(_scale(sections,14),1),(_bool_score("## Learning objectives" in text),1),(_bool_score("## Prerequisites" in text),1)])
    depth=_weighted([(_scale(full_words,6500),1.4),(_scale(course_words,3000),2),(_scale(average,320),1.3),(_scale(minimum,220),1),(_scale(formulas,6),1)])
    grounding=_weighted([(_scale(len(source_lines),16),2),(_bool_score(source_valid),1),(_bool_score(provenance),1),(_bool_score("## Source coverage" in text),1)])
    practice=_weighted([(_bool_score(solved),1.6),(_bool_score(corrected),1.6),(_bool_score(synthesis),1.2),(_scale(len(questions),5),1),(_scale(decision,28),1),(_scale(market,45),1)])
    ui=_weighted([(_scale(ui_count,5),2),(_bool_score(required),1.5),(_bool_score(practical),1.5),(_scale(len(type_set),4),1)])
    student=_weighted([(structure,1.3),(depth,1.8),(grounding,1.4),(_scale(formulas,7),1.2),(_bool_score(solved),1),(_scale(len(questions),5),.8),(_bool_score(checkpoint),.8)])
    professional=_weighted([(practice,2),(ui,1.5),(grounding,1),(_scale(decision,35),1.3),(_bool_score(corrected),1),(_bool_score(synthesis),1)])
    overall=_weighted([(structure,1.2),(depth,1.8),(grounding,1.5),(practice,1.7),(ui,1.4),(student,1.2),(professional,1.2)])
    critical={"minimum_8_modules":modules>=8,"minimum_8_written_lessons":lessons>=8,
        "cours_redige_min_3000_words":course_words>=3000,"avg_lesson_min_320_words":average>=320,
        "visible_prose_min_6500_words":full_words>=6500,"sources_min_16":len(source_lines)>=16,
        "source_locators_and_quotes_verified":source_valid,"ui_blocks_min_5":ui_count>=5,"required_ui_types":required,
        "practical_ui_type":practical,"solved_example":solved,"corrected_exercise":corrected,
        "quiz_min_5":len(questions)==5,"quiz_five_options":five_options,"quiz_unique_options":unique_options,
        "quiz_varied_correct_positions":set(answers)==set("ABCDE"),"quiz_unique_stems":len(set(questions))==len(questions),
        "student_persona_98":student>=threshold,"young_professional_persona_98":professional>=threshold,
        "quant_truth_claims":not truth_violations,
        "original_english_no_french_instruction":not french,"numerical_evidence_recomputed":numerical,
        "public_reference_present":len(references)>=1,"public_references_reviewed":len(references)==reviewed,
        "corpus_reference_anchors_verified":pinned_valid,"public_citation_ghosts_absent":not bool(re.search(r"\[S(?:\d+|x)\]",public))}
    issues=[name for name,passed in critical.items() if not passed]
    return {"slug":path.stem,"language":"en","gate":"PASS" if overall>=threshold and all(critical.values()) else "FAIL",
        "quality_score":overall,"student_quant_persona":student,"young_professional_persona":professional,
        "score_kind":"automated_content_heuristic_not_user_research","axes":{"structure":structure,"depth":depth,"grounding":grounding,"practice":practice,"ui_blocks":ui},
        "metrics":{"words_total":full_words,"words_cours_redige":course_words,"h2_sections":sections,"modules":modules,
        "lessons":lessons,"avg_lesson_words":average,"min_lesson_words":minimum,"formulas":formulas,"uiblocks":ui_count,
        "uiblock_types":sorted(type_set),"sources":len(source_lines),"noisy_sources":len(source_failures),"quiz_questions":len(questions),
        "public_reference_count":len(references),"registered_public_reference_count":reviewed,
        "source_failures":source_failures,"french_instruction_hits":french,"quant_truth_violations":truth_violations},"criticals":critical,"issues":issues,
        "artifact_sha256":hashlib.sha256(path.read_bytes()).hexdigest()}
