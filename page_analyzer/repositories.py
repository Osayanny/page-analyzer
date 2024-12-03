import os
import psycopg2 as pg2
from psycopg2.extras import DictCursor
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def _get_connection():
    connect = pg2.connect(DATABASE_URL)
    return connect


class Urls:
    def __init__(self):
        self.conn = _get_connection()

    def execute_query(self, query, parms=None, factory=DictCursor):
        with self.conn.cursor(cursor_factory=factory) as cur:
            cur.execute(query, parms)
            if query.lstrip().startswith('SELECT'):
                return cur.fetchall()
            else:
                return cur.fetchone()


    def get_content(self):
        query = "SELECT * FROM urls ORDER BY id DESC"
        rows = self.execute_query(query)

        self.conn.close()
        return [dict(row) for row in rows]

    def find(self, id):
        query = "SELECT * FROM urls WHERE id=%s"
        parms = (id,)
        row = self.execute_query(query, parms)

        self.conn.close()
        return dict(row[0]) if row else None

    def _find_by_name(self, name):
        query = "SELECT * FROM urls WHERE name ILIKE %s"
        parms = (name, )

        res = self.execute_query(query, parms)
        return res

    def _create(self, url):
        query = """
            NSERT INTO urls (name, created_at)
            VALUES (%s, %s) RETURNING id
            """
        parms = (url['name'], url['created_at'])

        id = self.execute_query(query,parms, factory=None)[0]
        url['id'] = id

        self.conn.commit()
        self.conn.close()
        return url

    def save(self, url):
        urls = self._find_by_name(url['name'])
        if not urls:
            return (self._create(url), 'success')
        else:
            self.conn.close()
            return (urls[0], 'exist')


class Checks:
    def __init__(self):
        self.conn = _get_connection()

    def execute_query(self, query, parms=None, factory=DictCursor):
        with self.conn.cursor(cursor_factory=factory) as cur:
            cur.execute(query, parms)
            if query.lstrip().startswith('SELECT'):
                return cur.fetchall()
            else:
                return cur.fetchone()

    def get_checks(self, id):
        query = """
            SELECT *
            FROM url_checks
            WHERE url_id=%s
            ORDER BY id DESC
            """
        parms = (id,)
        rows = self.execute_query(query, parms)

        self.conn.close()
        return [dict(row) for row in rows]

    def get_url_with_last_check(self):
        query = """
            SELECT
                url.id,
                url.name,
                MAX(checks.created_at) AS last_check,
                checks.status_code
            FROM urls AS url
            LEFT JOIN url_checks AS checks
            ON url.id = checks.url_id
            GROUP BY url.id, url.name, checks.status_code
            ORDER BY url.id DESC
            """
        rows = self.execute_query(query)

        self.conn.close()
        return [dict(row) for row in rows]

    def save(self, check):
        query = """
            INSERT INTO url_checks (
                    url_id,
                    status_code,
                    h1,
                    title,
                    description,
                    created_at
                )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id"""
        parms = (
            check['url_id'],
            check['code'],
            check['h1'],
            check['title'],
            check['description'],
            check['created_at']
        )
            
        id = self.execute_query(query, parms, factory=None)[0]
        check['id'] = id

        self.conn.commit()
        self.conn.close()
        return check
