# Pay&Claim-Sales-App-Python-Tkinter

## Project Description

This repository contains a desktop application built with Python's Tkinter library, designed to manage sales and order processes for small businesses or retail environments. It provides a user-friendly graphical interface for staff to handle item orders, track sales, and manage receipts, all while integrating with a MySQL database for robust data storage and retrieval. The application includes a comprehensive authentication system to manage user access and roles.

## Features

* **User Authentication**: Secure login, new user registration, and password change functionalities with `bcrypt` for password hashing.
* **Real-time Item Management**: Display and search for available items (e.g., drinks, food) from the database.
* **Order Creation**: Easily add selected items to a new or existing pending order.
* **Dynamic Order Details**: View and update items within an active order, including quantity adjustments and real-time total calculation.
* **Order Management**: Process, delete, or cancel orders.
* **Payment Processing**: (Inferred from code context) Functionality to finalize orders and generate bills.
* **Receipt Generation & Viewing**: (Inferred from code context) Ability to save and view transaction receipts.
* **Database Integration**: Seamless connection and interaction with a MySQL database for all application data (users, items, orders, order details).
* **User Interface**: Intuitive and responsive UI built with Tkinter, ensuring a smooth user experience.
* **Role-Based Access**: Supports different user roles (e.g., Admin, Employee) to manage permissions.

## Technologies Used

* **Python 3.x**: The core programming language.
* **Tkinter**: Python's standard GUI toolkit for creating the desktop interface.
* **MySQL**: Relational database management system for storing application data.
* **`mysql-connector-python`**: Python driver for connecting to MySQL databases.
* **`bcrypt`**: Library for securely hashing and verifying passwords.
* **`datetime`**: For handling date and time stamps for orders and transactions.

## Setup Instructions

To get this application up and running on your local machine, follow these steps:

### 1. Database Setup

1.  **Install MySQL**: Ensure you have MySQL installed and running on your system (e.g., via XAMPP, WAMP, MAMP, or a standalone MySQL server).
2.  **Create Database**: Create a new database named `PayAndClaimSales`.
    ```sql
    CREATE DATABASE PayAndClaimSales;
    USE PayAndClaimSales;
    ```
3.  **Create Tables**: Execute the following SQL commands to create the necessary tables:

    ```sql
    CREATE TABLE Users (
        UserID VARCHAR(50) PRIMARY KEY,
        UserName VARCHAR(100) UNIQUE NOT NULL,
        Password VARCHAR(255) NOT NULL,
        Role VARCHAR(50) NOT NULL
    );

    CREATE TABLE Items (
        ItemID VARCHAR(50) PRIMARY KEY,
        Name VARCHAR(255) NOT NULL,
        Unit VARCHAR(50),
        Cost DECIMAL(10, 2) NOT NULL,
        Category VARCHAR(100)
    );

    CREATE TABLE Orders (
        OrderID INT AUTO_INCREMENT PRIMARY KEY,
        UserID VARCHAR(50),
        Tables VARCHAR(50),
        OrderDate DATETIME,
        TotalAmount DECIMAL(10, 2),
        Status VARCHAR(50), -- e.g., 'Pending', 'Completed', 'Cancelled'
        FOREIGN KEY (UserID) REFERENCES Users(UserID)
    );

    CREATE TABLE OrderDetails (
        OrderDetailID INT AUTO_INCREMENT PRIMARY KEY,
        OrderID INT,
        ItemID VARCHAR(50),
        Quantity INT NOT NULL,
        TotalPrice DECIMAL(10, 2) NOT NULL,
        FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
        FOREIGN KEY (ItemID) REFERENCES Items(ItemID)
    );
    ```
4.  **Database Connection**: Ensure your MySQL server is accessible from `localhost` with the default `root` user and an empty password (as configured in `db_utils.py`). If your credentials differ, update the `connectDataBase` function accordingly.

### 2. Python Environment Setup

1.  **Clone the repository**:
    ```bash
    git clone [https://github.com/your-username/Pay-Claim-Sales-App-Python-Tkinter.git](https://github.com/your-username/Pay&Claim-Sales-App-Python-Tkinter.git)
    cd Pay-Claim-Sales-App-Python-Tkinter
    ```
2.  **Install Dependencies**: Install the required Python libraries using pip:
    ```bash
    pip install mysql-connector-python bcrypt
    ```
3.  **Organize Files**: Ensure your project files are organized as follows (based on previous discussions):
    * `main_app.py` (main application entry point)
    * `auth_manager.py` (for `LogInWindow`, `SignupWindow`, `ChangePassword`)
    * `db_utils.py` (for `connectDataBase`, `ExecuteQuery`)
    * `app_utils.py` (for `makecenter` and other utilities)
    * `order_management_logic.py` (for `OrderManagementLogic` class and order-related functions)
    * (Any other UI/logic files you create)

### 3. Running the Application

Execute the `main_app.py` file to start the application:

```bash
python main_app.py
```
### 4.Usage
1.  Login Screen: The application will first present a login window. You can log in with existing credentials, sign up for a new account, or change your password.
   Sign Up: Create a new user account, specifying a UserID, Username, Password, and Role (Admin/Employee).
   Login: Enter your Username and Password to access the main application.
2.   Main Application:
  Order Tab: View the menu, add items to an order, manage order details, and process payments.
  Uilities Tab: Access administrative functions like item settings (if implemented).
  Interactions: Use the provided buttons and treeviews to navigate, select items, add to orders, and perform sales operations.

### 5.Contributing
Contributions are welcome! If you have suggestions for improvements, new features, or bug fixes, feel free to open an issue or submit a pull request.

### 6. License
NO License
