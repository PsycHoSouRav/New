from flask import Flask, request, redirect, render_template, jsonify
import sqlite3
import hashlib

app = Flask(__name__)

# Initialize the SQLite database
def init_db():
    with sqlite3.connect('urls.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS url_mapping (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_id TEXT UNIQUE,
            original_url TEXT
        )''')
        conn.commit()

# Shorten URL
@app.route('/shorten', methods=['POST'])
def shorten_url():
    original_url = request.form['url']
    if not original_url:
        return jsonify({'error': 'URL is required'}), 400

    short_id = hashlib.md5(original_url.encode()).hexdigest()[:6]
    with sqlite3.connect('urls.db') as conn:
        c = conn.cursor()
        c.execute('INSERT OR IGNORE INTO url_mapping (short_id, original_url) VALUES (?, ?)', (short_id, original_url))
        conn.commit()

    short_url = f'{request.host_url}{short_id}'
    return render_template('short.html', short_url=short_url)

# Redirect to original URL
@app.route('/<short_id>')
def redirect_to_url(short_id):
    with sqlite3.connect('urls.db') as conn:
        c = conn.cursor()
        c.execute('SELECT original_url FROM url_mapping WHERE short_id = ?', (short_id,))
        row = c.fetchone()
        if row:
            return redirect(row[0])
        return 'URL not found', 404

# Home page
@app.route('/')
def index():
    return render_template('short.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
