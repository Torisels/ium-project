import pandas as pd
from recommendation_service.config import settings
from recommendation_service import utils


class UsersService:
    def __init__(self):
        data_folder = utils.get_folder_path(settings.data_folder_path)
        data_file = settings.users_data_file
        self.users: pd.DataFrame = pd.read_json(data_folder / data_file, lines=True)
        self.users.set_index("user_id", inplace=True)

    def user_exists(self, user_id: int) -> bool:
        return user_id in self.users.index
