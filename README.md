# 🧙 GitHub Wizard

> A GitHub CLI extension for neurodivergent developers. Smart session management, AI-powered task breakdown, and beautiful terminal UI.

## Features ✨

- **Hyperfocus Session Manager** - Save and resume work context automatically
- **Smart Task Breakdown** - Complex workflows split into manageable steps  
- **Beautiful Terminal UI** - Color-coded priorities, progress tracking with Rich
- **Multi-Repo Dashboard** - Status view across all your projects at once
- **Context Preservation** - Never lose your place between sessions
- **Pattern Learning** - Remembers your common workflows
- **Natural Language Commands** - Query repositories conversationally

## Installation

### Prerequisites
- Python 3.9+
- GitHub CLI (`gh`) installed
- GitHub personal access token

### Install as GitHub CLI Extension

```bash
gh extension install LyndzDev/gh-wizard
```

### Or Install Locally

```bash
git clone https://github.com/LyndzDev/gh-wizard
cd gh-wizard
pip install -e .
```

## Quick Start 🚀

```bash
# Start a hyperfocus session
gh wizard session start "HyperCode AST improvements"

# View your repos status
gh wizard dashboard

# Get a task breakdown
gh wizard break "Release HyperCode v2.0"

# Resume previous work
gh wizard session resume
```

## Architecture

```
gh-wizard/
├── src/gh_wizard/
│   ├── __init__.py           # Package initialization
│   ├── cli.py                # Click CLI entry point
│   ├── github_api.py         # GraphQL API client
│   ├── session.py            # Session management
│   ├── tasks.py              # Task breakdown engine
│   ├── notifications.py      # Smart notifications
│   ├── ai.py                 # Pattern learning & AI
│   ├── ui/                   # Terminal UI components
│   │   ├── __init__.py
│   │   ├── dashboard.py      # Dashboard renderer
│   │   ├── progress.py       # Progress tracking
│   │   └── colors.py         # Color schemes
│   └── utils/
│       ├── __init__.py
│       ├── config.py         # Configuration management
│       └── logger.py         # Logging setup
├── tests/
├── docs/
└── pyproject.toml
```

## Development

### Setup Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install in development mode with all dependencies
pip install -e ".[dev,docs]"

# Run tests
pytest

# Format code
black src/ tests/
ruff check src/ tests/

# Type checking
mypy src/
```

### Running Locally

```bash
python -m gh_wizard.cli --help
```

## Project Status

**Phase 1 (In Progress)** - MVP
- [ ] GitHub GraphQL API integration
- [ ] Basic session save/restore
- [ ] Multi-repo status dashboard
- [ ] CLI structure with Rich UI

**Phase 2 (Planned)** - Brain-Friendly Features
- [ ] Task breakdown engine
- [ ] Visual progress tracking
- [ ] Break reminders & Pomodoro
- [ ] Color-coded priorities

**Phase 3 (Planned)** - Intelligence
- [ ] Pattern learning
- [ ] Smart notifications
- [ ] AI context assistant
- [ ] Natural language commands

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details

## Author

Built by [Lyndz Williams](https://github.com/LyndzDev) for neurodivergent developers everywhere 💜
