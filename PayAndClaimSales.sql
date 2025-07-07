CREATE DATABASE Beverage;
USE Beverage;

CREATE TABLE Users (
    UserID VARCHAR(50) PRIMARY KEY,
    UserName VARCHAR(100) NOT NULL UNIQUE,
    Password VARCHAR(255) NOT NULL,
    Role ENUM('Admin', 'Employee') NOT NULL
);
CREATE TABLE Items (
    ItemID VARCHAR(50) PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Unit VARCHAR(20) NOT NULL,
    Cost INT NOT NULL CHECK (Cost > 0), -- Đảm bảo giá > 0
    Category VARCHAR(50) -- Thêm danh mục sản phẩm (ví dụ: Coffee, Tea)
);
CREATE TABLE Orders (
    OrderID INT AUTO_INCREMENT PRIMARY KEY,
    UserID VARCHAR(50),
    Tables VARCHAR(20) NOT NULL DEFAULT 'Takeaway',
    OrderDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    TotalAmount INT NOT NULL CHECK (TotalAmount >= 0), -- Đảm bảo tổng tiền >= 0
    Status ENUM('Pending', 'Completed', 'Cancelled') DEFAULT 'Pending', -- Trạng thái đơn hàng
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);
CREATE TABLE OrderDetails (
    OrderDetailID INT AUTO_INCREMENT PRIMARY KEY,
    OrderID INT,
    ItemID VARCHAR(50),
    Quantity INT NOT NULL CHECK (Quantity > 0), -- Đảm bảo số lượng > 0
    TotalPrice INT NOT NULL CHECK (TotalPrice >= 0), -- Đảm bảo tổng tiền >= 0
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
    FOREIGN KEY (ItemID) REFERENCES Items(ItemID)
);


INSERT INTO Users (UserID, UserName, Password, Role)
VALUES
('U001', 'huy_dth225650', '007', 'Admin'),
('U002', 'huykyun', '117', 'Employee'),
('U003', 'huanguohui', '007', 'Employee'),
('U004', 'hkhuang07', '007', 'Employee'),
('U005', 'hwangwoohui', '007', 'Employee');

INSERT INTO Items (ItemID, Name, Unit, Cost, Category)
VALUES
('CFE01', 'Coffee', 'cup', 24000, 'Coffee'),
('CFE02', 'Milk Coffee', 'cup', 31000, 'Coffee'),
('CFE03', 'Espresso', 'cup', 45000, 'Coffee'),
('TEA01', 'Lipton Tea', 'cup', 27000, 'Tea'),
('TEA02', 'Guava Tea', 'cup', 35000, 'Tea'),
('TEA03', 'Peach Tea', 'cup', 34000, 'Tea'),
('SMO01', 'Avocado Smoothie', 'cup', 45000, 'Smoothie'),
('SMO02', 'Orange Smoothie', 'cup', 45000, 'Smoothie'),
('SMO03', 'Strawberry Smoothie', 'cup', 45000, 'Smoothie');

SELECT * FROM Items;
SELECT * FROM Orders;
SELECT * FROM OrderDetails;
SELECT * FROM Users;

DELETE FROM OrderDetails;
DELETE FROM Orders;
DELETE FROM Users WHERE Password = "117";


ALTER TABLE Orders
ADD `Tables` VARCHAR(20) NOT NULL DEFAULT 'Takeaway';
ALTER TABLE Orders CHANGE COLUMN `Table` Tables VARCHAR(20) NOT NULL DEFAULT 'Takeaway';


#Tắt chế độ safe_update 
SET SQL_SAFE_UPDATES = 0;
SET SQL_SAFE_UPDATES = 1;