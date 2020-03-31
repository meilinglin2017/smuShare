from flask import Flask, jsonify, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from pprint import pprint
import os
from s3bucket import s3_upload_file, s3_download_file

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
host = 'aa77fccri7bpdt.cz4bsejequqa.us-west-2.rds.amazonaws.com' #'aa77fccri7bpdt.cz4bsejequqa.us-west-2.rds.amazonaws.com'
port = 5432
dbName = 'postgres' #'postgres' - default name given by RDS is postgres

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{}:{}@{}:{}/{}'.format(username, password, host, port, dbName)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

### Import models ###
from models import Material, Review, User, Course, Prof

### Common Variables used in multiple pages ###
# base_url = "http://localhost:5000/"
base_url = "http://eb-docker-flask.eba-v2wjze7x.us-west-2.elasticbeanstalk.com/"
common_var = {
    "base" : base_url,
    "home" : base_url + "home"
}


### Commit ONCE for testing

sample_user = User(
    username = "ilovesmt203",
    password = "abcdefgh"
)

db.session.add(sample_user)
db.session.commit()
db.session.refresh(sample_user)

sample_course_code = Course(
    course_code = "SMT203",
    course_name = "Smart City System and Management"
)

db.session.add(sample_course_code)
db.session.commit()
db.session.refresh(sample_course_code)

sample_prof = Prof(
    prof_email = "hxtan@smu.edu.sg",
    prof_name = "Tan Hwee Xian"
)

db.session.add(sample_prof)
db.session.commit()
db.session.refresh(sample_prof)


sample_material = Material(
    course_code = "SMT203",
    course_name = "Smart City System and Management",
    prof_name = "Tan Hwee Xian",
    course_term = "AY19/20S2",
    file_name = "Juicy Cheatsheet",
    file_path = "sample_path",
    rating_avg = 5.0,
    user_id = sample_user.user_id,
    course_id = sample_course_code.course_id,
    prof_id = sample_prof.prof_id,
    reviews = []
)


db.session.add(sample_course_code)
db.session.commit()
db.session.add(sample_prof)
db.session.commit()
db.session.add(sample_material)
db.session.commit()

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
    
    material = Material.query.filter_by(conditions).first()
    return material.serialize()
    

@app.route("/getReviews/", methods = ['GET'])
def getReviews():
    if 'file_id' in request.args:
        id = int(request.args.get('file_id'))
        review = Review.query.filter_by(file_id = id).first()
        return jsonify(review.serialize())
    
    reviews = Review.query.all()
    return jsonify([r.serialize() for r in reviews])

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

        reviews = []
        rating_avg = 0
        if 'reviews' in request.json:
            reviews = request.json['reviews']
            rating_avg = getRatingAvg(reviews)

        new_file = Material(
            course_code = course_code,
            course_name = course_name,
            prof_name = prof_name,
            course_term = course_term,
            file_name = file_name,
            file_path = "123",
            rating_avg = rating_avg,
            reviews = reviews,)
        db.session.add(new_file)
        db.session.commit()

        for review in reviews:
            new_review = Review(comments = review, file_id = new_file.file_id, review = "Hello")
            db.session.add(new_review)
            db.session.commit()

        return jsonify("{} was created".format(new_file))
    except KeyError:
        # Not all params are filled
        return jsonify({
            'status' : 405,
            'message' : 'Not all required parameters are filled'
        })
    except Exception as e:
        return str(e)
            

def getRatingAvg(reviews):
    total = 0
    for review in reviews:
        total += review['rating']
    return total/len(reviews)

#@app.route("/uploadFile/", methods = ['POST'])
#def uploadFile():
#    pass

@app.route("/uploadReview/", methods = ['POST'])
def uploadReview():
    empty_fields = ', '.join([field for field in ['file_id', 'review', 'rating'] if field not in request.json])
    if empty_fields != '':
        return jsonify('Parameter(s) {} not found'.format(empty_fields))

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

        return jsonify('{} score and the review was created for file ID {}'.format(rating,file_id))
    except Exception as e:
        return (str(e)) 

# Developer Methods
@app.route("/updateFile/", methods = ['PUT'])
def updateFile():
    pass

@app.route("/deleteFile/", methods = ['DELETE'])
def deleteFile():
    pass

@app.route("/deleteReview/", methods = ['DELETE'])
def deleteReview():
    # file_id = request.json['file_id'] # I think dont need file_id
    if 'review_id' not in request.json:
        return jsonify("Parameter(s) review_id is empty")
    review_id = request.json['review_id']
    review = Review.query.get(review_id)
    db.session.delete(review)
    db.session.commit()
    return jsonify('Review id {} is deleted'.format(review_id))

### FrontEnd Routes ###
@app.route("/")
def welcome():
    return render_template('welcome.html', common = common_var)

@app.route("/register/")
def register():
    return render_template('register.html', common = common_var)

@app.route("/login/")
def login():
    return render_template('login.html', common = common_var)

@app.route("/home/")
def home():
    return render_template('main.html', common = common_var)

@app.route("/detail/")
def detail():
    return render_template('detail.html', common = common_var)

@app.route("/upload/", methods=["GET","POST"])
def upload():
    if request.method == "POST":
        if request.files:

            ## Debug method - check Ubuntu
            print("below is locals")
            file_name = request.form['file_name']
            print(file_name)
            pprint(locals())
            print("above is locals")

            ## Upload of file
            image = request.files["image"]
            image.save(os.path.join(app.config["IMAGE_UPLOADS"], image.filename))
            
            ## append to Material Database
            try:
                new_material = Material(file_name=file_name, course_code='SMT203',course_name='Smart Cities', prof_name='Hwee Xian', course_term='AY19/20S2', rating_avg=4.5, file_path='zxc', reviews=None)
                db.session.add(new_material)
                db.session.commit()
                return jsonify('{} was created'.format(new_material))
            except Exception as e:
                return (str(e))

    profList = [p.prof_name for p in Prof.query.all()]
    courseDict = {}
    courses = Course.query.all()
    for course in courses:
        courseDict[course.course_code] = course.course_name

    return render_template('upload-new.html', common = common_var, profList = profList, courseDict = courseDict)

@app.route("/download/")
def download():
    return render_template('download.html', common = common_var)

if __name__ == '__main__':
    app.run(debug=True)