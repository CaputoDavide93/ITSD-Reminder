# Contributing to ITSD Reminder Bot

First off, thank you for considering contributing! 🎉

## 📜 Code of Conduct

This project is governed by our commitment to fostering an open and welcoming environment.

## 🤝 How Can I Contribute?

### 🐛 Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates.

**Include:**
- Clear and descriptive title
- Steps to reproduce the issue
- Expected vs actual behavior
- Your environment (OS, Python version, Docker version)

### 💡 Suggesting Enhancements

Please provide:
- Clear and descriptive title
- Detailed description of the proposed feature
- Explanation of why this would be useful

### 🔧 Pull Requests

1. **Fork** the repository
2. **Clone** your fork locally
3. **Create a branch** for your feature:
   ```bash
   git checkout -b feature/amazing-feature
   ```
4. **Make your changes** following our coding standards
5. **Test** your changes — run `pytest -q tests` (Slack is mocked) and, for behaviour changes, try the bot against a test Slack channel
6. **Commit** with a clear message:
   ```bash
   git commit -m "feat: add amazing feature"
   ```
7. **Push** to your fork:
   ```bash
   git push origin feature/amazing-feature
   ```
8. **Open a Pull Request**

## 📏 Coding Standards

### Python
- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints where appropriate
- Write docstrings for functions and classes

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

| Type | Description |
|------|-------------|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation changes |
| `refactor:` | Code refactoring |

## 📋 Pull Request Checklist

- [ ] Code follows project standards
- [ ] `ruff check src tests` passes
- [ ] `pytest -q tests` passes (add tests for new behaviour)
- [ ] Behaviour changes were tried against a test Slack channel (describe how in the PR)
- [ ] Documentation is updated if needed
- [ ] Commit messages follow convention

---

Thank you for contributing! 🙏
