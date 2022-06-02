import pandas as pd


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
