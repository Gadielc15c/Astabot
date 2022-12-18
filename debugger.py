import DB_CONN
import re
if __name__ == "__main__":
    # format = [".jpg", ".png", ".jpeg", ".jpge", ".tiff"]
    # resp = "waos.tiff" in format
    # print(resp)
    a_string = "A string is more than its parts!"
    matches = ["more", "wholesome", "milk"]

    if any(x in a_string for x in matches):
        print(True)
    else:
        print(False)
