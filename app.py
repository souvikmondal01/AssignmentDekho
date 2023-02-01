from flask import Flask, jsonify, request
from os import environ
from config import db, SECRET_KEY, AWS_ACCESS_KEY_ID, SECRET_ACCESS_KEY
from dotenv import load_dotenv
from datetime import datetime, date
import pytz
import boto3
import pandas as pd
from models.user import User
from models.assignment import Assignment
from models.shareUser import ShareUser

s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                         aws_secret_access_key=SECRET_ACCESS_KEY, region_name='us-west-2')


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = environ.get("DB_URI")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = False
    app.secret_key = SECRET_KEY
    db.init_app(app)
    print("DB Initialized Successfully")

    with app.app_context():
        @app.route("/")
        def index():
            return jsonify({"name": "AssignmentDekho"})

        @app.route("/signup", methods=["POST", "GET"])
        def signup():
            new_user = User(
                name=request.form["name"],
                username=request.form["username"],
                email=request.form["email"],
                password=request.form["password"]
            )
            user = User.query.filter_by(email=new_user.email).first()
            if user:
                return "user already exists"
            else:
                username = User.query.filter_by(
                    username=new_user.username).first()
                if username:
                    return "username already exists"
                else:
                    db.session.add(new_user)
                    db.session.commit()
                    return "user added successfully"

        @app.route("/login", methods=["POST", "GET"],)
        def login():
            email = request.form["email"]
            password = request.form["password"]
            user = User.query.filter_by(email=email).first()
            if user and user.password == password:
                return "login successful"
            elif user and user.password != password:
                return "invalid credentials"
            else:
                return "user does not exist"

        @app.route("/fetch_profile_details", methods=["POST", "GET"])
        def fetch_profile_details():
            email = request.form["email"]
            user = User.query.filter_by(email=email).first()
            if user:
                return jsonify({
                    "id": user.id,
                    "name": user.name,
                    "username": user.username,
                    "email": user.email})
            else:
                return "user does not exist"

        @app.route("/edit_user_details", methods=["POST", "GET"])
        def edit_user_details():
            email = request.form["email"]
            username = request.form["new_username"]
            user = User.query.filter_by(email=email).first()
            if user:
                username = User.query.filter_by(username=username).first()
                if username:
                    return "username already exists"
                else:
                    user.name = request.form["new_name"]
                    user.username = request.form["new_username"]
                    db.session.commit()
                    return "user updated successfully"
            else:
                return "user does not exist"

        @app.route("/delete_user", methods=["POST", "GET"])
        def delete_user():
            email = request.form["email"]
            user = User.query.filter_by(email=email).first()
            if user:
                db.session.delete(user)
                db.session.commit()
                return "user deleted successfully"
            else:
                return "user does not exist"

        @app.route("/upload_assignment", methods=["POST", "GET"])
        def upload_assignment():
            file = request.files["file"]
            doc_filename = file.filename
            s3_client.upload_file(
                Filename=doc_filename,
                Bucket="assignment-dekho-bucket",
                Key=doc_filename,)

            curr_date = str(date.today())
            curr_time = str(datetime.now(pytz.timezone("Asia/Kolkata")))

            email = request.form["email"]
            user = User.query.filter_by(email=email).first()
            if user:
                new_assignment = Assignment(
                    title=request.form["title"],
                    filename=doc_filename,
                    filelink=f"https://assignment-dekho-bucket.s3.us-west-2.amazonaws.com/{doc_filename}",
                    semester=request.form["semester"],
                    upload_date=curr_date,
                    upload_time=curr_time,
                    user_id=user.id
                )
                db.session.add(new_assignment)
                db.session.commit()

                return jsonify(msg="Assignment uploaded successfully")
            else:
                return "user does not exist"

        @app.route("/show_assignment", methods=["POST", "GET"])
        def show_assignment():
            email = request.form["email"]
            user = User.query.filter_by(email=email).first()
            if user:
                assignments = Assignment.query.filter_by(user_id=user.id).all()

                assignment_dict = {
                    "user_id": user.id,
                    "name": user.name,
                    "username": user.username,
                    "email": user.email,
                    "assignments": []
                }
                assignment_data = []

                for assignment in assignments:
                    index = assignments.index(assignment)

                    assignment_data.append({
                        "index": index,
                        "title": assignment.title,
                        "filename": assignment.filename,
                        "filelink": assignment.filelink,
                        "semester": assignment.semester,
                        "upload_date": assignment.upload_date,
                        "upload_time": assignment.upload_time
                    })
                assignment_dict["assignments"] = assignment_data

                return jsonify(assignment_dict)
            else:
                return "user does not exist"

        @app.route("/share_assignment", methods=["POST", "GET"])
        def share_assignment():
            email = request.form["email"]
            assignment_index = int(request.form["assignment_index"])
            friend_email = request.form["friend_email"]
            user = User.query.filter_by(email=email).first()
            if user:
                assignments = Assignment.query.filter_by(user_id=user.id).all()
                assignment = assignments[assignment_index]
                shared_user = ShareUser(
                    email=friend_email,
                    assignment_id=assignment.id,
                )
                db.session.add(shared_user)
                db.session.commit()
                return "Assignment shared successfully to "+friend_email

        @app.route("/show_shared_assignment", methods=["POST", "GET"])
        def show_shared_assignment():
            email = request.form["email"]
            shareUsers = ShareUser.query.filter_by(email=email).all()

            assignment_list = []
            for shareUser in shareUsers:
                sharedAssignmentId = shareUser.assignment_id
                assignments = Assignment.query.all()
                for assignment in assignments:
                    if assignment.id == sharedAssignmentId:
                        index = assignments.index(assignment)

                        assignment_list.append({
                            "index": index,
                            "title": assignment.title,
                            "filename": assignment.filename,
                            "filelink": assignment.filelink,
                            "semester": assignment.semester,
                            "upload_date": assignment.upload_date,
                            "upload_time": assignment.upload_time
                        })

            return assignment_list

        @app.route("/edit_assignments_details", methods=["POST", "GET"])
        def edit_assignments_details():
            email = request.form["email"]
            assignment_index = int(request.form["assignment_index"])
            user = User.query.filter_by(email=email).first()
            if user:
                assignments = Assignment.query.filter_by(user_id=user.id).all()

                assignment = assignments[assignment_index]
                assignment.title = request.form["new_title"]
                assignment.semester = request.form["new_semester"]
                db.session.commit()

                return "Assignment details updated"
            else:
                return "user does not exist"

        @app.route("/delete_assignment", methods=["POST", "GET"])
        def delete_assignment():
            email = request.form["email"]
            assignment_index = int(request.form["assignment_index"])
            user = User.query.filter_by(email=email).first()
            if user:
                assignments = Assignment.query.filter_by(user_id=user.id).all()
                assignment = assignments[assignment_index]
                db.session.delete(assignment)
                db.session.commit()
            else:
                return "user does not exist"

            return "Assignment deleted successfully"

        @app.route("/show_semester_assignment", methods=["POST", "GET"])
        def show_semester_assignment():
            email = request.form["email"]
            semester = request.form["semester"]
            user = User.query.filter_by(email=email).first()
            if user:
                assignments = Assignment.query.filter_by(user_id=user.id).all()
                assignment_list = []
                for assignment in assignments:
                    if assignment.semester == semester:
                        index = assignments.index(assignment)
                        assignment_list.append({
                            "index": index,
                            "title": assignment.title,
                            "filename": assignment.filename,
                            "filelink": assignment.filelink,
                            "semester": assignment.semester,
                            "upload_date": assignment.upload_date,
                            "upload_time": assignment.upload_time
                        })
                return assignment_list

            else:
                return "user does not exist"

        @app.route("/show_assignment_of_date", methods=["POST", "GET"])
        def show_assignment_of_date():
            email = request.form["email"]
            date = request.form["date"]
            user = User.query.filter_by(email=email).first()
            if user:
                assignments = Assignment.query.filter_by(user_id=user.id).all()
                assignment_list = []
                for assignment in assignments:
                    if assignment.upload_date == date:
                        index = assignments.index(assignment)
                        assignment_list.append({
                            "index": index,
                            "title": assignment.title,
                            "filename": assignment.filename,
                            "filelink": assignment.filelink,
                            "semester": assignment.semester,
                            "upload_date": assignment.upload_date,
                            "upload_time": assignment.upload_time
                        })
                return assignment_list

            else:
                return "user does not exist"

        @app.route("/show_assignment_of_daterange", methods=["POST", "GET"])
        def show_assignment_of_daterange():
            email = request.form["email"]
            start_date = request.form["start_date"]
            end_date = request.form["end_date"]
            dates = pd.date_range(start_date, end_date)

            user = User.query.filter_by(email=email).first()
            if user:
                assignments = Assignment.query.filter_by(user_id=user.id).all()
                assignment_list = []
                for assignment in assignments:
                    if assignment.upload_date in dates:
                        index = assignments.index(assignment)
                        assignment_list.append({
                            "index": index,
                            "title": assignment.title,
                            "filename": assignment.filename,
                            "filelink": assignment.filelink,
                            "semester": assignment.semester,
                            "upload_date": assignment.upload_date,
                            "upload_time": assignment.upload_time
                        })
                return assignment_list

            else:
                return "user does not exist"

        # db.drop_all()
        db.create_all()
        db.session.commit()
        return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
