#main_app_gui.py
import mysql.connector
from mysql.connector import Error
from tkinter import (
    LabelFrame, Tk, Frame, Label, Button, Entry, StringVar, Toplevel, Text, filedialog, messagebox, ttk
)
import datetime
from db_utils import ExecuteQuery # Import hàm tương tác DB
from db_utils import connectDataBase
from app_utils import makecenter    # Import hàm tiện ích UI
from tkinter import END # Đảm bảo đã import END cho Text/Entry widgets

class MainWindow:
    def __init__(self, master: Tk, user_id: str):
        self.master = master
        self.master.title("Order Drink Software")
        self.master.geometry("900x600")
        self.master.configure(bg="#f8f9fa")
        makecenter(self.master)

        self.user_id = user_id # Lưu UserID của người dùng đang đăng nhập
        
        # Global-like variables (now instance variables)
        self.quantity_bill = 0
        self.quantity_items = 0
        self.revenue = 0
        self.order_number = 0 # This needs to be managed from DB, not a simple global
        self.selected_table = StringVar(value="Takeaway") # Biến cho việc chọn bàn
        self.current_order_id = None # Lưu OrderID của đơn hàng đang xử lý

        self._setup_styles()
        self._setup_tabs()
        self._setup_order_tab()
        self._setup_layout_tab()
        self._setup_utilities_tab()
        self.refresh_order_and_detail_trees()
        
        # Initial data loading and binding fixes
        self.tree_order.bind("<<TreeviewSelect>>", self.tree_order_selected_index_change)
        self.tree_order.bind("<Return>", lambda event: self.btn_pay_click())
        self.tree_order_detail.bind("<Return>", lambda event: self.btn_order_click())
        self.tree_items.bind("<Return>", lambda event: self.btn_add_click())
        self.txt_find_item.bind("<Return>", lambda event: self.btn_find_click()) # Corrected binding for Entry

        self.refresh_order_and_detail_trees() # Tải dữ liệu đơn hàng và chi tiết
        self.load_items_to_tree() # Tải dữ liệu ban đầu

    # Style cho tab
    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background="skyblue",
            foreground="black",
            rowheight=21,
            fieldbackground="skyblue",
        )
        style.map("Treeview", background=[("selected", "green")])
        style.configure("TNotebook.Tab", font=("Arial", 10, "bold")) 
        
    #Setup Tabs
    def _setup_tabs(self):
        self.menutab = ttk.Notebook(self.master, style="TNotebook")
        self.menutab.pack(fill="both", expand=True)

        self.tab_order = Frame(self.menutab, bg="#AFEEEE")
        self.tab_layout = Frame(self.menutab, bg="#AFEEEE")
        self.tab_utilities = Frame(self.menutab, bg="#AFEEEE")

        self.menutab.add(self.tab_layout, text="Layout")
        self.menutab.add(self.tab_order, text="Order")
        self.menutab.add(self.tab_utilities, text="Utilities")

    def _setup_order_tab(self):
        # Tree_Item Zone (Menu)
        Label(self.tab_order, text="Menu", font=("Arial", 14, "bold"), bg="#AFEEEE").place(
            x=20, y=40
        )
        self.tree_items = ttk.Treeview(
            self.tab_order,
            columns=("ID", "Name", "Unit", "Cost", "Category"),
            show="headings",
            height=10,
        )
        self.tree_items.place(x=20, y=70, width=500, height=380)
        for column, width in [("ID", 60), ("Name", 120), ("Unit", 60), ("Cost", 80), ("Category", 100)]:
            self.tree_items.heading(column, text=column)
            self.tree_items.column(column, width=width, anchor="center")

        # Order Details Zone
        Label(
            self.tab_order, text="Order Details", font=("Arial", 14, "bold"), bg="#AFEEEE"
        ).place(x=550, y=10)
        self.tree_order_detail = ttk.Treeview(
            self.tab_order,
            columns=("OrderDetailID", "ItemID", "Quantity", "TotalPrice"), # Added OrderDetailID for easier manipulation
            show="headings",
            height=7,
        )
        self.tree_order_detail.place(x=550, y=40, width=320, height=200)
        for column, width in [("OrderDetailID", 0), ("ItemID", 80), ("Quantity", 80), ("TotalPrice", 80)]:
            self.tree_order_detail.heading(column, text=column)
            self.tree_order_detail.column(column, width=width, anchor="center")
            if column == "OrderDetailID":
                self.tree_order_detail.column(column, width=0, stretch=False) # Hide OrderDetailID

        # Order Zone
        Label(self.tab_order, text="Order", font=("Arial", 14, "bold"), bg="#AFEEEE").place(
            x=550, y=280
        )
        self.tree_order = ttk.Treeview(
            self.tab_order,
            columns=("OrderID", "UserID", "Table", "OrderDate", "TotalPrice", "Status"),
            show="headings",
            height=7,
        )
        self.tree_order.place(x=550, y=310, width=320, height=200)
        for column, width in [("OrderID", 64), ("UserID", 64), ("Table", 64), ("OrderDate", 64), ("TotalPrice", 64), ("Status", 64)]:
            self.tree_order.heading(column, text=column)
            self.tree_order.column(column, width=width, anchor="center")
            
        # Display Total, Bill, Items Entry
        Label(self.tab_order, text="Enter Items:", font=("Arial", 12, "bold"), bg="#AFEEEE").place(x=20, y=10)
        Label(self.tab_order, text="Total:", font=("Arial", 12, "bold"), bg="#AFEEEE").place(x=550, y=250)
        Label(self.tab_order, text="Bill:", font=("Arial", 12, "bold"), bg="#AFEEEE").place(x=550, y=520)
        Label(self.tab_order, text="VND", font=("Arial", 12, "bold"), bg="#AFEEEE").place(x=750, y=250)
        Label(self.tab_order, text="VND", font=("Arial", 12, "bold"), bg="#AFEEEE").place(x=750, y=520)
        
        self.txt_find_item = Entry(self.tab_order, textvariable=StringVar(), bg="white", font=("Arial", 12))
        self.txt_find_item.place(x=130, y=10, width=280)
        self.txt_total = Entry(self.tab_order, textvariable=StringVar(), bg="white", font=("Arial", 12), state='readonly')
        self.txt_total.place(x=600, y=250, width=150)
        self.txt_bill = Entry(self.tab_order, textvariable=StringVar(), bg="white", font=("Arial", 12), state='readonly')
        self.txt_bill.place(x=600, y=520, width=150)

        # Buttons
        btnAdd = Button(self.tab_order, text="Add", command=self.btn_add_click, fg="#F0F8FF", bg="#4169E1", font=("Arial", 10, "bold"))
        btnAdd.place(x=20, y=460, width=120, height=90)
        btnFind = Button(self.tab_order, text="Find", command=self.btn_find_click, fg="#F0F8FF", bg="#104E8B", font=("Arial", 10, "bold"))
        btnFind.place(x=430, y=10, width=90, height=40)
        btnOrder = Button(self.tab_order, text="Order", command=self.btn_order_click, bg="#F0F8FF", fg="#191970", font=("Arial", 10, "bold"))
        btnOrder.place(x=800, y=250, width=70)
        btnDelete = Button(self.tab_order, text="Delete", command=self.btn_delete_click, fg="#F0F8FF", bg="#00688B", font=("Arial", 10, "bold"))
        btnDelete.place(x=220, y=510, width=90, height=40)
        btnCancel = Button(self.tab_order, text="Cancel", command=self.btn_cancel_click, fg="#F0F8FF", bg="#4A708B", font=("Arial", 10, "bold"))
        btnCancel.place(x=320, y=510, width=90, height=40)
        btnPay = Button(self.tab_order, text="Pay", command=self.btn_pay_click, bg="#104E8B", fg="#F0F8FF", font=("Arial", 10, "bold"))
        btnPay.place(x=800, y=520, width=70)
        btnRefresh = Button(self.tab_order, text="Refresh Items", command=self.refresh_items_tree, bg="#27408B", fg="#F0F8FF", font=("Arial", 10, "bold"))
        btnRefresh.place(x=420, y=510, width=100, height=40)

        # Bindings are moved to __init__ for single definition
        # self.tree_order.bind("<<TreeviewSelect>>", self.tree_order_selected_index_change)
        # self.tree_order.bind("<Return>", lambda event: self.btn_pay_click())
        # self.tree_order_detail.bind("<Return>", lambda event: self.btn_order_click())
        # self.tree_items.bind("<Return>", lambda event: self.btn_add_click())
        # self.txt_find_item.bind("<Return>", lambda event: self.btn_find_click()) # Corrected here too

    def _setup_layout_tab(self):
        Label(self.tab_layout, text="Select Table Layout", font=("Arial", 14, "bold"), bg="#AFEEEE").pack(pady=10)
        frameTables = Frame(self.tab_layout, bg="#AFEEEE")
        frameTables.pack(fill="both", expand=True)

        tables = [f"Table {i}" for i in range(1, 82)]
        
        for i, table in enumerate(tables):
            btn = Button(
                frameTables,
                text=table,
                width=10,
                height=2,
                bg="#4682B4",
                fg="white",
                font=("Arial", 10),
                command=lambda t=table: self.select_table_handler(t),
            )
            btn.grid(row=i // 9, column=i % 9, padx=5, pady=5)
    def select_table_handler(self, table_name: str):
        self.selected_table.set(table_name)
        messagebox.showinfo("Selected table", f"You have selected a table: {table_name}")

        # Kiểm tra xem có đơn hàng "Pending" nào cho bàn này không
        query_pending_order = """
            SELECT OrderID FROM Orders 
            WHERE UserID = %s AND Tables = %s AND Status = 'Pending' 
            ORDER BY OrderDate DESC LIMIT 1
        """
        result = ExecuteQuery(query_pending_order, (self.user_id, table_name))

        if result:
            self.current_order_id = result[0][0]
            messagebox.showinfo("Current Orders", f"Loaded pending orders for table {table_name}: OrderID {self.current_order_id}")
        else:
            self.current_order_id = None
            messagebox.showinfo("Current Orders", f"There are no pending orders for table {table_name}. A new order will be created when a dish is added.")
        
        # Cập nhật hiển thị đơn hàng và chi tiết
        self.refresh_order_and_detail_trees()
        self.update_total_bill()
    def _setup_utilities_tab(self):
        self.frame_utilities = Frame(self.tab_utilities, bg="#AFEEEE")
        self.frame_utilities.pack(fill="both", expand=True)

        # 1. Statistics Section
        frameStats = LabelFrame(
            self.frame_utilities, text="Statistics", fg="white", bg="#4682B4", font=("Arial", 12, "bold")
        )
        frameStats.place(x=10, y=20, width=280, height=200)

        Label(frameStats, text="Bill Quantity:", font=("Arial", 10), fg="white", bg="#4682B4").grid(row=0, column=1, pady=5, sticky="w")
        Label(frameStats, text="Items Quantity:", font=("Arial", 10), fg="white", bg="#4682B4").grid(row=1, column=1, pady=5, sticky="w")
        Label(frameStats, text="Revenue (VND):", font=("Arial", 10), fg="white", bg="#4682B4").grid(row=2, column=1, pady=5, sticky="w")

        self.txt_num_bill = Entry(frameStats, textvariable=StringVar(), bg="#E0FFFF", width=20, state='readonly')
        self.txt_num_bill.grid(row=0, column=2, padx=10)
        self.txt_num_items = Entry(frameStats, textvariable=StringVar(), bg="#E0FFFF", width=20, state='readonly')
        self.txt_num_items.grid(row=1, column=2, padx=10)
        self.txt_revenue = Entry(frameStats, textvariable=StringVar(), bg="#E0FFFF", width=20, state='readonly')
        self.txt_revenue.grid(row=2, column=2, padx=10)
        self.update_statistics() # Cập nhật thống kê khi khởi tạo

        # 2. Receipt Management Section
        frameReceipt = LabelFrame(
            self.frame_utilities, text="Receipt Management", fg="white", bg="#4682B4", font=("Arial", 12, "bold")
        )
        frameReceipt.place(x=320, y=20, width=550, height=500)

        self.txt_receipt = Text(frameReceipt, width=60, height=25, bg="#E0FFFF")
        self.txt_receipt.pack(pady=10)

        btnSaveReceipt = Button(frameReceipt, text="Save Receipt", bg="#007bff", fg="white", font=("Arial", 10, "bold"), command=self.btn_save_receipt)
        btnSaveReceipt.pack(side="left", padx=10, pady=10)

        btnSeeReceipt = Button(frameReceipt, text="See Receipt", bg="#28a745", fg="white", font=("Arial", 10, "bold"), command=self.btn_open_receipt)
        btnSeeReceipt.pack(side="right", padx=10, pady=10)

        # 3. Utilities Section
        frameUtils = LabelFrame(
            self.frame_utilities, text="Utilities", fg="white", bg="#4682B4", font=("Arial", 12, "bold")
        )
        frameUtils.place(x=10, y=250, width=280, height=120)

        btnSetting = Button(frameUtils, text="Items Settings", bg="#6c757d", fg="white", font=("Arial", 10, "bold"), command=self.btn_items_setting)
        btnSetting.pack(pady=10, padx=10)

        btnExit = Button(frameUtils, text="Exit", bg="#dc3545", fg="white", font=("Arial", 10, "bold"), command=self.exit_app)
        btnExit.pack(pady=10, padx=10)

    # --- Utility Methods ---
    def refresh_items_tree(self):
        """Làm mới Treeview hiển thị danh sách Item."""
        for item in self.tree_items.get_children():
            self.tree_items.delete(item)
        self.load_items_to_tree()

    def load_items_to_tree(self):
        """Tải dữ liệu Items từ DB vào Treeview."""
        items = ExecuteQuery("SELECT ItemID, Name, Unit, Cost, Category FROM Items")
        if items:
            for item in items:
                self.tree_items.insert("", "end", values=item)

    def refresh_order_and_detail_trees(self):
        # Hàm này cần được bạn tự định nghĩa để làm mới treeview đơn hàng và chi tiết
        print("Refreshing order and detail trees...")
        # Xóa dữ liệu hiện có
        for item in self.tree_order.get_children():
            self.tree_order.delete(item)
        for item in self.tree_order_detail.get_children():
            self.tree_order_detail.delete(item)
        
        # Tải lại dữ liệu orders
        orders = ExecuteQuery("SELECT OrderID, UserID, Tables, OrderDate, TotalAmount, Status FROM Orders WHERE Status = 'Pending' OR Status = 'Completed'")
        if orders:
            for order in orders:
                self.tree_order.insert("", "end", values=order)

        # Tải lại dữ liệu order details cho current_order_id nếu có
        if self.current_order_id:
            details = ExecuteQuery("SELECT OrderDetailID, OrderID, ItemID, Quantity, TotalPrice FROM OrderDetails WHERE OrderID = %s", (self.current_order_id,))
            if details:
                for detail in details:
                    self.tree_order_detail.insert("", "end", values=detail)

    def update_total_bill(self):
        if not self.current_order_id:
            self.txt_total.config(state='normal')
            self.txt_total.delete(0, END)
            self.txt_total.insert(0, "0.00")
            self.txt_total.config(state='readonly')
            return

        total_amount = 0.0
        query_total = "SELECT SUM(TotalPrice) FROM OrderDetails WHERE OrderID = %s"
        result = ExecuteQuery(query_total, (self.current_order_id,))
        if result and result[0][0] is not None:
            total_amount = float(result[0][0])

        update_order_total_query = "UPDATE Orders SET TotalAmount = %s WHERE OrderID = %s"
        ExecuteQuery(update_order_total_query, (total_amount, self.current_order_id))

        self.txt_total.config(state='normal')
        self.txt_total.delete(0, END)
        self.txt_total.insert(0, f"{total_amount:.2f}")
        self.txt_total.config(state='readonly')


    def tree_order_selected_index_change(self, event):
        # Get selected item in self.tree_ordered
        selectedItem = self.tree_order.selection()
        if not selectedItem:
            self.txt_bill.config(state='normal')
            self.txt_bill.delete(0, END)
            self.txt_bill.config(state='readonly')
            self.current_order_id = None # No order selected
            self.refresh_order_and_detail_trees() # Clear order details
            return
        
        # Get value of the selected item
        item = self.tree_order.item(selectedItem, "values")
        self.current_order_id = item[0] # Update current_order_id based on selection
        total = item[4] # TotalPrice is at index 4 in tree_order (OrderID, UserID, Table, OrderDate, TotalPrice, Status)

        self.txt_bill.config(state='normal')
        self.txt_bill.delete(0, END)
        self.txt_bill.insert(0, total)
        self.txt_bill.config(state='readonly')

        #elf.refresh_order_and_detail_trees() # Reload order details for the selected order

    def update_statistics(self):
        """Cập nhật các số liệu thống kê."""
        total_bills_result = ExecuteQuery("SELECT COUNT(OrderID) FROM Orders WHERE Status = 'Paid'")
        self.quantity_bill = total_bills_result[0][0] if total_bills_result and total_bills_result[0][0] is not None else 0
        
        total_revenue_result = ExecuteQuery("SELECT SUM(TotalAmount) FROM Orders WHERE Status = 'Paid'")
        self.revenue = total_revenue_result[0][0] if total_revenue_result and total_revenue_result[0][0] is not None else 0.0

        # Sum of quantities of all items in completed orders
        total_items_result = ExecuteQuery("SELECT SUM(OD.Quantity) FROM OrderDetails OD JOIN Orders O ON OD.OrderID = O.OrderID WHERE O.Status = 'Paid'")
        self.quantity_items = total_items_result[0][0] if total_items_result and total_items_result[0][0] is not None else 0

        self.txt_num_bill.config(state='normal')
        self.txt_num_bill.delete(0, 'end')
        self.txt_num_bill.insert(0, str(self.quantity_bill))
        self.txt_num_bill.config(state='readonly')

        self.txt_num_items.config(state='normal')
        self.txt_num_items.delete(0, 'end')
        self.txt_num_items.insert(0, str(self.quantity_items))
        self.txt_num_items.config(state='readonly')

        self.txt_revenue.config(state='normal')
        self.txt_revenue.delete(0, 'end')
        self.txt_revenue.insert(0, f"{self.revenue:,.0f}")
        self.txt_revenue.config(state='readonly')

    # --- Event Handlers (previously Btn*_Click functions)---
    def btn_add_click(self):
        selectedItems = self.tree_items.selection() # Sử dụng self.ui['tree_items']
        if not selectedItems:
            messagebox.showinfo("Message", "You have not selected any item yet")
            return

        # Check if there is an existing pending order for the current user
        if not self.current_order_id:
            # Create a new order if no pending order exists
            orderDate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            initial_total_price = 0.0
            status = "Pending"
            table = self.selected_table.get() # Use selected table

            query_create_order = """
                INSERT INTO Orders (UserID, Tables, OrderDate, TotalAmount, Status)
                VALUES (%s, %s, %s, %s, %s)
            """
            # Không cần many=True cho một bản ghi
            ExecuteQuery(query_create_order, (self.user_id, table, orderDate, initial_total_price, status))

            # Get the newly created OrderID
            result = ExecuteQuery("SELECT OrderID FROM Orders WHERE UserID = %s AND Status = %s ORDER BY OrderDate DESC LIMIT 1", (self.user_id, "Pending"))
            if result:
                self.current_order_id = result[0][0]
            else:
                messagebox.showerror("Error", "Failed to retrieve new order ID.")
                return

        # Add selected items to the current order
        items_to_add_to_db = []
        for itemID_treeview in selectedItems:
            item_data = self.tree_items.item(itemID_treeview, "values") # Sử dụng self.ui['tree_items']
            if len(item_data) < 5: # Đảm bảo đủ các trường: ItemID, Name, Unit, Cost, Category
                continue

            item_id, name, unit, cost_str, category = item_data
            try:
                cost = float(cost_str)
            except ValueError:
                messagebox.showerror("Error", f"Invalid cost value for item {name}: {cost_str}")
                continue

            quantity = 1
            total_item_cost = cost * quantity

            # Check if item already exists in the current order details
            existing_order_detail = ExecuteQuery(
                "SELECT OrderDetailID, Quantity, TotalPrice FROM OrderDetails WHERE OrderID = %s AND ItemID = %s",
                (self.current_order_id, item_id)
            )

            if existing_order_detail:
                # Update existing order detail
                order_detail_id, current_quantity, current_total_price = existing_order_detail[0]
                new_quantity = current_quantity + quantity
                new_total_price = new_quantity * cost # Tính toán lại tổng giá dựa trên số lượng mới và giá gốc
                
                ExecuteQuery(
                    "UPDATE OrderDetails SET Quantity = %s, TotalPrice = %s WHERE OrderDetailID = %s",
                    (new_quantity, new_total_price, order_detail_id)
                )
            else:
                # Insert new order detail
                items_to_add_to_db.append((self.current_order_id, item_id, quantity, total_item_cost))
        
        if items_to_add_to_db:
            # Gọi ExecuteQuery với many=True để chèn nhiều bản ghi cùng lúc
            ExecuteQuery(
                "INSERT INTO OrderDetails (OrderID, ItemID, Quantity, TotalPrice) VALUES (%s, %s, %s, %s)",
                items_to_add_to_db, many=True
            )
        
        #messagebox.showinfo("Success", "Items added to order successfully!")
        self.refresh_order_and_detail_trees()
        self.update_total_bill()

    def btn_order_click(self):
        if not self.current_order_id:
            messagebox.showinfo("Message", "No active order to place.")
            return

        result = messagebox.askyesno(
            "Confirmation", "Are you sure you want to place this order?"
        )
        if not result:
            return

        # Update order status to 'Ordered' or a similar intermediate status
        success = ExecuteQuery("UPDATE Orders SET Status = %s WHERE OrderID = %s", ("Completed", self.current_order_id))
        
        if success is not None: # ExecuteQuery returns None on error
            messagebox.showinfo("Success", f"Order {self.current_order_id} has been placed.")
            self.current_order_id = None # Clear current order after placing
            self.refresh_order_and_detail_trees()
            self.update_statistics()
        else:
            messagebox.showerror("Error", "Failed to place order.")

    def btn_delete_click(self):
        selected_details = self.tree_order_detail.selection()
        if not selected_details:
            messagebox.showinfo("Message", "Please select items from Order Details to delete.")
            return

        if not self.current_order_id:
            messagebox.showerror("Error", "No active order selected.")
            return

        confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete the selected items from this order?")
        if not confirm:
            return

        try:
            for item_id_treeview in selected_details:
                detail_values = self.tree_order_detail.item(item_id_treeview, "values")
                order_detail_id = detail_values[0] # OrderDetailID is the first column

                ExecuteQuery("DELETE FROM OrderDetails WHERE OrderDetailID = %s", (order_detail_id,))
                self.tree_order_detail.delete(item_id_treeview)
            
            # After deleting items, check if the order has any remaining details
            remaining_details = ExecuteQuery("SELECT COUNT(*) FROM OrderDetails WHERE OrderID = %s", (self.current_order_id,))
            if remaining_details and remaining_details[0][0] == 0:
                # If no details left, delete the order itself
                ExecuteQuery("DELETE FROM Orders WHERE OrderID = %s", (self.current_order_id,))
                messagebox.showinfo("Info", "Order is empty, so it has been deleted.")
                self.current_order_id = None
            
            messagebox.showinfo("Success", "Selected items deleted successfully.")
            self.refresh_order_and_detail_trees()
            self.update_total_bill()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during deletion: {e}")

    def btn_cancel_click(self):
        if not self.current_order_id:
            messagebox.showinfo("Message", "No active order to cancel.")
            return

        result = messagebox.askyesno(
            "Confirmation", "Are you sure you want to cancel the current order and clear all its items?"
        )
        if not result:
            return

        try:
            # Delete all order details first
            ExecuteQuery("DELETE FROM OrderDetails WHERE OrderID = %s", (self.current_order_id,))
            
            # Then delete the order itself
            ExecuteQuery("DELETE FROM Orders WHERE OrderID = %s", (self.current_order_id,))

            messagebox.showinfo("Success", f"Order {self.current_order_id} has been cancelled and all its items cleared.")
            self.current_order_id = None # Clear current order
            self.refresh_order_and_detail_trees() # Refresh both trees
            self.update_total_bill() # Update total display
            self.update_statistics() # Update statistics

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while cancelling the order: {e}")

    def btn_pay_click(self):
        selected_order_items = self.tree_order.selection()
        if not selected_order_items:
            messagebox.showinfo("Message", "Please select an order to pay.")
            return
        
        selected_order_data = self.tree_order.item(selected_order_items[0], "values")
        order_id_to_pay = selected_order_data[0]
        current_status = selected_order_data[5] # Status is at index 5

        if current_status == "Paid":
            messagebox.showinfo("Info", "This order has already been paid.")
            return

        confirm = messagebox.askyesno("Confirm Payment", f"Confirm payment for Order ID: {order_id_to_pay}?")
        if not confirm:
            return
        
        # Update order status to 'Completed'
        success = ExecuteQuery("UPDATE Orders SET Status = %s WHERE OrderID = %s", ("Paid", order_id_to_pay))
        
        if success is not None:
            messagebox.showinfo("Success", f"Order {order_id_to_pay} marked as paid.")
            self.refresh_order_and_detail_trees() # Refresh to reflect status change
            self.update_statistics() # Update statistics as a bill is completed
            if self.current_order_id == order_id_to_pay:
                self.current_order_id = None # Clear if the paid order was the current one
                self.tree_order_detail.delete(*self.tree_order_detail.get_children()) # Clear details
                self.update_total_bill() # Reset total
        else:
            messagebox.showerror("Error", "Failed to update order status to paid.")


    def btn_find_click(self):
        search_term = self.txt_find_item.get().strip().lower()
        if not search_term:
            self.refresh_items_tree() # If search box is empty, show all items
            return

        matched_items_treeview_ids = []
        for itemID_treeview in self.tree_items.get_children():
            item_data = self.tree_items.item(itemID_treeview, "values")
            # Assume item_data structure: (ItemID, Name, Unit, Cost, Category)
            if len(item_data) < 5:
                continue 
            itemIDValue, name, unit, cost, category = item_data
            
            if (
                search_term in str(itemIDValue).lower()
                or search_term in str(name).lower()
                or search_term in str(unit).lower()
                or search_term in str(cost).lower()
                or search_term in str(category).lower()
            ):
                matched_items_treeview_ids.append(itemID_treeview)

        if matched_items_treeview_ids:
            # Deselect previously selected items
            self.tree_items.selection_remove(self.tree_items.selection())
            # Select and focus on found items
            for itemID_treeview in matched_items_treeview_ids:
                self.tree_items.selection_add(itemID_treeview)
                self.tree_items.focus(itemID_treeview)
            
            messagebox.showinfo(
                "Message", f"Suitable products {len(matched_items_treeview_ids)} found!"
            )
            # self.txt_find_item.delete(0, END) # Clear search box content after search
        else:
            messagebox.showinfo(
                "Notification", "No matching items found."
            )
    def TreeOrderSelectedIndexChange(self, event):
        # Get selected item in MainWindow.tree_ordered
        selectedItem = self.tree_order.selection()
        if not selectedItem:
            self.txt_bill.delete(0, END)
            return
        # Get value of the selected item
        item = self.tree_order.item(selectedItem, "values")
        if len(item) > 3: # Đảm bảo item có đủ phần tử
            total = item[3]
        else:
            total = "N/A" # Hoặc xử lý lỗi phù hợp

        self.txt_bill.delete(0, END)
        self.txt_bill.insert(0, total)

    def btn_save_receipt(self):
        # Sử dụng self.ui['tree_Temp'] nếu tree_Temp là một widget của UI
        items = self.tree_Temp.get_children()
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
                # Sử dụng self.ui['tree_Temp']
                item = self.tree_Temp.item(itemID, "value")
                # Đảm bảo item có đủ phần tử trước khi truy cập
                if len(item) >= 5:
                    file.write(
                        f"UserID:{item[0]}\nTable: {item[1]}\nDate: {item[2]}\nTotalPrice: {item[3]}\nStatus: {item[4]}\n"
                    )
                else:
                    file.write(f"Invalid item data: {item}\n") # Xử lý trường hợp dữ liệu không hợp lệ
            file.write("+" + "-" * 24 + "+" + "\n")
            # Sử dụng self.ui['txtRevenue'] nếu txtRevenue là một widget của UI
            if 'txtRevenue' in self and hasattr(self.txtRevenue, 'get'):
                file.write(f"Total: {self.txtRevenue.get()} VND\n")
            else:
                file.write(f"Total: N/A VND\n") # Hoặc xử lý lỗi phù hợp
            file.close()
        messagebox.showinfo("Save Receipt", f"Receipt saved to {filePath}")

    def btn_open_receipt(self):
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
                    # Sử dụng self.ui['txtReceipt'] nếu txtReceipt là một widget của UI
                    self.txtReceipt.delete("1.0", "end")  # Delete Now Content
                    self.txtReceipt.insert("1.0", fileContent)  # Add new content into widget
            except Exception as e:
                print(f"Error opening file: {e}")
                messagebox.showerror("Error", f"Could not open file: {e}")


    def SaveBill(self):
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
            # Sử dụng self.ui['txtReceipt'] nếu txtReceipt là một widget của UI
            file.write(self.txtReceipt.get("1.0", "end-1c"))
            file.close()
        messagebox.showinfo("Save Bill", f"Bill saved to {filePath}")

    # Create Setting Items
    def btn_items_setting(self):
        # Sử dụng self.ui['tree_items']
        items = self.tree_items.get_children()
        addItems = Toplevel(self.master) # Truyền self.master để Toplevel biết parent của nó
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
        # Dùng StringVar để dễ dàng lấy/set giá trị và bind với Entry
        item_id_var = StringVar()
        item_name_var = StringVar()
        item_unit_var = StringVar()
        item_cost_var = StringVar()
        item_category_var = StringVar()

        txtItemID = Entry(addItems, textvariable=item_id_var, bg="white", width=20)
        txtItemID.place(x=100, y=40)
        txtItemName = Entry(addItems, textvariable=item_name_var, bg="white", width=20)
        txtItemName.place(x=100, y=70)
        txtItemUnit = Entry(addItems, textvariable=item_unit_var, bg="white", width=20)
        txtItemUnit.place(x=100, y=100)
        txtItemCost = Entry(addItems, textvariable=item_cost_var, bg="white", width=20)
        txtItemCost.place(x=100, y=130)
        txtItemCategory = Entry(addItems, textvariable=item_category_var, bg="white", width=20)
        txtItemCategory.place(x=100, y=160)

        # Add Items
        def BtnAddItm_Click():
            itemID = item_id_var.get()
            itemName = item_name_var.get()
            itemUnit = item_unit_var.get()
            itemCost = item_cost_var.get()
            itemCategory = item_category_var.get()

            if itemID and itemName and itemCost:
                try:
                    # Sử dụng ExecuteQuery để tương tác với DB
                    query = "INSERT INTO Items (ItemID, Name, Unit, Cost, Category) VALUES (%s, %s, %s, %s, %s)"
                    params = (itemID, itemName, itemUnit, itemCost, itemCategory)
                    if ExecuteQuery(query, params):
                        # Sử dụng self.ui['tree_Items']
                        self.tree_items.insert(
                            "",
                            "end",
                            values=(itemID, itemName, itemUnit, itemCost, itemCategory),
                        )
                        item_id_var.set("")
                        item_name_var.set("")
                        item_unit_var.set("")
                        item_cost_var.set("")
                        item_category_var.set("")
                        messagebox.showinfo("Success", "Item added successfully!")
                    else:
                        messagebox.showerror("Error", "Failed to add item to database.")
                except Exception as err: # Bắt lỗi chung nếu có
                    messagebox.showerror("Error", f"An unexpected error occurred: {err}")
            else:
                messagebox.showinfo(
                    "Input Error", "Item ID, Item Name, and Item Cost cannot be empty!"
                )

        # Delete Items
        def BtnDeleteItm_Click():
            # Sử dụng self.ui['tree_Items']
            selected_item = self.tree_items.selection()
            if selected_item:
                itemID = self.tree_items.item(selected_item)["values"][0]
                try:
                    # Sử dụng ExecuteQuery
                    query = "DELETE FROM Items WHERE ItemID = %s"
                    params = (itemID,)
                    if ExecuteQuery(query, params):
                        self.tree_items.delete(selected_item)
                        messagebox.showinfo("Success", "Item deleted successfully!")
                    else:
                        messagebox.showerror("Error", "Failed to delete item from database.")
                except Exception as err:
                    messagebox.showerror("Error", f"An unexpected error occurred: {err}")
            else:
                messagebox.showinfo("Selection Error", "No item selected!")

        # Edit Items
        def BtnEditItm_Click():
            # Sử dụng self.ui['tree_Items']
            selected_item = self.tree_items.selection()
            if selected_item:
                # Lấy ItemID từ mục đang chọn để xác định bản ghi cần cập nhật
                original_itemID = self.tree_items.item(selected_item)["values"][0]

                itemID = item_id_var.get() # Lấy ItemID mới từ trường nhập liệu, có thể dùng để thay đổi ItemID
                itemName = item_name_var.get()
                itemUnit = item_unit_var.get()
                itemCost = item_cost_var.get()
                itemCategory = item_category_var.get()

                # Kiểm tra các trường bắt buộc
                if not itemID or not itemName or not itemCost:
                    messagebox.showinfo("Input Error", "Item ID, Item Name, and Item Cost cannot be empty!")
                    return

                try:
                    # Sử dụng ExecuteQuery
                    # Cập nhật tất cả các trường, sử dụng original_itemID để tìm bản ghi
                    query = """
                        UPDATE Items 
                        SET ItemID = %s, Name = %s, Unit = %s, Cost = %s, Category = %s
                        WHERE ItemID = %s
                    """
                    params = (itemID, itemName, itemUnit, itemCost, itemCategory, original_itemID)
                    
                    if ExecuteQuery(query, params):
                        # Cập nhật lại giao diện treeview
                        self.tree_items.item(
                            selected_item,
                            values=(itemID, itemName, itemUnit, itemCost, itemCategory),
                        )
                        # Xóa nội dung trong các trường nhập liệu
                        item_id_var.set("")
                        item_name_var.set("")
                        item_unit_var.set("")
                        item_cost_var.set("")
                        item_category_var.set("")
                        messagebox.showinfo("Success", "Item updated successfully!")
                    else:
                        messagebox.showerror("Error", "Failed to update item in database.")
                except Exception as err:
                    messagebox.showerror("Error", f"An unexpected error occurred: {err}")
            else:
                messagebox.showinfo("Selection Error", "No item selected for editing!")
        
        # Hàm để điền dữ liệu vào các trường khi chọn một mục trên tree_items
        def on_tree_items_select(event):
            selected_item = self.tree_items.selection()
            if selected_item:
                values = self.tree_items.item(selected_item, "values")
                if len(values) >= 5: # Đảm bảo có đủ dữ liệu
                    item_id_var.set(values[0])
                    item_name_var.set(values[1])
                    item_unit_var.set(values[2])
                    item_cost_var.set(values[3])
                    item_category_var.set(values[4])
                else:
                    messagebox.showwarning("Dữ liệu không hợp lệ", "Mục được chọn không có đủ dữ liệu.")
            else:
                # Xóa các trường nếu không có mục nào được chọn
                item_id_var.set("")
                item_name_var.set("")
                item_unit_var.set("")
                item_cost_var.set("")
                item_category_var.set("")

        # Liên kết sự kiện chọn trên tree_items với hàm on_tree_items_select
        self.tree_items.bind('<<TreeviewSelect>>', on_tree_items_select)

        # Create Button
        btnAddItm = Button(
            addItems, text="Add Item", bg="#4876FF", fg="#191970", command=BtnAddItm_Click
        )
        btnAddItm.place(x=10, y=230)
        btnExitAddItm = Button(
            addItems, text="Exit", bg="#6495ED", fg="#191970", command=BtnExitAddItm_Click
        )
        btnExitAddItm.place(x=200, y=270)
        btnEditItm = Button(
            addItems,
            text="Edit Item",
            bg="#1E90FF",
            fg="#191970",
            command=BtnEditItm_Click,
        )
        btnEditItm.place(x=170, y=230)
        btnDeleteItm = Button(
            addItems,
            text="Delete Item",
            bg="#5CACEE",
            fg="#191970",
            command=BtnDeleteItm_Click,
        )
        btnDeleteItm.place(x=80, y=230)

        addItems.mainloop()


    #============================================================
    def exit_app(self):
        """Thoát ứng dụng."""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.master.destroy()
