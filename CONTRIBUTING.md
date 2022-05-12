# Contributing Code

## Reviews

All contributions require a review from the [code owners](.github/CODEOWNERS).

## Code Style and Code Quality

The project uses several formatters and linters. `poetry` and `pre-commit-hooks` are used to manage and execute those.
When contributing code, please make sure to execute the checks.

After you have installed `poetry` for your platform install the tools required by DWYU: `poetry install`.
Then, you can execute all relevant checks via `poetry run pre-commit run --all-files` or configure `pre-commit-hooks`
to run automatically for each commit.

# Bug reports

Please make sure you are aware of the [known limitations](https://github.com/martis42/depend_on_what_you_use#known-limitations).

Please introduce a minimal example for reproducing the bug.
Ideally as a test case, but any minimal example helps.

# Feature changes/requests

- Please create an [issue](https://github.com/martis42/depend_on_what_you_use/issues) before changing features or introducing new features.
  Discussing your idea first makes sure it is in the interest of the project and your work will not be in vain due to following an undesired direction.
- Make sure you are aware of the existing [design decisions](docs/design_decisions.md).
- No feature shall be changed or introduced without adapting or adding tests accordingly.

# Trivial changes

Feel free to directly create pull requests without creating an issue for small improvements like fixing typos.
