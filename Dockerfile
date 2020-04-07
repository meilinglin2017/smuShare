FROM python:3.6
COPY ./smuShare/requirements.txt
WORKDIR /smuShare
RUN pip install -r requirements.txt 
EXPOSE 5000
CMD ["python", "manage.py", "runserver"]
