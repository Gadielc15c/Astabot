import DB_CONN
import re
if __name__ == "__main__":
    # exists = DB_CONN.execute_select(
    #     f'SELECT nameproducts FROM products WHERE nameproducts= "Laptop"')  # Devuelve bool 1: Existe, 0: No Existe
    # print(exists)
    # if exists:
    #     print("El usuario existe")
    # else:
    #     print("no existe")
    # url="https://www.google.com/search?q=traductor&rlz=1C1CHBD_esDO943DO943&oq=traductor&aqs=chrome.0.69i59l2j69i65.13877j0j7&sourceid=chrome&ie=UTF-8"
    # regex = re.compile(
    #     r'^(?:http|ftp)s?://'  # http:// or https://
    #     r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    #     r'localhost|'  # localhost...
    #     r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    #     r'(?::\d+)?'  # optional port
    #     r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    # resp = re.match(regex, url) is not None
    # print(resp)
    import string

    s="WAOS"
    print(s.lower())