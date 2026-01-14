import time
import os
from flask import Flask, render_template, request
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL Config (FROM docker-compose)
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB')

mysql = MySQL(app)

def wait_for_db():
    for i in range(10):
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    message VARCHAR(255)
                );
            """)
            mysql.connection.commit()
            cur.close()
            print("✅ MySQL connected successfully")
            return
        except Exception as e:
            print("⏳ Waiting for MySQL...", e)
            time.sleep(5)

wait_for_db()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        msg = request.form["message"]
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO messages (message) VALUES (%s)", (msg,))
        mysql.connection.commit()
        cur.close()

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM messages")
    data = cur.fetchall()
    cur.close()

    return render_template("index.html", messages=data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
