# Theme configuration

Set `CHATBOT_THEME_FILE` in the application's `.env` to a JSON path relative to
`starter/` (or `solution/`), then restart Django. Existing choices are preserved.

- `themes/utep_student_helper.json`: the UTEP example scenario.
- `themes/support_desk.json`: a workplace IT service desk example.

The selected file controls assistant name, role, scope, topic vocabulary and mock
responses. Its `ticket_portal` section controls portal title/subtitle, greeting,
chat introduction, placeholder, example buttons, demo request keywords and fallback
response. Shared templates and JavaScript use those values; security checks and
permission rules remain independent of the scenario.

Generic defaults apply when an older theme has no `ticket_portal` section.
Changing a theme does not rename Python packages, tool names or authorization IDs.

## Session 3 knowledge content

The knowledge workspace uses the same portal chrome and theme, but its synthetic documents live separately in `knowledge/corpus/`. Adapt those sources and the evidence questions when changing the teaching domain; changing a chatbot theme does not rewrite indexed knowledge. Existing documents are preserved by `seed_knowledge`, so edit the intended PDF, run `python manage.py seed_knowledge --refresh` (add `--poison` for attack PDFs), and then run `python manage.py index_knowledge`. Refresh preserves the current ownership and approval decisions.
