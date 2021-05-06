from typing import Optional


class GUser:
    id: int
    on_page: int
    query: Optional[str]
    way: Optional[str]
    row: Optional[int]
    sort: Optional[int]

    def __init__(self, from_sql: list):
        self.id = from_sql[0]
        self.on_page = from_sql[1]
        self.query = from_sql[2]
        self.way = from_sql[3]
        self.row = from_sql[4]
        self.sort = from_sql[5]
