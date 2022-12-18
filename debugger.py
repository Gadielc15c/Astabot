import DB_CONN
import re
import prettytable as pt
if __name__ == "__main__":
    # format = [".jpg", ".png", ".jpeg", ".jpge", ".tiff"]
    # resp = "waos.tiff" in format
    # print(resp)

    query = f'SELECT p.nameproducts Producto,pur.discount Descuento ,pur.total Total FROM purchase pur INNER JOIN products p  ON pur.product=p.idproducts INNER JOIN user u ON pur.user=u.iduser where pur.user=46'
    result = DB_CONN.execute_select(query)

    table = pt.PrettyTable(['PRODUCTO', 'DESCUENTO', 'TOTAL'])
    table.align['PRODUCTO'] = 'l'
    table.align['DESCUENTO'] = 'r'
    table.align['TOTAL'] = 'r'
    print(result)


