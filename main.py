from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Database setup
def init_db():
    conn = sqlite3.connect("bulbs.db")
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS bulbs (
        nodeID TEXT PRIMARY KEY NOT NULL UNIQUE,
        bulb1 TEXT DEFAULT 'OFF',
        bulb2 TEXT DEFAULT 'OFF',
        bulb3 TEXT DEFAULT 'OFF',
        bulb4 TEXT DEFAULT 'OFF',
        bulb5 TEXT DEFAULT 'OFF'
    )''')

    # Create users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        nodeID TEXT PRIMARY KEY NOT NULL UNIQUE,
        password TEXT NOT NULL
    )''')

     # Check if the adminNode already exists in the users table
    cursor.execute("SELECT * FROM users WHERE nodeID = ?", ('adminNode',))
    if not cursor.fetchone():
        # Insert default admin user
        cursor.execute("INSERT INTO users (nodeID, password) VALUES (?, ?)",
                       ('adminNode', generate_password_hash('admin123', method='pbkdf2:sha256')))
        # Insert corresponding bulbs data
        cursor.execute("INSERT INTO bulbs (nodeID, bulb1, bulb2, bulb3, bulb4, bulb5) VALUES (?, ?, ?, ?, ?, ?)",
                       ('adminNode', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF'))
    conn.commit()
    conn.close()

init_db()



# -------------------- Web Routes --------------------

# Home Route
@app.route('/')
def home():
    if "user" in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nodeID = request.form['nodeID']
        password = request.form['password']

        # Verify user credentials
        conn = sqlite3.connect("bulbs.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE nodeID=?", (nodeID,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[1], password):
            session['user'] = nodeID
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid nodeID or password.', 'danger')

    return render_template('signin.html')

# Logout Route
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))



# Dashboard Route (Web Portal for Bulb Control)
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if "user" not in session:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('login'))

    nodeID = session['user']

    # Fetch bulb data for the logged-in user
    conn = sqlite3.connect("bulbs.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bulbs WHERE nodeID = ?", (nodeID,))
    bulb = cursor.fetchone()
    conn.close()

    if not bulb:
        flash('No bulb data found for this user.', 'danger')
        return redirect(url_for('logout'))

    if request.method == 'POST':
        # Update bulbs
        bulb1 = request.form.get('bulb1', 'OFF')
        bulb2 = request.form.get('bulb2', 'OFF')
        bulb3 = request.form.get('bulb3', 'OFF')
        bulb4 = request.form.get('bulb4', 'OFF')
        bulb5 = request.form.get('bulb5', 'OFF')

        conn = sqlite3.connect("bulbs.db")
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE bulbs
            SET bulb1 = ?, bulb2 = ?, bulb3 = ?, bulb4 = ?, bulb5 = ?
            WHERE nodeID = ?
        """, (bulb1, bulb2, bulb3, bulb4, bulb5, nodeID))
        conn.commit()
        conn.close()

        flash('Bulb states updated successfully!', 'success')
        return redirect(url_for('dashboard',node_ID=nodeID))

    return render_template('index.html',node_ID = nodeID)



# -------------------- API Endpoints --------------------

# API Endpoint to get bulb states
@app.route('/api/get_state', methods=['GET'])
def get_state():
    nodeID = request.args.get('node_id')  
    conn = sqlite3.connect("bulbs.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bulbs WHERE nodeID=?", (nodeID,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify({
            'nodeID': row[0],
            'bulbs': {
                'bulb1': row[1],
                'bulb2': row[2],
                'bulb3': row[3],
                'bulb4': row[4],
                'bulb5': row[5],
            }
        })
    else:
        return jsonify({'error': 'User not found'}), 404

# API Endpoint to update a single bulb's state
@app.route('/api/update_bulb', methods=['POST'])
def update_bulb():
    data = request.json
    nodeID = data['node_id'] 
    bulb_name = data['bulb_name'] 
    bulb_state = data['bulb_state']

    conn = sqlite3.connect("bulbs.db")
    cursor = conn.cursor()
    cursor.execute(f"UPDATE bulbs SET {bulb_name} = ? WHERE nodeID = ?", (bulb_state, nodeID))
    conn.commit()
    conn.close()

    return jsonify({'message': f"{bulb_name} updated to {bulb_state} for user {nodeID}"}), 200

# -------------------- Run Server --------------------
if __name__ == '__main__':
    app.run(debug=True)
