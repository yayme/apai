
import os
import psycopg2
from functools import wraps
from flask import Response
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Get the database URL from Render environment variable
DATABASE_URL = os.environ.get('DATABASE_URL')

# Admin credentials (set your own username and password)
ADMIN_USER = os.environ.get('ADMIN_USER', 'admin')
ADMIN_PASS = os.environ.get('ADMIN_PASS', 'password')

# Basic Auth decorator
def check_auth(username, password):
    return username == ADMIN_USER and password == ADMIN_PASS

def authenticate():
    return Response(
        'Could not verify your access. Please provide valid credentials.',
        401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# Ensure table exists
def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    email = request.json.get('email')
    if not email:
        return jsonify({'success': False, 'message': 'No email provided.'}), 400
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute('INSERT INTO emails (email) VALUES (%s) ON CONFLICT DO NOTHING', (email,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Thank you! You will be notified.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin/emails')
@requires_auth
def show_emails():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute('SELECT email, created_at FROM emails ORDER BY created_at DESC')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        if not rows:
            return '<pre>No emails have been signed up yet.</pre>'
        emails_html = '\n'.join([f"{email} ({created_at})" for email, created_at in rows])
        return f"<pre>{emails_html}</pre>"
    except Exception as e:
        return f"<pre>Error: {str(e)}</pre>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
