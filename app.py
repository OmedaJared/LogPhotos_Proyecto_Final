from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from pymongo import MongoClient
from pymongo.errors import ConfigurationError, OperationFailure, ServerSelectionTimeoutError
from bson import ObjectId
from bcrypt import hashpw, gensalt, checkpw
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os
import secrets

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# MongoDB connection
mongo_uri = os.getenv('MONGO_URI')
if not mongo_uri or '<db_password>' in mongo_uri or '<password>' in mongo_uri or '<user>' in mongo_uri:
    print('WARNING: MONGO_URI contiene placeholders. Reemplaza usuario y contraseña reales en .env.')
    mongo_uri = os.getenv('MONGO_URI_LOCAL', 'mongodb://localhost:27017/trevi3')

try:
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
except OperationFailure as exc:
    raise SystemExit(
        'Error de autenticación de MongoDB Atlas. Revisa tu usuario, contraseña y permisos en Atlas.\n'
        f'{exc}'
    )
except (ConfigurationError, ServerSelectionTimeoutError) as exc:
    raise SystemExit(
        'Error conectando a MongoDB. Verifica tu URI en .env y tu conexión a internet.\n'
        f'{exc}'
    )

db = client['trevi3']  # database name
users_collection = db['users']
reset_tokens_collection = db['reset_tokens']

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.email = user_data['email']
        self.password_hash = user_data['password_hash']

@login_manager.user_loader
def load_user(user_id):
    user_data = users_collection.find_one({'_id': ObjectId(user_id)})
    if user_data:
        return User(user_data)
    return None

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class ResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Reset Link')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

@app.route('/')
@login_required
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user_data = users_collection.find_one({'email': form.email.data})
        if user_data and checkpw(form.password.data.encode('utf-8'), user_data['password_hash']):
            user = User(user_data)
            login_user(user)
            return redirect(url_for('home'))
        flash('Invalid email or password')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegisterForm()
    if form.validate_on_submit():
        if users_collection.find_one({'email': form.email.data}):
            flash('Email already registered')
            return redirect(url_for('register'))
        password_hash = hashpw(form.password.data.encode('utf-8'), gensalt())
        users_collection.insert_one({
            'email': form.email.data,
            'password_hash': password_hash
        })
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/reset', methods=['GET', 'POST'])
def reset():
    form = ResetForm()
    if form.validate_on_submit():
        user_data = users_collection.find_one({'email': form.email.data})
        if user_data:
            token = secrets.token_urlsafe(32)
            reset_tokens_collection.insert_one({
                'email': form.email.data,
                'token': token
            })
            msg = Message('Password Reset', sender=app.config['MAIL_USERNAME'], recipients=[form.email.data])
            msg.body = f'Click the link to reset your password: {url_for("reset_password", token=token, _external=True)}'
            mail.send(msg)
            flash('Reset link sent to your email')
        else:
            flash('Email not found')
    return render_template('reset.html', form=form)

@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    token_data = reset_tokens_collection.find_one({'token': token})
    if not token_data:
        flash('Invalid or expired token')
        return redirect(url_for('reset'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        password_hash = hashpw(form.password.data.encode('utf-8'), gensalt())
        users_collection.update_one({'email': token_data['email']}, {'$set': {'password_hash': password_hash}})
        reset_tokens_collection.delete_one({'token': token})
        flash('Password reset successful! Please login.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
