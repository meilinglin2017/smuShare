FROM python:3.6
COPY . /app
WORKDIR /app
RUN pip install -r req.txt 
EXPOSE 5000
CMD ["python", "manage.py", "runserver"]
