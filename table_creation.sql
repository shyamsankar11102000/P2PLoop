CREATE TABLE Customers (
    CustomerID SERIAL PRIMARY KEY,
    FirstName VARCHAR(100),
    LastName VARCHAR(100),
    Address VARCHAR(255),
    PhoneNumber VARCHAR(20),
    Email VARCHAR(100),
    DateOfBirth DATE,
    NationalID VARCHAR(20) UNIQUE,
    Role VARCHAR(20) CHECK (Role IN ('Lender', 'Borrower', 'Both')) DEFAULT 'Borrower',
    AccountStatus VARCHAR(20) CHECK (AccountStatus IN ('Active', 'Inactive', 'Suspended')) DEFAULT 'Active'
);
CREATE TABLE Loans (
    LoanID SERIAL PRIMARY KEY,
    BorrowerID INT,
    LoanAmount DECIMAL(15, 2),
    InterestRate DECIMAL(5, 2),
    LoanTermMonths INT,
    StartDate DATE,
    EndDate DATE,
    LoanStatus VARCHAR(20) CHECK (LoanStatus IN ('Pending', 'Active', 'Completed', 'Defaulted')) DEFAULT 'Pending',
    FOREIGN KEY (BorrowerID) REFERENCES Customers(CustomerID) ON DELETE CASCADE
);
CREATE TABLE LoanRepayments (
    RepaymentID SERIAL PRIMARY KEY,
    LoanID INT,
    RepaymentAmount DECIMAL(15, 2),
    RepaymentDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (LoanID) REFERENCES Loans(LoanID) ON DELETE CASCADE
);
CREATE TABLE Transactions (
    TransactionID SERIAL PRIMARY KEY,
    CustomerID INT,
    TransactionType VARCHAR(20) CHECK (TransactionType IN ('Deposit', 'Withdrawal', 'LoanDisbursement', 'Repayment')),
    Amount DECIMAL(15, 2),
    TransactionDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID) ON DELETE CASCADE
);
CREATE TABLE CreditScores (
    CreditScoreID SERIAL PRIMARY KEY,
    CustomerID INT,
    CreditScore INT CHECK (CreditScore >= 300 AND CreditScore <= 850),
    LastUpdated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID) ON DELETE CASCADE
);
CREATE TABLE LoanInvestments (
    InvestmentID SERIAL PRIMARY KEY,
    LoanID INT,
    LenderID INT,
    InvestmentAmount DECIMAL(15, 2),
    InvestmentDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (LoanID) REFERENCES Loans(LoanID) ON DELETE CASCADE,
    FOREIGN KEY (LenderID) REFERENCES Customers(CustomerID) ON DELETE CASCADE
);

CREATE TABLE Customers_NationalID (
    NationalID VARCHAR(20) PRIMARY KEY,
    CustomerID INT UNIQUE REFERENCES Customers(CustomerID) ON DELETE CASCADE
);
INSERT INTO Customers_NationalID (NationalID, CustomerID)
SELECT NationalID, CustomerID FROM Customers WHERE NationalID IS NOT NULL;

ALTER TABLE Customers DROP COLUMN NationalID;




