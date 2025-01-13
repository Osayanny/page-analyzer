
import psycopg2 as pg2
from psycopg2.extras import DictCursor, NamedTupleCursor


def get_cursor(factory=None):
    def wrapper(func):
        def inner(self, *args, **kwargs):
            with self.conn.cursor(cursor_factory=factory) as cur:
                res = func(cur, *args, **kwargs)
            return res
        return inner
    return wrapper


class Page:
    def __init__(self, DATABASE_URL):
        self.conn = pg2.connect(DATABASE_URL)

    def close(self):
        self.conn.close()

    def commit(self):
        self.conn.commit()

    @get_cursor(DictCursor)
    def get_urls(cursor):
        query = "SELECT * FROM urls ORDER BY id DESC"
        cursor.execute(query)
        urls = cursor.fetchall()
        return [dict(url) for url in urls]

    @get_cursor(NamedTupleCursor)
    def get_checks(cursor, url_id):
        query = "SELECT * FROM checks WHERE url_id=%s ORDER BY id DESC"
        params = (url_id, )
        cursor.execute(query, params)
        checks = cursor.fetchall()
        return checks

    @get_cursor(DictCursor)
    def get_last_check(cursor):
        query = """
            SELECT DISTINCT ON (url_id)
                url_id,
                status_code,
                created_at
            FROM checks
            ORDER BY
                url_id"""
        cursor.execute(query)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def get_urls_with_last_check(self):
        urls = self.get_urls()
        checks = self.get_last_check()
        url_with_last_check = {}

        for url in urls:
            url_with_last_check[url['id']] = url

        for check in checks:
            if check['url_id'] in url_with_last_check:
                url_with_last_check[check['url_id']].update({
                    'last_check': check['created_at'],
                    'status_code': check['status_code']
                })
            else:
                url_with_last_check[check['url_id']] = {
                    'last_check': check['created_at'],
                    'status_code': check['status_code']
                }
        urls = list(url_with_last_check.values())
        return urls

    @get_cursor(NamedTupleCursor)
    def find_url(cursor, id):
        query = "SELECT * FROM urls WHERE id=%s"
        params = (id,)
        cursor.execute(query, params)
        row = cursor.fetchone()
        return row

    @get_cursor(NamedTupleCursor)
    def find_url_by_name(cursor, name):
        query = "SELECT * FROM urls WHERE %s IN (SELECT name FROM urls)"
        params = (name, )
        cursor.execute(query, params)
        url = cursor.fetchone()
        return url

    @get_cursor()
    def create_url(cursor, url):
        query = """
            INSERT INTO urls (name, created_at)
            VALUES (%s, %s) RETURNING id
            """
        params = (url['name'], url['created_at'])
        cursor.execute(query, params)
        url_id = cursor.fetchone()[0]
        return url_id

    @get_cursor()
    def create_check(cursor, check):
        query = """
            INSERT INTO checks (
                url_id,
                status_code,
                h1,
                title,
                description,
                created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """
        params = (
            check['url_id'],
            check['status_code'],
            check['h1'],
            check['title'],
            check['description'],
            check['created_at']
            )
        cursor.execute(query, params)
