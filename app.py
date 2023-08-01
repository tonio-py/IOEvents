#imports fof app.py
import os
from flask import Flask, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from functools import wraps
import base64
import psycopg2
from io import BytesIO
from psycopg2 import extras
from datetime import date



#imports of routes.py
from flask import request, render_template, flash, redirect, url_for, flash, abort, session, jsonify, Response, render_template_string
from werkzeug.urls import url_parse
from flask_login import current_user, login_user, logout_user, login_required

#imports of forms.py
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField, DateField, SelectField, TextAreaField, TimeField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Regexp

#imports from models.py
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

#instantiate application and database
app = Flask(__name__)
app.config['SECRET_KEY'] = 'israel-and-ocran'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost/ioevents'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
# postgres://israel_py:8vbkNw2MrOZY7JbetemCQ8XDlWQ3FXBn@dpg-cj41h5l9aq0e0q2o0nlg-a/ioevents
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB limit

db = SQLAlchemy(app)
migrate = Migrate(app, db)

#create login manager
login_manager = LoginManager()
login_manager.init_app(app)


#declaration from forms
class RegistrationForm(FlaskForm):
    first_name = StringField('name', validators=[DataRequired()])
    surname  = StringField('surname', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    confirm_password = PasswordField('repeat password', validators=[DataRequired(), EqualTo('password')])
    phone_number = StringField('phone Number', validators=[ DataRequired(),Regexp(r'^\+?[1-9]\d{1,14}$', message='Invalid phone number')])
    ghana_card_id = StringField('ghana card id', validators=[DataRequired(), Regexp(r'^GHA-\d{9}-\d$', message="Invalid ghana card id")])
    account_type = RadioField('Account Type', choices=[('User', 'user'), ('Organizer','organizer')], default='user', validators=[DataRequired()])
    submit = SubmitField('Register')
    
class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    account_type = RadioField('Account Type', choices=[('User', 'user'), ('Organizer', 'organizer')], default='User', validators=[DataRequired()])
    submit = SubmitField('Login')

class CreateEvent(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    description = StringField('description', validators=[DataRequired()])
    image = FileField('image', validators=[FileRequired(), FileAllowed(['jpeg', 'jpg', 'png', 'png'])])
    location = StringField('location', validators=[DataRequired()])
    # city   = SelectField('select city', validators=[DataRequired()], choices=[('')] )
    gh_post = StringField('ghana post', validators=[DataRequired()])
    date = DateField('date', validators=[DataRequired()], format='%Y-%m-%d')
    submit = SubmitField('Create Event')

class CreateEventForm(FlaskForm):
    event_name = StringField('Event Name', validators=[DataRequired()])
    ghana_post = StringField('Ghana Post', validators=[DataRequired()])
    # date = DateField('Date', validators=[DataRequired()],format='%Y-%m-%d')
    # time = TimeField('Time', validators=[DataRequired()])
    pricing = SelectField('Pricing', choices=[('', 'Select'), ('Paid', 'Paid'), ('Free', 'Free')], validators=[DataRequired()])
    poster = FileField('Poster', validators=[FileRequired(), FileAllowed(['jpeg', 'jpg', 'png', 'png'])])
    ticket_number = StringField('Ticket Number', validators=[DataRequired(), Regexp('^\d+$', message='Please enter only numbers.')])
    description = TextAreaField('Description', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    genre = SelectField('Genre', choices=[
        ('', 'Select Event Category'),
        ('music-concerts', 'Music Concerts'),
        ('theater-performances', 'Theater Performances'),
        ('sports-events', 'Sports Events'),
        ('art-exhibitions', 'Art Exhibitions'),
        ('conferences-workshops', 'Conferences and Workshops'),
        ('festivals-carnivals', 'Festivals and Carnivals'),
        ('charity-events', 'Charity Events'),
        ('university-event', 'University Event'),
        ('community-gatherings', 'Community Gatherings'),
        ('educational-seminars', 'Educational Seminars'),
        ('cultural-celebrations', 'Cultural Celebrations'),
        ('networking-events', 'Networking Events'),
        ('religious-ceremonies', 'Religious Ceremonies'),
        ('church-event', 'Church Event'),
        ('weddings-receptions', 'Weddings and Receptions'),
        ('fashion-shows', 'Fashion Shows'),
        ('film-screenings', 'Film Screenings'),
        ('food-drink-events', 'Food and Drink Events'),
        ('technology-conventions', 'Technology Conventions'),
        ('business-expos', 'Business Expos'),
        ('comedy-shows', 'Comedy Shows'),
        ('political-rallies', 'Political Rallies')
    ], validators=[DataRequired()])

    submit = SubmitField('Create Event')

#declaration from models
attendance = db.Table('attendance',
                      db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
                      db.Column('event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True)
                      )

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100))
    surname = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(400))
    phone_number = db.Column(db.String(20))
    identification_card = db.Column(db.String(30))
    tickets = db.relationship('Ticket', backref='associated_user', lazy=True)
    events_attending = db.relationship('Event', secondary=attendance, backref='attendees')
    role = db.Column(db.String(20),nullable=False,  default='user')
    
    def __repr__(self):
        return '<User {}>'.format(self.username)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Organizer(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100))
    surname = db.Column(db.String(100))
    email  = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    password_hash = db.Column(db.String(400))
    identification_card = db.Column(db.String(20))
    events_created = db.relationship('Event', backref='organizer', lazy=True)
    role = db.Column(db.String(20), nullable=False, default='organizer')

    def __repr__(self):
        return '<Organizer {}>'.format(self.firstname)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    date = db.Column(db.Date)
    poster = db.Column(db.LargeBinary)
    gh_post = db.Column(db.String(100))
    organizer_id = db.Column(db.Integer, db.ForeignKey('organizer.id'), nullable=False)
    location = db.Column(db.String(100))
    description = db.Column(db.String(1000))
    event_category = db.Column(db.String(200))
    ticket_count = db.Column(db.Integer, nullable=False)
    event_price = db.Column(db.Integer, default=0)
    tickets = db.relationship('Ticket', backref='event')
    
    # image  = FileField('Image', validators=[FileRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'])])

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    qr_code = db.Column(db.String(300))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    organizer_id = db.Column(db.Integer, db.ForeignKey('organizer.id'), nullable=True)
    
    # user = db.relationship('User', backref='associated_ticket')
    # event = db.relationship('Event', backref='ticket')
    # organizer = db.relationship('Organizer', backref='ticket')


ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_flashed_messages(with_categories=False):
    """
    Custom implementation of get_flashed_messages to support categories.
    """
    flashes = app.jinja_env.globals['flashes']
    app.jinja_env.globals['flashes'] = []
    return flashes if with_categories else [msg for msg, _ in flashes]

