from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from dotenv import load_dotenv
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

# Load environment variables from .env file
load_dotenv()

# Create a Flask Instance
app = Flask(__name__)
# Add Database
# Old SQLite Database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# New MYSQL Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Necronomicon@localhost/user2'
# Secret Key
app.config['SECRET_KEY'] = "This is a Secret Key"
# Initialize the Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Blog Post Model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))
    
# Create a Post Form
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = StringField('Content', validators=[DataRequired()], widget=TextArea())
    author = StringField('Author', validators=[DataRequired()])
    slug = StringField('Slug', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route('/post')
def posts():
    # Grab all the posts from the database
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template('posts.html', posts=posts)

# Add Post Page
@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Posts(title=form.title.data, content=form.content.data, author=form.author.data, slug=form.slug.data)
        # Clear the form
        form.title.data = ''
        form.content.data = ''
        form.author.data = ''
        form.slug.data = ''
        # Add the post to the database
        db.session.add(post)
        db.session.commit()
        # Return Message
        flash('Blog Post added successfully')
    # Redirect to the webpage
    return render_template('add_post.html', form=form)

# Json 
@app.route('/date')
def get_current_date():
    favorite_pizza = {"John": "Pepperoni", "Sara": "Cheese", "Tim": "Mushroom"}
    return favorite_pizza
    # return {"Date": date.today()}


# Create Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)      # In Order to make tables in flask, it needs to use 'flask shell' in cmd
    favorite_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)        # then db.create_all() to create tables then exit()
    
    # Do Some Password Stuff
    password_hash = db.Column(db.String(128))
    
    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # Create a String
    def __repr__(self):
        return '<Name %r>' % self.name

@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash('User Deleted Successfully')
        our_users = Users.query.order_by(Users.date_added)
        return render_template('add_user.html', form=form, name=name, our_users=our_users)
    except:
        flash('Error... User Not Deleted Successfully')
        return render_template('add_user.html', form=form, name=name, our_users=our_users)


# Create a Form class
class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    favorite_color = StringField('Favorite Color')
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Passwords Must Match')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Update Database Record
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        try:
            db.session.commit()
            flash('User Updated Successfully')
            return render_template('update.html', form=form, name_to_update=name_to_update)
        except:
            flash('Error... User Not Updated Successfully')
            return render_template('update.html', form=form, name_to_update=name_to_update)
    else:
        return render_template('update.html', form=form, name_to_update=name_to_update, id=id)
    
# Create a Form class
class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Create a Password form class
class PasswordForm(FlaskForm):
    email = StringField('What is your email?', validators=[DataRequired()])
    password_hash = PasswordField('What is your password?', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hash the password
            hashed_pw = generate_password_hash(form.password_hash.data, method='pbkdf2:sha256')
            user = Users(name=form.name.data, email=form.email.data, favorite_color=form.favorite_color.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        form.password_hash.data = ''
        flash('User added successfully')
    our_users = Users.query.order_by(Users.date_added)
    return render_template('add_user.html', form=form, name=name, our_users=our_users)

# Create a route decorator
@app.route('/')
def index():
    first_name = "John"
    stuff = "This is bold text"
    favorite_pizza = ["Pepperoni", "Cheese", "Mushroom", 41]
    return render_template('index.html', first_name=first_name, stuff=stuff, favorite_pizza=favorite_pizza)

# localhost:5000/user/John
@app.route('/user/<name>')
def user(name):
    return render_template('user.html', user_name=name)

# Create Custom Error Pages

# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

# Create name page
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NameForm()
    # Validate Form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash('Form Submitted Successfully')
    return render_template('name.html', name=name, form=form)

# Create password test page
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()
    # Validate Form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        # Clear form
        form.email.data = ''
        form.password_hash.data = ''
        
        # Look up user by email address
        pw_to_check = Users.query.filter_by(email=email).first()
        
        # Check hashed password
        passed = check_password_hash(pw_to_check.password_hash, password)
        
        # flash('Form Submitted Successfully')
    return render_template('test_pw.html', email=email, password=password, pw_to_check=pw_to_check, passed=passed, form=form)