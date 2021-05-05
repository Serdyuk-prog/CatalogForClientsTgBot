import sqlite3
from dbs.gproduct import GProduct
from dbs.gcategory import GCategory
from typing import Optional
import re


db_name = 'dbs/gnrl.db'


def get_all_categories() -> list[GCategory]:
    with sqlite3.connect(db_name) as con:
        cur = con.cursor()

        try:
            ret_val = list()
            for cat in cur.execute('''select * from category'''):
                ret_val.append(GCategory(cat))
            return ret_val

        except Exception as e:
            print(e)
            return []


def get_category_by_id(category_id: int) -> Optional[GCategory]:
    with sqlite3.connect(db_name) as con:
        cur = con.cursor()
        try:
            cat = cur.execute('''SELECT * FROM category 
                                 WHERE id = ?''', (category_id,)).fetchone()
            if cat is None:
                return None
            else:
                return GCategory(cat)

        except Exception as e:
            print(e)
            return None


def get_all_products_by_category_id(category_id: int) -> list[GProduct]:
    with sqlite3.connect(db_name) as con:
        cur = con.cursor()

        try:
            prod = cur.execute('''SELECT * FROM product 
                                  WHERE category_id = ?
                                  ORDER BY name''', (category_id,)).fetchall()
            if prod is []:
                return []
            else:
                frmtd_cats = []
                for cat in prod:
                    frmtd_cats.append(GProduct(cat))
                return frmtd_cats

        except Exception as e:
            print(e)
            return []


def get_product_by_id(product_id: int) -> Optional[GProduct]:
    with sqlite3.connect(db_name) as con:
        cur = con.cursor()

        try:
            prod = cur.execute('''SELECT * FROM product 
                                            WHERE id = ?''', (product_id,)).fetchone()
            if prod is None:
                return None
            else:
                return GProduct(prod)

        except Exception as e:
            print(e)
            return None


def find_products_by_category(name_with_symbol: str, order_by_field_name: str = 'name',
                              row_count: int = -1, offset: int = -1) -> list[GProduct]:
    with sqlite3.connect(db_name) as con:
        cur = con.cursor()

        if name_with_symbol[2] != ' ':
            return []

        symbol = name_with_symbol[0] + name_with_symbol[1]
        name = re.sub(r"[^а-яА-Я]+", '', name_with_symbol)
        print("|" + name + "|" + symbol + "|")

        try:
            cat = cur.execute('''SELECT * FROM category 
                                  WHERE name = ? and identity = ?''', (name, symbol, )).fetchone()
            if cat is None:
                print("no cats")
                return []
            else:
                query = "SELECT * FROM product WHERE category_id = ? ORDER BY ?"
                params = [int(cat[0]), order_by_field_name]

                if order_by_field_name == '':
                    order_by_field_name = 'id'
                if row_count != -1:
                    query += "LIMIT ? "
                    params.append(row_count)
                    if offset != -1:
                        query += "OFFSET ? "
                        params.append(offset)

                prods = cur.execute(query, tuple(params)).fetchall()
                frmtd_prods = []
                for prod in prods:
                    frmtd_prods.append(GProduct(prod))

                return frmtd_prods

        except Exception as e:
            print(e)
            return []


def find_like_products_by_name(like_name: str, order_by_field_name: str = 'name',
                               row_count: int = -1, offset: int = -1) -> list[GProduct]:
    with sqlite3.connect(db_name) as con:
        cur = con.cursor()

        if len(like_name) > 70:
            like_name = like_name[:70]

        search_query = re.sub(' +', ' ', like_name.strip().lower())
        search_query = re.sub('[^а-яa-z ]', '', search_query)
        if search_query == '':
            return []

        try:
            query = "SELECT * FROM product ORDER BY ?"
            params = [order_by_field_name]

            if order_by_field_name == '':
                order_by_field_name = 'id'
            if row_count != -1:
                query += "LIMIT ? "
                params.append(row_count)
                if offset != -1:
                    query += "OFFSET ? "
                    params.append(offset)

            prods = cur.execute(query, tuple(params)).fetchall()
            rated_prods = []
            s_queries = search_query.split(' ')
            if len(s_queries) > 5:
                s_queries = s_queries[:5]
            for s_index in range(len(s_queries)):
                sq_len = len(s_queries[s_index])
                s_query = s_queries[s_index]
                if 3 < sq_len <= 5:
                    s_queries[s_index] = s_query[:sq_len-1]
                elif 5 < sq_len <= 7:
                    s_queries[s_index] = s_query[:sq_len-2]
                elif 7 < sq_len:
                    s_queries[s_index] = s_query[:round(sq_len * 6.5 / 10)]

            for prod in prods:
                rating = 0
                prod_name = str(prod[1] + ' ' + prod[2]).lower()
                for s_query in s_queries:
                    if s_query in prod_name:
                        rating += 1
                if rating != 0:
                    rated_prods.append([rating, prod])

            rated_prods.sort(key=lambda el: el[0], reverse=True)

            formatted_products = []
            for prod in rated_prods:
                formatted_products.append(GProduct(prod[1]))

            return formatted_products

        except Exception as e:
            print(e)
            return []
