"""Source-honest, deterministic English course authoring.

No translation API, paid writer or model-generated numerical claims. This is an
original authored curriculum plus checked calculator applications. Source text
is never used as a fill-in-the-blanks prose template or silently translated.
"""
from __future__ import annotations

from dataclasses import asdict, replace
import hashlib
import json
import re

from .course_blocks import detect_topic_key
from .course_english_content import COURSES
from .course_english_feedback import FEEDBACK
from .exercise_english import english_pack


SCHEMA = "tpl.course.english.v1"
PROVENANCE = "> Content provenance:\n> - **[extrait]** means a verbatim, explicitly delimited source quotation.\n> - **[reformule]** means an attributed pedagogical paraphrase.\n> - **[genere]** means original teaching content or a synthetic case; all displayed case results come from the deterministic calculation engine.\n> The instructional prose and derivations below are original [genere], not quotations or certified textbook translations.\n"

STAGES = (
    ("Contract and units", "Start with the economic object. Write down who pays whom, which event creates the cash flow and when that event is observed. A quantity without a currency, price basis or time convention cannot be validated by checking its magnitude alone. Preserve the original contract and build a separate normalised ticket; changing the source document to match the calculator would erase the evidence of a mismatch. Distinguish facts supplied in the question from choices introduced to make the teaching model solvable. If an exercise omits a necessary field, name the missing field before calculating. In an interview, this is a way to demonstrate judgement rather than evade the question. State a conditional assumption, explain its effect, and then solve the bounded problem that assumption defines. A reproducible answer allows another learner to recreate the same contract without guessing which convention the author intended."),
    ("Economic mechanism", "Explain the cash-flow mechanism in words before manipulating symbols. Identify the quantity being valued, the hedge or replication that motivates the formula, and the variable that is allowed to change. Keep a position's direction separate from the instrument's standalone price. A protection buyer, a fixed-rate payer and a long option do not share a universal sign rule. Map each sign to the actual cash flow of the product in this course. The model is useful because it isolates a mechanism under controlled assumptions; it cannot establish that all other mechanisms disappear. Ask what would happen in a limiting state, such as zero exposure, unchanged market inputs or an extinguished contract. A contradiction in that simple state is a stronger debugging signal than a plausible-looking result in the centre of the parameter range. Explain the mechanism to a sales colleague using currency and timing, then return to the notation to verify that both descriptions agree."),
    ("Mathematical argument", "Treat a derivation as a chain of justified transformations. State what is held fixed, identify the probability or discounting convention if one is used, and distinguish an exact identity from a local approximation. An equality between cash flows is stronger than a relationship that neglects higher-order terms. Write the intermediate steps so a reviewer can identify the point at which a modelling assumption enters. Dimensional analysis is part of the argument: discount factors are dimensionless, rates depend on a compounding convention and risk measures carry units. After deriving a result, test a boundary or a symmetric shock. This helps distinguish an algebra error from a model limitation. Do not turn a convenient mathematical hypothesis into an empirical claim about the market. In particular, a risk-neutral expectation does not forecast realised returns, and a deterministic scenario does not come with a probability merely because its output is precise."),
    ("Numerical implementation", "Implement the smallest transparent calculation that expresses the model. Store the input ticket, conventions and raw output before formatting rounded numbers for a reader. Use decimal rates internally and convert basis points or volatility points only at clearly identified boundaries. If an algorithm searches for a root, retain its bracket, stopping rule and repricing residual; convergence of an iteration is not by itself proof that the chosen contract is correct. A calculation that is not supported should fail explicitly rather than substitute another product. Compare a hand calculation or independently derived relation with the engine result. Differences at the last displayed digit can be rounding; a sign reversal or a factor of one hundred requires investigation. Keep teaching parameters separate from claimed market observations, and state whether the result is a unit price, a currency amount, a return or a local risk exposure."),
    ("Risk interpretation", "Translate the result into a response to a stated market move. A sensitivity is defined around a particular input state and convention. Its sign belongs to a signed position, while its magnitude depends on scale, maturity and the chosen risk coordinate. Test the response using an actual change in the underlying input rather than inferring it from a label. Separate the magnitude of a one-basis-point exposure from the signed P&L of a widening or a rate increase. For a larger shock, compare a local estimate with a consistent full repricing where the model supports one. The difference can reflect convexity, cross effects or changed contractual state; it should not be hidden inside an unrelated risk bucket. A hedge is a new trade with its own risks and costs. State the exposure it reduces, the instrument used and the important exposure that remains."),
    ("Control and counterexample", "Try to falsify the calculation before defending it. Recheck the input source, contract version, units and sign, then apply a control that is logically different from repeating the same function. A replication identity, a monotonicity condition, a limiting payoff or an independently computed finite difference can reveal an error that another identical run will reproduce. Keep the assumptions of the control visible: a bound that is valid for European exercise may not apply unchanged to an American feature, and a single-curve identity is not automatically a multi-curve valuation. Construct a counterexample by changing one assumption, not by changing the question after seeing the answer. Record what remains valid and which part of the conclusion must be withdrawn. This is also how a useful interview response demonstrates depth: it explains both why the calculation works and the precise circumstance in which it stops answering the economic question."),
    ("Scenario and model boundary", "Use a scenario to ask a conditional question, not to claim a forecast. Identify the shocked input, its size and units, the inputs held fixed and any contractual event crossed by the move. Reuse the same valuation basis when comparing before and after states. A large move may change both the risk and the active cash-flow state, so extrapolating the initial sensitivity can become misleading. State explicitly whether the scenario is a local approximation, a full model repricing or only a conditional payoff calculation. Those are different deliverables. If a required mechanism is outside the supported model, retain the result as a bounded teaching calculation and explain what additional model or data would be needed. More simulated paths do not repair an incorrect contract, and more decimal places do not repair a missing assumption. Preserve the distinction in the final recommendation."),
    ("Desk decision and communication", "Conclude with a decision that follows from the calculation rather than a generic recommendation to be careful. Give the result with units, identify the dominant risk, name the control performed and specify the assumption most likely to invalidate the conclusion. A desk can quote conditionally, hedge a defined exposure, monitor a risk, reduce a position or escalate an unsupported feature. Choose the action appropriate to this ticket and explain what evidence would change it. Keep clean educational valuation separate from commercial spread, official risk approval or suitability advice. A concise memo is the last layer of a reproducible record: it should link to the input and calculation rather than replace them. For an interview, practise stating the mechanism aloud first, then the numerical result, then a relevant limitation. Precision and professional judgement are complementary; neither compensates for the absence of the other."),
    ("Independent validation", "Reproduce the result through a different representation. Change the implementation path while retaining the economic contract, so a common input mistake does not survive both checks unnoticed. Examples include a cash-flow sum against a compact formula, a finite difference against an analytic derivative, or a deterministic benchmark against a simulated estimator. Choose a tolerance justified by rounding, root accuracy or sampling error. A tolerance selected only after observing a discrepancy is not an independent validation rule. Explain which source of error the comparison measures and which it cannot measure. Two implementations that share the same wrong payoff may agree perfectly, and a confidence interval about a biased specification does not certify the model. Preserve the alternative derivation, input snapshot and discrepancy so a reviewer can repeat the check without the original user's environment."),
    ("Transfer to a changed assumption", "A final transfer task changes one economically meaningful assumption and asks the learner to predict the effect before recomputing. Keep the remaining ticket fixed and identify whether the change affects a cash flow, a probability model, a risk coordinate or an operational constraint. Explain the expected direction if the model permits a reliable sign; if it does not, say why competing effects make a sign assertion unsafe. Recalculate only within supported limits and compare with the original answer. The objective is reasoning, not memorising the original number. A correct response may be to refuse an invalid model extension and describe the additional data or methodology required. Record the changed assumption and the learner's explanation separately from the numerical result. This distinguishes genuine transfer practice from a repeated worked example with a different heading."),
)


