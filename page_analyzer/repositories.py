
import psycopg2 as pg2
from psycopg2.extras import DictCursor


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

    @get_cursor(DictCursor)
    def get_checks(cursor, url_id):
        query = "SELECT * FROM checks WHERE url_id=%s"
        params = (url_id, )
        cursor.execute(query, params)
        checks = cursor.fetchall()
        return [dict(check) for check in checks]

    @get_cursor(DictCursor)
    def get_last_check(cursor):
        query = """
            SELECT
                url_id,
                status_code,
                MAX(created_at) as last_check
            FROM checks
            GROUP BY
                url_id,
                status_code"""
        cursor.execute(query)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    @get_cursor(DictCursor)
    def find_url(cursor, id):
        query = "SELECT * FROM urls WHERE id=%s"
        params = (id,)
        cursor.execute(query, params)
        row = cursor.fetchall()
        return dict(row[0]) if row else None

    @get_cursor(DictCursor)
    def find_url_by_name(cursor, name):
        query = "SELECT * FROM urls WHERE name ILIKE %s"
        params = (name, )
        cursor.execute(query, params)
        url = cursor.fetchall()
        return url

    @get_cursor()
    def create_url(cursor, url):
        query = """
            INSERT INTO urls (name, created_at)
            VALUES (%s, %s) RETURNING id
            """
        params = (url['name'], url['created_at'])
        cursor.execute(query, params)
        id = cursor.fetchone()[0]
        return id

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
