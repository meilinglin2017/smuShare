from flask import Flask, jsonify, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from pprint import pprint
import os
from s3bucket import s3_upload_file, s3_get_link
import requests
import psycopg2

app = Flask(__name__)
app.debug = True

# Change line for file saves
allowed = {'txt', 'pdf', 'doc', 'zip'}
app.config["IMAGE_UPLOADS"] = "" ##"/mnt/c/users/deken/desktop/GitHubRepositories/smuShare/static/upload" ## This is used to slot in S3 bucket.
app.config["HOST"] = "0.0.0.0"
app.config["PORT"] = "5000"

# Change values when RDS db is created. Rather, RDS is created,
# but test on local drive first. Connecting to EC2, S3, RDS
# we will do it later with the parameters.
username = 'smtusername'
password = 'smtpassword'
host = 'smushare.cz4bsejequqa.us-west-2.rds.amazonaws.com' #'aa77fccri7bpdt.cz4bsejequqa.us-west-2.rds.amazonaws.com' 'aa77fccri7bpdt.cz4bsejequqa.us-west-2.rds.amazonaws.com'
port = 5432
dbName = 'postgres' #'postgres' - default name given by RDS is postgres
driver = 'postgresql+psycopg2://'

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://{}:{}@{}:{}/{}'.format(username, password, host, port, dbName)
# app.config['SQLALCHEMY_DATABASE_URI'] = driver + os.environ[username] + ':' + os.environ[password]  + '@' + os.environ[host] + ':' + os.environ[port]  + '/' + os.environ[dbName]
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

### Import models ###
from models import Material, Review, User, Course, Prof

### Common Variables used in multiple pages ###
base_url = "http://localhost:5000/"
# base_url = "http://smushare.ml/"
common_var = {
    "base" : base_url,
    "home" : base_url + "home"
}


### Commit ONCE for testing

# sample_user = User(
#     username = "ilovesmt203",
#     password = "abcdefgh",
#     email = "smtisfun@smu.edu.sg"
# )

# db.session.add(sample_user)
# db.session.commit()
# db.session.refresh(sample_user)

# sample_course_code = Course(
#     course_code = "SMT203",
#     course_name = "Smart City System and Management"
# )

# db.session.add(sample_course_code)
# db.session.commit()
# db.session.refresh(sample_course_code)

# sample_prof = Prof(
#     prof_email = "hxtan@smu.edu.sg",
#     prof_name = "Tan Hwee Xian"
# )

# db.session.add(sample_prof)
# db.session.commit()
# db.session.refresh(sample_prof)


# sample_material = Material(
#     course_code = "SMT203",
#     course_name = "Smart City System and Management",
#     prof_name = "Tan Hwee Xian",
#     course_term = "AY19/20S2",
#     file_name = "Juicy Cheatsheet",
#     file_path = "sample_path",
#     rating_avg = 5.0,
#     user_id = sample_user.user_id,
#     course_id = sample_course_code.course_id,
#     prof_id = sample_prof.prof_id,
#     reviews = []
# )


# db.session.add(sample_course_code)
# db.session.commit()
# db.session.add(sample_prof)
# db.session.commit()
# db.session.add(sample_material)
# db.session.commit()

### Definitions without API Routes ###
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed

### API Routes ###
# User Methods
@app.route("/searchFile/", methods = ['GET'])
def searchFile():
    conditions = {}
    attributes = ['file_name', 'prof_name', 'course_name', 'course_code']
    for attr in attributes:
        if attr in request.args:
            conditions[attr] = request.args.get(attr)
    
    materials = Material.query.filter_by(conditions)
    return [m.serialize() for m in materials], 200
    

@app.route("/getReviews/", methods = ['GET'])
def getReviews():
    if 'file_id' in request.args:
        id = int(request.args.get('file_id'))
        review = Review.query.filter_by(file_id = id).first()
        return jsonify(review.serialize()), 200
    
    reviews = Review.query.all()
    return jsonify([r.serialize() for r in reviews]), 200

# We do not need to have an uploadFile already because
# we have /upload/ that receive both POST and GET. That is
# done on the front-end and back-end instead of 
# back-end only.

