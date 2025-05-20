import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",         # адрес MySQL-сервера
        user="root",              # имя пользователя MySQL
        password="123456789", # пароль пользователя MySQL
        database="skillpath"      # имя базы данных
    )