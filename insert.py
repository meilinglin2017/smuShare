from sqlalchemy import create_engine  
from sqlalchemy import Column, String  
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import sessionmaker

db_string = "postgres://admin:donotusethispassword@aws-us-east-1-portal.19.dblayer.com:15813/compose"

db = create_engine(db_string)  
base = declarative_base()