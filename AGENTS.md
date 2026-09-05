# Agent Guide

## Project

Depend on what you use (DWYU) is a Bazel aspect for C++ projects.
It checks that C++ targets directly depend on the targets that provide their included headers.
It also detects unused dependencies and can validate `implementation_deps` usage when that feature is enabled.

## Repository Layout

- `dwyu/cc/` contains the public Starlark API and the C++ aspect implementation.
- `dwyu/apply_fixes/` contains the Python command-line tool that applies fixes in BUILD files for the problems discoverd by DWYU.
- `dwyu/private/` contains internal Starlark utilities.
- `test/` contains unit, integration, workspace, benchmark, and BCR-release tests.
- `examples/` contains complete Bazel workspaces that demonstrate and test user-facing configurations.
- `docs/` contains project, API, and troubleshooting documentation.

## Contribution Rules

- Read [CONTRIBUTING.md](CONTRIBUTING.md) before making non-trivial changes.
- Feature changes require a prior issue discussion; trivial documentation and typo fixes may be proposed directly.
- Read [docs/project/design_rationales.md](docs/project/design_rationales.md) before changing behavior or design.
- Update or add tests whenever behavior changes.
- Use Conventional Commits for commit messages.
- All contributions require review from the code owners.
- Keep changes narrowly scoped and do not revert unrelated worktree changes.

## Development And Validation

- Use Bazel 7.6.0 or later and Python 3.10 or later.
- Run the narrowest applicable Bazel target or test while developing.
- Run `prek run --all-files` when `prek` is installed, or `pre-commit run --all-files` when `pre-commit` is installed, for baseline formatting and linting checks.
- Run `scripts/test_stack_core.sh` for pre-commit checks, Bazel unit tests, sanitizers, DWYU, clang-tidy, C++11 compatibility, aspect-script tests, and example builds.
- Run `scripts/test_stack_integration.sh` for example, workspace-integration, aspect, and apply-fixes integration tests.
- Run the relevant stack script before proposing a broad or cross-cutting change when the environment supports it.

## Code And Documentation Style

- Follow existing Bazel, Starlark, Python, and shell patterns in the nearest related code.
- Do not hand-edit generated files; use the repository's existing generators or checks when applicable.
- Format Markdown with `mdformat` through the configured pre-commit tooling.
- In Markdown source, start each sentence on a new line and do not manually wrap long sentences.
- Use `<br>` only when a forced line break is needed in rendered Markdown.

## Working With Tests

- Prefer extending the nearest existing test case over creating a parallel test framework.
- Keep test fixtures and examples representative of the user-facing Bazel behavior being changed.
- For a change to the apply-fixes tool, inspect and update the relevant cases under `test/apply_fixes/`.
- For a change to the aspect, inspect and update the matching tests under `test/aspect/` and the relevant examples.
