from flask import Flask, jsonify, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from pprint import pprint
from application import app,db
import os

app = Flask(__name__)
app.debug = True

username = 'smtusername'
password = 'smtpassword'
host = 'aa77fccri7bpdt.cz4bsejequqa.us-west-2.rds.amazonaws.com' #'aa77fccri7bpdt.cz4bsejequqa.us-west-2.rds.amazonaws.com'
port = 5432
dbName = 'postgres' #'postgres' - default name given by RDS is postgres

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{}:{}@{}:{}/{}'.format(username, password, host, port, dbName)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from models import Material, Review, User, Course, Prof

sample_material = Material(
    course_code = "SMT203",
    course_name = "Smart City System and Management",
    prof_name = "Tan Hwee Xian",
    course_term = "AY19/20S2",
    file_name = "Juicy Cheatsheet",
    file_path = "sample_path",
    rating_avg = 5.0,
    reviews = []
)

sample_course_code = Course(
    course_code = "SMT203",
    course_name = "Smart City System and Management"
)

sample_prof = Prof(
    prof_email = "hxtan@smu.edu.sg",
    prof_name = "Tan Hwee Xian"
)

db.session.add(sample_material)
db.session.add(sample_course_code)
db.session.add(sample_prof)
db.session.commit()