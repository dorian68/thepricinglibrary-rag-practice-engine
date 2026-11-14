"""Learner projections that preserve authored answers and historical files."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re


def accepted_english_course(root: Path, filename: str) -> str | None:
    """Read exactly the English bytes accepted by both content review gates.

    A draft file alone never makes a language available. The private, operator-
    controlled index records the reviewed hash; changing a published file closes
    delivery until its new contents have been reviewed. French legacy scripts
    keep their existing delivery contract.
    """
    if Path(filename).name != filename or not filename.endswith(".md"):
        return None
    try:
        private_root = Path(root).resolve(strict=True)
        directory = (private_root / "en").resolve(strict=True)
        if directory == private_root or not directory.is_relative_to(private_root):
            return None
        index_path = (directory / "_index.json").resolve(strict=True)
        path = (directory / filename).resolve(strict=True)
        if index_path.parent != directory or path.parent != directory:
            return None
        if index_path.stat().st_size > 262_144 or path.stat().st_size > 4_194_304:
            return None
        index = json.loads(index_path.read_text(encoding="utf-8"))
        if not isinstance(index, dict) or index.get("schema_version") != "tpl.course.language-index.v1":
            return None
        entries = index.get("courses")
        if not isinstance(entries, list):
            return None
        matching = [row for row in entries if isinstance(row, dict) and row.get("slug") == filename[:-3]]
        if len(matching) != 1:
            return None
        entry = matching[0]
        digest = entry.get("sha256")
        if entry.get("status") != "accepted_98_and_independent_review" or not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            return None
        content = path.read_bytes()
        if len(content) > 4_194_304 or hashlib.sha256(content).hexdigest() != digest:
            return None
        return content.decode("utf-8")
    except (OSError, ValueError, TypeError, RuntimeError):
        return None


def spread_uniform_quiz_answers(markdown: str) -> str:
    """Avoid an accidental all-A/all-B key without rewriting any answer.

    Only a complete, unambiguous 3+ question bank with the same answer letter
    throughout is transformed. Explanations, correct option text and source
    files stay unchanged. This is a study quiz, not certified assessment.
    """
    section_re = re.compile(r"(?mi)^##[^\n]*(?:quiz)[^\n]*\n[\s\S]*?(?=^## |\Z)")
    question_re = re.compile(r"(?m)^\*\*Q\d+\.[^\n]*\*\*[ \t]*$")
    option_re = re.compile(r"(?m)^- ([A-E])\) (.+)$")
    answer_re = re.compile(r"((?:R[eé]ponse|Answer):[ \t]*\*\*)([A-E])(\*\*)", re.I)

    def project(section):
        text = section.group(0)
        starts = list(question_re.finditer(text))
        questions = []
        for index, match in enumerate(starts):
            end = starts[index + 1].start() if index + 1 < len(starts) else len(text)
            body = text[match.start():end]
            options, answer = list(option_re.finditer(body)), answer_re.search(body)
            if len(options) not in (4, 5) or answer is None:
                return text
            if [m[1] for m in options] != list("ABCDE"[:len(options)]):
                return text
            if len({m[2] for m in options}) != len(options):
                return text
            questions.append((body, options, answer))
        if len(questions) < 3 or len({answer[2] for _, _, answer in questions}) != 1:
            return text
        rendered = [text[:starts[0].start()]]
        for index, (body, options, answer) in enumerate(questions):
            values = [m[2] for m in options]
            old_index = ord(answer[2]) - ord("A")
            if not 0 <= old_index < len(values):
                return text
            wanted = index % len(values)
            rotation = (wanted - old_index) % len(values)
            reordered = values[-rotation:] + values[:-rotation] if rotation else values
            number = iter(range(len(values)))
            body = option_re.sub(lambda _: f"- {chr(65 + (i := next(number)))}) {reordered[i]}", body)
            body = answer_re.sub(lambda m: m[1] + chr(65 + wanted) + m[3], body)
            rendered.append(body)
        return "".join(rendered)

    return section_re.sub(project, markdown)
