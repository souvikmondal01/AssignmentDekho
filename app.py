from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from os import environ
from config import db, SECRET_KEY, AWS_ACCESS_KEY_ID, SECRET_ACCESS_KEY
from dotenv import load_dotenv
from datetime import datetime, date
import pytz
from io import BytesIO
import boto3
import pandas as pd
from models.user import User
from models.assignment import Assignment
from models.shareUser import ShareUser

s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                         aws_secret_access_key=SECRET_ACCESS_KEY, region_name='us-west-2')


def create_app():
    app = Flask(_name_)
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

        # db.drop_all()
        db.create_all()
        db.session.commit()
        return app


if _name_ == '_main_':
    app = create_app()
    app.run(debug=True)
