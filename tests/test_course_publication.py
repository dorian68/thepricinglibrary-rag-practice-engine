from __future__ import annotations

import hashlib
import json
import re

import pytest

from pricinglibrary_rag.api import _COURSE_REFERENCE_ALLOWLIST, _public_course_markdown
from pricinglibrary_rag.course_publication import accepted_english_course, spread_uniform_quiz_answers


def test_only_exact_reviewed_bytes_make_english_available(tmp_path):
    directory = tmp_path / "en"
    directory.mkdir()
    path = directory / "fixture.md"
    content = "# Synthetic English fixture\n\nNo commercial-content quality claim.\n"
    path.write_bytes(content.encode("utf-8"))
    assert accepted_english_course(tmp_path, path.name) is None
    index = {"schema_version":"tpl.course.language-index.v1", "approval_basis":"synthetic_test_fixture_only",
             "courses":[{"slug":"fixture", "sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
                         "status":"draft"}]}
    def write_index():
        (directory / "_index.json").write_text(json.dumps(index), encoding="utf-8")
    write_index()
    assert accepted_english_course(tmp_path, path.name) is None
    index["courses"][0]["status"] = "accepted_98_and_independent_review"
    write_index()
    assert accepted_english_course(tmp_path, path.name) == content
    path.write_bytes((content + "Unreviewed edit.\n").encode("utf-8"))
    assert accepted_english_course(tmp_path, path.name) is None
    path.write_bytes(content.encode("utf-8"))
    index["courses"].append(dict(index["courses"][0]))
    write_index()
    assert accepted_english_course(tmp_path, path.name) is None


@pytest.mark.parametrize("filename", ["../fixture.md", "en/fixture.md", "_index.json", "fixture"])
def test_english_publication_rejects_noncanonical_paths(tmp_path, filename):
    assert accepted_english_course(tmp_path, filename) is None


def _bank(letters):
    return "## Quiz de cours\n\n" + "\n\n".join(
        f"**Q{i+1}. What changes under scenario {i+1}?**\n" +
        "\n".join(f"- {letter}) Scenario {i+1} answer {letter}" for letter in "ABCD") +
        f"\n  - Réponse: **{answer}**. Explain the assumptions for scenario {i+1}."
        for i, answer in enumerate(letters)) + "\n\n## Next lesson\nContent unchanged."


def _correct_texts(markdown):
    blocks = re.findall(r"(?ms)^\*\*Q\d+\..*?(?=^\*\*Q|^## |\Z)", markdown)
    return [dict(re.findall(r"(?m)^- ([A-D])\) (.+)$", block))[
        re.search(r"Réponse: \*\*([A-D])\*\*", block)[1]] for block in blocks]


def test_uniform_quiz_key_is_spread_without_changing_correct_answers_or_explanations():
    original = _bank("BBBBB")
    projected = spread_uniform_quiz_answers(original)
    assert _correct_texts(projected) == _correct_texts(original)
    assert len(set(re.findall(r"Réponse: \*\*([A-D])\*\*", projected))) == 4
    assert projected.count("Explain the assumptions") == 5
    assert "## Next lesson\nContent unchanged." in projected
    assert spread_uniform_quiz_answers(projected) == projected
    varied = _bank("ADBCB")
    assert spread_uniform_quiz_answers(varied) == varied


def test_malformed_quiz_is_left_for_editorial_review_instead_of_guessing_an_answer():
    malformed = _bank("AAAAA").replace("Réponse: **A**", "No key supplied", 1)
    assert spread_uniform_quiz_answers(malformed) == malformed


def test_english_projection_keeps_real_lesson_math_and_reviewed_references_only():
    anchor = _COURSE_REFERENCE_ALLOWLIST["vanilla-options-quote"][0][0]
    # A short registry anchor alone is intentionally not a publishable quote.
    # This synthetic test excerpt exercises the projection, not corpus rights.
    fixture_quote = "Synthetic projection fixture: " + anchor + " with explicit carry conventions and a local hedge."
    original = f"""---
slug: vanilla-options-quote
language: en
---
# European options
## Written course
### Lesson 1 - Carry
The call uses matching continuous carry and discounting assumptions.
$$C-P=S e^{{-qT}}-K e^{{-rT}}$$
_[genere - theorie, formules verifiees par un professionnel]_
<!-- Superseded generic quiz and internal editorial note. -->
## References
- *Reviewed source* — «{fixture_quote}»
- *Invented source* — «This unrelated purported quotation must not pass the reviewed anchor registry.»
## Source coverage
Internal retrieval diagnostics should stay private.
## Source Appendix (back-office)
Private source machinery and chunk identifiers.
"""
    result = _public_course_markdown(original)
    assert "## Written course" in result and "### Lesson 1 - Carry" in result
    assert "$$C-P=S e^{-qT}-K e^{-rT}$$" in result
    assert "## References" in result and anchor in result
    assert not any(word in result for word in ("Superseded", "Invented", "retrieval diagnostics", "chunk identifiers", "professionnel", "[genere"))
