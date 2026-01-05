# 🧙 GitHub Wizard

> A GitHub CLI extension for neurodivergent developers. Smart session management, AI-powered task breakdown, and beautiful terminal UI.

## Features ✨

- **Hyperfocus Session Manager** - Save and resume work context automatically
- **Pomodoro Timer** - Integrated focus timer with break reminders and stats
- **Eisenhower Matrix** - Prioritize tasks by urgency and importance
- **Smart Task Breakdown** - Complex workflows split into manageable steps  
- **Beautiful Terminal UI** - Color-coded priorities, progress tracking with Rich
- **Multi-Repo Dashboard** - Status view across all your projects at once
- **Daily Stats** - Track your focus time, sessions, and completed tasks
- **Context Preservation** - Never lose your place between sessions

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

### 1. Manage Priorities
Start by organizing your tasks using the Eisenhower Matrix:

```bash
# Add a new task
gh wizard priorities add

# View your matrix
gh wizard priorities matrix

# List tasks by priority
gh wizard priorities list
```

### 2. Focus with Pomodoro
Start a focus session to get work done:

```bash
# Start a standard Pomodoro session (25m work / 5m break)
gh wizard pomodoro start

# Work on a specific task from your matrix
gh wizard pomodoro work-on "Fix login bug"
```

### 3. Track Progress
See how you're doing:

```bash
# View daily statistics
gh wizard stats

# View your repos status (Coming Soon)
gh wizard dashboard
```

### 4. Manage Sessions
Save your context when you need to switch gears:

```bash
# Start a hyperfocus session
gh wizard session start "HyperCode AST improvements"

# Pause and save context
gh wizard session pause

# Resume previous work
gh wizard session resume
```

## Command Reference

| Command Group | Command | Description |
|--------------|---------|-------------|
| **priorities** | `add` | Add a task to the Eisenhower Matrix |
| | `matrix` | View tasks in the 4-quadrant matrix |
| | `list` | List tasks as a simple list |
| | `done [id]` | Mark a task as complete |
| **pomodoro** | `start` | Start a timer (default: 25m work, 5m short, 15m long) |
| | `work-on [id]` | Start a timer for a specific task |
| | `complete-task` | Complete a task and record stats |
| **session** | `start [name]` | Begin a new named session |
| | `resume` | Resume the last active session |
| | `pause` | Pause current session |
| | `list` | List all saved sessions |
| **general** | `stats` | Show daily focus stats |
| | `break [task]` | AI breakdown of a complex task |
| | `dashboard` | Multi-repo status view |

## Architecture

```
gh-wizard/
├── src/gh_wizard/
│   ├── __init__.py           # Package initialization
│   ├── cli.py                # Click CLI entry point
│   ├── pomodoro.py           # Pomodoro timer logic
│   ├── priorities.py         # Eisenhower Matrix logic
│   ├── stats.py              # Statistics tracking
│   ├── session.py            # Session management
│   ├── tasks.py              # Task breakdown engine
│   ├── github_api.py         # GraphQL API client
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

## Project Status

**Phase 1 (Completed)** - Core Foundation
- [x] CLI structure with Rich UI
- [x] Basic session save/restore
- [x] GitHub API integration foundation

**Phase 2 (In Progress)** - Brain-Friendly Features
- [x] Eisenhower Matrix (Priorities)
- [x] Pomodoro Timer
- [x] Visual progress tracking
- [x] Daily Statistics
- [ ] Break reminders customization

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
