import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None

def get_names(db_file, term):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    conn = create_connection(db_file)
    cur = conn.cursor()
    # cur.execute('SELECT name, type FROM searchIndex LIMIT 50')
    cur.execute('SELECT name FROM searchIndex WHERE name LIKE ? LIMIT 50', (term + '%',))
    # query = 'SELECT name FROM searchIndex WHERE name LIKE ' + term + '%'
    # cur.execute(query)
    # print(query)

    # return cur.fetchone()
    return cur.fetchall()
