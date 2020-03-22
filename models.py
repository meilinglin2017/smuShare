import datetime

from application import db

# File Info db table (Cannot use File cause is existing python object already)
class Material(db.Model):
    __tablename__ = 'file_info'

    file_ID = db.Column(db.Integer, primary_key = True)
    course_code = db.Column(db.String(10), nullable = False)
    course_name = db.Column(db.String(200), nullable = False)
    prof_name = db.Column(db.String(200), nullable = False)
    course_term = db.Column(db.String(20), nullable = False)
    file_name = db.Column(db.String(200), nullable = False)
    rating_avg = db.Column(db.Float, nullable = False)
    file_path = db.Column(db.String(200), nullable = False)
    upload_date = db.Column(db.DateTime, default = datetime.datetime.utcnow)

    # One file may have multiple reviews, but it belongs to only one prof, one course and one user.
    file_reviews = db.relationship('Review', back_populates = 'materials', uselist = True, cascade = 'all, delete-orphan', lazy = True)
    user_upload = db.relationship('User', back_populates= 'uploads', lazy = True)
    course_info = db.relationship('Course', back_populates = 'courses', lazy = True)
    professor_notes = db.relationship('Prof', back_populates= 'professors', lazy = True)

    def __init__(self, course_code, course_name, prof_name, course_term, file_name, rating_avg, file_path, reviews = None):
        self.course_code = course_code
        self.course_name = course_name
        self.prof_name = prof_name
        self.course_term = course_term
        self.file_name = file_name
        self.rating_avg = rating_avg
        self.file_path = file_path
        self.reviews = [] if reviews is None else reviews

    def __repr__(self):
        return "{}_{}".format(self.file_name, self.file_ID)
    
    def serialize(self):
        return {
            'file_ID' : self.file_ID,
            'course_code' : self.course_code,
            'course_name' : self.course_name,
            'prof_name' : self.prof_name,
            'course_term' : self.course_term,
            'file_name' : self.file_name,
            'rating_avg' : self.rating_avg,
            'file_path' : self.file_path,
            'upload_date' : self.upload_date,
            'reviews' : [{
                'review_ID' : r.rating_ID,
                'rating' : r.rating,
                'review' : r.review,
                'review_date' : r.review_date
            } for r in self.reviews]
        }

## Commenting off db tables below as init without complete table causes fatal error.

# Review Info db table
class Review(db.Model):
    __tablename__ = 'review_info'

    review_ID = db.Column(db.Integer, primary_key = True)
    rating = db.Column(db.Float, nullable = False)
    review = db.Column(db.String(2048), nullable = False)
    review_date = db.Column(db.DateTime, default = datetime.datetime.utcnow)
    file_id = db.Column(db.Integer, db.ForeignKey("file_info.file_ID"), nullable = False)

    materials = db.relationship('Material', back_populates = 'reviews')
    users = db.relationship('User', back_populates = 'user_reviews')

    def __init__(self, rating, review, file_id):
        self.rating = rating
        self.review = review
        self.file_id = file_id

    def __repr__(self):
        return "<review_id: {}>".format(self.review_ID)

    def serialize(self):
        return {
            'review_ID' : self.review_ID,
            'rating' : self.rating,
            'review' : self.review,
            'review_date' : self.review_date
        }
    


# User Info db table
class User(db.Model):
    __tablename__ = 'user_info'

    user_id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), nullable = False)
    #Lets assume this password is already hashed...
    password = db.Column(db.String(16), nullable = False)

    reviews = db.relationship('Review', back_populates = 'users', uselist = True, lazy = True)
    uploads = db.relationship('Material', back_populates = 'user_upload', uselist = True, lazy = True)

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.reviews = []
        self.uploads = []
    
    def __repr__(self):
        return "{} is created".format(self.username)
    
    def serialize(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'password': self.password,
            'reviews': [r.review for r in self.reviews],
            'uploads': [f.upload for f in self.uploads]
        }


# Course Info db table
class Course(db.Model):
    __tablename__ = 'course_info'

    course_id = db.Column(db.Integer, primary_key = True)
    course_code = db.Column(db.String(6), nullable = False)
    course_name = db.Column(db.String(80), nullable = False)

    courses = db.relationship('Material', back_populates = 'course_info', uselist = False, lazy = True)
    by_professor = db.relationship('Professor', back_populates = 'course_by', uselist = False, lazy = True)

    def __init__(self, course_code, course_name):
        self.course_code = course_code
        self.course_name = course_name
        self.professors = []

    def __repr__(self):
        return "{} is created".format(self.course_code)
    
    def serialize(self):
        return {
            'course_id': self.course_id,
            'course_code': self.course_code,
            'course_name': self.course_name,
            'professors': [p.name for p in self.professors]
        }

# Prof Info db table
class Prof(db.Model):
    __tablename__ = 'prof_info'

    prof_id = db.Column(db.Integer, primary_key = True)
    prof_email = db.Column(db.String(80), nullable = False)
    prof_name = db.Column(db.String(80), nullable = False)

    professors = db.relationship('Material', back_populates = 'professor_notes', uselist = False, lazy = True)
    course_by = db.relationship('Course', back_populates = 'by_professor', uselist = False, lazy = True)

    def __init__(self, prof_email, prof_name):
        self.prof_email = prof_email
        self.prof_name = prof_name
        self.courses = []

    def __repr__(self):
        return "{} is created".format(self.prof_name)

    def serialize(self):
        return {
            'prof_id' : self.prof_id,
            'prof_email': self.prof_email,
            'prof_name' : self.prof_name,
            'courses' : [c.course for c in self.courses]
        }