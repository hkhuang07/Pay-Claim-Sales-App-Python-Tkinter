# auth_utils.py
from tkinter import Tk, Label, Entry, Button, StringVar, Toplevel, messagebox, Checkbutton # Thêm Checkbutton nếu chưa có
import bcrypt
from db_utils import ExecuteQuery # Import hàm tương tác DB
from app_utils import makecenter    # Import hàm tiện ích UI


# LOGIN FUNCTION
# Login Window
# Sửa đổi để chấp nhận một hàm callback khi đăng nhập thành công
def LogInWindow(on_login_success): 
    # Create Login_Window
    loginWin = Tk()
    loginWin.title("LOGIN")
    loginWin.geometry("320x200")
    loginWin.configure(bg="#AFEEEE")

    makecenter(loginWin)

    lblLogInTiltle = Label(
        loginWin, text="LOG IN", font=("Arial", 14, "bold"), bg="#AFEEEE"
    ).place(x=100, y=10)
    lblUserName = Label(
        loginWin, text="User name: ", font=("Arial", 10, "bold"), bg="#AFEEEE"
    ).place(x=10, y=50)
    lblUserPass = Label(
        loginWin, text="Passwork: ", font=("Arial", 10, "bold"), bg="#AFEEEE"
    ).place(x=10, y=80)
    txtUserName = Entry(loginWin, width=20, bg="#e0f7fa", font=("Arial", 12))
    txtUserName.place(x=100, y=50)
    txtUserPass = Entry(loginWin, width=20, bg="#e0f7fa", show="*", font=("Arial", 12))
    txtUserPass.place(x=100, y=80)
    txtUserName.focus()

    # Định nghĩa userID là biến cục bộ trong hàm HandleLogin hoặc truyền nó qua hàm
    # Bỏ global userID ở đây vì userID sẽ được truyền qua callback
    def HandleLogin():
        username = txtUserName.get().strip()
        password = txtUserPass.get().strip()

        if not username or not password:
            messagebox.showwarning("Wanrning", "Please enter username and password!")
            return
        # Query database for user information
        result = ExecuteQuery(
            """SELECT UserID,Password,Role 
                                  FROM Users 
                                  WHERE UserName=%s
                                  """,
            (username,),
        )
        if result:
            userid, hashedPassword, role = result[0]
            if bcrypt.checkpw(password.encode(), hashedPassword.encode()):
                messagebox.showinfo("Success", f"Welcome {username}! Role: {role}")
                loginWin.destroy()
                # Gọi hàm callback được truyền vào và truyền UserID
                on_login_success(userid) 
            else:
                messagebox.showerror("Error", "Invalid username or password!")
        else:
            messagebox.showerror("Error", "Invalid username or password!")

    def ApplicationExit():
        result = messagebox.askyesno("Message", "Do you want to exit?")
        if result:
            loginWin.destroy()

    bntLogin = Button(
        loginWin,
        text="Login",
        bg="#104E8B",
        fg="#F0F8FF",
        font=("Arial", 10, "bold"),
        command=HandleLogin,
    )
    bntLogin.place(x=10, y=150)
    btnExit = Button(
        loginWin,
        text="Exit",
        bg="#191970",
        fg="#F0F8FF",
        font=("Arial", 10, "bold"),
        command=ApplicationExit,
    )
    btnExit.place(x=250, y=150)
    btnSignup = Button(
        loginWin,
        text="Sign up",
        fg="#191970",
        bg="#AFEEEE",
        font=("Arial", 10, "bold"),
        command=SignupWindow,
    )
    btnSignup.place(x=10, y=110)
    btnChangePassword = Button(
        loginWin,
        text="Change Password",
        bg="#AFEEEE",
        fg="#191970",
        font=("Arial", 10, "bold"),
        command=ChangePassword,
    )
    btnChangePassword.place(x=160, y=110)

    txtUserPass.bind("<Return>", lambda event: HandleLogin())
    txtUserName.bind("<Return>", lambda event: txtUserPass.focus())
    loginWin.mainloop()


