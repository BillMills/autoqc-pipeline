import util.post as post
import util.main as main
import sys, sqlite3

tests = main.importQC(sys.argv[1])
tablename = 'quota'

def add_test(testname, tablename, database='iquod.db'):
    conn = sqlite3.connect(database, isolation_level=None)
    cur = conn.cursor()
    query = 'ALTER TABLE ' + tablename + ' ADD ' + testname + ' BLOB;'
    cur.execute(query)

for test in tests:
    add_test(test.lower(), tablename)
