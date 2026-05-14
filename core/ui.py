"""
core/ui.py — Centralized UI toolkit for the Nodeway CLI.
All styled output flows through here to keep the rest of the codebase clean.
Inspired by Claude Code's terminal UX.
"""

import sys
import time
import threading
import shutil
import os
import platform

from prompt_toolkit import prompt as pt_prompt
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.shortcuts import clear


# ─── Enable ANSI escape codes on Windows ─────────────────────────────
# Without this, colors and box-drawing chars show as garbage on cmd/powershell

def _enable_windows_ansi():
    """Enable Virtual Terminal Processing on Windows so ANSI codes work."""
    if platform.system() != "Windows":
        return
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        # STD_OUTPUT_HANDLE = -11
        handle = kernel32.GetStdHandle(-11)
        # ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        mode = ctypes.c_ulong()
        kernel32.GetConsoleMode(handle, ctypes.byref(mode))
        kernel32.SetConsoleMode(handle, mode.value | 0x0004)
    except Exception:
        # Fallback — this sometimes helps on older Windows
        os.system("")

_enable_windows_ansi()



# ─── ANSI color codes ────────────────────────────────────────────────

class Colors:
    RESET    = "\033[0m"
    BOLD     = "\033[1m"
    DIM      = "\033[2m"
    ITALIC   = "\033[3m"
    UNDERLINE = "\033[4m"

    # Foreground
    BLACK    = "\033[30m"
    RED      = "\033[31m"
    GREEN    = "\033[32m"
    YELLOW   = "\033[33m"
    BLUE     = "\033[34m"
    MAGENTA  = "\033[35m"
    CYAN     = "\033[36m"
    WHITE    = "\033[37m"

    # Bright foreground
    BRIGHT_BLACK   = "\033[90m"
    BRIGHT_RED     = "\033[91m"
    BRIGHT_GREEN   = "\033[92m"
    BRIGHT_YELLOW  = "\033[93m"
    BRIGHT_BLUE    = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN    = "\033[96m"
    BRIGHT_WHITE   = "\033[97m"

    # Background
    BG_RED     = "\033[41m"
    BG_GREEN   = "\033[42m"
    BG_YELLOW  = "\033[43m"
    BG_BLUE    = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN    = "\033[46m"

C = Colors


# ─── Terminal width helper ────────────────────────────────────────────

def term_width():
    """Get terminal width, default 80 if detection fails."""
    try:
        return shutil.get_terminal_size().columns
    except:
        return 80


# ─── Styled print ────────────────────────────────────────────────────

def success(msg):
    """Print a success message with a green checkmark."""
    print(f"  {C.BRIGHT_GREEN}✓{C.RESET} {msg}")

def error(msg):
    """Print an error message with a red X."""
    print(f"  {C.BRIGHT_RED}✗{C.RESET} {msg}")

def info(msg):
    """Print an info message with a cyan dot."""
    print(f"  {C.BRIGHT_CYAN}●{C.RESET} {msg}")

def warn(msg):
    """Print a warning message with a yellow triangle."""
    print(f"  {C.BRIGHT_YELLOW}⚠{C.RESET} {msg}")

def dim(msg):
    """Print dimmed/secondary text."""
    print(f"  {C.DIM}{msg}{C.RESET}")

def muted(msg):
    """Return a dimmed string (doesn't print)."""
    return f"{C.DIM}{msg}{C.RESET}"

def accent(msg):
    """Return a cyan-accented string (doesn't print)."""
    return f"{C.BRIGHT_CYAN}{msg}{C.RESET}"

def bold(msg):
    """Return a bold string (doesn't print)."""
    return f"{C.BOLD}{msg}{C.RESET}"


# ─── Dividers ─────────────────────────────────────────────────────────

def divider(char="─", color=C.BRIGHT_BLACK):
    """Print a horizontal divider line."""
    w = term_width() - 4
    print(f"  {color}{char * w}{C.RESET}")

def blank():
    """Print a blank line."""
    print()


# ─── Panels (bordered output blocks) ─────────────────────────────────

def panel(title, lines, color=C.BRIGHT_CYAN, width=None):
    """
    Render a bordered panel, like Claude Code's response blocks.

    Args:
        title: Panel header text
        lines: List of strings to display inside
        color: ANSI color for the border
        width: Panel width (auto-detected if None)
    """
    w = (width or term_width()) - 4
    inner = w - 4  # padding inside the box

    # Top border
    print(f"  {color}╭{'─' * (w - 2)}╮{C.RESET}")

    # Title
    padded_title = f" {title} "
    title_len = len(title) + 2
    remaining = w - 2 - title_len
    print(f"  {color}│{C.RESET}{C.BOLD}{padded_title}{C.RESET}{' ' * remaining}{color}│{C.RESET}")

    # Separator under title
    print(f"  {color}├{'─' * (w - 2)}┤{C.RESET}")

    # Content lines
    for line in lines:
        # Strip ANSI for length calculation
        stripped = _strip_ansi(line)
        pad = inner - len(stripped)
        if pad < 0:
            pad = 0
        print(f"  {color}│{C.RESET}  {line}{' ' * pad}{color}│{C.RESET}")

    # Bottom border
    print(f"  {color}╰{'─' * (w - 2)}╯{C.RESET}")