# Signup window
def SignupWindow():
    signupWin = Toplevel()
    signupWin.title("SIGN UP ACCOUNT")
    signupWin.resizable(height=True, width=True)
    signupWin.geometry("320x200")
    signupWin.configure(bg="#AFEEEE")

    signupWin.attributes("-topmost", 1)  # Make sure it stays on top
    signupWin.lift()
    makecenter(signupWin)

    def HashPassword(password):
        # Create Salt and Hash password
        salt = bcrypt.gensalt()
        hashedPassword = bcrypt.hashpw(password.encode(), salt)
        return hashedPassword

    lblIDSignUp = Label(
        signupWin, text="User ID: ", font=("Arial", 10, "bold"), bg="#AFEEEE"
    ).place(x=40, y=40)
    lblUserSignUp = Label(
        signupWin, text="User name: ", font=("Arial", 10, "bold"), bg="#AFEEEE"
    ).place(x=40, y=70)
    lblPasSignUp = Label(
        signupWin, text="Passwork: ", font=("Arial", 10, "bold"), bg="#AFEEEE"
    ).place(x=40, y=100)

    txtIDSignUp = Entry(signupWin, width=23, bg="#e0f7fa")
    txtUserSignUp = Entry(signupWin, width=23, bg="#e0f7fa")
    txtPasSignUp = Entry(signupWin, width=23, bg="#e0f7fa", show="*")

    txtIDSignUp.place(x=120, y=40)
    txtUserSignUp.place(x=120, y=70)
    txtPasSignUp.place(x=120, y=100)

    role = StringVar(value="")
    """
    Label(signupWin, text="Role: ", font=("Arial", 10, "bold"), bg="#AFEEEE").place(
        x=40, y=130
    )
    chkAdmin = Checkbutton(
        signupWin,
        text="Admin",
        variable=role,
        onvalue="Admin",
        offvalue="",
        bg="#AFEEEE",
    )
    chkAdmin.place(x=200, y=130)
    chkEmployee = Checkbutton(
        signupWin,
        text="Employee",
        variable=role,
        onvalue="Employee",
        offvalue="",
        bg="#AFEEEE",
    )
    chkEmployee.place(x=120, y=130)
    """
    def CreateAccount():
        userid = txtIDSignUp.get().strip()
        username = txtUserSignUp.get().strip()
        password = txtPasSignUp.get().strip()
        """ selectedRole = role.get()
        if not selectedRole:
            messagebox.showwarning("Warning", "Please select exactly one role!")
            return"""

        # Valid Input
        if not userid or not username or not password:
            messagebox.showwarning("Warning", "All fields are required!")
            return
        
        try:
            result = ExecuteQuery("SELECT * FROM Users WHERE UserName =%s", (username,))
            if result:
                messagebox.showerror("Error", "Username already exists!")
            else:
                hashedPassword = HashPassword(password)

                ExecuteQuery(
                    """INSERT INTO Users (UserID,UserName,Password,Role) 
                                 VALUES (%s,%s,%s,%s)
                                 """,
                    (userid, username, hashedPassword.decode(), "Employee"),
                )
                messagebox.showinfo("Success", "Account created successfully!")
                signupWin.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def ExitSignUp():
        result = messagebox.askyesno("Message", "Do you want return Login Window ?")
        if result:
            signupWin.destroy()

    lblSignUpTiltle = Label(
        signupWin, text="    Sign Up", font=("Arial", 14, "bold"), bg="#AFEEEE"
    ).place(x=100, y=10)
    btnCreate = Button(
        signupWin,
        text="Create Account",
        bg="#1874CD",
        fg="#F0F8FF",
        font=("Arial", 12, "bold"),
        command=CreateAccount,
    )
    btnCreate.place(x=40, y=160)
    btnExitSignUp = Button(
        signupWin,
        text="Exit",
        bg="#4682B4",
        fg="#F0F8FF",
        font=("Arial", 12, "bold"),
        command=ExitSignUp,
    )
    btnExitSignUp.place(x=220, y=160)


