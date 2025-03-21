from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
import json
from flask import jsonify

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
    conn = psycopg2.connect(**DATABASE_CONFIG)
    return conn

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    cursor = conn.cursor()

    query1 = """
    SELECT TO_CHAR(startdate, 'YYYY-MM') AS Month, sum(loanamount) AS LoanedAmount
    FROM Loans
    GROUP BY TO_CHAR(startdate, 'YYYY-MM')
    ORDER BY Month
    LIMIT 12;
    """
    cursor.execute(query1)
    trend_data = cursor.fetchall()

    # Process the data for the graph
    months_cc = [row[0] for row in trend_data]
    total_loan_amount = [float(row[1]) for row in trend_data]

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
    trend_data = cursor.fetchall()

    # Process the data for the graph
    score_range = [row[0] for row in trend_data]
    customer_count = [float(row[1]) for row in trend_data]


    if request.method == 'POST':
        # Get the search criteria from the form
        customer_id = request.form.get('customer_id')
        customer_name = request.form.get('customer_name')
        credit_score = request.form.get('credit_score')

        # Build dynamic query based on form inputs
        query = """
        SELECT
            c.CustomerID,
            c.FirstName || ' ' || c.LastName AS CustomerName,
			round(avg(creditscore)) as creditscores,
            COALESCE(SUM(l.loanamount), 0) AS TotalBorrowed,
            COALESCE(SUM(t.investmentamount), 0) AS TotalInvested
        FROM
            Customers c
        LEFT JOIN CreditScores cs ON c.CustomerID = cs.CustomerID
        LEFT JOIN Loans l ON l.BorrowerID = c.CustomerID
        LEFT JOIN loaninvestments t ON t.LenderID = c.CustomerID
        where 1=1
        """

        # Append conditions based on user inputs
        if customer_id:
            query += f" AND c.CustomerID = {customer_id}"
        if customer_name:
            query += f" AND (FirstName || ' ' || LastName) LIKE %s"
        if credit_score:
            query += f" AND CreditScore >= {credit_score}"
        query+=f" GROUP BY c.CustomerID, c.FirstName, c.LastName ORDER BY c.CustomerID"

        # Execute the query with the parameters
        cursor = conn.cursor()
        cursor.execute(query, ('%' + customer_name + '%',))  # Pass the parameter for customer_name safely
        customers_summary = cursor.fetchall()
        conn.close()
        return render_template('index.html', customers_summary=customers_summary, months_cc=months_cc, total_loan_amount=total_loan_amount, score_range=score_range, customer_count=customer_count)
    conn.close()
    return render_template('index.html', customers_summary=None, months_cc=months_cc, total_loan_amount=total_loan_amount, score_range=score_range, customer_count=customer_count)



# Route to view all customers
@app.route('/customers')
def view_customers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Customers")
    customers = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('customers.html', customers=customers)

# Route to view all loans
@app.route('/loans')
def view_loans():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Loans")
    loans = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('loans.html', loans=loans)

# Route to add a new customer
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
        cursor.close()
        conn.close()
        flash("Customer added successfully!", "success")
        return redirect(url_for('view_customers'))

    return render_template('add_customer.html')


# Main entry point
if __name__ == '__main__':
    app.run(debug=True)
