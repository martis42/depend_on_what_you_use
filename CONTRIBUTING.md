# Bug reports

- Make sure you are aware of the [known limitations](https://github.com/martis42/depend_on_what_you_use#known-limitations).
- Please provide a minimal example for reproducing the bug.

# Feature changes/requests

- Please create an [issue](https://github.com/martis42/depend_on_what_you_use/issues) before changing features or introducing new features.
  Discussing your idea first makes sure it is in the interest of the project and your work will not be in vain due to following an undesired direction.
- Make sure you are aware of the existing [design rationales](docs/project_design_rationales.md).

# Trivial changes

Feel free to directly create pull requests for small improvements like fixing typos without creating an issue first.
Please have a look at the rules for [contributing code](#contributing-code) before doing so.

# Contributing code

## Commits

Commit messages should follow the [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) style.

## Reviews

All contributions require a review from the [code owners](.github/CODEOWNERS).

## Testing

No feature shall be changed or introduced without adapting or adding tests accordingly.

## Code Quality

The project uses several formatters and linters which are executed with [pre-commit](https://github.com/pre-commit/pre-commit).
Given you have installed `pre-commit` locally, you can run all basic checks via `pre-commit run --all-files`.

There are also bash scripts for executing most steps of the CI:

- [test_basic.sh](./test_basic.sh) - Linting and fast tests
- [test_full.sh](./test_full.sh) - Full test suite including integration tests

## Code Style

### Markdown

Most of the markdown stile is automatically enforced with [mdformat](https://github.com/executablebooks/mdformat).
Some part is however maintained manually:

- Each sentence starts in a new line.
- Sentences are not wrapped, no matter how long they are.
- `<br>` is used to enforce a newline.
