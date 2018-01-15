package querydb

import (
	"database/sql"
	//"fmt"
	_ "github.com/go-sql-driver/mysql"
	"log"
)

func checkerr(err error) {
	if err != nil {
		log.Panicln(err.Error())
	}
}

func New(host string, user string, pass string, port string, dbname string) (*sql.DB, error) {
	db, err := sql.Open("mysql", user+":"+pass+"@tcp("+host+":"+port+")/"+dbname)
	checkerr(err)
	return db, err
}

//fetch data from database
func FetchRows(db *sql.DB, sqlstr string, args ...interface{}) ([]map[string]string, error) {
	stmtOut, err := db.Prepare(sqlstr)
	checkerr(err)
	defer stmtOut.Close()

	rows, err := stmtOut.Query(args...)
	checkerr(err)
	columns, err := rows.Columns()
	checkerr(err)
	values := make([]sql.RawBytes, len(columns))
	scanArgs := make([]interface{}, len(values))

	ret := make([]map[string]string, 0)
	for i := range values {
		scanArgs[i] = &values[i]
	}

	for rows.Next() {
		err = rows.Scan(scanArgs...)
		checkerr(err)
		var value string
		vmap := make(map[string]string, len(scanArgs))
		for i, col := range values {
			if col == nil {
				value = "NULL"
			} else {
				value = string(col)
			}
			vmap[columns[i]] = value
		}
		ret = append(ret, vmap)
	}
	return ret, nil
}

// for data update and delete
func exec(db *sql.DB, sqlstr string, args ...interface{}) (int64, error) {
	stmtIns, err := db.Prepare(sqlstr)
	checkerr(err)
	defer stmtIns.Close()

	result, err := stmtIns.Exec(args...)
	checkerr(err)
	return result.RowsAffected()
}

// for insert data to database
func insert(db *sql.DB, sqlstr string, args ...interface{}) (int64, error) {
	stmtIns, err := db.Prepare(sqlstr)
	checkerr(err)
	defer stmtIns.Close()
	result, err := stmtIns.Exec(args...)
	checkerr(err)
	return result.LastInsertId()
}
