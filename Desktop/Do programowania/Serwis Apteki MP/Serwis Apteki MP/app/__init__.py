class FirebirdModule(BaseModule):

    id = "firebird"
    name = "Firebird"
    icon = "firebird.svg"

    def create_page(self):
        return FirebirdPage()