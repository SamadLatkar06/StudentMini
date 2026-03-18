from flask import Flask, render_template, request, redirect, url_for, session
from functools import wraps
from datetime import datetime
import pymysql
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'smart-campus-secret-key-2024'

# ---------------- IMAGE CONFIG ---------------- #

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------- DATABASE CONNECTION ---------------- #

def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="820850",
        database="smartc",
        cursorclass=pymysql.cursors.DictCursor
    )


# ---------------- DECORATORS ---------------- #

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def authority_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'authority':
            return redirect(url_for('welcome'))
        return f(*args, **kwargs)
    return decorated


def repairer_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'teacher':
            return redirect(url_for('welcome'))
        return f(*args, **kwargs)
    return decorated


# ---------------- ROUTES ---------------- #

@app.route('/')
def welcome():
    if 'user_id' in session:
        role = session.get('role')
        if role == 'authority':
            return redirect(url_for('admin'))
        if role == 'student':
            return redirect(url_for('choose_department'))
        if role == 'teacher':
            return redirect(url_for('repairer'))
    return render_template('welcome.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        role = request.form.get('role')

        conn = get_connection()
        cursor = conn.cursor()

        if role == 'student':
            roll_no = request.form.get('roll_no')
            cursor.execute(
                "SELECT id, name, role FROM users WHERE roll_no=%s AND role='student'",
                (roll_no,)
            )
        else:
            email = request.form.get('email')
            password = request.form.get('password')
            cursor.execute(
                "SELECT id, name, role FROM users WHERE email=%s AND password=%s",
                (email, password)
            )

        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['role'] = user['role']
            return redirect(url_for('welcome'))
        else:
            return render_template('login.html', error="Invalid Credentials")

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('welcome'))


@app.route('/choose-department')
@login_required
def choose_department():
    return render_template('choose_department.html')


@app.route('/map')
@login_required
def lab_map():
    return render_template('lab_map.html')


# ---------------- SUBMIT ISSUE WITH IMAGE ---------------- #

@app.route('/submit', methods=['POST'])
@login_required
def submit():

    title = request.form.get('title')
    description = request.form.get('description')
    category = request.form.get('category')
    location = request.form.get('location')
    department = request.form.get('department')
    lab_name = request.form.get('lab_name')
    pc_number = request.form.get('pc_number')
    reported_by = session.get('user_id')

    photo = request.files.get('photo')
    filename = None

    if photo and allowed_file(photo.filename):
        unique_name = str(datetime.now().timestamp()).replace('.', '') + "_" + secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_name))
        filename = unique_name

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO issues
        (title, description, category, department, lab_name, pc_number,
         location, reported_by, status, created_at, image)
        VALUES (%s, %s, %s, %s, %s, %s,
                %s, %s, 'Submitted', %s, %s)
    """, (title, description, category, department,
          lab_name, pc_number, location,
          reported_by, datetime.now(), filename))

    conn.commit()
    conn.close()

    return redirect(url_for('choose_department'))


@app.route('/repairer')
@repairer_required
def repairer():

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM issues ORDER BY created_at DESC")
    issues = cursor.fetchall()
    conn.close()

    return render_template('repairer.html', issues=issues, user=session.get('user_name'))


@app.route('/admin')
@authority_required
def admin():

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM issues ORDER BY created_at DESC")
    issues = cursor.fetchall()
    conn.close()

    return render_template('admin.html', issues=issues, user=session.get('user_name'))


if __name__ == '__main__':
    app.run(debug=True)
