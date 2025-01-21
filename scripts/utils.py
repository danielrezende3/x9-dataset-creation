from os import listdir
from os.path import isfile, join
from pathlib import Path

EXCLUDE_FROM_LIST = ["problem_145.py", "problem_187.py"]


def get_files_from_folder(folder: Path) -> list[Path]:
    return [
        Path(folder) / f
        for f in listdir(folder)
        if isfile(join(folder, f)) and f not in EXCLUDE_FROM_LIST
    ]