# In case need to reference for /upload/
@app.route("/uploadFile/", methods = ['POST'])
def uploadFile():
    try:
        file_name = request.json['file_name']
        prof_name = request.json['prof_name']
        course_code = request.json['course_code']
        course_name = request.json['course_name']
        course_term = request.json['course_term']
        input_file = request.json['input_file']

        user_id = request.json['user_id']
        course_id = request.json['course_id']
        prof_id = request.json['prof_id']

        new_file = Material(
            course_code = course_code,
            course_name = course_name,
            prof_name = prof_name,
            course_term = course_term,
            file_name = file_name,
            file_path = "thisisatempurl",
            user_id = user_id,
            course_id = course_id,
            prof_id = prof_id)
        db.session.add(new_file)
        db.session.commit()
        db.session.refresh(new_file)

        # Save file to web directory for boto3 to read
        s3_filename = new_file.id + "_" + file_name
        input_file.save(s3_filename)
        s3_file = open(s3_filename, "rb")
        s3_upload_file(s3_filename, s3_file)
        new_file.file_path = s3_get_link(s3_filename)
        db.session.commit()

        # Remove file from web directory
        s3_file.close()
        os.remove(s3_filename)

        return jsonify("{} was created".format(new_file)), 201
    except KeyError:
        # Not all params are filled
        return jsonify('Not all required parameters are filled'), 400
    except Exception as e:
        return str(e)
            
def getRatingAvg(reviews):
    total = 0
    for review in reviews:
        total += review['rating']
    return total/len(reviews)

@app.route("/uploadReview/", methods = ['POST'])
def uploadReview():
    empty_fields = ', '.join([field for field in ['file_id', 'review', 'rating'] if field not in request.json])
    if empty_fields != '':
        return jsonify('Parameter(s) {} not found'.format(empty_fields)), 400

    file_id = request.json['file_id']
    review = request.json['review']
    rating = request.json['rating']

    try:
        filez = Material.query.filter_by(id=file_id).first()
        if filez is None:
            return ('{} does not exist'.format(filez))
        new_review = Review(rating=rating, review=review, file_id=file_id)
        db.session.add(new_review)
        db.session.commit()

        return jsonify('{} score and the review was created for file ID {}'.format(rating,file_id)), 201
    except Exception as e:
        return (str(e)) 

# Developer Methods
@app.route("/updateFile/", methods = ['PUT'])
def updateFile():
    if 'file_id' not in request.json:
        return jsonify('file_id not entered')
    
    file_id = request.json['file_id']
    target_file = Material.query.get(file_id)
    if target_file is None:
        return jsonify("File id {} does not exist".format(file_id)), 404
    
    if 'file_name' in request.json:
        target_file.file_name = request.json['file_name']
    if 'prof_name' in request.json:
        target_file.prof_name = request.json['prof_name']
    if 'course_code' in request.json:
        target_file.course_code = request.json['course_code']
    if 'course_term' in request.json:
        target_file.course_term = request.json['course_term']
    db.session.commit()
    return jsonify(target_file.serialize()), 200

@app.route("/deleteFile/", methods = ['DELETE'])
def deleteFile():
    if 'file_id' not in request.json:
        return jsonify('file_id not entered')
    
    file_id = request.json['file_id']
    material = Material.query.get(file_id)
    db.session.delete(material)
    db.session.commit()
    return jsonify("File id {} is deleted".format(file_id)), 200

@app.route("/deleteReview/", methods = ['DELETE'])
def deleteReview():
    # file_id = request.json['file_id'] # I think dont need file_id
    if 'review_id' not in request.json:
        return jsonify("Parameter(s) review_id is empty")
    review_id = request.json['review_id']
    review = Review.query.get(review_id)
    db.session.delete(review)
    db.session.commit()
    return jsonify('Review id {} is deleted'.format(review_id)), 200

