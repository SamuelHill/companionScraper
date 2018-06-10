import psycopg2

# http://initd.org/psycopg/docs/usage.html

class PostgreSQLHandler:
    def __init__(self, db = 'companion_support', user = 'companion_melder',\
                    host = 'localhost', port = '5432', password = '123'):
        self.db=db
        self.user=user
        self.host=host
        self.port=port
        self.password=password
        connect_str = "dbname='{}' user='{}' host='{}' port={} password='{}'" \
            .format(self.db, self.user, self.host, self.port, self.password)
        self.conn = psycopg2.connect(connect_str)
    def __del__(self):
        if self.conn:
            self.conn.close()
    def execute(self, query):
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            self.conn.commit()
            return rows
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            print("Cannot execute query.\n")
            print(e)
        finally:
            if cursor:
                cursor.close()
    def executeUpdate(self, query, is_commit=True):
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            if is_commit:
                self.conn.commit()
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            print("Cannot execute updates.\n")
            print(e)
        finally:
            if cursor:
                cursor.close()
        return


def main():
    p = PostgreSQLHandler()
    p.executeUpdate("""DROP TABLE IF EXISTS tutorials;""")
    p.executeUpdate("""CREATE TABLE IF NOT EXISTS tutorials (id integer, name varchar(10));""")
    p.executeUpdate("""INSERT INTO tutorials VALUES (1, 'aaa');""")
    p.executeUpdate("""INSERT INTO tutorials VALUES (2, 'bbb');""")
    p.executeUpdate("""INSERT INTO tutorials VALUES (3, 'ccc');""")
    p.executeUpdate("""INSERT INTO tutorials VALUES (4, 'ddd');""")
    res = p.execute("""select * from tutorials""")
    for t in res:
        for f in t:
            print('%s ' % f, end='')
        print()

if __name__== "__main__":
    main()

