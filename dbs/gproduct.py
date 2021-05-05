from typing import Optional


class GProduct(object):
    id: int
    name: str
    desc: Optional[str]
    quantity: Optional[str]
    price: float
    amount: int
    uly_bring: int
    info: str

    def __init__(self, from_sql: list):
        self.id = from_sql[0]
        self.name = from_sql[1]
        self.desc = from_sql[2]
        self.quantity = from_sql[3]
        self.price = from_sql[4]
        self.amount = from_sql[5]
        self.uly_bring = from_sql[6]
        self.info = from_sql[7]
