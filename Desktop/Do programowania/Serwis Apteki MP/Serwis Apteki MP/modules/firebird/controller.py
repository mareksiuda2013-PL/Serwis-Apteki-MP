from services.firebird import FirebirdService
from services.firebird.database_service import DatabaseService


class FirebirdController:

    def __init__(self):

        self.firebird = FirebirdService()
        self.database = DatabaseService()

    def info(self):

        return self.firebird.get_info()

    def inspect_database(self, path):

        return self.database.inspect(path)