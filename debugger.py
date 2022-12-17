import DB_CONN

if __name__ == "__main__":
    exists = DB_CONN.execute_select(
        f'SELECT nameproducts FROM products WHERE nameproducts= "Laptop"')  # Devuelve bool 1: Existe, 0: No Existe
    print(exists)
    if exists:
        print("El usuario existe")
    else:
        print("no existe")
