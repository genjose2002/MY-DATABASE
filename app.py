from flask import Flask, render_template, redirect, url_for, request
import sqlite3
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/GenZip PC/Desktop/Testing/user.db'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember me')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    first_name = StringField('First name', validators=[InputRequired(), Length(min=4, max=15)])
    last_name = StringField('Last name', validators=[InputRequired(), Length(min=4, max = 15)])
    date_of_birth = StringField('Date of Birth', validators=[InputRequired(), Length(min=4, max=15)]) 
    age = StringField('Age', validators=[InputRequired(), Length(min=1, max=2)])
    address = StringField('Address', validators=[InputRequired(), Length(min=4, max=15)])

#con = sqlite3.connect("user.db")  
#print("Database opened successfully")  
#con.execute("create table user (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, password TEXT NOT NULL, first_name TEXT NOT NULL, last_name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, address TEXT NOT NULL, date_of_birth TEXT NOT NULL, age INTEGER NOT NULL)")  
#print("Table created successfully")  

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    first_name = db.Column(db.String(15), unique=True)
    last_name = db.Column(db.String(15), unique=True)
    date_of_birth = db.Column(db.String(15), unique=True)
    age = db.Column(db.Integer, unique=True)
    address = db.Column(db.String(15), unique=True)

@app.route("/")  
def index():  
    return render_template("index.html"); 

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))

        return '<h1>Invalid username or password</h1>'
        #return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password, first_name=form.first_name.data, last_name=form.last_name.data, date_of_birth=form.date_of_birth.data, address=form.address.data, age=form.age.data)
        db.session.add(new_user)
        db.session.commit()

        return '<h1>New user has been created!</h1>'
        #return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

    return render_template('signup.html', form=form)
 
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/add")  
def add():  
    return render_template("add.html")  
 
@app.route("/savedetails",methods = ["POST","GET"])  
def saveDetails():  
    msg = "msg"  
    if request.method == "POST":  
        try:  
            first_name = request.form["first_name"]  
            last_name = request.form["last_name"]
            email = request.form["email"]  
            address = request.form["address"]
            date_of_birth = request.form["date_of_birth"]
            age = request.form["age"]  
            with sqlite3.connect("user.db") as con:  
                cur = con.cursor()  
                cur.execute("INSERT into user (first_name, last_name, email, address, date_of_birth, age) values (?,?,?,?,?,?)",(first_name,last_name,email,address,date_of_birth,age))  
                con.commit()  
                msg = "User successfully Added"  
        except:  
            con.rollback()  
            msg = "We can not add the user to the list"  
        finally:  
            return render_template("success.html",msg = msg)  
            con.close()   

@app.route("/view")  
def view():  
    con = sqlite3.connect("user.db")  
    con.row_factory = sqlite3.Row  
    cur = con.cursor()  
    cur.execute("select * from user")  
    rows = cur.fetchall()  
    return render_template("view.html",rows = rows)

@app.route("/view2")  
def view2():  
    con = sqlite3.connect("user.db")  
    con.row_factory = sqlite3.Row  
    cur = con.cursor()  
    cur.execute("select * from user where age >= 21")  
    rows = cur.fetchall() 
    return render_template("view2.html",rows = rows)   

@app.route("/delete")  
def delete():  
    return render_template("delete.html")  

@app.route("/deleterecord",methods = ["POST"])  
def deleterecord():  
    id = request.form["id"]  
    with sqlite3.connect("user.db") as con:  
        try:  
            cur = con.cursor()  
            cur.execute("delete from user where id = ?",id)  
            msg = "record successfully deleted"  
        except:  
            msg = "can't be deleted"  
        finally:  
            return render_template("delete_record.html",msg = msg)
   
if __name__ == '__main__':
   app.run(debug = True)