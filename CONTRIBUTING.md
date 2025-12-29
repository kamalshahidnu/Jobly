# Contributing to Jobly

Thank you for your interest in contributing to Jobly! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, inclusive, and professional in all interactions.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in Issues
2. Create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Screenshots if applicable

### Suggesting Features

1. Check if the feature has been suggested in Issues
2. Create a new issue with:
   - Clear description of the feature
   - Use case and benefits
   - Possible implementation approach
   - Any relevant examples or mockups

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/jobly.git
   cd jobly
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set up development environment**
   ```bash
   cd backend
   poetry install
   poetry run pre-commit install
   ```

4. **Make your changes**
   - Follow the code style (Black, Ruff)
   - Add tests for new functionality
   - Update documentation as needed
   - Keep commits atomic and well-described

5. **Run tests and linting**
   ```bash
   poetry run pytest
   poetry run black .
   poetry run ruff check .
   poetry run mypy jobly
   ```

6. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

   Use conventional commits:
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `test:` - Test additions/changes
   - `refactor:` - Code refactoring
   - `style:` - Formatting changes
   - `chore:` - Maintenance tasks

7. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request**
   - Provide clear description of changes
   - Reference any related issues
   - Ensure all checks pass

## Development Guidelines

### Code Style

- Follow PEP 8 guidelines
- Use Black for formatting (line length: 100)
- Use Ruff for linting
- Add type hints where applicable
- Write docstrings for public functions/classes

### Testing

- Write tests for new features
- Aim for >80% code coverage
- Use pytest fixtures for common setup
- Test both success and failure cases

### Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions/classes
- Update relevant documentation in `docs/`
- Include examples where helpful

### Agent Development

When creating new agents:

1. Extend `BaseAgent` class
2. Implement `execute()` method
3. Add type hints for input/output
4. Write comprehensive docstrings
5. Add unit tests
6. Update agent registry
7. Document in `docs/AGENTS.md`

### Adding Dependencies

1. Use Poetry to add dependencies:
   ```bash
   poetry add package-name
   ```

2. Document why the dependency is needed
3. Keep dependencies minimal
4. Prefer well-maintained packages

## Project Structure

```
jobly/
├── backend/
│   ├── jobly/          # Main package
│   │   ├── agents/     # AI agents
│   │   ├── models/     # Data models
│   │   ├── services/   # Business logic
│   │   ├── tools/      # Utilities
│   │   ├── ui/         # User interfaces
│   │   └── ...
│   └── tests/          # Test suite
├── frontend/           # React frontend (Phase 2)
├── docker/             # Docker configurations
└── docs/               # Documentation
```

## Review Process

1. **Automated checks** - CI runs tests and linting
2. **Code review** - Maintainers review your code
3. **Feedback** - Address any requested changes
4. **Approval** - Once approved, PR will be merged

## Getting Help

- **Questions?** Open a Discussion
- **Stuck?** Ask in Issues
- **Chat?** Join our Discord (link TBD)

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Credited in release notes
- Thanked in the community

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Jobly! 🙏
