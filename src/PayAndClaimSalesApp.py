from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog
import datetime
import mysql.connector
from mysql.connector import Error
import bcrypt

# Global Variable
userID = ""
quantityBill = 0
quantityItems = 0
revenue = 0
orderNumber = 0

#============================================================

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

    #============================================================

# LOGIN FUNCTION
# Login Window
def LogInWindow():  
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

    def HandleLogin():
        global userID
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
                userID = userid
                MainWindow()
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
        bg="limegreen",
        fg="white",
        font=("Arial", 10, "bold"),
        command=HandleLogin,
    )
    bntLogin.place(x=10, y=150)
    btnExit = Button(
        loginWin,
        text="Exit",
        bg="red",
        fg="white",
        font=("Arial", 10, "bold"),
        command=ApplicationExit,
    )
    btnExit.place(x=250, y=150)
    btnSignup = Button(
        loginWin,
        text="Sign up",
        fg="black",
        bg="yellow",
        font=("Arial", 10, "bold"),
        command=SignupWindow,
    )
    btnSignup.place(x=10, y=110)
    btnChangePassword = Button(
        loginWin,
        text="Change Password",
        bg="orange",
        fg="black",
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
    txtPasSignUp = Entry(signupWin, width=23, bg="#e0f7fa")

    txtIDSignUp.place(x=120, y=40)
    txtUserSignUp.place(x=120, y=70)
    txtPasSignUp.place(x=120, y=100)

    role = StringVar(value="")

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

    def CreateAccount():
        # connection = connectDataBase() # Connect to Database   #cursor = connection.cursor()
        userid = txtIDSignUp.get().strip()
        username = txtUserSignUp.get().strip()
        password = txtPasSignUp.get().strip()
        selectedRole = role.get()
        if not selectedRole:
            messagebox.showwarning("Warning", "Please select exactly one role!")
            return

        # Valid Input
        if not userid or not username or not password:
            messagebox.showwarning("Warning", "All fields are required!")
            return
        """
            if len(password) < 8 or not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password):
                messagebox.showwarning("Warning", "Password must be at least 8 characters long and contain both letters and numbers!")
                return"""
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
                    (userid, username, hashedPassword.decode(), selectedRole),
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
        bg="green",
        fg="white",
        font=("Arial", 12, "bold"),
        command=CreateAccount,
    )
    btnCreate.place(x=40, y=160)
    btnExitSignUp = Button(
        signupWin,
        text="Exit",
        bg="red",
        fg="white",
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
                    ExecuteQuery(
                        "UPDATE Users SET Password = %s WHERE UserID = %s",
                        (hashedNewPassword.decode(), userID),
                    )
                    messagebox.showinfo("Success", "Password changed successfully!")
                    changePassWin.destroy()
                else:
                    messagebox.showerror("Error", "Current password is incorrect!")
            else:
                messagebox.showerror("Error", "User not found!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    btnChange = Button(
        changePassWin,
        text="Change Password",
        bg="green",
        fg="white",
        font=("Arial", 12, "bold"),
        command=HandleChangePassword,
    )
    btnChange.place(x=20, y=180)
    btnExit = Button(
        changePassWin,
        text="Exit",
        bg="red",
        fg="white",
        font=("Arial", 12, "bold"),
        command=changePassWin.destroy,
    )
    btnExit.place(x=220, y=180)

    txtCurrentPassword.focus()

    #============================================================

# USER INTERFACE FUNCTION
# Macke CenterWindow
def makecenter(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry("{}x{}+{}+{}".format(width, height, x, y))

def LoadItemsToTree(tree):
    connection = connectDataBase()
    if not connection:
        messagebox.showerror("Error", "Failed to connect to database!")
        return
    try:
        cursor = connection.cursor()
        # Query data form Items table
        query = "SELECT ItemID,Name,Unit,Cost,Category FROM Items WHERE Cost > 0"
        cursor.execute(query)
        rows = cursor.fetchall()  # Get all result

        if not rows:
            messagebox.showinfo("Information", "No items found in the database.")
            return
        # Delete old data in TreeView
        for item in tree.get_children():
            tree.delete(item)
        # Add data into tree_Items
        for row in rows:
            tree.insert("", "end", value=row)
        tree.selection_remove(tree.selection())
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        cursor.close()
        connection.close()

def RefreshTreeView(tree):
    try:
        LoadItemsToTree(tree)
        # messagebox.showinfo("Success","TreeView refreshed successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to refresh TreeView: {e}")


# Window
def MainWindow():
    # Create Window
    window = Tk()
    window.title("Order Drink Software")
    window.geometry("900x600")
    window.configure(bg="#f8f9fa")  # Light Background more friendly
    makecenter(window)

    # Make style
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Treeview",
        background="skyblue",
        foreground="black",
        rowheight=21,
        fiedbackground="skyblue",
    )
    style.map("Treeview", background=[("selected", "green")])

    # Create Tabs_Menu
    menutab = ttk.Notebook(window, style="TNotebook")
    menutab.pack(fill="both", expand=True)
    tabOrder = Frame(menutab, bg="#AFEEEE")
    tabLayout = Frame(menutab, bg="#AFEEEE")
    tabUtilities = Frame(menutab, bg="#AFEEEE")
    menutab.add(tabLayout, text="Layout")
    menutab.add(tabOrder, text="Order")
    menutab.add(tabUtilities, text="Utilities")

    # =====TAB ORDER=====#
    # Tree_Item Zone
    Label(tabOrder, text="Menu", font=("Arial", 14, "bold"), bg="#AFEEEE").place(
        x=20, y=40
    )
    tree_Items = ttk.Treeview(
        tabOrder,
        columns=("ID", "Name", "Unit", "Cost", "Category"),
        show="headings",
        height=10,
    )
    tree_Items.place(x=20, y=70, width=500, height=380)
    # Create Title and Size for Column
    columns = [("ID", 60), ("Name", 120), ("Unit", 60), ("Cost", 80), ("Category", 100)]
    for column, width in columns:
        tree_Items.heading(column, text=column)
        tree_Items.column(column, width=width, anchor="center")

    # Order Details Zone
    Label(
        tabOrder, text="Order Details", font=("Arial", 14, "bold"), bg="#AFEEEE"
    ).place(x=550, y=10)
    tree_OrderDetail = ttk.Treeview(
        tabOrder,
        columns=("OrderID", "ItemID", "Quantity", "TotalPrice"),
        show="headings",
        height=7,
    )
    tree_OrderDetail.place(x=550, y=40, width=320, height=200)
    # Create Title and Size for Column
    columnOrderDetails = [
        ("OrderID", 80),
        ("ItemID", 80),
        ("Quantity", 80),
        ("TotalPrice", 80),
    ]
    for column, width in columnOrderDetails:
        tree_OrderDetail.heading(column, text=column)
        tree_OrderDetail.column(column, width=width, anchor="center")

    # Order Zone
    Label(tabOrder, text="Order", font=("Arial", 14, "bold"), bg="#AFEEEE").place(
        x=550, y=280
    )
    tree_Order = ttk.Treeview(
        tabOrder,
        columns=("UserID", "Table", "OrderDate", "TotalPrice", "Status"),
        show="headings",
        height=7,
    )
    tree_Order.place(x=550, y=310, width=320, height=200)
    # Create Title and Size for Column
    columnOrder = [
        ("UserID", 64),
        ("Table", 64),
        ("OrderDate", 64),
        ("TotalPrice", 64),
        ("Status", 64),
    ]
    for column, width in columnOrder:
        tree_Order.heading(column, text=column)
        tree_Order.column(column, width=width, anchor="center")
    # Tree For Recept
    tree_Temp = ttk.Treeview(
        tabOrder,
        columns=("UserID", "Table", "OrderDate", "TotalPrice", "Status"),
        show="headings",
        height=0,
    )
    tree_Temp.place(x=550, y=310, width=0, height=0)
    # Create Title and Size for Column
    columnOrder = [
        ("UserID", 64),
        ("Table", 64),
        ("OrderDate", 64),
        ("TotalPrice", 64),
        ("Status", 64),
    ]
    for column, width in columnOrder:
        tree_Temp.heading(column, text=column)
        tree_Temp.column(column, width=width, anchor="center")

    # Display Total
    Label(
        tabOrder, text="Enter Items:", font=("Arial", 12, "bold"), bg="#AFEEEE"
    ).place(x=20, y=10)
    Label(tabOrder, text="Total:", font=("Arial", 12, "bold"), bg="#AFEEEE").place(
        x=550, y=250
    )
    Label(tabOrder, text="Bill:", font=("Arial", 12, "bold"), bg="#AFEEEE").place(
        x=550, y=520
    )
    Label(tabOrder, text="VND", font=("Arial", 12, "bold"), bg="#AFEEEE").place(
        x=750, y=250
    )
    Label(tabOrder, text="VND", font=("Arial", 12, "bold"), bg="#AFEEEE").place(
        x=750, y=520
    )
    txtItems = Entry(tabOrder, textvariable=StringVar(), bg="white", font=("Arial", 12))
    txtItems.place(x=130, y=10, width=280)
    txtTotal = Entry(tabOrder, textvariable=StringVar(), bg="white", font=("Arial", 12))
    txtTotal.place(x=600, y=250, width=150)
    txtBill = Entry(tabOrder, textvariable=StringVar(), bg="white", font=("Arial", 12))
    txtBill.place(x=600, y=520, width=150)

    # Load data into TreeView
    LoadItemsToTree(tree_Items)
    
    #============================================================

    def BtnAdd_Click():
        global userID  # User ID
        orderID = None
        # Connect to database
        connection = connectDataBase()
        if not connection:
            messagebox.showerror("Error", "Database connecton failed!")
            return
        try:
            cursor = connection.cursor()
            # Get selected items in tree_Items
            selectedItems = tree_Items.selection()
            if not selectedItems:
                messagebox.showinfo("Message", "You have not selected any item yet")
                return
            # Check is Tree_Order have Order with status is "Pending"
            pendingOrder = None
            for order in tree_Order.get_children():
                orderData = tree_Order.item(order, "values")
                if orderData[4] == "Pending":
                    pendingOrder = orderData
                    break
            if not pendingOrder:
                # Create new Order if haven't Order with "Pending" status
                orderDate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                totalPrice = 0  # initialize value
                status = "Pending"  # Default status
                table = "Takeway"

                # Add order into 'Orders'
                cursor.execute(
                    """
                                        INSERT INTO Orders (UserID,Tables,OrderDate,TotalAmount,Status)
                                        VALUES (%s,%s,%s,%s,%s)
                                        """,
                    (userID, table, orderDate, totalPrice, status),
                )
                connection.commit()
                if cursor.rowcount == 0:
                    messagebox.showerror("Error", "Failed to create a new order.")
                    return

                # Get OrderID of item with Pending status from Orders table
                cursor.execute(
                    """
                                    SELECT OrderID FROM Orders
                                    WHERE UserID = %s AND Status = %s
                                    """,
                    (userID, "Pending"),
                )
                result = cursor.fetchone()
                # cursor.fetchall()

                if result:
                    orderID = result[0]
                else:
                    messagebox.showerror(
                        "Error", "No pending order found. Please create a new order."
                    )
                    return

                # Update TreeView tree_Order
                tree_Order.insert(
                    "",
                    "end",
                    values=(userID, table, orderDate, totalPrice, status),
                )
                # Update TreeView tree_Temp
                tree_Temp.insert(
                    "",
                    "end",
                    values=(userID, table, orderDate, totalPrice, status),
                )
                # messagebox.showinfo("Message","New order created successfully!")
            else:
                # Get OrderID of item with Pending status from Orders table
                cursor.execute(
                    """
                                    SELECT OrderID FROM Orders
                                    WHERE UserID = %s AND Status = %s
                                    """,
                    (userID, "Pending"),
                )
                result = cursor.fetchone()
                if result:
                    orderID = result[0]
                else:
                    messagebox.showerror("Error", "Could not find pending order ID.")
                    return

            cursor.fetchall()  # Hoặc cursor.nextset()

            # OrderDetails list and TotalPrice
            orderDetails = []  # Storage list orderdetails
            totalCost = 0  # Totalprice for all selected items

            for itemID in selectedItems:
                item = tree_Items.item(itemID, "values")
                if len(item) < 4:
                    continue

                itemID, name, unit, cost, category = item
                quantity = 1
                cost = int(cost)

                # Check if item already exists in tree_OrderDetails
                itemExists = False
                for child in tree_OrderDetail.get_children():
                    existingItem = tree_OrderDetail.item(child, "values")
                    if existingItem[1] == itemID:  # Check if ItemID matches
                        currentQuantity = int(existingItem[2])
                        newQuantity = currentQuantity + quantity
                        newTotalPrice = newQuantity * cost
                        # Update quantity and cost tree_OrderDetails
                        tree_OrderDetail.item(
                            child,
                            values=(orderID, itemID, newQuantity, newTotalPrice),
                        )
                        # Update information in database
                        cursor.execute(
                            """
                                            UPDATE OrderDetails
                                            SET Quantity = %s, TotalPrice = %s
                                            WHERE OrderID = %s AND ItemID = %s
                                            """,
                            (newQuantity, newTotalPrice, orderID, itemID),
                        )
                        connection.commit()

                        totalCost += newTotalPrice - (currentQuantity * cost)
                        itemExists = True
                        break
                # If item not exists , add new
                if not itemExists:
                    totalItemCost = cost * quantity
                    totalCost += totalItemCost

                    # Add into TreeView tree_OrderDetail
                    tree_OrderDetail.insert(
                        "",
                        "end",
                        values=(orderID, itemID, quantity, totalItemCost),
                    )
                    # Storage Order Details into List
                    orderDetails.append((orderID, itemID, quantity, totalItemCost))

            # Add all order details into OrderDetails Table
            if orderDetails:
                cursor.executemany(
                    """
                                    INSERT INTO OrderDetails (OrderID,ItemID,Quantity,TotalPrice)
                                    VALUES (%s,%s,%s,%s)
                                    """,
                    orderDetails,
                )
                connection.commit()

            # Update TotalAmount for Tree_Order table
            cursor.execute(
                """
                                    SELECT SUM(TotalPrice) FROM OrderDetails WHERE OrderID = %s
                                    """,
                (orderID,),
            )
            totalPrice = cursor.fetchone()[0] or 0
            neworderDate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                """
                                    UPDATE Orders 
                                    SET TotalAmount = %s,
                                        OrderDate = %s
                                    WHERE OrderID = %s
                                    """,
                (totalPrice, neworderDate, orderID),
            )
            connection.commit()

            # Update Tree_Order
            for order in tree_Order.get_children():
                if tree_Order.item(order, "values")[0] == str(orderID):
                    tree_Order.item(
                        order, values=(orderID, pendingOrder[0], totalPrice, "Pending")
                    )
                    break

            # Update Tree_Temp
            for order in tree_Order.get_children():
                if tree_Temp.item(order, "values")[0] == str(orderID):
                    tree_Temp.item(
                        order, values=(orderID, pendingOrder[0], totalPrice, "Pending")
                    )
                    break

            calculatedTotal = 0
            for item in tree_OrderDetail.get_children():
                totalPrice = tree_OrderDetail.item(item, "values")[3]
                calculatedTotal += int(totalPrice)
            # Update txtTotal
            txtTotal.delete(0, "end")
            txtTotal.insert(0, calculatedTotal)

            # Success noitification
            # messagebox.showinfo("Success",f"Added/Update {len(selectedItems)} items to order {orderID}. Total cost: {totalCost}",)
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Database error: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        finally:
            if "cursor" in locals():
                cursor.close()
            if "connection" in locals():
                connection.close()

    def BtnDelete_Click():
        global quantityBill, quantityItems

        selectedItems = tree_OrderDetail.selection()
        if not selectedItems:
            messagebox.showinfo("Message", "You have not selectedany order to delete.")
            return

        result = messagebox.askyesno(
            "Confirmation", "Are you sure you want to delete the selected orders?"
        )
        if not result:
            return

        try:
            # Prepare Data
            deletePairs = [
                (
                    tree_OrderDetail.item(item, "values")[0],  # OrderID
                    tree_OrderDetail.item(item, "values")[1],
                )  # ItemID
                for item in selectedItems
            ]

            # Validate Data
            if not deletePairs:
                messagebox.showerror("Error", "No valid ItemID found in selection.")
                return

            # Database operations
            connection = connectDataBase()
            if not connection:
                messagebox.showerror("Error", "Database connection failed!")
                return

            cursor = connection.cursor()

            # Delete each pair (OrderId, ItemID)
            for orderID, itemID in deletePairs:
                query = "DELETE FROM OrderDetails WHERE OrderID = %s AND ItemID = %s"
                cursor.execute(query, (orderID, itemID))

            # Update GUI
            for item in selectedItems:
                tree_OrderDetail.delete(item)

            # Delete Order with Status = 'Pending' in Order Table
            if len(tree_OrderDetail.get_children()) < 1:
                queryOrder = "DELETE FROM `Orders` WHERE Status = %s"
                cursor.execute(queryOrder, ("Pending",))
                quantityBill -= 1

            connection.commit()

            for item in tree_Order.get_children():
                itemValues = tree_Order.item(item, "value")

            # Ensure correct indexign for "Status"
            statusIndex = 4
            if len(itemValues) > statusIndex and itemValues[statusIndex] == "Pending":
                tree_Order.delete(item)

            # Update Totals
            remainingTotalCost = sum(
                int(tree_OrderDetail.item(item, "values")[3])
                for item in tree_OrderDetail.get_children()
            )

            # Update txtTotal
            txtTotal.delete(0, END)
            txtTotal.insert(0, remainingTotalCost)
            quantityItems -= len(selectedItems)

            messagebox.showinfo(
                "Success", "Selected orders have been deleted successfully."
            )
        except Exception as e:
            if connection:
                connection.rollback()
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            if "cursor" in locals():
                cursor.close()
            if "connection" in locals():
                connection.close()

    def BtnCancel_Click():
        # Get all items in tree_OrderDetails
        selectedItems = tree_OrderDetail.get_children()
        if not selectedItems:
            messagebox.showinfo("Message", "You have not selected any item yet")
            return

        # Display confirmation Dialog
        result = messagebox.askyesno(
            "Confirmation", "Are you sure you want ti cancel the selected orders?"
        )
        if not result:
            return

        try:
            # Connect to Database
            connection = connectDataBase()
            if not connection:
                messagebox.showerror("Error", "Database connection failed!")
                return
            cursor = connection.cursor()

            # Get OrderID of item with Pending status from Orders table
            cursor.execute(
                """
                            SELECT OrderID FROM Orders
                            WHERE UserID = %s AND Status = %s
                            """,
                (userID, "Pending"),
            )
            result = cursor.fetchone()
            if result:
                currentOrderID = result[0]
            else:
                messagebox.showerror("Error", "No current OrderID found.")
                return

            cursor.fetchall()  # Hoặc cursor.nextset()

            while cursor.nextset():
                pass

            # Delete all data in OrderDetails Table
            query = "DELETE FROM OrderDetails WHERE OrderID =%s"
            cursor.execute(query, (currentOrderID,))

            cursor.execute(
                """
                                DELETE FROM Orders WHERE OrderID = %s
                                """,
                (currentOrderID,),
            )
            connection.commit()
            # Delete all items in tree_OrderDetails
            for itemID in selectedItems:
                tree_OrderDetail.delete(itemID)
            for itemID in tree_Order.get_children():
                tree_Order.delete(itemID)

            # Update Totals
            remainingTotalCost = sum(
                int(tree_OrderDetail.item(item, "values")[3])
                for item in tree_OrderDetail.get_children()
            )

            # Update txtTotal
            txtTotal.delete(0, END)
            txtTotal.insert(0, remainingTotalCost)

            messagebox.showinfo(
                "Success", "All orders have been canceled successfully."
            )
        except Exception as e:
            # Rollback if have error
            if connection:
                connection.rollback()
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            # Close connection database
            if "cursor" in locals():
                cursor.close()
            if "connection" in locals():
                connection.close()

    def BtnPay_Click():
        global revenue, quantityBill, quantityItems

        # Get selectedItem in tree_Order
        selectedOrder = tree_Order.selection()
        if not selectedOrder:
            messagebox.showinfo("Message", "You have not selected any item yet.")
            return
        # Display confirm pay dialog
        result = messagebox.askyesno(
            "Confirmation", "Are you sure you want to pay for the selected orders?"
        )
        if not result:
            return
        try:
            # Connect to database:
            connection = connectDataBase()
            if not connection:
                messagebox.showerror("Error", "Database connection failded!")
                return
            cursor = connection.cursor()
            orderIDs = []
            for item in selectedOrder:
                userid = tree_Order.item(item, "values")[0]
                orderDateStr = tree_Order.item(item, "values")[2]
                status = tree_Order.item(item, "values")[4]
                # print(str(orderDateStr))
            try:
                orderDate = datetime.datetime.strptime(
                    orderDateStr, "%Y-%m-%d %H:%M:%S"
                )
                formattedDate = orderDate.strftime("%Y-%m-%d %H:%M:%S")
                if status == "Pending":
                    messagebox.showerror(
                        "Error", "You need to completed order before pay!"
                    )
                    return
            except ValueError:
                messagebox.showerror(
                    "Error", f"Invalid date format for UserID {userid}."
                )

            # Get OrderID from database
            query = """
                            SELECT OrderID FROM Orders
                            WHERE UserID = %s AND OrderDate = %s
                        """
            cursor.execute(query, (userid, formattedDate))
            result = cursor.fetchone()
            if result:
                orderIDs.append(result[0])
            else:
                messagebox.showerror("Error", "No valid orders found.")
                return

            totalCostSelected = 0
            for currentOrderID in orderIDs:
                # Get order information from Orders table
                queryOrder = "SELECT * FROM Orders WHERE OrderID = %s"
                cursor.execute(queryOrder, (currentOrderID,))
                orderInfor = cursor.fetchone()

            if not orderInfor:
                messagebox.showerror(
                    "Error", f"No order found with OrderID: {currentOrderID}"
                )

            # Get order details from OrderDetails Table
            queryOrderDetails = "SELECT * FROM OrderDetails WHERE OrderID = %s"
            cursor.execute(queryOrderDetails, (currentOrderID,))
            orderDetails = cursor.fetchall()

            if not orderDetails:
                messagebox.showerror(
                    "Error", f"No order details found with OrderID: {currentOrderID}"
                )

            # Caculate TotalPrice
            totalCost = sum(detail[3] for detail in orderDetails)
            totalCostSelected += totalCost
            try:
                bill = int(txtBill.get().strip()) if txtBill.get().strip() else 0
            except ValueError:
                messagebox.showerror("Error", "Invalid bill value.")
                return

            # Print Order
            # Create Bill Screen
            billscreen = Toplevel()
            billscreen.title("Bill Infomation")
            billscreen.resizable(height=True, width=True)
            billscreen.minsize(height=400, width=390)
            billscreen.configure(bg="#00274d")

            billscreen.attributes("-topmost", 1)  # Make sure it stays on top
            billscreen.lift()
            makecenter(billscreen)

            # Create Text Bill Information
            txtBillInfo = Text(billscreen, width=45, height=20)
            txtBillInfo.place(x=10, y=10)

            # Hiển thị thông tin hóa đơn trong Text
            txtBillInfo.insert(END, "Drink Order Bill:\n")
            txtBillInfo.insert(END, f"Order ID: {currentOrderID}\n")
            txtBillInfo.insert(END, f"UserID: {orderInfor[1]}\n")
            txtBillInfo.insert(END, f"Table: {orderInfor[5]}\n")
            txtBillInfo.insert(END, f"Date: {orderInfor[2]}\n")
            txtBillInfo.insert(END, "+" + "-" * 43 + "+\n")
            for detail in orderDetails:
                txtBillInfo.insert(
                    END,
                    f"Item: {detail[2]} | Quantity: {detail[3]} | Price: {detail[4]} VND\n",
                )
            txtBillInfo.insert(END, "+" + "-" * 43 + "+\n")
            txtBillInfo.insert(END, f"Total: {bill} VND\n")

            def Exit():
                billscreen.destroy()

            btnExit = Button(
                billscreen,
                text="Close",
                font=("Arial", 10, "bold"),
                fg="white",
                bg="Red",
                command=Exit,
            )
            btnExit.place(x=285, y=350, height=40, width=90)
            btnBill = Button(
                billscreen,
                text="Bill",
                font=("Arial", 10, "bold"),
                fg="black",
                bg="cyan",
                command=SaveBill,
            )
            btnBill.place(x=10, y=350, height=40, width=90)

            # Update revenue
            revenue += int(bill)
            txtRevenue.delete(0, END)
            txtRevenue.insert(0, revenue)

            # Delete selected item out of tree_Order
            for itemID in selectedOrder:
                tree_Order.delete(itemID)

            # Save change into Database
            connection.commit()
            messagebox.showinfo("Success", "Payment completed successfully.")

            # Update txtBill
            txtBill.delete(0, END)
            billscreen.mainloop()
        except Exception as e:
            if connection:
                connection.rollback()
            messagebox.showerror("Error", f"An occourred: {str(e)}")
        finally:
            if "cursor" in locals():
                cursor.close()
            if "connection" in locals():
                connection.close()

    def BtnOrder_Click():
        global orderNumber, quantityBill, quantityItems, userID

        # Get Selected Table Infor
        tableName = selectedTable.get()

        # Clear Old Order
        if txtReceipt.get("1.0", "end").strip():
            txtReceipt.delete("1.0", "end")

        try:
            # Connect to database
            connection = connectDataBase()
            if not connection:
                messagebox.showerror("Error", "Database connection failed!")
                return
            cursor = connection.cursor()

            # Check if there are orthers in tree_Order
            items = tree_Order.get_children()
            if not items:
                messagebox.showinfo("Message", "You have not selected any item yet")
                return

            # Get total price from txtTotal
            totalCost = int(txtTotal.get().strip()) if txtTotal.get().strip() else 0

            # Filter orders with "Pending" status
            pendingOrder = [
                itemID
                for itemID in items
                if tree_Order.item(itemID, "values")[4] == "Pending"
            ]
            if not pendingOrder:
                messagebox.showinfo("Message", "No orders with 'Pending' status!")
                return

            # Get datetime now and formating
            currentDateTime = datetime.datetime.now()
            formattedDateTime = currentDateTime.strftime("%Y-%m-%d %H:%M:%S")

            # Update TotalPrice in tree_Order and database for all "Pending" orders
            for itemID in pendingOrder:
                order = tree_Order.item(itemID, "values")
                userID, table, orderDate, totalPrice, status = (
                    order[0],
                    order[1],
                    order[2],
                    order[3],
                    order[4],
                )

                # Update the TotalPrice and Table for the current "Pending" order
                cursor.execute(
                    """UPDATE Orders 
                                SET TotalAmount = %s, Tables = %s,OrderDate = %s  
                                WHERE Status = %s""",
                    (totalCost, tableName, formattedDateTime, "Pending"),
                )
                tree_Order.item(
                    itemID,
                    values=(userID, tableName, formattedDateTime, totalPrice, status),
                )

            cursor.execute(
                "UPDATE Orders SET Status = %s WHERE Status = %s",
                ("Completed", "Pending"),
            )
            tree_Order.item(
                pendingOrder,
                values=(userID, tableName, formattedDateTime, totalCost, "Completed"),
            )

            # Comit changes to database
            connection.commit()

            # Update GUI information
            txtNumBill.delete(0, "end")
            txtNumBill.insert(0, orderNumber)
            quantityItems += len(tree_OrderDetail.get_children())
            quantityBill += 1
            txtNumItems.delete(0, "end")
            txtNumItems.insert(0, quantityItems)
            txtTotal.delete(0, "end")

            # Delete items in Order_Details
            for child in tree_OrderDetail.get_children():
                tree_OrderDetail.delete(child)

            # Display sucess message
            messagebox.showinfo("Success", "Order updated sucessfully!")

        except Exception as e:
            if connection:
                connection.rollback()
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            if "cursor" in locals():
                cursor.close()
            if "connection" in locals():
                connection.close()
        # Cancel selected items in tree_Ordered and tree_Items
        tree_OrderDetail.selection_remove(tree_OrderDetail.selection())
        tree_Items.selection_remove(tree_Items.selection())

    def BtnFind_Click():
        search_term = txtItems.get().strip().lower()
        if not search_term:
            messagebox.showinfo("Message", "Enter an item name or item id, please!")
            return
        # Initialize storagelist items found
        matchedItems = []

        for itemID in tree_Items.get_children():
            item = tree_Items.item(itemID, "values")
            itemIDValue, name, unit, cost, category = item
            if (
                search_term in itemIDValue.lower()
                or search_term in name.lower()
                or search_term in unit.lower()
                or search_term in str(cost).lower()
                or search_term in category.lower()
            ):
                matchedItems.append(itemID)

        if matchedItems:
            # Delete seleted item before it
            tree_Items.selection_remove(tree_Items.selection())
            # Selected and display rows found
            for itemID in matchedItems:
                tree_Items.selection_add(itemID)
                tree_Items.focus(itemID)
            messagebox.showinfo(
                "Message", f"Found {len(matchedItems)} matching item(s)."
            )
            txtItems.delete(0, END)
        else:
            messagebox.showinfo(
                "Message",
                "No matching item found! Try checking your input or search criteria.",
            )

    def TreeOrderSelectedIndexChange(event):
        # Get selected item in tree_Ordered
        selectedItem = tree_Order.selection()
        if not selectedItem:
            txtBill.delete(0, END)
            return
        # Get value of the selected item
        item = tree_Order.item(selectedItem, "values")
        total = item[3]

        txtBill.delete(0, END)
        txtBill.insert(0, total)

    tree_Order.bind("<<TreeviewSelect>>", TreeOrderSelectedIndexChange)
    tree_Order.bind("<Return>", lambda event: BtnPay_Click())
    tree_OrderDetail.bind("<Return>", lambda event: BtnOrder_Click())
    tree_Items.bind("<Return>", lambda event: BtnAdd_Click())
    txtItems.bind("<Return>", lambda event: BtnFind_Click())

    def SaveReceipt():
        items = tree_Temp.get_children()
        now = datetime.datetime.now()
        receiptName = f"Receipt_{now.strftime('%Y%m%d_%H%M%S')}.txt"
        # Open savedialog to save bill
        filePath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=receiptName,
            filetypes=[("Text file", "*.txt")],
        )
        if not filePath:
            return  # User canceled save operation
        with open(filePath, "w") as file:
            file.write("Drink Order Receipt:\n")
            file.write(f"Date: {now.strftime('%Y-%m-%d %H:%M:%S')}\n")
            file.write("+" + "-" * 24 + "+" + "\n")
            for itemID in items:
                item = tree_Temp.item(itemID, "value")
                file.write(
                    f"UserID:{item[0]}\nTable: {item[1]}\nDate: {item[2]}\nTotalPrice: {item[3]}\nStatus: {item[4]}\n"
                )
            file.write("+" + "-" * 24 + "+" + "\n")
            file.write(f"Total: {txtRevenue.get()} VND\n")
            file.close()
        messagebox.showinfo("Save Receipt", f"Receipt saved to {filePath}")

    def OpenReceipt():
        messagebox.showinfo("Message", "Select the file which begin with Receipt_* ")
        filePath = filedialog.askopenfilename(
            filetypes=[("Text File", "*.txt"), ("All Files", "*.*")]
        )
        if filePath:
            try:
                with open(filePath, "r") as file:
                    # Read content file
                    fileContent = file.read()
                    # Show content into widget Text
                    txtReceipt.delete("1.0", "end")  # Delete Now Content
                    txtReceipt.insert("1.0", fileContent)  # Add new content into widget
            except Exception as e:
                print(f"Error opening file: {e}")

    def SaveBill():
        now = datetime.datetime.now()
        billName = f"Bill_{now.strftime('%Y%m%d_%H%M%S')}.txt"
        # Open savedialog to save bill
        filePath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=billName,
            filetypes=[("Text file", "*.txt")],
        )
        if not filePath:
            return  # User canceled save operation
        with open(filePath, "w") as file:
            file.write(txtReceipt.get("1.0", "end-1c"))
            file.close()
        messagebox.showinfo("Save Bill", f"Bill saved to {filePath}")

    # Create Setting Items
    def ItemSetting():
        items = tree_Items.get_children()
        addItems = Toplevel()
        addItems.title("Items Setting")
        addItems.resizable(height=True, width=True)
        addItems.minsize(height=300, width=235)
        addItems.configure(bg="#00274d")

        addItems.attributes("-topmost", 1)  # Make sure it stays on top
        addItems.lift()
        makecenter(addItems)

        def BtnExitAddItm_Click():
            addItems.destroy()

        # Create Label
        lblItemSettingTitle = Label(
            addItems,
            text="ITEM SETTING",
            font=("Arial", 14, "bold"),
            bg="#00274d",
            fg="white",
        )
        lblItemSettingTitle.place(x=50, y=10)
        lblItemsID = Label(addItems, text="Item ID:", bg="#00274d", fg="white")
        lblItemsID.place(x=10, y=40)
        lblItemsName = Label(addItems, text="Item Name:", bg="#00274d", fg="white")
        lblItemsName.place(x=10, y=70)
        lblItemsUnit = Label(addItems, text="Items Unit:", bg="#00274d", fg="white")
        lblItemsUnit.place(x=10, y=100)
        lblItemsCost = Label(addItems, text="Item Cost:", bg="#00274d", fg="white")
        lblItemsCost.place(x=10, y=130)
        lblItemsCategory = Label(
            addItems, text="Item Category:", bg="#00274d", fg="white"
        )
        lblItemsCategory.place(x=10, y=160)
        # Create Entry
        txtItemID = Entry(addItems, textvariable=StringVar, bg="white", width=20)
        txtItemID.place(x=100, y=40)
        txtItemName = Entry(addItems, textvariable=StringVar, bg="white", width=20)
        txtItemName.place(x=100, y=70)
        txtItemUnit = Entry(addItems, textvariable=StringVar, bg="white", width=20)
        txtItemUnit.place(x=100, y=100)
        txtItemCost = Entry(addItems, textvariable=StringVar, bg="white", width=20)
        txtItemCost.place(x=100, y=130)
        txtItemCategory = Entry(addItems, textvariable=StringVar, bg="white", width=20)
        txtItemCategory.place(x=100, y=160)

        # Add Items
        def BtnAddItm_Click():
            itemID = txtItemID.get()
            itemName = txtItemName.get()
            itemUnit = txtItemUnit.get()
            itemCost = txtItemCost.get()
            itemCategory = txtItemCategory.get()

            if itemID and itemName and itemCost:
                try:
                    db = connectDataBase()
                    cursor = db.cursor()
                    cursor.execute(
                        "INSERT INTO Items (ItemID, Name, Unit, Cost, Category) VALUES (%s, %s, %s, %s,%s)",
                        (itemID, itemName, itemUnit, itemCost, itemCategory),
                    )
                    db.commit()
                    db.close()
                    tree_Items.insert(
                        "",
                        "end",
                        values=(itemID, itemName, itemUnit, itemCost, itemCategory),
                    )
                    txtItemID.delete(0, END)
                    txtItemName.delete(0, END)
                    txtItemUnit.delete(0, END)
                    txtItemCost.delete(0, END)
                    txtItemCategory.delete(0, END)
                    messagebox.showinfo("Success", "Item added successfully!")
                except mysql.connector.Error as err:
                    messagebox.showerror("Error", f"Error: {err}")
            else:
                messagebox.showinfo(
                    "Input Error", "Item ID, Item Name, and Item Cost cannot be empty!"
                )

        # Delete Items
        def BtnDeleteItm_Click():
            selected_item = tree_Items.selection()
            if selected_item:
                itemID = tree_Items.item(selected_item)["values"][0]
                try:
                    db = connectDataBase()
                    cursor = db.cursor()
                    cursor.execute("DELETE FROM Items WHERE ItemID = %s", (itemID,))
                    db.commit()
                    db.close()
                    tree_Items.delete(selected_item)
                    messagebox.showinfo("Success", "Item deleted successfully!")
                except mysql.connector.Error as err:
                    messagebox.showerror("Error", f"Error: {err}")
            else:
                messagebox.showinfo("Selection Error", "No item selected!")

        # Edit Items
        def BtnEditItm_Click():
            selected_item = tree_Items.selection()
            if selected_item:
                itemID = tree_Items.item(selected_item)["values"][0]
                itemName = txtItemName.get()
                itemUnit = txtItemUnit.get()
                itemCost = txtItemCost.get()
                itemCategory = txtItemCategory.get()

                if itemName and itemCost:
                    try:
                        db = connectDataBase()
                        cursor = db.cursor()
                        cursor.execute(
                            """
                                        UPDATE Items 
                                        SET Name = %s, Unit = %s, Cost = %s 
                                        WHERE ItemID = %s
                                    """,
                            (itemName, itemUnit, itemCost, itemID),
                        )
                        db.commit()
                        db.close()

                        # Cập nhật lại giao diện
                        tree_Items.item(
                            selected_item,
                            values=(itemID, itemName, itemUnit, itemCost, itemCategory),
                        )
                        txtItemID.delete(0, END)
                        txtItemName.delete(0, END)
                        txtItemUnit.delete(0, END)
                        txtItemCost.delete(0, END)
                        txtItemCategory.delete(0, END)
                        messagebox.showinfo("Success", "Item updated successfully!")
                    except mysql.connector.Error as err:
                        messagebox.showerror("Error", f"Error: {err}")
                else:
                    messagebox.showinfo(
                        "Input Error", "Item Name and Item Cost cannot be empty!"
                    )
            else:
                messagebox.showinfo("Selection Error", "No item selected!")

        # Create Button
        btnAddItm = Button(
            addItems, text="Add Item", bg="green", fg="white", command=BtnAddItm_Click
        )
        btnAddItm.place(x=10, y=230)
        btnExitAddItm = Button(
            addItems, text="Exit", bg="red", fg="white", command=BtnExitAddItm_Click
        )
        btnExitAddItm.place(x=200, y=270)
        btnEditItm = Button(
            addItems,
            text="Edit Item",
            bg="yellow",
            fg="black",
            command=BtnEditItm_Click,
        )
        btnEditItm.place(x=170, y=230)
        btnDeleteItm = Button(
            addItems,
            text="Delete Item",
            bg="red",
            fg="white",
            command=BtnDeleteItm_Click,
        )
        btnDeleteItm.place(x=80, y=230)

        addItems.mainloop()


    #============================================================

    # Add Button
    btnAdd = Button(
        tabOrder,
        text="Add",
        command=BtnAdd_Click,
        fg="white",
        bg="Green",
        font=("Arial", 10, "bold"),
    )
    btnAdd.place(x=20, y=460, width=120, height=90)
    # Find Button
    btnFind = Button(
        tabOrder,
        text="Find",
        command=BtnFind_Click,
        fg="white",
        bg="#1E90FF",
        font=("Arial", 10, "bold"),
    )
    btnFind.place(x=430, y=10, width=90, height=40)
    # Order Button
    btnOrder = Button(
        tabOrder,
        text="Order",
        command=BtnOrder_Click,
        bg="#28a745",
        fg="white",
        font=("Arial", 10, "bold"),
    )
    btnOrder.place(x=800, y=250, width=70)
    # Delete Button
    btnDelete = Button(
        tabOrder,
        text="Delete",
        command=BtnDelete_Click,
        fg="red",
        bg="yellow",
        font=("Arial", 10, "bold"),
    )
    btnDelete.place(x=220, y=510, width=90, height=40)
    # Cancel Button
    btnCancel = Button(
        tabOrder,
        text="Cancel",
        command=BtnCancel_Click,
        fg="white",
        bg="red",
        font=("Arial", 10, "bold"),
    )
    btnCancel.place(x=320, y=510, width=90, height=40)
    # Pay button
    btnPay = Button(
        tabOrder,
        text="Pay",
        command=BtnPay_Click,
        bg="Orange",
        fg="white",
        font=("Arial", 10, "bold"),
    )
    btnPay.place(x=800, y=520, width=70)
    # Refresh button
    btnRefresh = Button(
        tabOrder,
        text="Refresh Items",
        command=RefreshTreeView(tree_Items),
        bg="#007bff",
        fg="white",
        font=("Arial", 10, "bold"),
    )
    btnRefresh.place(x=420, y=510, width=100, height=40)

    # =====TAB LAYOUT=====#
    Label(
        tabLayout, text="Select Table Layout", font=("Arial", 14, "bold"), bg="#AFEEEE"
    ).pack(pady=10)
    frameTables = Frame(tabLayout, bg="#AFEEEE")
    frameTables.pack(fill=BOTH, expand=True)

    tables = [f"Table {i}" for i in range(1, 82)]
    selectedTable = StringVar(value="Takeway")

    def selectTableHalder(tableName):
        selectedTable.set(tableName)
        messagebox.showinfo("Table Selected", f"You have selected {tableName}.")

    # Display table buttons
    for i, table in enumerate(tables):
        btn = Button(
            frameTables,
            text=table,
            width=10,
            height=2,
            bg="#4682B4",
            fg="white",
            font=("Arial", 10),
            command=lambda t=table: selectTableHalder(t),
        )
        btn.grid(row=i // 9, column=i % 9, padx=5, pady=5)

    # === TAB UTILITIES === #
    frameUtilities = Frame(tabUtilities, bg="#AFEEEE")
    frameUtilities.pack(fill=BOTH, expand=True)

    def Exit():
        if messagebox.askyesno("Exit", "Do you want to exit now?"):
            window.destroy()

    # 1. Statistics Section
    frameStats = LabelFrame(
        frameUtilities,
        text="Statistics",
        fg="white",
        bg="#4682B4",
        font=("Arial", 12, "bold"),
    )
    frameStats.place(x=10, y=20, width=280, height=200)

    Label(
        frameStats, text="Bill Quantity:", font=("Arial", 10), fg="white", bg="#4682B4"
    ).grid(row=0, column=1, pady=5, sticky=W)
    Label(
        frameStats, text="Items Quantity:", font=("Arial", 10), fg="white", bg="#4682B4"
    ).grid(row=1, column=1, pady=5, sticky=W)
    Label(
        frameStats, text="Revenue (VND):", font=("Arial", 10), fg="white", bg="#4682B4"
    ).grid(row=2, column=1, pady=5, sticky=W)

    txtNumBill = Entry(frameStats, textvariable=StringVar(), bg="#E0FFFF", width=20)
    txtNumBill.grid(row=0, column=2, padx=10)
    txtNumItems = Entry(frameStats, textvariable=StringVar(), bg="#E0FFFF", width=20)
    txtNumItems.grid(row=1, column=2, padx=10)
    txtRevenue = Entry(frameStats, textvariable=StringVar(), bg="#E0FFFF", width=20)
    txtRevenue.grid(row=2, column=2, padx=10)

    # 2. Receipt Management Section
    frameReceipt = LabelFrame(
        frameUtilities,
        text="Receipt Management",
        fg="white",
        bg="#4682B4",
        font=("Arial", 12, "bold"),
    )
    frameReceipt.place(x=320, y=20, width=550, height=500)

    txtReceipt = Text(frameReceipt, width=60, height=25, bg="#E0FFFF")
    txtReceipt.pack(pady=10)

    btnSaveReceipt = Button(
        frameReceipt,
        text="Save Receipt",
        bg="#007bff",
        fg="white",
        font=("Arial", 10, "bold"),
        command=SaveReceipt,
    )
    btnSaveReceipt.pack(side=LEFT, padx=10, pady=10)

    btnSeeReceipt = Button(
        frameReceipt,
        text="See Receipt",
        bg="#28a745",
        fg="white",
        font=("Arial", 10, "bold"),
        command=OpenReceipt,
    )
    btnSeeReceipt.pack(side=RIGHT, padx=10, pady=10)

    # 3. Utilities Section
    frameUtils = LabelFrame(
        frameUtilities,
        text="Utilities",
        fg="white",
        bg="#4682B4",
        font=("Arial", 12, "bold"),
    )
    frameUtils.place(x=10, y=250, width=280, height=120)

    btnSetting = Button(
        frameUtils,
        text="Items Settings",
        bg="#6c757d",
        fg="white",
        font=("Arial", 10, "bold"),
        command=ItemSetting,
    )
    btnSetting.pack(pady=10, padx=10)

    btnExit = Button(
        frameUtils,
        text="Exit",
        bg="#dc3545",
        fg="white",
        font=("Arial", 10, "bold"),
        command=Exit,
    )
    btnExit.pack(pady=10, padx=10)

    window.mainloop()


# MAIN
connectDataBase()
LogInWindow()
