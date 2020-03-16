from flask import Flask, jsonify, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os



app = Flask(__name__)
app.debug = True

# Change line for file saves
app.config["IMAGE_UPLOADS"] = "/mnt/c/users/deken/desktop/GitHub\ Repositories/smuShare/static/upload"

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

### API Routes ###
# User Methods
@app.route("/searchFile/", methods = ['GET'])
def searchFile():
    pass

@app.route("/getReviews/", methods = ['GET'])
def getReviews():
    pass

@app.route("/uploadFile/", methods = ['POST'])
def uploadFile():
    pass

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
    return render_template('welcome.html')

@app.route("/register/")
def register():
    return render_template('register.html')

@app.route("/login/")
def login():
    return render_template('login.html')

@app.route("/home/")
def home():
    return render_template('main.html')

@app.route("/detail/")
def detail():
    return render_template('detail.html')

@app.route("/upload/", methods=["GET","POST"])
def upload():
    if request.method == "POST":
        if request.files:
            image = request.files["image"]
            print(image)
            return redirect(request.url)
    return render_template('upload.html')

@app.route("/download/")
def download():
    return render_template('download.html')

if __name__ == '__main__':
    app.run(debug=True)