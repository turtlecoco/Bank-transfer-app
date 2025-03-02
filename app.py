from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Function to connect to the database
def get_db_connection():
    conn = sqlite3.connect("bank.db")
    conn.row_factory = sqlite3.Row
    return conn

# Root Route to Confirm API is Running
@app.route('/')
def home():
    return jsonify({"message": "Flask API is running!"})

# Route to set transfer limits
@app.route('/set_transfer_limit', methods=['POST'])
def set_transfer_limit():
    data = request.json
    limit = float(data.get("limit"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE accounts SET transfer_limit=? WHERE id='MAIN'", (limit,))
    conn.commit()
    conn.close()

    return jsonify({"message": f"Transaction limit updated to ${limit}"}), 200

# Route to process transfers
@app.route('/transfer', methods=['POST'])
def transfer_funds():
    data = request.json
    recipient_id = data.get("recipient_id")
    amount = float(data.get("amount"))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT balance, transfer_limit FROM accounts WHERE id='MAIN'")
    main_balance, transfer_limit = cursor.fetchone()

    cursor.execute("SELECT balance FROM accounts WHERE id=?", (recipient_id,))
    recipient = cursor.fetchone()

    if not recipient:
        return jsonify({"error": "Recipient ID not found."}), 400

    if amount > main_balance:
        return jsonify({"error": "Insufficient balance."}), 400

    if amount > transfer_limit:
        return jsonify({"error": f"Transfer amount exceeds the limit of ${transfer_limit}."}), 400

    # Process transfer
    cursor.execute("UPDATE accounts SET balance = balance - ? WHERE id='MAIN'", (amount,))
    cursor.execute("UPDATE accounts SET balance = balance + ? WHERE id=?", (amount, recipient_id))

    # Log transaction
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO transactions (sender, recipient, amount, timestamp) VALUES (?, ?, ?, ?)",
                   ("MAIN", recipient_id, amount, timestamp))

    conn.commit()
    conn.close()

    return jsonify({"message": "Transfer Successful", "amount": amount, "recipient": recipient_id, "time": timestamp})

# Route to fetch transaction history
@app.route('/transactions', methods=['GET'])
def get_transactions():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions")
    transactions = cursor.fetchall()
    conn.close()

    transactions_list = [dict(row) for row in transactions]
    return jsonify(transactions_list)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')



