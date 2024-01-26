import pymysql
from pymysql.cursors import DictCursor

def connection():
    try:
        connection = pymysql.connect(
            host='82.146.35.88',
            user='school',
            password='Q1w2e3r4',
            db='school',
            charset='cp1251',
            cursorclass=DictCursor
        )
        print("С базой соединились")
        return connection
    except Exception as e:
        print(f"Нет соединения. Ошибка: {str(e)}")
