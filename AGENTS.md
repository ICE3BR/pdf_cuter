# Repository Guidelines

## Project Structure

The application entrypoint is `main.py`; PDF processing is isolated in `pdf_service.py`, and automated checks live in `tests/`. Keep sample PDFs and other non-code resources under an assets or fixtures directory when adding new files. Keep generated files, virtual environments, caches, and local configuration out of version control. Before adding a new top-level directory, check whether an existing source, test, or asset location is appropriate.

## Build, Test, and Development Commands

Use the commands defined by `pyproject.toml` and `README.md` as the source of truth. This project uses `uv` and Python 3.13:

- `uv sync` creates or updates the local environment and installs runtime/development dependencies.
- `uv run python main.py` starts the GUI locally.
- `uv run pytest` runs the complete test suite.
- `./build.ps1` builds the Windows executable with PyInstaller.
- `./build.ps1 -Clean` removes only the generated `build` and `dist` directories before building.

Run the project’s formatter and linter before opening a pull request if they are configured. Do not commit generated output or machine-specific settings. GUI changes should also be checked manually in both light and dark themes.

## Coding Style & Naming

Follow the existing Python conventions. Use four spaces for indentation and avoid unrelated formatting changes. Name modules and functions in `snake_case`, classes in `PascalCase`, and constants in `UPPER_SNAKE_CASE`. Prefer small, focused functions and clear names, especially around PDF parsing, page selection, GUI state, and file output.

The GUI uses `customtkinter` with `tkinterdnd2` for drag-and-drop. Keep the default appearance mode light and preserve the functional light/dark toggle. PDF work runs in `threading.Thread`; use `threading.Event` for cooperative cancellation, and schedule all widget updates through the GUI event loop with `after()`. Worker threads must not manipulate widgets directly.

## Testing Guidelines

Add or update tests with every behavior change. Cover normal PDFs, invalid or empty input, protected files, page-boundary cases, cancellation cleanup, repeated output names, and output-file errors where applicable. Name tests after the behavior they verify, such as `test_extracts_selected_pages`. Run `uv run pytest` locally before submitting changes. For GUI-only changes, manually verify file selection, drag-and-drop, progress, cancellation, help, clickable portfolio link, and both appearance modes.

## Commits & Pull Requests

Write short, imperative commit subjects (for example, `Fix page range validation`). Pull requests should explain the user-visible change, include reproduction or verification steps, link related issues, and attach screenshots or sample output when the change affects a UI or generated PDF. Keep each pull request focused and mention any known limitations.

## Security & Configuration

Never commit credentials, private documents, or local environment files. Treat uploaded PDFs and output paths as untrusted input; validate file types and paths, sanitize output names, and handle failures without exposing sensitive content. Never alter or delete the original PDF. Generated output belongs under the user’s Downloads directory, while build artifacts remain outside version control.
