class GCategory(object):
    id: int
    name: str
    identity: str

    def __init__(self, from_sql: list):
        self.id = from_sql[0]
        self.name = from_sql[1]
        self.identity = from_sql[2]

    def get_name(self) -> str:
        return self.identity + ' ' + self.name
