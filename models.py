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

    reviews = db.relationship('Review', back_populates = 'material', uselist = True, cascade = 'all, delete-orphan', lazy = True)

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

    material = db.relationship('Material', back_populates = 'reviews')

    def __init__(self, review_ID, rating, review, review_date):
        self.review_ID = review_ID
        self.rating = rating
        self.review = review
        self.review_date = review_date

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
#class User(db.Model):
#    __tablename__ = 'user_info'

# Course Info db table
#class Course(db.Model):
#    __tablename__ = 'course_info'

# Prof Info db table
#class Prof(db.Model):
#    __tablename__ = 'prof_info'