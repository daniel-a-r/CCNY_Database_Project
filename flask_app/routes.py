from flask import redirect, url_for, render_template, flash, request
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
        name = register_form.name.data.strip().lower()
        email = register_form.email.data
        hashed_password = bcrypt.generate_password_hash(register_form.password.data).decode('utf-8')
        query = '''
        INSERT INTO user (name, email, password)
        VALUES(%s, %s, %s)
        '''
        data = [name, email, hashed_password]
        cursor = mysql.connection.cursor()
        cursor.execute(query, data)
        mysql.connection.commit()
        cursor.close()
        flash('valid form', 'success')
    else:
        flash('invalid form', 'danger')
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
        rv = cursor.fetchall()
        print(rv)
        cursor.close()
        
        flash('Successful login', 'success')
    return render_template('login.html', title='Login', form=login_form)


@app.route("/logout")
def logout():
    return redirect(url_for("home"))