def _widget(kind, title, params):
    return "```uiblock\n" + f"type: {kind}\ntitle: {title}\nparams: " + json.dumps(params, ensure_ascii=False) + "\n```"


def calculator_ticket(course, ticket=None):
    """Adapt legacy parser keywords only; never substitute a fallback scenario.

    These three old calculator families parse French technical labels. The
    authored English ticket is fixed by the course specification; its numbers,
    product and units stay unchanged. Both strings are retained in metadata.
    """
    value=ticket or course.ticket
    rules={
        "bond": (("market value","notionnel"),("modified duration","duration"),("yield rises","le taux monte de")),
        "barrier": (("FX down-and-out call","Option barriere FX down-and-out"),("barrier ","barriere down-and-out "),("notional EUR","notionnel EUR"),("Terminal spot","Spot a")),
        "autocall": (("initial level","niveau initial"),("autocall barrier","barriere autocall"),
                     ("coupon barrier","barriere coupon"),("protection barrier","barriere protection"),
                     ("per observation with memory","par observation avec memoire"),("notional","notionnel"),("Observed levels","Niveaux observes")),
    }
    for original,replacement in rules.get(course.key,()):
        value=re.sub(re.escape(original),lambda match: replacement,value,flags=re.I)
    if re.findall(r"\d+(?:\.\d+)?",value)!=re.findall(r"\d+(?:\.\d+)?",ticket or course.ticket):
        raise ValueError("Parser keyword adaptation changed numerical constraints")
    return value


