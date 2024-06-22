FROM python:3.8
COPY /techtrends /app
WORKDIR /app
RUN pip install -r $PWD/requirements.txt
EXPOSE 3111
RUN python $PWD/init_db.py
CMD [ "python", "app.py"]