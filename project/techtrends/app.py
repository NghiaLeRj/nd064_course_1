import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging
from datetime import datetime

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Function to get number of db connection
def get_db_connections():
    connection = get_db_connection()
    #cursor = connection.cursor()
    connection_count  = connection.execute('SELECT * FROM posts').fetchone()[0]
    #num_posts = len(posts)
    connection.close()
    return connection_count

# Function to get number of posts
def get_num_posts():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    num_posts = len(posts)
    connection.close()
    return num_posts

# Logging message
def logging_msg(message):
    #Get current datetime
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime('%d/%m/%Y %H:%M:%S')
    logging.info(f'{formatted_datetime.replace(" ", ", ")} - {message}')

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        return render_template('404.html'), 404
    else:
        #Get log msg
        post_title = post['title']
        log_msg = f'Article "{post_title}" retrieved!'
        logging_msg(str(log_msg))
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    #Get log msg
    log_msg = f'About Us retrieved!'
    logging_msg(str(log_msg))
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            #Get log msg
            log_msg = f'New post "{title}" was created!'
            logging_msg(log_msg)
            return redirect(url_for('index'))

    return render_template('create.html')

# Define the healthcheck endpoint
@app.route('/healthz', methods=('GET', 'POST'))
def healthz():
    response = {
        'result': 'OK - healthy'
    }
    return jsonify(response), 200

# Define the metrics endpoint
@app.route('/metrics', methods=('GET', 'POST'))
def metrics():
    db_connection_count = get_db_connections()
    posts_count = get_num_posts()
    response = {
        'db_connection_count': db_connection_count,
        'post_count': posts_count
    }
    return jsonify(response), 200

# Configure logging
def log_init():
    logging.basicConfig(
        level=logging.DEBUG,  # Set the log level
        format='%(levelname)s:%(name)s:%(message)s',  # Set the log format
        handlers=[
            logging.FileHandler("app.log"),  # Log to a file
            logging.StreamHandler()  # Log to console
        ]
    )
    # Create a logger
    logger = logging.getLogger(__name__)
    return logger

# start the application on port 3111
if __name__ == "__main__":
   log_init()
   app.run(host='0.0.0.0', port='3111', debug=True)