def _strip_ansi(s):
    """Remove ANSI escape sequences from a string for length calculations."""
    import re
    return re.sub(r'\033\[[0-9;]*m', '', s)


# ─── Tables ───────────────────────────────────────────────────────────

def render_table(headers, rows, color=C.BRIGHT_CYAN):
    """
    Render a clean table with box-drawing characters.

    Args:
        headers: List of column header strings
        rows: List of lists (each inner list = one row)
        color: ANSI color for the borders
    """
    if not rows:
        dim("No data to display.")
        return

    # Calculate column widths
    col_widths = []
    for i, header in enumerate(headers):
        max_w = len(header)
        for row in rows:
            if i < len(row):
                cell = _strip_ansi(str(row[i]))
                max_w = max(max_w, len(cell))
        col_widths.append(max_w + 2)  # padding

    # Build border strings
    top    = f"  {color}╭" + "┬".join("─" * w for w in col_widths) + f"╮{C.RESET}"
    mid    = f"  {color}├" + "┼".join("─" * w for w in col_widths) + f"┤{C.RESET}"
    bottom = f"  {color}╰" + "┴".join("─" * w for w in col_widths) + f"╯{C.RESET}"

    def format_row(cells, is_header=False):
        parts = []
        for i, w in enumerate(col_widths):
            cell = str(cells[i]) if i < len(cells) else ""
            stripped = _strip_ansi(cell)
            pad = w - len(stripped) - 1
            if is_header:
                parts.append(f" {C.BOLD}{cell}{C.RESET}{' ' * pad}")
            else:
                parts.append(f" {cell}{' ' * pad}")
        return f"  {color}│{C.RESET}" + f"{color}│{C.RESET}".join(parts) + f"{color}│{C.RESET}"

    print(top)
    print(format_row(headers, is_header=True))
    print(mid)
    for row in rows:
        print(format_row(row))
    print(bottom)


# ─── Spinner ──────────────────────────────────────────────────────────

class Spinner:
    """
    Animated spinner context manager for blocking operations.
    Usage:
        with Spinner("Connecting..."):
            do_blocking_thing()
    """
    FRAMES = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"

    def __init__(self, message="Loading..."):
        self.message = message
        self._stop = threading.Event()
        self._thread = None

    def _spin(self):
        idx = 0
        while not self._stop.is_set():
            frame = self.FRAMES[idx % len(self.FRAMES)]
            sys.stdout.write(f"\r  {C.BRIGHT_CYAN}{frame}{C.RESET} {self.message}")
            sys.stdout.flush()
            idx += 1
            time.sleep(0.08)
        # Clear spinner line
        sys.stdout.write(f"\r{' ' * (len(self.message) + 6)}\r")
        sys.stdout.flush()

    def __enter__(self):
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *args):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1)


# ─── Interactive prompts ──────────────────────────────────────────────

def confirm_prompt(message, default=False):
    """
    Styled yes/no confirmation prompt.

    Args:
        message: Question to ask
        default: Default value if user hits enter

    Returns:
        bool
    """
    hint = "Y/n" if default else "y/N"
    try:
        answer = pt_prompt(
            ANSI(f"  {C.BRIGHT_YELLOW}?{C.RESET} {message} {C.DIM}({hint}){C.RESET} ")
        ).strip().lower()

        if not answer:
            return default
        return answer in ("y", "yes")
    except (EOFError, KeyboardInterrupt):
        print()
        return False


def password_prompt(message="Password"):
    """Styled password input (masked)."""
    try:
        return pt_prompt(
            ANSI(f"  {C.BRIGHT_YELLOW}🔑{C.RESET} {message}: "),
            is_password=True
        )
    except (EOFError, KeyboardInterrupt):
        print()
        return None