# Change Password
def ChangePassword():
    changePassWin = Toplevel()
    changePassWin.title("Change Password")
    changePassWin.geometry("320x240")
    changePassWin.configure(bg="#AFEEEE")
    makecenter(changePassWin)

    Label(
        changePassWin, text="CHANGE PASSWORD", font=("Arial", 14, "bold"), bg="#AFEEEE"
    ).place(x=50, y=10)
    Label(
        changePassWin, text="User Name: ", font=("Arial", 10, "bold"), bg="#AFEEEE"
    ).place(x=20, y=40)
    Label(
        changePassWin,
        text="Current Password: ",
        font=("Arial", 10, "bold"),
        bg="#AFEEEE",
    ).place(x=20, y=70)
    Label(
        changePassWin, text="New Password: ", font=("Arial", 10, "bold"), bg="#AFEEEE"
    ).place(x=20, y=100)
    Label(
        changePassWin,
        text="Confirm Password: ",
        font=("Arial", 10, "bold"),
        bg="#AFEEEE",
    ).place(x=20, y=130)

    txtUserName = Entry(changePassWin, width=20, bg="#e0f7fa", font=("Arial", 12))
    txtCurrentPassword = Entry(
        changePassWin, width=20, show="*", bg="#e0f7fa", font=("Arial", 12)
    )
    txtNewPassword = Entry(
        changePassWin, width=20, show="*", bg="#e0f7fa", font=("Arial", 12)
    )
    txtConfirmPassword = Entry(
        changePassWin, width=20, show="*", bg="#e0f7fa", font=("Arial", 12)
    )

    txtUserName.place(x=150, y=40, width=130)
    txtCurrentPassword.place(x=150, y=70, width=130)
    txtNewPassword.place(x=150, y=100, width=130)
    txtConfirmPassword.place(x=150, y=130, width=130)

    def HandleChangePassword():
        userName = txtUserName.get().strip()
        currentPassword = txtCurrentPassword.get().strip()
        newPassword = txtNewPassword.get().strip()
        confirmPassword = txtConfirmPassword.get().strip()

        if not currentPassword or not newPassword or not confirmPassword:
            messagebox.showwarning("Warning", "All fields are required!")
            return

        if newPassword != confirmPassword:
            messagebox.showerror("Error", "New password and confirmation do not match!")
            return

        try:
            # Query user information to verify current password
            result = ExecuteQuery(
                "SELECT Password FROM Users WHERE UserName = %s", (userName,)
            )
            if result:
                hashedPassword = result[0][0]
                if bcrypt.checkpw(currentPassword.encode(), hashedPassword.encode()):
                    # Hash the new password
                    hashedNewPassword = bcrypt.hashpw(
                        newPassword.encode(), bcrypt.gensalt()
                    )
                    # Update password in the database
                    # Cần đảm bảo userID được định nghĩa (ví dụ: thông qua một biến global hoặc truyền vào)
                    # Hoặc tìm UserID dựa vào UserName ở đây
                    update_result = ExecuteQuery(
                        "UPDATE Users SET Password = %s WHERE UserName = %s",
                        (hashedNewPassword.decode(), userName), # Sửa UserID thành UserName
                    )
                    if update_result is not None: # ExecuteQuery trả về None nếu lỗi, hoặc không gì nếu thành công cho UPDATE
                        messagebox.showinfo("Success", "Password changed successfully!")
                        changePassWin.destroy()
                    else:
                        messagebox.showerror("Error", "Failed to update password. Database error.")
                else:
                    messagebox.showerror("Error", "Current password is incorrect!")
            else:
                messagebox.showerror("Error", "User not found!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    btnChange = Button(
        changePassWin,
        text="Change Password",
        bg="#AFEEEE",
        fg="#191970",
        font=("Arial", 12, "bold"),
        command=HandleChangePassword,
    )
    btnChange.place(x=20, y=180)
    btnExit = Button(
        changePassWin,
        text="Exit",
        bg="#AFEEEE",
        fg="#191970",
        font=("Arial", 12, "bold"),
        command=changePassWin.destroy,
    )
    btnExit.place(x=220, y=180)

    txtCurrentPassword.focus()

    #============================================================