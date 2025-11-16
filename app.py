# app.py
from flask import Flask, jsonify, request, render_template, send_file, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from io import BytesIO
import json
from datetime import datetime, date, time

# ---------- CONFIG ----------
# change user:password if needed. For XAMPP default: user=root, password empty.
DB_USER = "root"
DB_PASS = ""            # put password if you set one
DB_HOST = "127.0.0.1"
DB_PORT = 3306
DB_NAME = "dbms"

DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

# ---------- APP INIT ----------
app = Flask(__name__,static_folder='static',template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ---------- JSON serializer helper ----------
def _default_serializer(obj):
    # handle date/time/datetime
    if isinstance(obj, (datetime, date, time)):
        return obj.isoformat()
    # bytes -> string
    if isinstance(obj, (bytes, bytearray)):
        return obj.decode('utf-8')
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

def safe_jsonify(data, status=200):
    """Return a Flask response with JSON-serialized `data` using the default serializer."""
    text = json.dumps(data, default=_default_serializer, ensure_ascii=False)
    return app.response_class(text, mimetype='application/json'), status

# ---------- MODELS ----------
class Course(db.Model):
    __tablename__ = 'course'
    course_code = db.Column(db.String(20), primary_key=True)
    course_title = db.Column(db.String(255), nullable=False)
    credits = db.Column(db.Integer)

class Exam(db.Model):
    __tablename__ = 'exams'
    exam_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_code = db.Column(db.String(20), db.ForeignKey('course.course_code'), nullable=False)
    course_title = db.Column(db.String(200))
    exam_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    venue_note = db.Column(db.Text)

class Room(db.Model):
    __tablename__ = 'rooms'
    room_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    room_code = db.Column(db.String(50), unique=True, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    building = db.Column(db.String(100))
    floor = db.Column(db.Integer)

class Student(db.Model):
    __tablename__ = 'students'
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roll_no = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    department = db.Column(db.String(100))
    year = db.Column(db.Integer)

class StudentExam(db.Model):
    __tablename__ = 'student_exam'
    student_exam_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id', ondelete='CASCADE'), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.exam_id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(20), default='registered')
    __table_args__ = (db.UniqueConstraint('student_id', 'exam_id', name='ux_student_exam'),)

class SeatAssignment(db.Model):
    __tablename__ = 'seat_assignment'
    seat_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.exam_id', ondelete='CASCADE'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.room_id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id', ondelete='CASCADE'), nullable=False)
    seat_number = db.Column(db.Integer, nullable=False)
    __table_args__ = (
        db.UniqueConstraint('exam_id', 'room_id', 'seat_number', name='ux_exam_room_seat'),
        db.UniqueConstraint('exam_id', 'student_id', name='ux_exam_student'),
    )

class Invigilator(db.Model):
    __tablename__ = 'invigilators'
    invigilator_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    employee_no = db.Column(db.String(100), unique=True)
    dept = db.Column(db.String(100))

class InvigilatorAvailability(db.Model):
    __tablename__ = 'invigilator_availability'
    avail_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    invigilator_id = db.Column(db.Integer, db.ForeignKey('invigilators.invigilator_id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    __table_args__ = (db.UniqueConstraint('invigilator_id','date','start_time','end_time', name='ux_inv_avail'),)

class InvigilationAssignment(db.Model):
    __tablename__ = 'invigilation_assignment'
    assign_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.exam_id', ondelete='CASCADE'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.room_id', ondelete='CASCADE'), nullable=False)
    invigilator_id = db.Column(db.Integer, db.ForeignKey('invigilators.invigilator_id', ondelete='CASCADE'), nullable=False)
    role = db.Column(db.String(50), default='invigilator')
    __table_args__ = (db.UniqueConstraint('exam_id','room_id','invigilator_id', name='ux_inv_assign'),)

# ---------- Routes (render templates) ----------
@app.route('/')
def index():
    return render_template('dashboard.html', page='dashboard', title='Dashboard')

@app.route('/exams')            # renders template only
def exams_page():
    return render_template('exams.html', page='exams', title='Exams')

