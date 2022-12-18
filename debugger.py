import DB_CONN
import re
if __name__ == "__main__":
    # format = [".jpg", ".png", ".jpeg", ".jpge", ".tiff"]
    # resp = "waos.tiff" in format
    # print(resp)

    res=DB_CONN.execute_select(f'SELECT p.idproducts FROM purchase pur INNER JOIN  products p  ON pur.product=p.idproducts INNER JOIN  user u ON pur.user=u.iduser  WHERE u.iduser=46 GROUP BY p.nameproducts ORDER BY count(p.nameproducts)  desc LIMIT 1 ;')
    print(res[0][0])