def _pack(course, calculator, ticket=None):
    raw=calculator.build_pack(calculator_ticket(course,ticket),family_hint=course.family)
    if not raw.steps:
        raise RuntimeError(f"No verified numerical pack for English course {course.slug}")
    view=english_pack(raw)
    # Legacy curve-parser conventions are metadata inputs; learner-facing
    # substitutions use English labels while retaining every numeric literal.
    return replace(view,steps=[replace(step,substitution=step.substitution.replace("frequence=annuelle","frequency=annual")) for step in view.steps])


def _calculation(pack, *, all_steps=True, selected=0):
    steps = pack.steps if all_steps else [pack.steps[selected % len(pack.steps)]] if pack.steps else []
    if not steps:
        return "No numerical result is available for this ticket. Escalate the unsupported input; do not invent a correction."
    lines = []
    for index, step in enumerate(steps, 1):
        lines.extend([f"{index}. **{step.label}**", f"   - Formula: `{step.formula}`.",
                      f"   - Substitution: `{step.substitution}`.", f"   - Result: **{step.result}**.",
                      f"   - Interpretation: {step.desk_comment}"])
    return "\n".join(lines)


def _scenario_widget(pack, title):
    return _widget("scenario_table", title, {"rowLabel": "Checked calculation", "cols": ["Substitution", "Result", "Meaning"],
        "rows": [step.label for step in pack.steps], "cells": [[s.substitution, s.result, s.desk_comment] for s in pack.steps],
        "sourceStatus": "Deterministic synthetic teaching ticket; not market observations or an executable quote."})