@app.route('/rooms')
def rooms_page():
    return render_template('rooms.html', page='rooms', title='Rooms')

@app.route('/students')
def students_page():
    return render_template('students.html', page='students', title='Students')

@app.route('/invigilators')
def invigilators_page():
    return render_template('invigilators.html', page='invigilators', title='Invigilators')

@app.route('/assign')
def assign_page():
    return render_template('assign.html', page='assign', title='Assign Seats')

# ---------- API endpoints (CRUD) ----------
@app.route('/api/state')
def api_state():
    """Return entire state (for demo UI)."""
    # careful with big data; this is fine for demo/test
    courses = [c.__dict__ for c in Course.query.all()]
    for c in courses: c.pop('_sa_instance_state', None)
    exams = [e.__dict__ for e in Exam.query.order_by(Exam.exam_date).all()]
    for e in exams:
        e.pop('_sa_instance_state', None)
        # convert date/time objects to strings so jsonify can serialize them
        if 'exam_date' in e and e['exam_date'] is not None:
            e['exam_date'] = str(e['exam_date'])
        if 'start_time' in e and e['start_time'] is not None:
            e['start_time'] = str(e['start_time'])
        if 'end_time' in e and e['end_time'] is not None:
            e['end_time'] = str(e['end_time'])
    rooms = [r.__dict__ for r in Room.query.all()]
    for r in rooms: r.pop('_sa_instance_state', None)
    students = [s.__dict__ for s in Student.query.all()]
    for s in students: s.pop('_sa_instance_state', None)
    invs = [i.__dict__ for i in Invigilator.query.all()]
    for i in invs: i.pop('_sa_instance_state', None)

    # load registrations into dict exam_id -> list(student_id)
    regs = {}
    for se in StudentExam.query.all():
        regs.setdefault(str(se.exam_id), []).append(se.student_id)

    # use safe serializer to ensure any remaining python objects are JSON-serializable
    data = {
        'courses': courses,
        'exams': exams,
        'rooms': rooms,
        'students': students,
        'invigilators': invs,
        'regs': regs,
    }
    return safe_jsonify(data)

# Create room
@app.route('/api/rooms', methods=['POST'])
def api_add_room():
    data = request.get_json() or {}
    rc = data.get('room_code')
    cap = data.get('capacity')
    room = Room(room_code=rc, capacity=int(cap), building=data.get('building'), floor=data.get('floor'))
    db.session.add(room)
    db.session.commit()
    return jsonify({'room_id': room.room_id, 'room_code': room.room_code, 'capacity': room.capacity}), 201

# Create exam
@app.route('/api/exams', methods=['POST'])
def api_add_exam():
    data = request.get_json() or {}
    course_code = data.get('course_code')
    if not Course.query.get(course_code):
        # create lightweight course row if not exists (optional)
        c = Course(course_code=course_code, course_title=data.get('course_title', course_code))
        db.session.add(c)
        db.session.flush()
    exam = Exam(
        course_code=course_code,
        course_title=data.get('course_title', course_code),
        exam_date=datetime.strptime(data.get('exam_date'), "%Y-%m-%d").date(),
        start_time=datetime.strptime(data.get('start_time'), "%H:%M").time(),
        end_time=datetime.strptime(data.get('end_time'), "%H:%M").time(),
        venue_note=data.get('venue_note')
    )
    db.session.add(exam)
    db.session.commit()
    return jsonify({'exam_id': exam.exam_id}), 200

# Add student
@app.route('/api/students', methods=['POST'])
def api_add_student():
    data = request.get_json() or {}
    stud = Student(roll_no=data.get('roll'), name=data.get('name'), department=data.get('dept'), year=data.get('year'))
    db.session.add(stud)
    db.session.commit()
    return jsonify({'student_id': stud.student_id}), 201

# Delete student
@app.route('/api/students/<int:sid>', methods=['DELETE'])
def api_del_student(sid):
    s = Student.query.get_or_404(sid)
    db.session.delete(s)
    db.session.commit()
    return '', 204

