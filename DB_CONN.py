import ENV_VARs
import mysql.connector
from mysql.connector import errorcode


def open_connection():
    mydb, cursor = None, None
    try:
        mydb = mysql.connector.connect(
            host=ENV_VARs.mysql_host,
            user=ENV_VARs.mysql_user,
            password=ENV_VARs.mysql_password,
            database=ENV_VARs.mysql_database
        )
        cursor = mydb.cursor()
    except mysql.connector.Error as e:
        if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Username or password is wrong")
        elif e.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(e)

    return mydb, cursor


def execute_sql(sql_string):
    mydb, cursor = open_connection()
    cursor.execute(sql_string)
    mydb.commit()
    cursor.close()
    return


def execute_select(sql_select):
    mydb, cursor = open_connection()
    cursor.execute(sql_select)
    list_ = cursor.fetchall()
    cursor.close()
    return list_


if __name__ == "__main__":
    pass
