from firebird.driver import connect

DATABASE = r"C:\KSBAZA\KS-APW\WAPTEKA.FDB"

try:
    con = connect(
        DATABASE,
        user="SYSDBA",
        password="masterkey",
    )

    print("OK")

    cur = con.cursor()
    cur.execute("select current_user from rdb$database")

    print(cur.fetchone())

    con.close()

except Exception as e:
    print(type(e).__name__)
    print(e)