from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.debug = True

# Change values when db is created
username = ''
password = ''
host = ''
port = 5432
dbName = ''
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
def register():
    return render_template('login.html')

@app.route("/home/")
def home():
    return render_template('main.html')

@app.route("/detail/")
def register():
    return render_template('detail.html')

@app.route("/download/")
def register():
    return render_template('download.html')

if __name__ == '__main__':
    app.run(debug=True)