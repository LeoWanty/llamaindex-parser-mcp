# Agent Instructions

This document outlines the process for AI agents to contribute to this project. Please follow these guidelines to ensure a smooth development workflow.

## Project Overview

This project is an MCP (Machine-Checked Protocol) server for `llamaindex` parsers. The goal is to expose `llamaindex`'s data parsing capabilities as a service.

## Agent Development Process

Follow these steps when working on this project:

1.  **Clarify Requirements**: If the user's request is not specific enough, ask clarifying questions and present a summary of the updated requirements to ensure alignment.

2.  **Propose a Plan**: Before writing any code, propose a clear, step-by-step plan.

3.  **Integrate Feedback**: If the user provides feedback on the plan, integrate it before proceeding.

4.  **Implementation Strategy**:
    *   **Documentation**: Can be written directly.
    *   **Updating Existing Features**: Changes can be made directly to the existing code.
    *   **New Features**:
        1.  First, create placeholders for classes, methods, and functions.
        2.  Add tests that showcase the intended functionality of the new feature.
        3.  After user validation of the placeholders and tests, fill in the implementation details.

5.  **Ensure Tests Pass**: All tests must pass before submitting work. If tests need to be rewritten, ask the user for permission first.

## Dependencies

- **Management**: Project dependencies are managed in the `pyproject.toml` file using the `uv` dependency manager. Do not edit files manually; use `uv` commands.
- **Adding Dependencies**: When adding a new dependency, use `uv add <package_name>`. For development-only dependencies, use `uv add <package_name> --dev`.
- **Installation**: To set up the project for local development, run `uv sync` to install dependencies from the lock file, followed by `uv pip install -e .` to install the local package in editable mode.

## Testing

- **Framework**: This project uses `pytest` for testing.
- **Running Tests**: Run the test suite using the `pytest` command from the root of the repository.
- **Test Coverage**: All new features must be accompanied by tests.
- **Passing Tests**: Ensure that all tests are passing before submitting your changes.

## Code Style and Linting

- **Linter & Formatter**: This project uses `ruff` for linting and code formatting.
- **Usage**: Before submitting your changes, run `ruff check . --fix` to fix any linting issues and `ruff format .` to format the code.

## Versioning

- **Source of Truth**: The project version is managed in the `pyproject.toml` file under the `[project].version` key.
- **Bumping**: Do not update the project version unless explicitly asked to do so by the user.

## Submitting Changes

Once you have completed all the steps above:

1.  **Propose Changes**: Propose your changes to the user for review.
2.  **Request Publishing**: If the user approves, ask for the changes to be published to a branch.
