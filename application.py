from flask import Flask, jsonify, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from pprint import pprint
import os

app = Flask(__name__)
app.debug = True

# Change line for file saves
allowed = {'txt', 'pdf', 'doc', 'zip'}
app.config["IMAGE_UPLOADS"] = "/mnt/c/users/deken/desktop/GitHubRepositories/smuShare/static/upload"
#app.config["HOST"] = "0.0.0.0"
#app.config["PORT"] = "5000"

# Change values when RDS db is created. Rather, RDS is created,
# but test on local drive first. Connecting to EC2, S3, RDS
# we will do it later with the parameters.
username = 'smtusername'
password = 'smtpassword'
host = 'localhost' #'smt-testdb.cwbn7tc9bebt.ap-southeast-1.rds.amazonaws.com'
port = 5432
dbName = 'smusharedb' #'postgres' - default name given by RDS is postgres

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{}:{}@{}:{}/{}'.format(username, password, host, port, dbName)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

### Import models ###
from models import Material, Review

### Common Variables used in multiple pages ###
base_url = "http://localhost:5000/"
common_var = {
    "base" : base_url,
    "home" : base_url + "home"
}

### Definitions without API Routes ###
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed

### API Routes ###
# User Methods
@app.route("/searchFile/", methods = ['GET'])
def searchFile():
    search_key = ['file_name', 'prof_name', 'course_name', 'course_code']
    file_name = request.args.get('file_name', False)
    prof_name = request.args.get('prof_name', False)
    course_name = request.args.get('course_name', False)
    course_code = request.args.get('course_code', False)
    

@app.route("/getReviews/", methods = ['GET'])
def getReviews():
    pass

# We do not need to have an uploadFile already because
# we have /upload/ that receive both POST and GET. That is
# done on the front-end and back-end instead of 
# back-end only.

#@app.route("/uploadFile/", methods = ['POST'])
#def uploadFile():
#    pass

@app.route("/uploadReview/", methods = ['POST'])
def uploadReview():
    pass

# Developer Methods
@app.route("/updateFile/", methods = ['PUT'])
def updateFile():
    pass

@app.route("/deleteFile/", methods = ['DELETE'])
def deleteFile():
    pass

@app.route("/deleteReview/", methods = ['DELETE'])
def deleteReview():
    pass

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

    return render_template('upload.html', common = common_var)

@app.route("/download/")
def download():
    return render_template('download.html', common = common_var)

if __name__ == '__main__':
    app.run(debug=True)