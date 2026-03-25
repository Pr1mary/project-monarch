import pymysql
import pymysql.cursors

class DbConn:
  def __init__(self, host: str, port: int, user: str, password: str, database: str):
    self.config = {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "database": database,
        "cursorclass": pymysql.cursors.DictCursor,
        "autocommit": True
    }

  def query(self, sql: str, params=None):
    conn = pymysql.connect(**self.config)
    try:
      with conn.cursor() as cursor:
        cursor.execute(sql, params)
        if cursor.description:  # SELECT
          return cursor.fetchall()
        return cursor.rowcount  # INSERT/UPDATE/DELETE
    finally:
      conn.close()
