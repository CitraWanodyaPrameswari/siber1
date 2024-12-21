from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_sqlalchemy import SQLAlchemy
from markupsafe import escape

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(50), nullable=False)

# Create database
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    students = Student.query.all()
    escaped_students = [
        {
            "id": student.id,
            "name": escape(student.name),
            "age": student.age,
            "grade": escape(student.grade)
        }
        for student in students
    ]
    return render_template('index.html', students=escaped_students)

@app.route('/add', methods=['POST'])
def add_student():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    name = escape(request.form['name'])
    age = int(request.form['age'])
    grade = escape(request.form['grade'])

    new_student = Student(name=name, age=age, grade=grade)
    db.session.add(new_student)
    db.session.commit()
    flash("Student added successfully!", "success")
    return redirect('/')

@app.route('/delete/<int:id>', methods=['GET'])
def delete_student(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash("Student deleted successfully!", "success")
    return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'password':
            session['logged_in'] = True
            flash("Login successful!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials, please try again.", "danger")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
