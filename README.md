# Nodeway CLI

A production-grade command-line interface for the Nodeway hosting platform. Inspired by the sleek UX of Claude Code and Vercel CLI.

## Features

- 🚀 **Interactive Shell**: Full REPL with auto-completion and command history.
- 📁 **File Manager**: Manage server files with a clean, panel-based interface.
- 📟 **Live Console**: Real-time server terminal via WebSockets.
- 🛡️ **Secure Auth**: Local credential encryption and secure session handling.
- ⚡ **Modern Architecture**: Built with `Typer`, `prompt-toolkit`, and `src/` layout.

## Installation

### From PyPI
```bash
pip install nodeway
```

### From npm
```bash
npm install nodeway
```

### From Source
```bash
git clone https://github.com/nodeway/nodeway-cli.git
cd nodeway-cli
pip install -e .
```

## Usage

### Interactive Mode (Recommended)
Simply run `nodeway` to enter the interactive shell:
```bash
nodeway
```

### One-off Commands
```bash
nodeway login
nodeway servers list
nodeway shell <server_id>
```

## Architecture

- **`nodeway.api`**: Low-level API client wrappers.
- **`nodeway.services`**: Business logic and complex workflows (e.g., WebSocket handling).
- **`nodeway.commands`**: CLI command handlers.
- **`nodeway.ui`**: Centralized UI toolkit for consistent styling.
- **`nodeway.core`**: Configuration management and constants.

## Future Roadmap

- [ ] Standalone Binary builds (PyInstaller)
- [ ] NPM Wrapper support
- [ ] GitHub Actions for automated releases

## License

MIT
