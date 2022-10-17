from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from operator import itemgetter

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance_api.db'
db=SQLAlchemy(app)
admins=[{'name':'vijay',"password":'1234'}]


class Students(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    studentname=db.Column(db.String(length=60),nullable=False,unique=True)
    rollno=db.Column(db.Integer(),nullable=False,unique=True)


class Attendance(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    rollno=db.Column(db.Integer(),db.ForeignKey('students.rollno'),nullable=False)
    date=db.Column(db.String(10),nullable=False)
    attendance_value=db.Column(db.String(10))


@app.route("/login",methods=["GET","POST"])
def login():
    if request.method == "POST":
        new_name=request.form['name']
        new_pass=request.form['password']
        if(new_name == 'vijay' and new_pass == '1234'):
            return jsonify({'message':"Admin found"}),200
        else:
            return jsonify("Username or password invalid"),401
    else:
        return "invalid",401

@app.route("/hi",methods=["GET","POST"])
def hi():
    return "hi anush"


@app.route("/add_student",methods=["GET","POST"])
def add_student():
    if request.method == "POST":
        stu_name=request.form['student_name']
        stu_rollno=request.form['student_rollno']
        tempval=Students(studentname=stu_name,rollno=stu_rollno)
        try:
            db.session.add(tempval)
            db.session.commit()
            return jsonify({'message':"Student added successfully"}),200
        except exc.IntegrityError:
            db.session.rollback()
            return jsonify({'message':"Rollnumber already exist"})

@app.route("/display_student",methods=["GET"])
def display_student():
    if request.method == "GET":
        student=[]
        query=Students.query.all()
        for i in query:
            student.append({'name':i.studentname,'rollno':i.rollno})
        if len(student)>0:
            return jsonify(student)
        else:
            return jsonify({'message':"No record found"})
    
@app.route("/add_attendance",methods=["POST"])
def add_attendance():
    if request.method == "POST":
        at_temp=[]
        temp=[]
        message=[]
        students_attendance=request.get_json()
        date=datetime.now().strftime("%d-%m-%Y")
        details=Students.query.all()
        at_details=Attendance.query.filter_by(date=date)
        for x in details:
            temp.append(x.rollno)
        for x in at_details:
            at_temp.append(x.rollno)
        for i in students_attendance:
            if i['rollno'] in temp:
                if i['rollno'] not in at_temp:
                    tempval=Attendance(rollno=i['rollno'],date=date,attendance_value=i['value'])
                    db.session.add(tempval)
                    db.session.commit()
                    message.append({'mesage':f"Attendance added for {i['rollno']}"})
                else:
                    message.append({'mesage':f"Attendance already added for {i['rollno']}"})
            else:
                return jsonify({'message':"rollnumber not found"}),400
        if(len(message)>=1):
            return jsonify(message)
        else:
            return jsonify({'message':"no record found"})
        

@app.route("/display_attendance",methods=["GET"])
def display_attendance():
    if request.method == "GET":
        attendance=[]
        attendance_details=Attendance.query.all()
        for i in attendance_details:
            attendance.append({'rollno':i.rollno,'date':i.date,'attendance_value':i.attendance_value})
        if len(attendance)>0:
            new_attendance=sorted(attendance,key=itemgetter('rollno'))
            return jsonify(new_attendance)
        else:
            return jsonify({'message':"No record found"})

@app.route("/display_student_attendance/<int:roll>",methods=["GET"])
def display_student_attendance(roll):
    if request.method == "GET":
        student_attendance=[]
        student_detail=Attendance.query.all()
        print(student_detail)
        for i in student_detail:
            if i.rollno == roll:
                student_attendance.append({'rollno':i.rollno,'date':i.date,'value':i.attendance_value})
        if len(student_attendance)>0:
            return jsonify(student_attendance)
        else:
            return jsonify({'message':"No record found"})


@app.route("/attendance",methods=["GET"])
def show_attendance():
    if request.method == "GET":
        values=[]
        student=Students.query.all()
        for i in student:
            Present_count=0
            Absent_count=0
            temp=Attendance.query.filter_by(rollno=i.rollno).all()
            for j in temp:
                if j.attendance_value == "Present":
                    Present_count+=1
                elif j.attendance_value == "Absent":
                    Absent_count+=1
            values.append({'name':i.studentname,'rollno':i.rollno,'total_days_present':Present_count,'total_days_absent':Absent_count})
        if len(values)>=1:
            return jsonify(values)
        else:
            return jsonify({'message':'no record found'})

@app.route("/delete/<int:roll>",methods=["DELETE"])
def delete(roll):
    if request.method=="DELETE":
        details=Students.query.all()
        for i in details:
            if i.rollno == roll:
                Students.query.filter_by(rollno=roll).delete()
                Attendance.query.filter_by(rollno=roll).delete()
                db.session.commit()
                return jsonify({'message':"student deleted successfully"})
        else:
            return jsonify({'message':"roll number not exist"})

if __name__ == "__main__":
    app.run(debug=True)
