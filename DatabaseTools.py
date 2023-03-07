import os
import sqlite3


class DatabaseGuard:
    def __init__(self):
        self.db_path = 'database/friends.db'
        if not os.path.exists('database') or not os.path.exists(self.db_path):
            self.init_database()
        self.main_con = sqlite3.connect(self.db_path)

    def init_database(self):
        if not os.path.exists('database'):
            os.mkdir('database')
        con = sqlite3.connect(self.db_path)
        with con:
            con.executescript("""
                CREATE TABLE USER_INFO (
                    uid INTEGER NOT NULL UNIQUE,
                    fnick TEXT,
                    crawled INTEGER,
                    relations INTEGER,
                    real_relations INTEGER
                );

                CREATE TABLE RELATION (
                    m_uid INTEGER NOT NULL,
                    f_uid INTEGER NOT NULL
                );
            """)

    def add_user(self, uid, fnick):
        with self.main_con:
            if list(self.main_con.execute('SELECT * FROM USER_INFO WHERE uid = ?', (uid,))):
                return
            else:
                self.main_con.execute('INSERT INTO USER_INFO(uid, fnick, crawled) VALUES (?, ?, 0)', (uid, fnick))

    def add_relation(self, m_uid, f_uid):
        with self.main_con:
            self.main_con.execute('INSERT INTO RELATION(m_uid, f_uid) VALUES (?, ?)', (m_uid, f_uid))

    def select_uid(self):
        with self.main_con:
            return list(self.main_con.execute("SELECT m_uid FROM RELATION"))

    def select_relations_by_uid(self, m_uid):
        with self.main_con:
            return list(self.main_con.execute('SELECT * FROM RELATION WHERE m_uid = ?', (m_uid,)))

    def set_crawled(self, uid):
        with self.main_con:
            self.main_con.execute('UPDATE USER_INFO SET crawled = ? WHERE uid = ?', (1, uid))

    def select_crawled(self, uid):
        with self.main_con:
            if list(self.main_con.execute('SELECT * FROM USER_INFO WHERE uid = ? AND crawled = ?', (uid, 1))):
                return True
            else:
                return False

    def select_tier1_uid(self):
        with self.main_con:
            return list(self.main_con.execute('SELECT uid FROM USER_INFO WHERE relations > 0'))

    def select_tier2_uid(self):
        with self.main_con:
            return list(self.main_con.execute('SELECT uid FROM USER_INFO WHERE real_relations > 0'))

    def update_relations_by_uid(self, uid, count):
        with self.main_con:
            self.main_con.execute('UPDATE USER_INFO SET relations = ? WHERE uid = ?', (count, uid))

    def update_real_relations_by_uid(self, uid, count):
        with self.main_con:
            self.main_con.execute('UPDATE USER_INFO SET real_relations = ? WHERE uid = ?', (count, uid))
