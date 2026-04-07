# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Web Builder is a simple static site generator written in Python. It scans a source directory tree, then generates a target directory containing HTML (rendered from Markdown via markdown-it-py with CommonMark), copied images, and static files. All pages use "pretty URLs" (e.g., `about/index.html` instead of `about.html`).

## Commands

- **Run the builder:** `uv run build <source> <target>`
- **Lint/format (via pre-commit):** `uv run pre-commit run --all-files`
- **Ruff only:** `uv run ruff check` / `uv run ruff format`
- **Run tests:** `uv run pytest`

## Tooling

- Python 3.14, managed with `uv`
- Pre-commit hooks: ruff-check and ruff-format
- Tests via pytest (tests in `tests/`)

## Architecture

The pipeline is two phases: **scan** then **build**.

1. **`__main__.py`** — CLI entry point. Parses `source` and `target` args, calls `scan_source()` then `build_target()`.
2. **`scanner.py`** — Recursively walks the source directory, building a tree of `Node` objects. Special files `index.md` and `config.json` are attached as content/config to their parent directory node rather than becoming child nodes. Dotfiles and symlinks are skipped.
3. **`node.py`** — `Node` class representing a source entry. Each node has a `NodeType` (HOME, DIRECTORY, PAGE, IMAGE, STATIC) determined by whether it's a dir or by file extension. Nodes compute their own `directory_target`, `copy_target`, and `content_target` paths relative to the output root.
4. **`builder.py`** — Walks the node tree and for each node: creates directories, copies static/image files, and renders Markdown content to `index.html`. Backs up existing target directories with a timestamp suffix before building.
