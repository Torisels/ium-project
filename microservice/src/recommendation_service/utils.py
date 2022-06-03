import pandas as pd
from pathlib import Path
import sys


def load_models():
    return {
        "basic": 1,
        "advanced": 3,
        "random": 4
    }


def user_exists(user_id: int, users: pd.DataFrame) -> bool:
    return user_id in users["user_id"].values


def load_users():
    users = pd.read_json("../../../data/users.jsonl", lines=True)
    return users


def get_folder_path(relative_path: str) -> Path:
    return (Path(sys.argv[0]).parent / relative_path).resolve()


def get_api_version(version_file_path: str) -> str:
    with open(get_folder_path(version_file_path), "r") as f:
        return f.read().strip()
