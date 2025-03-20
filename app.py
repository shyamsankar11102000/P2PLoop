from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flashing messages

# Database connection details
DATABASE_CONFIG = {
    'dbname': 'your_db_name',
    'user': 'your_user',
    'password': 'your_password',
    'host': 'localhost',
    'port': '5432'
}

# Helper function to get database connection
def get_db_connection():
    conn = psycopg2.connect(**DATABASE_CONFIG)
    return conn

@app.route('/')
def home():
    return render_template('index.html')

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