def user_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'user':
            abort(403)  # Return a forbidden error if the user is not authenticated as a user
        return func(*args, **kwargs)
    return decorated_view

def organizer_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'organizer':
            abort(403)  # Return a forbidden error if the user is not authenticated as an organizer
        return func(*args, **kwargs)
    return decorated_view

def zip_lists(a, b):
    return zip(a, b)
def split_by_delimiter(value, delimiter):
    return value.split(delimiter)

def get_month_in_words(date_string):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    month_number = int(date_string.split("-")[1])
    return months[month_number - 1]

app.jinja_env.filters['zip'] = zip_lists
app.jinja_env.filters['split_by_delimeter'] = split_by_delimiter
app.jinja_env.filters['get_month_in_words'] = get_month_in_words

@login_required
@organizer_required
@app.route('/delete/organizer/<int:organizer_id>/event/<int:event_id>')
def delete_event(organizer_id, event_id):
    event = Event.query.filter_by(id=event_id, organizer_id=organizer_id).first()
    if event:
        db.session.delete(event)
        db.session.commit()
    return redirect(url_for('organizer_my_events'))

@login_required
@organizer_required
@app.route('/update/organizer/<int:organizer_id>/event/<int:event_id>', methods=['POST', 'GET'])
def update_event(organizer_id, event_id):
    event = Event.query.filter_by(id=event_id, organizer_id=organizer_id).first()
    if request.method == "POST":
        pass
    else:
        event_name = event.name
        event_poster = event.poster
        event_description = event.description
        event_ticket_count = event.ticket_count
        return render_template('update_event.html', event_name=event_name, event_poster=event_poster, event_description=event_description, event_ticket_count=event_ticket_count)





# route declaration here
@login_manager.user_loader
def load_user(user_id):
    if session.get('my_role') == 'user_role':
        return  Users.query.get(int(user_id))
    return Organizer.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    # do stuff
    return "You are not logged in. Click here to get <a href="+ str("/")+">back to Index Page</a>"



@app.route('/')
def index():
    today = date.today()
    image_array = []
    events = Event.query.filter(Event.date >= today).order_by(Event.date).limit(9).all()
    for event in events:
        image_dati = event.poster
        encoded_bytes = base64.b64encode(bytes(image_dati)).decode('utf-8')
        image_array.append(encoded_bytes)
    return render_template('index.html', events=events, image_array=image_array)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(csrf_enabled=False)
    if request.method == "GET":
        return render_template('register.html', form=form)
    else:
        if form.validate_on_submit():
            if form.account_type.data == 'User':
                first_name = form.first_name.data
                last_name  = form.surname.data
                mail  = form.email.data
                password = form.password.data
                tel_number = form.phone_number.data
                ghana_card_id = form.ghana_card_id.data
                user = Users(firstname=first_name, surname=last_name, email=mail, phone_number=tel_number, identification_card=ghana_card_id)
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                flash('Account has been created sucessfully', category='success')
                return redirect(url_for('login'))
            else:
                first_name = form.first_name.data
                last_name = form.surname.data
                mail = form.email.data
                password = form.password.data
                tel_number  = form.phone_number.data
                ghana_card_id = form.ghana_card_id.data
                organizer = Organizer(firstname=first_name, surname=last_name, email=mail, phone_number=tel_number, identification_card= ghana_card_id)
                organizer.set_password(password)
                db.session.add(organizer)
                db.session.commit()
                flash('Organizer Account has been created sucessfully', category='success')
                return redirect(url_for('login'))
                
        else:
            flash('Please enter the appropriate details', category='error')
            return redirect(url_for('register'))


