from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('expenses.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = sqlite3.connect('expenses.db')
    
    # Create the table if it doesn't exist
    # Reverted to basic expense tracking without 'type' or 'recurring' columns
    conn.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

# Add Transaction
@app.route('/add-expense', methods=['POST'])
def add_expense():
    data = request.json
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO expenses (amount, category, description, date) VALUES (?, ?, ?, ?)",
        (data['amount'], data['category'], data['description'], data['date'])
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Expense added successfully"})

# Get All Transactions
@app.route('/get-expenses')
def get_expenses():
    conn = get_db_connection()
    expenses = conn.execute("SELECT * FROM expenses ORDER BY date DESC").fetchall()
    conn.close()
    return jsonify([dict(row) for row in expenses])

# Delete Transaction
@app.route('/delete-expense/<int:id>', methods=['DELETE'])
def delete_expense(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM expenses WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Deleted successfully"})

# Edit Transaction
@app.route('/edit-expense/<int:id>', methods=['PUT'])
def edit_expense(id):
    data = request.json
    conn = get_db_connection()
    conn.execute(
        "UPDATE expenses SET amount=?, category=?, description=?, date=? WHERE id=?",
        (data['amount'], data['category'], data['description'], data['date'], id)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Updated successfully"})

# Summary API
@app.route('/summary')
def summary():
    conn = get_db_connection()

    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    month = today.strftime('%Y-%m')
    year = today.strftime('%Y')

    day_total = conn.execute(
        "SELECT SUM(amount) FROM expenses WHERE date=?",
        (today,)
    ).fetchone()[0] or 0

    week_total = conn.execute(
        "SELECT SUM(amount) FROM expenses WHERE date BETWEEN ? AND ?",
        (week_start, today)
    ).fetchone()[0] or 0

    month_total = conn.execute(
        "SELECT SUM(amount) FROM expenses WHERE strftime('%Y-%m', date)=?",
        (month,)
    ).fetchone()[0] or 0

    year_total = conn.execute(
        "SELECT SUM(amount) FROM expenses WHERE strftime('%Y', date)=?",
        (year,)
    ).fetchone()[0] or 0

    category_data = conn.execute(
        "SELECT category, SUM(amount) as total FROM expenses GROUP BY category"
    ).fetchall()

    conn.close()

    return jsonify({
        "day": day_total,
        "week": week_total,
        "month": month_total,
        "year": year_total,
        "category": [dict(row) for row in category_data]
    })

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0',port=5000)