import psycopg2
from faker import Faker
import random

# Initialize Faker instance to generate fake data
fake = Faker()

# Connect to your PostgreSQL database
conn = psycopg2.connect(
    dbname="P2PLoop",  # Change with your DB name
    user="postgres",       # Change with your DB user
    password="1313",  # Change with your DB password
    host="localhost",       # Or your DB host
    port="5432"             # Or your DB port
)
cursor = conn.cursor()

# Function to insert customer data (Lender or Borrower)
def insert_customers(n):
    for _ in range(n):
        first_name = fake.first_name()
        last_name = fake.last_name()
        address = fake.address()
        phone_number = fake.phone_number()[:20]  # Truncate to 20 characters
        email = fake.email()
        date_of_birth = fake.date_of_birth(minimum_age=18, maximum_age=75).strftime('%Y-%m-%d')
        national_id = fake.ssn()[:20]  # Truncate to 20 characters
        role = random.choice(['Lender', 'Borrower', 'Both'])
        account_status = random.choice(['Active', 'Inactive', 'Suspended'])
        
        cursor.execute("""
            INSERT INTO Customers (FirstName, LastName, Address, PhoneNumber, Email, DateOfBirth, NationalID, Role, AccountStatus)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (first_name, last_name, address, phone_number, email, date_of_birth, national_id, role, account_status))

    conn.commit()

# Function to insert loan data
def insert_loans(n, customers_count):
    for _ in range(n):
        borrower_id = random.randint(1, customers_count)
        loan_amount = round(random.uniform(1000, 50000), 2)
        interest_rate = round(random.uniform(5.0, 15.0), 2)
        loan_term_months = random.randint(12, 60)
        start_date = fake.date_this_decade()
        end_date = fake.date_this_decade()
        loan_status = random.choice(['Pending', 'Active', 'Completed', 'Defaulted'])

        cursor.execute("""
            INSERT INTO Loans (BorrowerID, LoanAmount, InterestRate, LoanTermMonths, StartDate, EndDate, LoanStatus)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (borrower_id, loan_amount, interest_rate, loan_term_months, start_date, end_date, loan_status))

    conn.commit()

# Function to insert loan investments
def insert_loan_investments(loans_count, customers_count, n):
    for _ in range(n):
        loan_id = random.randint(1, loans_count)
        lender_id = random.randint(1, customers_count)
        investment_amount = round(random.uniform(100, 10000), 2)
        cursor.execute("""
            INSERT INTO LoanInvestments (LoanID, LenderID, InvestmentAmount)
            VALUES (%s, %s, %s)
        """, (loan_id, lender_id, investment_amount))

    conn.commit()

# Function to insert loan repayments
def insert_loan_repayments(loans_count, n):
    for _ in range(n):
        loan_id = random.randint(1, loans_count)
        repayment_amount = round(random.uniform(50, 5000), 2)
        cursor.execute("""
            INSERT INTO LoanRepayments (LoanID, RepaymentAmount)
            VALUES (%s, %s)
        """, (loan_id, repayment_amount))

    conn.commit()

# Function to insert transaction data (Deposit, Withdrawal, LoanDisbursement, Repayment)
def insert_transactions(n, customers_count):
    transaction_types = ['Deposit', 'Withdrawal', 'LoanDisbursement', 'Repayment']
    
    for _ in range(n):
        customer_id = random.randint(1, customers_count)
        transaction_type = random.choice(transaction_types)
        amount = round(random.uniform(10, 5000), 2)  # Random amount between $10 and $5000
        transaction_date = fake.date_this_year().strftime('%Y-%m-%d')  # Random date within the current year

        cursor.execute("""
            INSERT INTO Transactions (CustomerID, TransactionType, Amount, TransactionDate)
            VALUES (%s, %s, %s, %s)
        """, (customer_id, transaction_type, amount, transaction_date))

    conn.commit()

# Function to insert credit score data
def insert_credit_scores(customers_count, n):
    for _ in range(n):
        customer_id = random.randint(1, customers_count)
        credit_score = random.randint(300, 850)  # Credit score between 300 and 850
        last_updated = fake.date_this_year().strftime('%Y-%m-%d')  # Random date within the current year

        cursor.execute("""
            INSERT INTO CreditScores (CustomerID, CreditScore, LastUpdated)
            VALUES (%s, %s, %s)
        """, (customer_id, credit_score, last_updated))

    conn.commit()

# Populate tables with data
customers_count = 10000  # 10,000 customers
loans_count = 500  # 500 loans
loan_investments_count = 5000  # 5,000 loan investments
loan_repayments_count = 3000  # 3,000 loan repayments
transactions_count = 5000  # 5,000 transactions
credit_scores_count = 10000  # 10,000 credit score records (one per customer)

#print("Inserting customers...")
#insert_customers(customers_count)

#print("Inserting loans...")
#insert_loans(loans_count, customers_count)

#print("Inserting loan investments...")
#insert_loan_investments(loans_count, customers_count, loan_investments_count)

#print("Inserting loan repayments...")
#insert_loan_repayments(loans_count, loan_repayments_count)

#print("Inserting transactions...")
#insert_transactions(transactions_count, customers_count)

print("Inserting credit scores...")
insert_credit_scores(customers_count, credit_scores_count)

# Close the connection
cursor.close()
conn.close()

print("Data population complete.")