### Middleman Routes ###
"""
These routes will call the api and redirect to frontend
"""
@app.route("/authenticate/<form_action>/", methods = ['POST'])
def check_user(form_action):
    error_msg = []
    if form_action == 'register':
        prev_html = 'register.html'
        auth_url = common_var['base'] + "authenticate/register/"
        if set(('email', 'username', 'password', 'password2')) > set(request.form):
            error_msg.append("Some fields are empty")
            return render_template('register.html', common = common_var, auth_url = auth_url, errors = error_msg)

        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        password2 = request.form['password2']

        user = User.query.filter_by(username = username).first()
        if user is not None:
            error_msg.append("Username already exist")
        if password != password2:
            error_msg.append("Passwords does not match")
        
        # No error add user to database
        if error_msg == []:
            try:
                new_user = User(username = username, password = password, email = email)
                db.session.add(new_user)
                db.session.commit()
            except Exception as e:
                return str(e)
    
    if form_action == 'login':
        prev_html = 'login.html'
        auth_url = common_var['base'] + "authenticate/login/"
        if set(('username', 'password')) > set(request.form):
            error_msg.append("Some fields are empty")
            return render_template('login.html', common = common_var, auth_url = auth_url, errors = error_msg)
        
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username = username).first()
        if '@' in username:
            user = User.query.filter_by(email = username).first()
        
        if user is None:
            error_msg.append("Username/Email not registered yet")
        elif password != user.password:
            error_msg.append("Password is incorrect")

        # No error so save user to session
        if error_msg == []:
            common_var['session_user'] = user
            
    if error_msg != []:
        return render_template(prev_html, common = common_var, auth_url = auth_url, errors = error_msg)
    return redirect(common_var['home'])

@app.route("/uploading/", methods = ['POST'])
def uploading():
    profList = [p.prof_name for p in Prof.query.all()]
    courseDict = {}
    courses = Course.query.all()
    for course in courses:
        courseDict[course.course_code] = course.course_name
    
    error_msg = []
    if 'input_file' not in request.files:
        error_msg.append("No file is selected")

    if set(('prof_name', 'course_code', 'course_name', 'course_term',
            'input_file', 'user_id', 'course_id', 'prof_id')) > set(request.json):
        error_msg.append("Some fields are empty")
        return render_template('upload.html', common = common_var, profList = profList, courseDict = courseDict, errors = error_msg)
    
    input_file = request.files['input_file']
    if input_file.filename == '':
        error_msg.append("No file is selected")
        return render_template('upload.html', common = common_var, profList = profList, courseDict = courseDict, errors = error_msg)

    # file_name = request.json['file_name']
    # course_term = request.json['course_term']

    # user_id = request.json['user_id']
    # course_id = request.json['course_id']
    # prof_id = request.json['prof_id']

    params = request.form
    # File details
    params['input_file'] = input_file
    params['file_name'] = input_file.filename

    # Prof and Course details
    prof_name = request.form['prof_name']
    course_code = request.form['course_code']
    course_name = request.form['course_name']

    prof = Prof.query.filter_by(prof_name = prof_name)
    course = Course.query.filter_by(course_code = course_code)

    if prof is None:
        new_prof = Prof(prof_name = prof_name)
        db.session.add(new_prof)
        db.session.commit()
        db.session.refresh(new_prof)
        prof = new_prof
    if course is None:
        new_course = Course(course_code = course_code, course_name = course_name)
        db.session.add(new_course)
        db.session.commit()
        db.session.refresh(new_course)
        course = new_course
    if prof not in course.professors:
        course.professors.append(prof)

    params['prof_id'] = prof.prof_id
    params['course_id'] = course.course_id

    req = requests.post(common_var['base'] + 'uploadFile/', params = params)
    return req.text

### FrontEnd Routes ###
@app.route("/")
def welcome():
    return render_template('welcome.html', common = common_var)

@app.route("/register/")
def register():
    auth_url = common_var['base'] + "authenticate/register/"
    return render_template('register.html', common = common_var, auth_url = auth_url)

@app.route("/login/")
def login():
    auth_url = common_var['base'] + "authenticate/login/"
    return render_template('login.html', common = common_var, auth_url = auth_url)

@app.route("/home/")
def home():
    materials = [m.serialize() for m in Material.query.all()]
    return render_template('main.html', common = common_var, materials = materials)

@app.route("/detail/<int:file_id>/")
def detail(file_id):
    material = Material.query.get(file_id)
    if material is None:
        return render_template('main.html', common = common_var)
    return render_template('detail.html', common = common_var, material = material.serialize())

@app.route("/upload/")
def upload_page():
    profList = [p.prof_name for p in Prof.query.all()]
    courseDict = {}
    courses = Course.query.all()
    for course in courses:
        courseDict[course.course_code] = course.course_name

    return render_template('upload.html', common = common_var, profList = profList, courseDict = courseDict)

@app.route("/download/<int:file_id>/")
def download_page(file_id):
    material = Material.query.get(file_id)
    if material is None:
        return render_template('main.html', common = common_var)
    return render_template('download.html', common = common_var, material = material.serialize())

if __name__ == '__main__':
    app.run(debug=True)