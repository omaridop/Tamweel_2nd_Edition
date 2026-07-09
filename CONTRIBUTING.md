# Contributing to Tamweel AI

First off, thank you for considering contributing to Tamweel AI. It's people like you that make open source such a fantastic community!

## 1. Setting Up Your Development Environment

To start developing on Tamweel AI locally:

1. Clone the repository: `git clone https://github.com/your-org/tamweel-ai.git`
2. Copy the `.env.example` file to `.env` and fill in your keys.
3. Boot the environment using Docker:
   ```bash
   docker compose up --build
   ```

## 2. Running Tests

We expect all new features and bug fixes to be tested before submission.
Our test suite resides in the `tests/` directory.

To run the automated test suite locally:
```bash
python -m pytest tests/ -v
```

## 3. Code Style Expectations

- **Backend**: We follow `PEP 8` and enforce strictly typed Python (`mypy` compliant). All code is checked via `flake8`.
- **Frontend**: We follow React best practices, using functional components and hooks. ESLint is enforced.
- **Commits**: Please use conventional commits (e.g., `feat: added caching`, `fix: auth bug`).

## 4. Pull Request Guidelines

1. **Fork** the repository and create your branch from `main`.
2. **Ensure tests pass** before opening a PR.
3. **Describe your changes** clearly in the PR description.
4. Do **not** commit `.env` files, `.pkl` models (unless updating the baseline), or database dumps.
5. A maintainer will review your code. Please be open to feedback and iteration!
