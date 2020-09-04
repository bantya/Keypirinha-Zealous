import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)

        return conn
    except Error as e:
        print(e)

    return None

def get_wildcard_term(wildcard, term):
    if wildcard == 'yes':
        if term.startswith('*') == True:
            start = term.startswith('*');
            term = term[1:]
            term = '%' + term

        if term.endswith('*') == True:
            end = term.endswith('*');
            term = term[0:-1]
            term = term + '%'
    else:
        term = '%' + term + '%'

    return term

def get_names(db_file, term, wildcard, count):
    conn = create_connection(db_file)
    cur = conn.cursor()

    term = get_wildcard_term(wildcard, term);

    cur.execute('SELECT name FROM searchIndex WHERE name LIKE ? LIMIT ?', (
        term,
        count,
    ))

    return cur.fetchall()

def get_types_names(db_file, term, wildcard, count, type, type2 = None):
    type = ''.join(type)
    conn = create_connection(db_file)
    cur = conn.cursor()

    term = get_wildcard_term(wildcard, term);

    if type2 is None:
        cur.execute(
            'SELECT name FROM searchIndex WHERE type = ? AND name LIKE ? LIMIT ?',
            (type, term, count)
        )
    else:
        cur.execute(
            'SELECT name FROM searchIndex WHERE type IN (?, ?) AND name LIKE ? LIMIT ?',
            (type, type2, term, count)
        )

    return cur.fetchall()