@app.route('/login', methods=["POST", "GET"])
def login():
    form = LoginForm(csrf_enabled=False)
    if request.method == "GET":
        return render_template('login.html', form=form)
    else:
        if form.validate_on_submit():
            print(form.account_type.data)
            if form.account_type.data == 'User':
                session['my_role'] = 'user_role'
                user = Users.query.filter_by(email=form.email.data).first()
                if user and user.check_password(form.password.data):
                    login_user(user, remember=False)
                    next_page = request.args.get('next')
                    return redirect(next_page) if next_page else redirect(url_for('user_profile', _external=True))
                return "You entered the incorrect data"
            else:
                session['my_role'] = 'organizer_role'
                organizer = Organizer.query.filter_by(email=form.email.data).first()
                if organizer and organizer.check_password(form.password.data):
                    login_user(organizer, remember=False)
                    next_page = request.args.get('next')
                    return redirect(next_page) if next_page else redirect(url_for('organizer_profile', _external=True))
        else:
            return "You entered an inccorrect data"
           



@app.route('/about')
def about():
    return render_template('about.html')



@app.route('/user_profile')
@login_required
@user_required
def user_profile():
    return render_template('userprofile.html', current_user=current_user)


@app.route('/search_events')
@login_required
def search_events():
    return "search events"

@app.route('/my_calendar')
@login_required
@user_required
def my_calendar():
    return "my calendar"

@app.route('/my_events')
@login_required
@user_required
def my_events():
    return "hello"


@app.route('/logout')
@login_required
def logout():
    session.pop('user_role', None)
    logout_user()
    return redirect(url_for('index'))
    
@app.route('/organizer_profile')
@login_required
@organizer_required
def organizer_profile():
    return render_template('organizerprofile.html')


@app.route('/update/organizer_profile/<int:organizer_id>', methods=['POST', 'GET'])
def update_organizer_profile(organizer_id):
    if request.method == 'POST':
        pass
    else:
        return render_template('update_organizer_profile.html')


@app.route('/organizer_create_events', methods=["POST", "GET"])
@login_required
@organizer_required
def organizer_create_events():
    # create_event_form  = CreateEventForm(csrf_enabled=False)
    if request.method == "POST":
        image_file = request.files['poster']
        print(image_file.filename)
        if not allowed_file(image_file.filename):
            return jsonify({'error': 'Invalid file extension. Only JPG, JPEG, PNG, and GIF files are allowed.'}), 400
        print(request.form)
        event_name = request.form.get('event_name')
        ghana_post = request.form.get("ghana_post")
        time = request.form.get('time')
        date = request.form.get('date')
        try:
            price = request.form.get('price')
            
        except:
            price = None
            print()
        pricing = request.form.get('pricing')
        description = request.form.get('description')
        location  = request.form.get('location')
        event_category = request.form.get('genre')
        ticket_number = request.form.get('ticket_number')
        new_event = Event(name=event_name, date=date, gh_post=ghana_post, location=location, description=description, event_price=price, ticket_count=ticket_number, event_category=event_category, poster=image_file.read())
        current_user.events_created.append(new_event)
        db.session.add(new_event)
        db.session.commit()
        flash('Event has be succesfully created', category='success')
        return redirect(url_for('organizer_create_events'))
    else:
        return render_template('create_events.html')

@app.route('/organizer_calendar', methods=['POST', 'GET'])
@login_required
@organizer_required
def organizer_calendar():
    if request.method == 'GET':
        events = current_user.events_created
        for j in events:
            print(j.date)
        return render_template('organizer_calendar.html', events=events)




@app.route('/organizer_my_events')
@login_required
@organizer_required
def organizer_my_events():
    events = current_user.events_created
    image_data = events[0].poster
    encoded_bytes = base64.b64encode(bytes(image_data)).decode('utf-8')
    image_array = []
    for event in events:
        image_dati = event.poster
        encoded_bytes = base64.b64encode(bytes(image_dati)).decode('utf-8')
        image_array.append(encoded_bytes)
        
    return render_template('organizer_events.html', events=events, image_array=image_array)


@app.route('/organizer_statistics')
@login_required
@organizer_required
def organizer_statistics():
    return render_template("organizer_statistics.html")
if __name__ == '__main__':
    app.run(debug=True)


