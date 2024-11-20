import os
import psycopg2 as pg2
from psycopg2.extras import DictCursor
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
connect = pg2.connect(DATABASE_URL)


class Urls:
    def __init__(self, conn=connect):
        self.conn = conn

    def get_content(self):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM urls ORDER BY id DESC")
            rows = cur.fetchall()
        return [dict(row) for row in rows]

    def find(self, id):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM urls WHERE id=%s", (id,))
            row = cur.fetchone()
        return dict(row) if row else None

    def _find_by_name(self, name):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM urls WHERE name ILIKE %s", (name, ))
            res = cur.fetchall()
        return res

    def _create(self, url):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id", # noqa
                (url['name'], url['created_at']))
            id = cur.fetchone()[0]
            url['id'] = id
        self.conn.commit()
        return url

    def save(self, url):
        urls = self._find_by_name(url['name'])
        if not urls:
            return (self._create(url), 'success')
        else:
            return (urls[0], 'exist')
