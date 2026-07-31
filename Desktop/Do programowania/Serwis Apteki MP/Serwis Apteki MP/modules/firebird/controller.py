from services.firebird import FirebirdService


class FirebirdController:

    def __init__(self):

        self.service = FirebirdService()

    def info(self):

        return self.service.get_info()