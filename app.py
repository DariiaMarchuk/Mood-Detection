#%%
from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from datetime import datetime
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import io
import base64
from collections import Counter

app = Flask(__name__)
app.secret_key = '4567'  

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == '4567':  
            session['hr_logged_in'] = True
            return redirect(url_for('hr_dashboard'))
        else:
            return '''
                <h3>Неправильний пароль</h3>
                <a href="/login">Спробувати ще раз</a>
            '''
    return '''
        <form method="post">
            <h2>Вхід до HR панелі</h2>
            <input type="password" name="password" placeholder="Введіть пароль">
            <input type="submit" value="Увійти">
        </form>
    '''

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS feedback (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT,
                 mood TEXT,
                 comment TEXT,
                 timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                 )''')
    conn.commit()
    conn.close()

def init_weekly_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS weekly_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            team_conflict TEXT,
            management_support TEXT,
            suggestions TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        mood = request.form['mood']
        comment = request.form['comment']
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO feedback (username, mood, comment) VALUES (?, ?, ?)", 
                  (username, mood, comment))
        conn.commit()
        conn.close()

        
        return redirect('/thankyou')
    return render_template('index.html')

@app.route('/thankyou')
def thankyou():
    return "Дякуємо за ваш фідбек!"

@app.route('/weekly', methods=['GET', 'POST'])
def weekly():
    if request.method == 'POST':
        username = request.form['username']
        team_conflict = request.form['team_conflict']
        management_support = request.form['management_support']
        suggestions = request.form['suggestions']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO weekly_feedback (
                username, team_conflict, management_support, suggestions
            ) VALUES (?, ?, ?, ?)
        ''', (username, team_conflict, management_support, suggestions))
        conn.commit()
        conn.close()

        return redirect('/thankyou')
    return render_template('weekly.html')

@app.route('/weekly_dashboard')
def weekly_dashboard():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT username, feedback, conflict, support, suggestions, timestamp FROM weekly_feedback ORDER BY timestamp DESC")
    data = c.fetchall()
    conn.close()
    return render_template('weekly.html', data=data)

def create_percentage_bar_chart(data, title):
    counter = Counter(data)
    total = sum(counter.values())
    percentages = {k: (v / total) * 100 for k, v in counter.items()}

    fig, ax = plt.subplots()
    bars = ax.bar(percentages.keys(), percentages.values(), color='skyblue')
    ax.set_title(title)
    ax.set_ylabel("Відсоток (%)")
    ax.set_ylim(0, 100)

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 1, f'{height:.1f}%', ha='center')

    plt.xticks(rotation=15)
    plt.tight_layout()
    img = io.BytesIO()
    plt.savefig(img, format='png')
    plt.close(fig)
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode()

@app.route('/hr_dashboard')
def hr_dashboard():
    if not session.get('hr_logged_in'):
        return redirect(url_for('login'))
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("SELECT username, mood, comment, timestamp FROM feedback ORDER BY timestamp DESC")
    daily_rows = c.fetchall()

    c.execute("SELECT mood FROM feedback")
    moods = [row[0] for row in c.fetchall()]

    c.execute("SELECT username, team_conflict, management_support, suggestions, timestamp FROM weekly_feedback ORDER BY timestamp DESC")
    weekly_rows = c.fetchall()

    c.execute("SELECT team_conflict FROM weekly_feedback")
    conflicts = [row[0] for row in c.fetchall()]

    c.execute("SELECT management_support FROM weekly_feedback")
    support = [row[0] for row in c.fetchall()]

    conn.close()

    mood_chart = create_percentage_bar_chart(moods, "Employee mood (%)")
    conflict_chart = create_percentage_bar_chart(conflicts, "Conflicts within the team (%)")
    support_chart = create_percentage_bar_chart(support, "Support from management (%)")

    return render_template('hr_dashboard.html',
                           daily_rows=daily_rows,
                           weekly_rows=weekly_rows,
                           mood_chart=mood_chart,
                           conflict_chart=conflict_chart,
                           support_chart=support_chart)

@app.route('/logout')
def logout():
    session.pop('hr_logged_in', None)
    return redirect('/')

if __name__ == '__main__':
    init_db()
    init_weekly_db()
    app.run(debug=True)
    