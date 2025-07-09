# db_utils.py
import mysql.connector
from mysql.connector import Error
from tkinter import messagebox # Vẫn cần messagebox cho lỗi kết nối DB

# DATABASE FUNCTION
# Connect To Database
def connectDataBase():
    try:
        connection = mysql.connector.connect(
            host="localhost", user="root", password="", database="PayAndClaimSales"
        )
        if connection.is_connected():
            print("Database connected successfully!")
            return connection
    except Error as e:
        messagebox.showerror("Error", f"Error connecting to MySQL:{e}")
        return None
    
# Excute Query
def ExecuteQuery(query, params=None, many=False): # Thêm tham số 'many'
    connection = connectDataBase()
    if not connection:
        return None
    try:
        cursor = connection.cursor()
        if many: # Nếu many là True, sử dụng executemany
            cursor.executemany(query, params)
        else: # Ngược lại, sử dụng execute như bình thường
            cursor.execute(query, params or ())

        if query.strip().lower().startswith("select"):
            return cursor.fetchall()
        connection.commit()
        return True # Trả về True cho các truy vấn INSERT/UPDATE/DELETE thành công
    except Error as e:
        print(f"Database error: {e}")
        messagebox.showerror("Database error", f"Error excute query: {e}") # Thêm thông báo lỗi cho người dùng
        return False # Trả về False nếu có lỗi
    finally:
        if connection and connection.is_connected(): # Đảm bảo connection tồn tại và đang mở
            cursor.close()
            connection.close()

    """# Excute Query
def ExecuteQuery(query, params=None):
    connection = connectDataBase()
    if not connection:
        return None
    try:
        cursor = connection.cursor()
        
        cursor.execute(query, params or ())
        if query.strip().lower().startswith("select"):
            return cursor.fetchall()
        connection.commit()
    except Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        cursor.close()
        connection.close()

    #=====================================================
    """
