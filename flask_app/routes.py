from flask import redirect, url_for, render_template, flash, request, session
from flask_app import app, mysql, bcrypt
from flask_app.forms import RegisterForm, LoginForm


@app.route('/')
@app.route('/home/')
def home():
    return render_template('index.html', title='Home')


@app.route('/register/', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        email = register_form.email.data.lower()
        query = '''
        SELECT * FROM user
        WHERE email = %s
        '''
        cursor = mysql.connection.cursor()
        cursor.execute(query, [email])
        result = cursor.fetchall()
        if result:
            flash('Email already in use. Please use another', 'warning')
        else:
            name = register_form.name.data.strip()
            hashed_password = bcrypt.generate_password_hash(register_form.password.data).decode('utf-8')
            query = '''
            INSERT INTO user (name, email, password)
            VALUES(%s, %s, %s)
            '''
            data = [name, email, hashed_password]
            cursor.execute(query, data)
            mysql.connection.commit()
            flash('valid registration', 'success')
        cursor.close()
    return render_template('register.html', title='Register', form=register_form)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        email = login_form.email.data
        query = '''
        SELECT * FROM user
        WHERE email = %s
        '''
        cursor = mysql.connection.cursor()
        cursor.execute(query, [email])
        result = cursor.fetchall()
        
        if result:
            hashed_password = result[0][3]
            password_match = bcrypt.check_password_hash(hashed_password, login_form.password.data)
            print(password_match)
            if password_match:
                flash('valid password', 'success')
            else:
                flash('Invalid password', 'danger')
        else:
            flash('That email does not exist. Please double check or register for an account.', 'warning')
        
        cursor.close()
    return render_template('login.html', title='Login', form=login_form)


@app.route('/profile')
def profile():
    pass


@app.route("/logout")
def logout():
    return redirect(url_for("home"))