def _practical_widget(course, pack):
    if course.key in {"vanilla_bs", "stochastic"}:
        price=next(float(s.result) for s in pack.steps if s.label=="Call price")
        return _widget("payoff","Synthetic call: distinguish terminal payoff from net premium",{"kind":"call","strike":100,"spot":100,"premium":price,"qty":1})
    if course.key=="greeks":
        return _widget("greeks_scenario","Signed book: compare spot and volatility contributions",{"delta":250000,"gamma":-80000,"vega":120000,"theta":-15000,"spotMove":-2,"volMove":3})
    if course.key=="barrier":
        return _widget("payoff","Conditional FX barrier payoff; path survival required",{"kind":"barrier","strike":1.1,"spot":1.08,"barrier":1,"rebate":0})
    if course.key=="autocall":
        return _widget("payoff","Synthetic autocall: threshold and capital-state experiment",{"kind":"autocall","spot":100,"notional":1000000,"autocallBarrier":1.0,"couponBarrier":.7,"protectionBarrier":.6,"couponRate":.06})
    if course.key=="vol_smile":
        return _widget("vol_smile","Flat 20% benchmark: change a quote coordinate",{"matrix":[[.2]*5 for _ in range(5)]})
    if course.key=="monte_carlo":
        return _widget("monte_carlo","European GBM benchmark: estimate and sampling precision",{"paths":20000,"spot":100,"strike":100,"vol":.2,"T":1})
    labels={"swap":["Short-tenor rate","Long-tenor rate"],"yield_curve":["First pillar quote","Last pillar quote"],
            "bond":["Reference rate","Credit spread"],"cds":["Single-name spread","Index spread"],
            "var":["First risk factor","Second risk factor"]}[course.key]
    return ("This separate two-factor experiment uses a **hypothetical correlation of 0.6**, not an estimate from market data or this ticket. "
            "Its purpose is to examine why offsetting parallel risk does not remove a twist or basis exposure. "
            "The positive-semidefinite matrix is an input to that experiment; it does not calibrate the curve, price the product or certify a hedge.\n\n"
            + _widget("corr_matrix","Synthetic dependence lab: expose imperfect hedge alignment",{"labels":labels,"matrix":[[1,.6],[.6,1]]}))


