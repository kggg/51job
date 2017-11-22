#!/usr/bin/env python
#encoding:utf-8

import MySQLdb
import MySQLdb.cursors


class Database:
    def __init__(self, dbname=None, dbhost=None, user=None, dbpass=None, dport=3306):
        self._dbuser = user
        self._dbpassword = dbpass
        self._dbhost = dbhost
        self._dbname = dbname
        self._dbcharset = 'utf8'
        self._dbport = int(dport)
        self._conn = self.connectMySQL()
        
        if(self._conn):
            self._cursor = self._conn.cursor()        

    def connectMySQL(self):
        conn = False
        try:
            conn = MySQLdb.connect(host=self._dbhost,
                    user=self._dbuser,
                    passwd=self._dbpassword,
                    db=self._dbname,
                    port=self._dbport,
                    cursorclass=MySQLdb.cursors.DictCursor,
                    charset=self._dbcharset,
                    )
        except Exception,data:
            self._logger.error("connect database failed, %s" % data)
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
        except MySQLdb.Error, e:
            try:
                sqlError =  "Error %d:%s" % (e.args[0], e.args[1])
                return sqlError
            except IndexError:
                return "MySQL Error:%s" % str(e)
            except MySQLdb.Warning, w:
                sqlWarning =  "Warning:%s" % str(w)
                self._conn.rollback()
                return sqlWarning

    def Query(self, sql):
        cur = self._cursor
        try:
            cur.execute(sql)
            self._conn.commit()
            rows = cur.fetchall()
            return rows
        except MySQLdb.Error, e:
            try:
                sqlError =  "Error %d:%s" % (e.args[0], e.args[1])
                return sqlError
            except IndexError:
                return "MySQL Error:%s" % str(e)
            except MySQLdb.Warning, w:
                sqlWarning =  "Warning:%s" % str(w)
                self._conn.rollback()
                return sqlWarning
        

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
        except MySQLdb.Error, e:
            try:
                sqlError =  "Error %d:%s" % (e.args[0], e.args[1])
            except IndexError:
                print "MySQL Error:%s" % str(e)
        return res


    def close(self):
        if(self._conn):
            try:
                if(type(self._cursor)=='object'):
                    self._cursor.close()
                if(type(self._conn)=='object'):
                    self._conn.close()
            except Exception, data:
                self._logger.warn("close database exception, %s,%s,%s" % (data, type(self._cursor), type(self._conn)))




