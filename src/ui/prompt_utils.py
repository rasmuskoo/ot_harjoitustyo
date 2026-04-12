"""Utilities for terminal input prompts."""

from getpass import getpass


def prompt(label: str) -> str:
    """Show a flushed prompt and return one line of user input."""
    print(label, end="", flush=True)
    return input()


def prompt_secret(label: str) -> str:
    """Read hidden input when possible, fallback to visible input."""
    try:
        return getpass(label)
    except OSError:
        return prompt(label)