def select_menu(title, options, display_fn=None):
    """
    Interactive arrow-key selector menu.

    Args:
        title: Menu title
        options: List of option values
        display_fn: Optional function to format each option for display.
                    Receives (option, index). If None, uses str(option).

    Returns:
        Selected option value, or None if cancelled.
    """
    if not options:
        warn("No options available.")
        return None

    selected = 0

    # Hide cursor
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

    try:
        print(f"\n  {C.BOLD}{title}{C.RESET}\n")
        start_line = None

        while True:
            # Move cursor up to redraw if not first draw
            if start_line is not None:
                sys.stdout.write(f"\033[{len(options)}A")

            for i, option in enumerate(options):
                if display_fn:
                    label = display_fn(option, i)
                else:
                    label = str(option)

                if i == selected:
                    sys.stdout.write(f"  {C.BRIGHT_CYAN}❯{C.RESET} {C.BRIGHT_WHITE}{label}{C.RESET}\033[K\n")
                else:
                    sys.stdout.write(f"    {C.DIM}{label}{C.RESET}\033[K\n")

            sys.stdout.flush()
            start_line = True

            # Read keypress
            key = _read_key()

            if key == "up":
                selected = (selected - 1) % len(options)
            elif key == "down":
                selected = (selected + 1) % len(options)
            elif key == "enter":
                # Show cursor again
                sys.stdout.write("\033[?25h")
                sys.stdout.flush()
                return options[selected]
            elif key == "escape" or key == "ctrl-c":
                sys.stdout.write("\033[?25h")
                sys.stdout.flush()
                return None

    except Exception:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
        return None


def _read_key():
    """Read a single keypress, handling arrow keys and special keys."""
    if platform.system() == "Windows":
        import msvcrt
        key = msvcrt.getch()

        if key == b'\xe0' or key == b'\x00':
            key2 = msvcrt.getch()
            if key2 == b'H':
                return "up"
            elif key2 == b'P':
                return "down"
            elif key2 == b'K':
                return "left"
            elif key2 == b'M':
                return "right"
        elif key == b'\r':
            return "enter"
        elif key == b'\x1b':
            return "escape"
        elif key == b'\x03':
            return "ctrl-c"

        return key.decode("utf-8", errors="ignore")
    else:
        import tty
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            key = sys.stdin.read(1)

            if key == '\x1b':
                seq = sys.stdin.read(2)
                if seq == '[A':
                    return "up"
                elif seq == '[B':
                    return "down"
                elif seq == '[C':
                    return "right"
                elif seq == '[D':
                    return "left"
                return "escape"
            elif key == '\r' or key == '\n':
                return "enter"
            elif key == '\x03':
                return "ctrl-c"
            return key
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


# ─── Banner ───────────────────────────────────────────────────────────

# Modern blue color for the ASCII art
_BRICK = "\033[38;5;75m"
# Slightly darker shade for depth
_BRICK_DIM = "\033[38;5;69m"

def render_banner(version="1.0.0", username=None):
    """
    Render a Claude Code-style splash screen with:
    1. Bordered welcome box
    2. Big chunky ASCII art
    3. Login status line
    """
    blank()

    # ── Welcome box ──
    welcome_text = f" ✻ Welcome to {C.BOLD}Nodeway CLI{C.RESET} v{version}! "
    welcome_stripped = _strip_ansi(welcome_text)
    box_w = len(welcome_stripped) + 2
    print(f"  {C.BRIGHT_BLACK}╭{'─' * box_w}╮{C.RESET}")
    print(f"  {C.BRIGHT_BLACK}│{C.RESET}{welcome_text} {C.BRIGHT_BLACK}│{C.RESET}")
    print(f"  {C.BRIGHT_BLACK}╰{'─' * box_w}╯{C.RESET}")

    blank()

    # ── Big ASCII art — chunky brick style ──
    art = [
        " ███╗   ██╗  ██████╗  ██████╗  ███████╗ ██╗    ██╗  █████╗  ██╗   ██╗",
        " ████╗  ██║ ██╔═══██╗ ██╔══██╗ ██╔════╝ ██║    ██║ ██╔══██╗ ╚██╗ ██╔╝",
        " ██╔██╗ ██║ ██║   ██║ ██║  ██║ █████╗   ██║ █╗ ██║ ███████║  ╚████╔╝ ",
        " ██║╚██╗██║ ██║   ██║ ██║  ██║ ██╔══╝   ██║███╗██║ ██╔══██║   ╚██╔╝  ",
        " ██║ ╚████║ ╚██████╔╝ ██████╔╝ ███████╗ ╚███╔███╔╝ ██║  ██║    ██║   ",
        " ╚═╝  ╚═══╝  ╚═════╝  ╚═════╝  ╚══════╝  ╚══╝╚══╝  ╚═╝  ╚═╝    ╚═╝   ",
    ]

    for line in art:
        print(f"  {_BRICK}{line}{C.RESET}")

    blank()

    # ── Login status line ──
    if username:
        print(f"  {C.BRIGHT_GREEN}🎉{C.RESET} Logged in as {C.BOLD}{C.BRIGHT_WHITE}{username}{C.RESET}. Type {C.BOLD}help{C.RESET} to get started.")
    else:
        print(f"  {C.BRIGHT_YELLOW}⚡{C.RESET} Not logged in. Type {C.BOLD}login{C.RESET} to authenticate.")

    blank()


# ─── Clear screen ────────────────────────────────────────────────────

def clear_screen():
    """Cross-platform clear screen."""
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")
