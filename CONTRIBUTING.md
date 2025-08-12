# Contribution Guidelines

This document outlines the guidelines for contributing to this project. Please read these guidelines before contributing.

## Code Style and Linting

We use [Ruff](https://github.com/astral-sh/ruff) for code formatting and linting. Please format and lint your code with Ruff before submitting a pull request.

To check for linting errors, run:
```bash
ruff check .
```

To automatically fix linting errors and format the code, run:
```bash
ruff format .
```

We follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide for Python code. Ruff helps enforce this standard.

## Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification for our commit messages. This helps us maintain a clear and descriptive commit history.

Each commit message should consist of a **header**, a **body**, and a **footer**.

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

- **type**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `ci`, `build`, `perf`.
- **scope**: The scope of the change (e.g., `server`, `parser`, `deps`).
- **description**: A short summary of the change.

Example:
```
feat(parser): add support for parsing docx files
```

## Branching Strategy

- We use a simple feature branching strategy.
- All new features and bug fixes should be developed in a separate branch.
- Branch names should be descriptive and prefixed with `feat/`, `fix/`, `docs/`, etc.
- Once the feature or fix is complete, open a pull request to merge it into the `main` branch.

## Testing

- All new features should be accompanied by tests.
- All bug fixes should include a regression test.
- Make sure all tests pass before submitting a pull request.
- To run the tests, use the following command: `pytest`

## How to Contribute

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them with a descriptive commit message.
4. Push your changes to your fork.
5. Open a pull request to the `main` branch of the original repository.
6. Make sure to describe your changes in the pull request.
7. Wait for a review and address any feedback.
8. Once your pull request is approved, it will be merged into the `main` branch.

Thank you for contributing to our project!
