# Private lesson content

Full paid lessons and corpus extracts are not distributed in this public code
repository. Supply operator-reviewed lesson Markdown in this directory, or set
`TPL_COURSE_SCRIPTS_DIR` to a private content directory on the backend host.

The course API enforces signed identity and server-owned entitlements before
serving those files. A source checkout does not include a licence to a textbook
corpus or evidence that commercial source rights have been cleared.

English variants live under `en/`. Delivery additionally requires
`en/_index.json` with schema `tpl.course.language-index.v1` and one entry per
accepted slug: its exact raw-file SHA-256 and status
`accepted_98_and_independent_review`. A file alone, an unreviewed status or a
changed hash does not enable that language in the catalogue or reader. The
strict content gate and independent review precede promotion; the French
delivery contract remains unchanged. See `docs/ENGLISH_COURSE_ACCEPTANCE.md`
and `scripts/generate_english_courses.py --help` for the controlled workflow.

On 2026-11-14, generated course artifacts were removed from the current Git tree
without deleting local files or rewriting previous history. Earlier public Git
history may still contain those artifacts; excluding them now does not revoke
copies already published. Review historical disclosure and source rights before
a public commercial launch.