# Add invigilator
@app.route('/api/invigilators', methods=['POST'])
def api_add_invigilator():
    data = request.get_json() or {}
    inv = Invigilator(name=data.get('name'), employee_no=data.get('emp'), dept=data.get('dept'))
    db.session.add(inv)
    db.session.commit()
    return jsonify({'invigilator_id': inv.invigilator_id}), 201

# Delete invigilator
@app.route('/api/invigilators/<int:iid>', methods=['DELETE'])
def api_del_invigilator(iid):
    inv = Invigilator.query.get_or_404(iid)
    db.session.delete(inv)
    db.session.commit()
    return '', 204

# Register all students into an exam (demo convenience)
@app.route('/api/register_all', methods=['POST'])
def api_register_all():
    data = request.get_json() or {}
    exam_id = data.get('exam_id')
    if not exam_id:
        return jsonify({'error': 'exam_id required'}), 400
    all_students = Student.query.all()
    for s in all_students:
        # ignore duplicates
        exists = StudentExam.query.filter_by(student_id=s.student_id, exam_id=exam_id).first()
        if not exists:
            db.session.add(StudentExam(student_id=s.student_id, exam_id=exam_id, status='registered'))
    db.session.commit()
    return jsonify({'registered': len(all_students)}), 200

# Assign seats server-side (greedy)
@app.route('/api/assign/<int:exam_id>', methods=['POST'])
def api_assign_seats(exam_id):
    # load registered student ids
    regs = StudentExam.query.filter_by(exam_id=exam_id).all()
    student_ids = [r.student_id for r in regs]
    if not student_ids:
        return jsonify({'error': 'no registrations for exam'}), 400

    # clear existing seat assignments for this exam
    SeatAssignment.query.filter_by(exam_id=exam_id).delete()
    db.session.commit()

    rooms = Room.query.order_by(Room.capacity.desc()).all()
    assignments = {}
    idx = 0
    total = len(student_ids)
    for r in rooms:
        assignments[r.room_id] = []
        for seat_no in range(1, r.capacity + 1):
            if idx >= total:
                break
            sid = student_ids[idx]
            stud = Student.query.get(sid)
            sa = SeatAssignment(exam_id=exam_id, room_id=r.room_id, student_id=sid, seat_number=seat_no)
            db.session.add(sa)
            assignments[r.room_id].append({'seat': seat_no, 'student': {'student_id': stud.student_id, 'roll_no': stud.roll_no, 'name': stud.name}})
            idx += 1
        if idx >= total:
            break
    db.session.commit()

    if idx < total:
        return jsonify({'warning': f'Not enough seats. {total-idx} unseated', 'assignments': assignments}), 200
    return jsonify({'assignments': assignments}), 200

# Clear seat assignments
@app.route('/api/clear_assign', methods=['POST'])
def api_clear_assign():
    SeatAssignment.query.delete()
    db.session.commit()
    return jsonify({'status': 'ok'})

# Export DB snapshot as JSON (demo)
@app.route('/api/export')
def api_export():
    # dump basic data
    out = {
        'courses':[{'course_code':c.course_code,'course_title':c.course_title,'credits':c.credits} for c in Course.query.all()],
        'exams':[{'exam_id':e.exam_id,'course_code':e.course_code,'exam_date':str(e.exam_date)} for e in Exam.query.all()],
        'rooms':[{'room_id':r.room_id,'room_code':r.room_code,'capacity':r.capacity} for r in Room.query.all()],
        'students':[{'student_id':s.student_id,'roll_no':s.roll_no,'name':s.name} for s in Student.query.all()],
    }
    b = BytesIO()
    b.write(json.dumps(out, indent=2).encode('utf-8'))
    b.seek(0)
    return send_file(b, mimetype='application/json', as_attachment=True, download_name='examseater-db.json')

# ---------- Run ----------
if __name__ == '__main__':
    print("Using DATABASE_URI:", DATABASE_URI)
    app.run(debug=True)
