import ENV_VARs
import mysql.connector
from mysql.connector import errorcode

def open_connection():
    """
    :return: STATE OF CONNECTION
    """
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
    """
    :param sql_string: GETS STRING TO PERFOM SELECT, UPDATE OR DELETE
    :return: RETURNS NOTHING
    """
    mydb, cursor = open_connection()
    cursor.execute(sql_string)
    mydb.commit()
    cursor.close()
    return


def execute_select(sql_select):
    """
    :param sql_select: GETS STRING TO PERFORM INSERTS
    :return:
    """
    mydb, cursor = open_connection()
    cursor.execute(sql_select)
    list_ = cursor.fetchall()
    cursor.close()

    if len(list_) > 0:
        return list_

    return []


if __name__ == "__main__":
    pass
