# Contributing to AidOps AI

Thank you for your interest in contributing to AidOps AI! This document provides guidelines and instructions for contributing to the project.

## 🎯 Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## 🚀 Getting Started

### Prerequisites

**Backend:**
- Python 3.11+
- pip and virtualenv
- Redis (for local development)

**Frontend:**
- Node.js 20+
- npm or yarn

### Development Setup

1. **Fork and clone the repository:**
```bash
git clone https://github.com/yourusername/aidops-ai.git
cd aidops-ai
```

2. **Set up backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env
```

3. **Set up frontend:**
```bash
cd frontend
npm install
cp .env.example .env.local
```

4. **Install pre-commit hooks:**
```bash
pip install pre-commit
pre-commit install
```

## 📝 Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions or updates

### 2. Make Your Changes

Follow the coding standards outlined below.

### 3. Test Your Changes

**Backend:**
```bash
cd backend
pytest tests/ -v
ruff check .
black --check .
mypy app/
```

**Frontend:**
```bash
cd frontend
npm run lint
npm run type-check
npm test
```

### 4. Commit Your Changes

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git commit -m "feat: add grant matching workflow"
git commit -m "fix: resolve citation display bug"
git commit -m "docs: update API documentation"
```

Commit types:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Test additions or updates
- `chore:` - Maintenance tasks

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with:
- Clear description of changes
- Link to related issues
- Screenshots (for UI changes)
- Test results

## 🏗️ Project Structure

```
aidops-ai/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── api/      # API routes
│   │   ├── core/     # Core models and providers
│   │   ├── services/ # Business logic
│   │   ├── agents/   # LangChain agents
│   │   └── utils/    # Utilities
│   ├── tests/        # Backend tests
│   └── evals/        # Evaluation harness
├── frontend/         # Next.js frontend
│   └── src/
│       ├── app/      # Next.js pages
│       ├── components/ # React components
│       ├── lib/      # Utilities
│       └── types/    # TypeScript types
├── data/sample/      # Sample datasets
├── infra/            # Infrastructure configs
└── docs/             # Documentation
```

## 💻 Coding Standards

### Backend (Python)

**Style:**
- Follow PEP 8
- Use `black` for formatting (line length: 100)
- Use `ruff` for linting
- Use type hints everywhere

**Example:**
```python
from typing import Optional

async def process_document(
    file_path: str,
    chunk_size: int = 500,
    metadata: Optional[dict] = None
) -> list[DocumentChunk]:
    """Process a document and return chunks.
    
    Args:
        file_path: Path to the document
        chunk_size: Size of each chunk in tokens
        metadata: Optional metadata to attach
        
    Returns:
        List of document chunks
    """
    # Implementation
    pass
```

**Testing:**
- Write tests for all new features
- Aim for >80% code coverage
- Use pytest fixtures for common setup
- Mock external dependencies

### Frontend (TypeScript/React)

**Style:**
- Use TypeScript strict mode
- Follow React best practices
- Use functional components with hooks
- Use Tailwind CSS for styling

**Example:**
```typescript
interface MessageProps {
  content: string
  role: 'user' | 'assistant'
  citations?: Citation[]
}

export function Message({ content, role, citations }: MessageProps) {
  return (
    <div className={cn('rounded-lg p-4', {
      'bg-primary text-primary-foreground': role === 'user',
      'bg-muted': role === 'assistant'
    })}>
      <p>{content}</p>
      {citations && <CitationList citations={citations} />}
    </div>
  )
}
```

**Testing:**
- Write component tests for UI components
- Test user interactions
- Test edge cases and error states

## 🔍 Code Review Process

All contributions go through code review:

1. **Automated Checks**: CI must pass (linting, type-checking, tests)
2. **Code Review**: At least one maintainer approval required
3. **Testing**: Verify changes work in demo mode
4. **Documentation**: Update docs if needed

### Review Checklist

- [ ] Code follows project style guidelines
- [ ] Tests added for new features
- [ ] All tests passing
- [ ] Documentation updated
- [ ] No breaking changes (or properly documented)
- [ ] Commit messages follow conventions
- [ ] PR description is clear and complete

## 🐛 Reporting Bugs

Use GitHub Issues with the bug template:

**Required Information:**
- AidOps AI version
- Operating system
- Python/Node.js version
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs
- Screenshots (if applicable)

## 💡 Suggesting Features

Use GitHub Issues with the feature template:

**Required Information:**
- Clear description of the feature
- Use case and motivation
- Proposed implementation (optional)
- Alternatives considered
- Impact on existing features

## 📚 Documentation

Documentation improvements are always welcome:

- **Code Comments**: Explain complex logic
- **Docstrings**: All public functions/classes
- **README**: Keep up-to-date
- **API Docs**: Document new endpoints
- **Architecture Docs**: Explain design decisions

## 🔐 Security

**Reporting Security Issues:**
- Do NOT open public issues for security vulnerabilities
- Email security@aidops-ai.example.com
- Include detailed description and reproduction steps
- Allow time for fix before public disclosure

## 📋 Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests pass locally

## Screenshots (if applicable)
Add screenshots for UI changes

## Related Issues
Closes #123
```

## 🎓 Learning Resources

**Backend:**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangChain Documentation](https://python.langchain.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

**Frontend:**
- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

**RAG & AI:**
- [Pinecone Learning Center](https://www.pinecone.io/learn/)
- [OpenAI Cookbook](https://github.com/openai/openai-cookbook)

## 🤝 Community

- GitHub Discussions for questions
- Discord server (link TBD)
- Monthly community calls

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to AidOps AI! 🙏
