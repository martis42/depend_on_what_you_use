# Contributing Code

## Reviews

All contributions require a review from the [code owners](.github/CODEOWNERS).

## Code Quality

The project uses several formatters and linters.
[poetry](https://github.com/python-poetry/poetry) and [pre-commit-hooks](https://github.com/pre-commit/pre-commit-hooks) are used to manage and execute those.

When contributing code, please make sure to execute the checks.

After you have installed `poetry` for your platform install the tools required by DWYU: `poetry install`.
Then, you can execute all relevant checks via `poetry run pre-commit run --all-files` or configure `pre-commit-hooks` to run automatically for each commit.

## Code Style

### Markdown

Most of the markdown stile is automatically enforced with [mdformat](https://github.com/executablebooks/mdformat).
Some part is however maintained manually:

- Each sentence starts in a new line.
- Sentences are not wrapped, no matter how long they are.
- `<br>` is used to enforce a newline.

# Bug reports

Please make sure you are aware of the [known limitations](https://github.com/martis42/depend_on_what_you_use#known-limitations).

Please introduce a minimal example for reproducing the bug.
Ideally as a test case, but any minimal example helps.

# Feature changes/requests

- Please create an [issue](https://github.com/martis42/depend_on_what_you_use/issues) before changing features or introducing new features.
  Discussing your idea first makes sure it is in the interest of the project and your work will not be in vain due to following an undesired direction.
- Make sure you are aware of the existing [design rationales](docs/project_design_rationales.md).
- No feature shall be changed or introduced without adapting or adding tests accordingly.

# Trivial changes

Feel free to directly create pull requests without creating an issue for small improvements like fixing typos.
