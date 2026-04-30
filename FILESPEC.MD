Ello to all the future devs working on this project if you are confused on the structure well here it is a short explaination of what each file does. 

Regards,
Sparklee.dev

# Nodeway CLI – Architecture & File Structure

This document explains the structure of the Nodeway CLI project, what each file does, and why it exists.
The goal is to help contributors quickly understand how the system is organized and where to add new features.

---

## 🧱 Overview

The project is split into clear layers:

* **CLI Layer (`commands/`)** → Handles user input and output
* **Service Layer (`services/`)** → Handles API + WebSocket logic
* **Core Layer (`core/`)** → Shared utilities and client setup
* **Config Layer (`config.py`)** → Manages persistent configuration

---

## 📁 Project Structure

```
nodeway/
│
├── main.py
├── config.py
│
├── core/
│   ├── client.py
│   ├── utils.py
│
├── services/
│   ├── server_service.py
│   ├── websocket_service.py
│
├── commands/
│   ├── auth.py
│   ├── servers.py
│   ├── console.py
│   ├── files.py
│
└── requirements.txt
```

---

## 🚀 Entry Point

### `main.py`

**What it does:**

* Starts the CLI
* Parses user input
* Routes commands to appropriate handlers

**Why it exists:**

* Keeps CLI logic centralized
* Prevents command logic from being scattered across files

---

## ⚙️ Configuration

### `config.py`

**What it does:**

* Loads and saves configuration from `~/.nodeway/config.json`
* Stores:

  * API key
  * Panel URL
  * Default server (optional)

**Why it exists:**

* Centralizes configuration handling
* Avoids duplicating file I/O across the project

---

## 🧠 Core Layer

### `core/client.py`

**What it does:**

* Creates and returns a configured `PterodactylClient`

**Why it exists:**

* Prevents repeating client initialization everywhere
* Ensures consistent API usage across the project

---

### `core/utils.py`

**What it does:**

* Contains reusable helper functions
* Examples:

  * Server selector (interactive menu)
  * Formatting helpers
  * CLI display utilities

**Why it exists:**

* Avoids duplicating common logic
* Keeps command files clean

---

## 🔌 Service Layer

### `services/server_service.py`

**What it does:**

* Wraps all server-related API calls:

  * list servers
  * start/stop/restart
  * utilization/stats

**Why it exists:**

* Separates API logic from CLI logic
* Makes it easier to modify backend behavior without touching commands

---

### `services/websocket_service.py`

**What it does:**

* Handles WebSocket connections for console streaming
* Manages:

  * authentication
  * message handling
  * sending commands

**Why it exists:**

* Isolates complex WebSocket logic
* Keeps CLI layer simple and readable

---

## 💻 Command Layer

Each file represents a command group.

---

### `commands/auth.py`

**What it does:**

* Handles authentication-related commands:

  * `login`
  * `whoami`
  * `clean` (logout/reset)

**Why it exists:**

* Keeps auth logic separate from other commands
* Makes it easier to extend (e.g., multi-account support)

---

### `commands/servers.py`

**What it does:**

* Handles server-related commands:

  * `servers list`
  * `servers start`
  * `servers stop`
  * `servers restart`
  * `servers stats`

**Why it exists:**

* Groups all server operations in one place
* Provides a structured command system

---

### `commands/console.py`

**What it does:**

* Connects to server console via WebSocket
* Streams logs and allows command input

**Why it exists:**

* Separates real-time logic from standard commands
* Keeps console complexity isolated

---

### `commands/files.py`

**What it does:**

* Placeholder for file management commands:

  * list files
  * read/write files
  * delete files

**Why it exists:**

* Prepares the project for future expansion
* Keeps file operations separate from server logic

---

## 📦 Dependencies

### `requirements.txt`

**What it does:**

* Lists all required Python packages

**Why it exists:**

* Ensures reproducible environments
* Simplifies setup for contributors

---

## 🧠 Design Principles

### 1. Separation of Concerns

* CLI logic ≠ API logic ≠ WebSocket logic

### 2. Single Responsibility

* Each file has one clear purpose

### 3. Reusability

* Shared logic goes into `core/` or `services/`

### 4. Scalability

* New features should fit into existing layers without restructuring

---

## ➕ Adding New Features

When adding functionality:

* CLI command → `commands/`
* API interaction → `services/`
* Shared helpers → `core/`

Example:

* Add backups → `commands/backups.py` + `services/backup_service.py`

---

## ⚠️ Rules

* Do not call the API directly inside `commands/`
* Do not handle user input inside `services/`
* Avoid global state outside `config.py`

---

## 💬 Summary

This structure is designed to keep the project:

* Easy to understand
* Easy to extend
* Easy to maintain

If something feels “out of place”, it probably is—follow the layer rules above.
