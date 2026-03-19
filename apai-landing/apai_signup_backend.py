from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__)
EMAIL_FILE = 'emails.txt'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    email = request.json.get('email')
    if not email:
        return jsonify({'success': False, 'message': 'No email provided.'}), 400
    with open(EMAIL_FILE, 'a') as f:
        f.write(email + '\n')
    return jsonify({'success': True, 'message': 'Thank you! You will be notified.'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
