import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None


def get_names(db_file, term, count):
    conn = create_connection(db_file)
    cur = conn.cursor()
    cur.execute('SELECT name FROM searchIndex WHERE name LIKE ? LIMIT ?', (
        '%' + term + '%',
        count,
    ))

    return cur.fetchall()


def get_types_names(db_file, term, count, type, type2=None):
    type = ''.join(type)
    conn = create_connection(db_file)
    cur = conn.cursor()
    if type2 is None:
        cur.execute(
            'SELECT name FROM searchIndex WHERE type = ? AND name LIKE ? LIMIT ?',
            (type, '%' + term + '%', count))
    else:
        cur.execute(
            'SELECT name FROM searchIndex WHERE type IN (?, ?) AND name LIKE ? LIMIT ?',
            (type, type2, '%' + term + '%', count))

    return cur.fetchall()
