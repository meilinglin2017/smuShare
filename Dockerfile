FROM  python:3-onbuild
COPY . /app
WORKDIR /app
RUN pip install -r req.txt 
EXPOSE 5000
CMD ["python", "manage.py", "runserver"]
