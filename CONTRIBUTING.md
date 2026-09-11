# Python coding standard

Keep the code easy to read, especially for someone learning the agent workflow.

- Use four spaces for indentation and one statement per line.
- Use Ruff's consistent formatting: double quotes, blank lines between definitions and an 88-character wrapping target. Long strings may exceed that target.
- Group imports into standard-library, third-party and project imports. Remove unused imports and variables.
- Use descriptive names such as `state`, `observation` and `question_vector` instead of unexplained single letters in the workflow.
- Give important classes and operations short docstrings. Explain decisions and constraints, rather than narrating obvious assignments.
- Keep exceptions and fallback paths explicit. Preserve existing time boundaries, account isolation and review behavior during cleanup.
- Add useful type annotations when changing interfaces; do not claim that formatter or lint checks provide complete type checking.

These conventions use [PEP 8](https://peps.python.org/pep-0008/) as a readability guide and [Ruff's Black-style formatter](https://docs.astral.sh/ruff/formatter/) for consistent layout. The 88-character wrapping target is this project's formatter convention, rather than PEP 8's default 79-character limit.

## Format and check

From an activated project virtual environment:

```bash
pip install -r requirements.txt -r requirements-dev.txt
python -m ruff check --fix .
python -m ruff format .
python -m ruff check .
python -m ruff format --check .
```

`pyproject.toml` contains the shared configuration and pins the required Ruff version. `requirements-dev.txt` pins the installed version. `.editorconfig` sets Python/TOML indentation and line endings in compatible editors.

The linter checks imports, unused names, undefined names and selected syntax/style errors. It does not replace a code review, security review or a type checker. Review automatic fixes before committing.

## Verify a change

```bash
python -m unittest discover -s tests -p product_test.py
python tests/video_ui_test.py
```

For the evidence workspace, start its backend with `npm run dev`, then run `python tests/streamlit_smoke.py`. These tests use controlled evidence/provider fixtures and do not need a new paid video analysis.

GitHub Actions checks Python formatting and lint, then runs the existing product and Streamlit tests alongside the TypeScript checks. A formatting violation makes CI fail; CI does not rewrite files. Format checks are also available locally before committing.
