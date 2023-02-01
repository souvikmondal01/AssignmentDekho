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
            
        # db.drop_all()
        db.create_all()
        db.session.commit()
        return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
