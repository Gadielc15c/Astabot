import DB_CONN

if __name__ == "__main__":
    exists = DB_CONN.execute_select(
        f'SELECT username FROM user WHERE username = "Lorenzo"')  # Devuelve bool 1: Existe, 0: No Existe
    print(exists)
    if not exists:
        print("El usuario no existe")
    else:
        print("Si existe")
