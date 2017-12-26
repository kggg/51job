#!/usr/bin/env python3
import pymysql
import sys

class Database:
    def __init__(self, dbname=None, dbhost=None, user=None, dbpass=None, dport=3306):
        self._dbuser = user
        self._dbpassword = dbpass
        self._dbhost = dbhost
        self._dbname = dbname
        self._dbcharset = 'utf8'
        self._dbport = int(dport)
        self._conn = self.Connect()

        if self._conn:
            self._cursor = self._conn.cursor()

    def Connect(self):
        conn = False
        try:
            conn = pymysql.connect(host=self._dbhost,
                    user=self._dbuser,
                    passwd=self._dbpassword,
                    db=self._dbname,
                    port=self._dbport,
                    charset=self._dbcharset,
                    )
        except Exception as e:
            print("connect database failed: %s" %e)
            conn = False
        return conn

    def cur(self):
        cur = self._cursor
        if(cur):
            cur.execute('SET NAMES utf8;')
            cur.execute('SET CHARACTER SET utf8;')
            cur.execute('SET character_set_connection=utf8;')
            return cur
        else:
            return False

    def InsertDB(self, sql, params):
        cur = self._cursor
        try:
            cur.execute(sql, params)
            self._conn.commit()
            insert_id = cur.lastrowid
            return insert_id
        except Exception as e:
            print(e)
            self._conn.rollback()
        return False

    def Query(self, sql):
        cur = self._cursor
        try:
            cur.execute(sql)
            self._conn.commit()
            rows = cur.fetchall()
            return rows
        except Exception as e:
            print(e)
            self._conn.rollback()
        return False    

    def CheckDB(self, sql, position, company):
        res = False
        sqli = sql
        cur = self._cursor
        try:
            cur.execute(sqli,(position, company))
            self._conn.commit()
            res = cur.fetchone()
            if not res:
                res = False
        except:
            print("MySQL Error:%s")
            return False
        return res        

    def close(self):
        if self._conn:
            try:
                if(type(self._cursor)=='object'):
                    self._cursor.close()
                if(type(self._conn)=='object'):
                    self._conn.close()
            except Exception as e:
                self._logger.warn("close database exception, %s,%s,%s" % (e, type(self._cursor), type(self._conn)))

if __name__ == '__main__':
    db = Database("blog","127.0.0.1","webuser","Webuser_192")
    sql = "select * from user"
    res = db.Query(sql)
    if res:
        for i in res:
            print(i)
    db.close()

