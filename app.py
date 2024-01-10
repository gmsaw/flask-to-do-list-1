from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    week_number = db.Column(db.Integer)

year = datetime.now().year

def informasi_hari_dan_minggu():
    # Mendapatkan tanggal hari ini
    tanggal_sekarang = datetime.now()

    # Mendapatkan tanggal awal tahun
    tahun_sekarang = tanggal_sekarang.year
    tanggal_awal_tahun = datetime(tahun_sekarang, 1, 1)

    # Menyesuaikan minggu keberapa dan hari keberapa berdasarkan 5 Januari
    tanggal_awal_minggu_pertama = tanggal_awal_tahun - timedelta(days=tanggal_awal_tahun.weekday())
    minggu_keberapa = ((tanggal_sekarang - tanggal_awal_minggu_pertama).days // 7) + 1
    hari_keberapa_dalam_minggu = (tanggal_sekarang.weekday() + 1)  # Menggunakan 1-7, Senin sampai Minggu

    # Menghitung persentase hari terlewati dalam minggu
    persentase_hari_terlewati = (hari_keberapa_dalam_minggu / 7) * 100

    return minggu_keberapa, hari_keberapa_dalam_minggu, persentase_hari_terlewati

def jum_minggu(year):
    tanggal_awal = datetime(year, 1, 1)
    tanggal_akhir = datetime(year, 12, 31)
    selisih_hari = (tanggal_akhir - tanggal_awal).days + 1  # Termasuk tanggal akhir

    # Menghitung jumlah minggu
    weeks = selisih_hari // 7
    
    return weeks

@app.route('/')
@app.route('/home')
def index():
    global year
    weeks, days, percent = informasi_hari_dan_minggu()
    weeks_in_year = jum_minggu(year)
    percent = f"{percent:.2f}"

    return render_template('index.html', year=year, weeks_in_year=weeks_in_year, weeks=weeks, days=days, percent=percent)

from flask import request

from flask import request

@app.route('/to-do', methods=['GET', 'POST'])
def to_do():
    if request.method == 'POST':
        # Handle form submission to add a new task
        content = request.form['content']
        week_number = request.form.get('week', type=int)

        existing_task = Task.query.filter_by(content=content, completed=False, week_number=week_number).first()

        if not existing_task:
            new_task = Task(content=content, week_number=week_number)

            try:
                db.session.add(new_task)
                db.session.commit()
                return redirect(url_for('to_do', week=week_number))
            except:
                return 'There was an issue adding your task.'
        else:
            return 'Task with the same content already exists and is not completed.'
    else:
        # Display tasks for the specified week or the current week
        selected_week = request.args.get('week', default=informasi_hari_dan_minggu()[0], type=int)
        tasks = Task.query.filter_by(week_number=selected_week).all()
        weeks, _, _ = informasi_hari_dan_minggu()  # Calculate current week
        weeks_in_year = jum_minggu(year)  # Calculate total weeks in the year

        return render_template('to-do.html', tasks=tasks, selected_week=selected_week, weeks_in_year=weeks_in_year, current_week=weeks)

@app.route('/add', methods=['POST'])
def add():
    content = request.form['content']
    week_number = request.form.get('week', type=int)  # Get the selected week from the form

    existing_task = Task.query.filter_by(content=content, completed=False, week_number=week_number).first()

    if not existing_task:
        new_task = Task(content=content, week_number=week_number)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect(url_for('to_do', week=week_number))  # Redirect to the selected week
        except:
            return 'There was an issue adding your task.'
    else:
        return 'Task with the same content already exists and is not completed.'


@app.route('/complete/<int:id>')
def complete(id):
    task = Task.query.get(id)
    task.completed = not task.completed

    try:
        db.session.commit()
        return redirect(url_for('/to-do'))
    except:
        return 'There was an issue completing the task.'

@app.route('/delete/<int:id>')
def delete(id):
    task = Task.query.get(id)

    try:
        db.session.delete(task)
        db.session.commit()
        return redirect('/to-do')
    except:
        return 'There was an issue deleting the task.'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)