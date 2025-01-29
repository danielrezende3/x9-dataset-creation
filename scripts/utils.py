from os import listdir
from os.path import isfile, join
from pathlib import Path
import re
from typing import NoReturn


def log_error(file_name, message: str) -> NoReturn:
    """Logs an error message to the console and exits the program."""

    print(f"{file_name}: error: {message}")
    exit(1)


def get_files_from_folder(folder: Path) -> list[Path]:
    """Get a list of files in a folder"""
    return sorted(
        [Path(folder) / f for f in listdir(folder) if isfile(join(folder, f))],
        key=natural_key,  # Use a custom sorting key
    )


def validate_directories(file_name: str, *paths: Path) -> None:
    """Validate that all provided paths exist and are directories."""
    for path in paths:
        if not path.is_dir():
            log_error(file_name, f"Path '{path}' does not exist or is not a directory")


def natural_key(file_path: Path) -> list[str | int]:
    """Extract numeric parts of the file name for sorting"""
    return [
        int(text) if text.isdigit() else text
        for text in re.split(r"(\d+)", file_path.name)
    ]
