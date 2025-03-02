import sqlite3

# Connect to the database
conn = sqlite3.connect("bank.db")
cursor = conn.cursor()

# Create `accounts` table
cursor.execute('''CREATE TABLE IF NOT EXISTS accounts (
                    id TEXT PRIMARY KEY, 
                    name TEXT, 
                    age INTEGER, 
                    balance REAL, 
                    transfer_limit REAL)''')

# Create `transactions` table
cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    sender TEXT, 
                    recipient TEXT, 
                    amount REAL, 
                    timestamp TEXT)''')

# Insert a MAIN account (if missing)
cursor.execute("SELECT * FROM accounts WHERE id='MAIN'")
if not cursor.fetchone():
    cursor.execute("INSERT INTO accounts (id, name, age, balance, transfer_limit) VALUES ('MAIN', 'Main Account', 0, 10000, 5000)")

# Save and close
conn.commit()
conn.close()

print("Database setup completed!")
