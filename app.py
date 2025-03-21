from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flashing messages

# Database connection details
DATABASE_CONFIG = {
    'dbname': 'P2PLoop',
    'user': 'postgres',
    'password': '1313',
    'host': 'localhost',
    'port': '5432'
}

# Helper function to get database connection
def get_db_connection():
    return psycopg2.connect(**DATABASE_CONFIG)

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query 1: Loan Trends
    query1 = """
    SELECT TO_CHAR(startdate, 'YYYY-MM') AS Month, SUM(loanamount) AS LoanedAmount
    FROM Loans
    GROUP BY TO_CHAR(startdate, 'YYYY-MM')
    ORDER BY Month
    LIMIT 12;
    """
    cursor.execute(query1)
    loan_trend_data = cursor.fetchall()
    months_cc = [row[0] for row in loan_trend_data]
    total_loan_amount = [float(row[1]) for row in loan_trend_data]

    # Query 2: Credit Score Distribution
    query2 = """
    SELECT 
        CASE 
            WHEN CreditScore BETWEEN 300 AND 579 THEN 'Poor'
            WHEN CreditScore BETWEEN 580 AND 669 THEN 'Fair'
            WHEN CreditScore BETWEEN 670 AND 739 THEN 'Good'
            WHEN CreditScore BETWEEN 740 AND 799 THEN 'Very Good'
            ELSE 'Excellent'
        END AS ScoreRange,
        COUNT(*) AS CustomerCount
    FROM CreditScores
    GROUP BY ScoreRange
    ORDER BY ScoreRange;
    """
    cursor.execute(query2)
    credit_trend_data = cursor.fetchall()
    score_range = [row[0] for row in credit_trend_data]
    customer_count = [int(row[1]) for row in credit_trend_data]  # Use int since it’s a count

    query3 = """
    SELECT 
        c.CustomerID, 
        c.FirstName || ' ' || c.LastName AS CustomerName, 
        SUM(l.LoanAmount) AS TotalBorrowed
    FROM Customers c
    JOIN Loans l ON c.CustomerID = l.BorrowerID
    GROUP BY c.CustomerID, c.FirstName, c.LastName
    ORDER BY TotalBorrowed DESC
    LIMIT 5;
    """
    cursor.execute(query3)
    top_customers = cursor.fetchall()

    query4 = """
    SELECT 
    c.CustomerID, 
    c.FirstName || ' ' || c.LastName AS CustomerName, 
    SUM(li.InvestmentAmount) AS TotalInvested
    FROM Customers c
    JOIN LoanInvestments li ON c.CustomerID = li.LenderID
    GROUP BY c.CustomerID, c.FirstName, c.LastName
    ORDER BY TotalInvested DESC
    LIMIT 5;
    """
    cursor.execute(query4)
    top_lenders = cursor.fetchall()

    query = """
        SELECT
            c.CustomerID,
            c.FirstName || ' ' || c.LastName AS CustomerName,
            ROUND(AVG(cs.creditscore)) AS creditscores,
            COALESCE(SUM(l.loanamount), 0) AS TotalBorrowed,
            COALESCE(SUM(t.investmentamount), 0) AS TotalInvested
        FROM Customers c
        LEFT JOIN CreditScores cs ON c.CustomerID = cs.CustomerID
        LEFT JOIN Loans l ON l.BorrowerID = c.CustomerID
        LEFT JOIN LoanInvestments t ON t.LenderID = c.CustomerID
        WHERE 1=1
        """
    params = []

    if request.method == 'POST':
        # Get form inputs
        customer_id = request.form.get('customer_id')
        customer_name = request.form.get('customer_name')
        credit_score = request.form.get('credit_score')

        if customer_id:
            query += " AND c.CustomerID = %s"
            params.append(customer_id)
        if customer_name:
            query += " AND (c.FirstName || ' ' || c.LastName) LIKE %s"
            params.append(f"%{customer_name}%")
        if credit_score:
            query += " AND cs.creditscore >= %s"
            params.append(credit_score)

    query += " GROUP BY c.CustomerID, c.FirstName, c.LastName ORDER BY c.CustomerID"

    cursor.execute(query, params)
    customers_summary = cursor.fetchall()
    conn.close()
    return render_template('index.html', customers_summary=customers_summary, 
                              months_cc=months_cc, total_loan_amount=total_loan_amount, 
                              score_range=score_range, customer_count=customer_count, top_customers=top_customers, top_lenders=top_lenders)

# Other routes remain unchanged
@app.route('/customers')
def view_customers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Customers")
    customers = cursor.fetchall()
    conn.close()
    return render_template('customers.html', customers=customers)


@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone_number = request.form['phone_number']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Customers (FirstName, LastName, Email, PhoneNumber)
            VALUES (%s, %s, %s, %s)
        """, (first_name, last_name, email, phone_number))
        conn.commit()
        conn.close()
        flash("Customer added successfully!", "success")
        return redirect(url_for('view_customers'))
    return render_template('add_customer.html')



@app.route('/loan_details', methods=['GET', 'POST'])
def loan_details():
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        # Step 1: User submits the loan_id
        loan_id = request.form['loan_id']

        # Step 2: Query the loan details from the database
        cursor.execute("""
            SELECT LoanID, LoanAmount, InterestRate, StartDate, EndDate, LoanStatus
            FROM Loans WHERE LoanID = %s
        """, (loan_id,))
        loan = cursor.fetchone()

        if loan is None:
            flash('No loan found with this ID.', 'danger')
            return redirect(url_for('loan_details'))  # Redirect back if no loan found

        # Step 3: Handle payment submission
        if 'payment_amount' in request.form:
            payment_amount = request.form['payment_amount']
            payment_date = request.form['payment_date']

            # Insert the payment into LoanRepayments table
            cursor.execute("""
                INSERT INTO LoanRepayments (LoanID, RepaymentAmount, RepaymentDate)
                VALUES (%s, %s, %s)
            """, (loan_id, payment_amount, payment_date))
            conn.commit()
            cursor.execute("""
    SELECT LoanID, LoanAmount, InterestRate, StartDate, EndDate, LoanStatus
    FROM Loans WHERE LoanID = %s
""", (loan_id,))
            loan = cursor.fetchone()
            loan_amount = loan[1]
            new_remaining_balance = loan_amount - int(payment_amount)

            if new_remaining_balance <= 0:
                    new_status = 'Completed'
                    new_remaining_balance = 0  # Loan is fully paid off
            else:
                    new_status = loan[5]

                # Update RemainingBalance and LoanStatus in the Loans table
            cursor.execute("""
                    UPDATE Loans
                    SET LoanAmount = %s, LoanStatus = %s
                    WHERE LoanID = %s
                """, (new_remaining_balance, new_status, loan_id))
            conn.commit()

            # Flash success message
            flash(f'Payment of {payment_amount} for Loan ID {loan_id} added successfully.', 'success')
            return redirect(url_for('loan_details'))  # Reload loan details after payment

        return render_template('loan_details.html', loan=loan)

    # If it's a GET request, show the form to input loan_id
    return render_template('loan_details_input.html')




if __name__ == '__main__':
    app.run(debug=True)