# main.py
from tkinter import Tk
from db_utils import connectDataBase
from auth_utils import LogInWindow # Giữ nguyên import này vì file giờ là auth_utils.py
from main_app_gui import MainWindow # Import class MainWindow

def start_main_application(user_id):
    """
    Hàm này được gọi khi người dùng đăng nhập thành công.
    Khởi tạo và chạy ứng dụng chính.
    """
    root_main_app = Tk()
    app = MainWindow(root_main_app, user_id)
    root_main_app.mainloop()

if __name__ == "__main__":
    # 1. Connect to Database (optional, can be done lazily in db_utils)
    # connectDataBase() # connectDataBase() now handles its own errors and connection management
    
    # 2. Start Login Window
    # The LogInWindow function will call start_main_application upon successful login.
    LogInWindow(start_main_application) # Gọi với callback
    
    print("Application finished.")