def _quiz(course):
    blocks = []
    offset = list(COURSES).index(course.key) if course.key in COURSES else 0
    for number, (stem, correct, distractors, explanation) in enumerate(course.quiz, 1):
        reasons=dict(zip(distractors,FEEDBACK[course.key][number-1],strict=True))
        position = (offset + number - 1) % 5
        options = list(distractors)
        options.insert(position, correct)
        lines = [f"**Q{number}. {stem}**", ""]
        lines += [f"{letter}. {text}" for letter, text in zip("ABCDE", options)]
        lines += ["", f"Answer: **{'ABCDE'[position]}**. {explanation}", "", "Why the other answers fail:"]
        for letter, option in zip("ABCDE", options):
            if letter != "ABCDE"[position]:
                lines.append(f"- {letter}: {reasons[option]}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def _sources(context, course):
    """Short, exact quotations plus the raw locator ledger, never reconstructed."""
    from .generation import MaterialGenerator
    from .api import _COURSE_REFERENCE_ALLOWLIST, _reference_match_text
    rules = _COURSE_REFERENCE_ALLOWLIST.get(course.slug, ())
    original_chunks={(item.chunk.document_id,item.chunk.chunk_index):item.chunk.content
        for item in context.retrieved if hasattr(item.chunk,"document_id") and hasattr(item.chunk,"chunk_index")}
    ledger, references, seen, budget = [], [], set(), {}
    for item in context.sources:
        raw = item.snippet or ""
        if not MaterialGenerator._presentable_source_snippet(raw):
            continue
        if re.search(r"\b(?:journal of|university press|bibliograph|isbn|doi\.org)\b",raw,re.I):
            continue
        keywords=MaterialGenerator._FAMILY_KEYWORDS.get(course.family,())
        if keywords and not any(word in (raw+" "+(item.title or "")).lower() for word in keywords):
            continue
        title = re.sub(r"\s*[-–—]?\s*[\[(]?\s*PDFDrive\s*[\])]?\s*", "", item.title or "Source document", flags=re.I).strip()
        if title.count("(")>title.count(")"): title=title.rstrip(" (")
        words = re.findall(r"\S+", raw)
        excerpt = " ".join(words[:12])
        locator = (item.document_id, item.chunk_index)
        original=original_chunks.get(locator)
        if original is not None and _reference_match_text(excerpt) not in _reference_match_text(original):
            continue
        if locator in seen:
            continue
        seen.add(locator)
        ledger.append({"marker": f"S{len(ledger)+1}", "document_id": item.document_id,
            "chunk_index": item.chunk_index, "title": title, "snippet": excerpt,
            "snippet_sha256": hashlib.sha256(raw.encode()).hexdigest(), "retrieval_score": item.score})
        anchors = [anchor for anchor, document, index in rules if (document, index) == locator]
        if anchors:
            # Retain a contiguous, whitespace-normalised piece of the actual
            # quotation that includes an already independently reviewed anchor.
            sentences=re.split(r"(?<=[.!?])\s+(?=[A-Z])",re.sub(r"\s+"," ",raw).strip())
            complete=[sentence for sentence in sentences if len(sentence.split())<=24
                      and len(re.sub(r"[^A-Za-z0-9]","",sentence))>=45
                      and re.search(r"[.!?]$",sentence)]
            candidates = complete+[" ".join(words[i:i+24]) for i in range(max(1, len(words)-23))]
            quote = next((value for value in candidates if any(a in _reference_match_text(value) for a in anchors)), "")
            if quote and budget.get(item.document_id, 0) + len(quote.split()) <= 24 and len(references) < 4:
                if not re.search(r"[.!?]$",quote): quote+="…"
                references.append(f"- *{title}* — «{quote}»")
                budget[item.document_id] = budget.get(item.document_id, 0) + len(quote.split())
    return ledger, references


def build_english_course(request, context, calculator):
    key = detect_topic_key(request.topic, request.product, request.concepts)
    course = COURSES.get(key)
    if course is None:
        return (f"# English course unavailable: {request.topic}\n\nNo authored English curriculum currently matches this topic. "
                "No French substitute or source-grounding claim is made. Request a supported course or author and review a new curriculum.",
                {"schema_version": SCHEMA, "language": "en", "authoring_status": "unsupported_topic", "release_eligible": False})
    count = max(8, min(10, request.module_count))
    lessons = course.lessons[:count]
    pack = _pack(course, calculator)
    ledger, references = _sources(context, course)
    blocks = [f"# {course.title}", PROVENANCE, "## Course promise",
              f"Price, explain and challenge **{course.product}** in a bounded bank-derivatives interview case. "
              "The target is a master's student or early-career markets candidate. Work from the actual cash flows to an auditable result and a conditional desk decision. "
              "The material is practice, not a prediction of hiring outcomes or certification of professional competence.",
              "## Level and study plan", f"Level: {request.level}. Suggested study time: {request.duration_minutes} minutes. Language: English. "
              "Split the course into short sessions: first attempt the task without the correction, then compare the numerical method, and finally explain a changed assumption aloud.",
              "## Prerequisites", course.prerequisite, "## Learning objectives",
              f"- Reconstruct the cash flows of {course.product} and state their units.\n- Derive the principal valuation or risk relation under explicit assumptions.\n"
              "- Reproduce the verified numerical ticket and perform an independent control.\n- Explain a misconception and a changed assumption.\n- Produce a conditional quote, hedge, monitoring or escalation memo.",
              "## Contract and controlled assumptions", course.boundary,
              "## Module plan"]
    for index, lesson in enumerate(lessons, 1):
        blocks.append(f"### Module {index} - {lesson.title}\nObjective: {lesson.challenge}\nDeliverable: a written calculation or argument, an independent control and a desk action.")
    blocks.append("## Written course")
    for index, lesson in enumerate(lessons, 1):
        stage, method = STAGES[index-1]
        selected = pack.steps[(index-1) % len(pack.steps)] if pack.steps else None
        body = [f"### Lesson {index} - {lesson.title}", "**Desk situation.** " + lesson.challenge,
                "**Concept.** " + lesson.concept, f"**Working method — {stage.lower()}.** {method}",
                "**Assumptions.** Use the controlled contract stated above; the derivation does not silently extend its domain.", "**Equation and derivation.**", "$$\n" + lesson.equation + "\n$$",
                "\n".join(f"{n}. {step}" for n, step in enumerate(lesson.derivation, 1)),
                "**Checked application.** The following is one component of the common teaching ticket, not a market observation. "
                "Keep its unit and conditioning assumptions when explaining it; it is not a general result for every contract with the same product name.",
                _calculation(pack, all_steps=False, selected=index-1),
                "**Try before checking.** " + lesson.challenge,
                "**Reasoned correction.** " + lesson.answer,
                "**Decision checkpoint.** Identify the action justified by your answer and the assumption that would invalidate it. Retain your written reasoning for review.",
                _widget("equation", lesson.title, {"latex": lesson.equation}),
                _scenario_widget(pack, f"Lesson {index}: compare the ticket's verified quantities")]
        if index in {1, max(1,len(lessons)//2),len(lessons)}:
            body.append(_practical_widget(course,pack))
        blocks.append("\n\n".join(body))
    blocks += ["## Worked numerical example", "Synthetic calculator ticket (not a live quote):\n\n" + course.ticket,
               "### Model assumptions", "\n".join(f"- {value}" for value in pack.assumptions),
               "### Verified result and method", _calculation(pack),
               "### Independent controls", _control_protocol(course),
               "## Corrected exercises", _exercises(course, calculator),
               "## Synthesis desk case — model to decision", _capstone(course, pack),
               "## Course-specific quiz", _quiz(course),
               "## Calculation and implementation lab", _implementation_lab(course, pack),
               "## Model limitations", "\n".join(f"- {value}" for value in pack.warnings), course.boundary,
               "## Student and junior-professional checkpoint", _checkpoint(course),
               "## Source coverage", f"{len(ledger)} readable retrieved chunk locators were retained. "
               "The instructional prose is original; retrieving a chapter is not evidence that its authors wrote or endorsed this course. "
               "Short quotations below are verbatim and retain their original language. Source coverage does not grant redistribution rights. "
               "The corpus may lack a dedicated worked solution, and no extracted exercise or solution is claimed.",
               "## References", "\n".join(references) if references else "No readable source quotation is available. The course is not eligible for source-backed publication.",
               "## Source Appendix (back-office)",
               "\n".join(f"- [{s['marker']}] {s['title']} (document {s['document_id']}, chunk {s['chunk_index']}): {s['snippet']}" for s in ledger)]
    metadata = {"schema_version": SCHEMA, "language": "en", "authoring_status": "original_english_deterministic",
        "llm": "template", "llm_used": False, "course_title": course.title,
        "course_slug": course.slug, "topic_key": key, "module_count": len(lessons),
        "release_eligible": False, "release_gate": "strict_98_plus_independent_review_required",
        "calculation_pack": asdict(pack), "source_ledger": ledger,
        "authored_ticket":course.ticket,"calculator_ticket":calculator_ticket(course),
        "no_live_market_data": True, "no_automatic_mastery": True}
    return "\n\n".join(blocks), metadata


def _control_protocol(course):
    return f"""Use four distinct controls on this {course.product} ticket.

1. **Contract control.** Reconstruct who receives each cash flow and when. Identify exercise, observation, reset or default conditions before applying a valuation expression. Confirm currency and price basis. A perfect match to the wrong payoff is still a failed control.
2. **Unit and sign control.** Convert rates from percentages, basis points or volatility points at a named boundary. Scale unit prices by signed exposure only once. Explain the sign using the economic cash flow rather than a memorised association with the product name. Keep gross sensitivity magnitudes separate from signed scenario P&L.
3. **Independent mathematical control.** Use a cash-flow identity, monotonicity result, boundary value or independent finite difference. Document the assumptions that make the control valid. Re-running the same engine with the same inputs demonstrates reproducibility but does not independently validate its formula.
4. **Decision control.** Ask whether the displayed result answers the actual request. A conditional terminal payoff is not a current price; a local P&L estimate is not a fully revalued stress; a model reference is not an executable quote. Name the missing model, data or contractual information before proposing an action beyond the supported calculation.

For any disagreement, preserve both outputs and reconcile inputs before changing the model. State a tolerance justified by display rounding or numerical approximation, not a threshold chosen after observing the error. Record the review so that another student can reproduce the same control without access to your browser state.
"""


def _exercises(course, calculator):
    # Separate written tasks over a fixed auditable ticket; no artificial claim
    # that changing headings creates an unseen numerical transfer assessment.
    pack = _pack(course, calculator)
    questions = [
        ("Reconstruct and calculate", "Starting from the supplied ticket, state the contract, all rate/risk conventions and the signed position. Reproduce each computed quantity before looking at the correction. Explain why the currency or risk unit is attached to that quantity.", _calculation(pack)),
        ("Find the operational error", f"A colleague supplies the same computed values but treats them as a guarantee that every {course.product} can be quoted and perfectly hedged at those numbers. Identify the unsupported inference and propose a control before using the result.", _control_protocol(course)),
        ("Defend the changed assumption", "Keep the numerical ticket fixed, then change one contractual or modelling assumption named in the course boundary. State which original results remain useful and which calculation must be replaced. Do not supply a new price if the model does not support the changed contract.", course.boundary + "\n\n" + course.risk + "\n\nA correct transfer answer identifies the changed assumption, the mechanism affected, the additional data or model required and a bounded action. A plausible extra number is not an acceptable substitute for that chain of reasoning."),
    ]
    blocks = []
    for index, (title, question, correction) in enumerate(questions, 1):
        blocks += [f"### Exercise {index} — {title}", "**Task.** " + question,
                   "**Correction.**\n\n" + correction,
                   "**Self-review.** Check the method, units, sign, assumptions and limitation separately. Record what you originally wrote before reading this correction. "
                   "Agreement with the numerical result is one observation; it does not establish that you explained the hedge or recognised the model boundary. "
                   "A reviewer should be able to identify the exact line you would change after feedback rather than a generic statement that more practice is needed."]
    return "\n\n".join(blocks)


def _capstone(course, pack):
    result = pack.steps[-1].result if pack.steps else "unavailable"
    return f"""A sales colleague requests an immediate indication on the teaching ticket while one of the assumptions is awaiting confirmation. You have a deterministic output, a risk limit to respect and an interview panel asking you to justify the decision. Treat the deadline as an operational constraint, not permission to invent a market input.

**Initial evidence.** The contract is {course.product}. The stated numerical ticket is: {course.ticket} The final reported calculation component is {result}; it is not automatically the option's price or a complete profitability measure. Identify what the component measures before using it in a sentence. The primary risks are: {course.risk}

**Required submission.** Produce a six-part memo. First identify the product, side, currency, scale and observation or exercise conditions. Second list given inputs separately from assumptions introduced by the model. Third reproduce the calculation and attach the unit of each intermediate quantity. Fourth show an independent control, including the assumptions under which it is valid. Fifth describe one adverse scenario and distinguish a local approximation from a full repricing. Sixth choose a conditional action and a trigger for revisiting it.

**Reasoned decision.** If the missing information is inside the assumptions that materially determine the result, issue only a clearly conditional educational reference and request confirmation. If the requested contract lies outside the model boundary, escalate rather than relabel it as a supported product. If the inputs are complete and controls reconcile, explain the reference result and the remaining hedge risk before discussing any commercial spread. Official risk approval, suitability and an actual executable market quote require evidence outside this teaching case.

**What makes the answer useful.** A trader needs to understand the cash amount and dominant risk; a risk colleague needs the stress and model boundary; sales needs an explanation that does not promise certainty the calculation cannot provide. Keep those perspectives consistent with the same ticket and timestamp. Do not make three different assumptions to make three narratives sound persuasive. Preserve the learner's own memo so later feedback can be compared with the original reasoning.

**Debrief.** Ask which assumption drove the answer most strongly and how you would obtain better evidence. State whether a more advanced model would change the economic contract, only the approximation, or merely the numerical accuracy. Those are different reasons to improve the calculation and should lead to different next actions.
"""


def _implementation_lab(course, pack):
    tool_instruction = (f"Use `tpl tools example {course.tool}` to inspect the corresponding canonical tool's actual schema, then adapt a copy with the same economic conventions. "
                        "The tool example is a separate synthetic ticket: do not assume it has the course's notional or maturity without comparing every field."
                        if course.tool else "This course uses a bounded course-specific calculator scenario; it does not expose a dedicated full market pricer for this contract. "
                        "Reproduce its stated formula directly and preserve the distinction between scenario cash flow, local risk estimate and a full present-value calculation.")
    return f"""The calculation is a model experiment with a declared ticket. Export the numerical inputs and results before editing them. {tool_instruction} A course-bound scenario that lacks a dedicated full pricer must stay a scenario, not masquerade as one.

### Reproducibility record
Keep product, signed side, quantity, currency, valuation date, expiry or cash-flow schedule, day count, compounding, market-input provenance and model limitations. Add the raw output and any version or analysis identifier exposed by the selected engine. A display screenshot is not enough because a later user cannot reconstruct the exact input conventions from a rounded chart. Never include a login token in an exported record, notebook, forum post or shared link.

### One-variable experiment
Predict the effect of a small change before calculating it. Choose an input the model actually supports and hold the other contractual fields fixed. Record original and changed values with units. Recompute and compare with the predicted direction or local sensitivity. If the effect does not have a universally valid sign, explain the competing mechanisms rather than manufacture one. A failed prediction is useful evidence: identify the assumption or cash-flow effect you overlooked.

### Numerical and model error
Separate input error, floating-point or root-finding error, simulation sampling error, local approximation error and economic model error. More precision can reduce numerical error; more paths can reduce sampling error; neither makes an incorrect payoff or an unsupported market assumption correct. In the present case, the controlled boundary is: {course.boundary} Treat that boundary as part of the result, not a footnote that can be discarded when quoting.

### Risk and sign experiment
Reverse the position sign while keeping the underlying contract fixed. A signed portfolio PV and its linear exposures should reverse, whereas an unsigned contractual payoff definition and a positive risk magnitude may not. Explain which quantity is which before asserting symmetry. Then scale the notional or quantity and verify linear scaling only where the contract and model imply it. Some risk statistics or nonlinear aggregation rules do not scale by simply adding standalone values.

### Independent implementation
Write a small spreadsheet or notebook using the equations in the derivation rather than copying formatted output. Use explicit decimal rates and labelled columns. Show one boundary or cash-flow identity and explain its expected result in advance. Choose a tolerance according to the numerical method. A second implementation that simply calls the same function is a reproducibility check; describe it honestly and add an independently reasoned control if validation is required.

### Review and communication
Explain the result aloud in under two minutes: contract, mechanism, number and unit, dominant risk, control and limitation. Then answer a follow-up that changes one assumption. Preserve your initial answer and identify the correction after review. This course does not automatically grade the written argument, certify mastery or claim an employer will use the same question. Its measurable output is your retained calculation and reasoning, with enough detail to be reviewed by another person.
"""


def _checkpoint(course):
    return f"""**Master's student.** Derive the principal relationship without reading the worked solution. State the role of every input, reproduce the calculator result and explain a boundary case. Answer the quiz and explain why at least one plausible distractor is wrong. A learner who remembers the number but cannot explain the assumptions should repeat the derivation and transfer task.

**Junior front-office candidate.** Translate the {course.product} result into a signed exposure and a conditional desk action. Identify which control you performed, which market or contract information remains unverified and which risk the proposed hedge leaves behind. Distinguish a theoretical reference from executable pricing and official approval.

**Evidence and review.** Keep the original written answer, the corrected method, the changed-assumption response and a short note on what improved. Review those records after an interval rather than marking completion from page opening alone. Completion is a declared learning action; the presence of a model answer does not establish independent performance. Ask a peer or instructor to challenge the economic explanation, not just compare the displayed result.
"""
