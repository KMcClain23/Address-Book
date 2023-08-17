from app import app, db
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import ContactsForm, RegistrationForm, LoginForm
from app.models import Address_book, User, Contact

# Add a route
@app.route('/')
def index():

    return render_template('index.html')

# ----------------------------------------------------------------------------------------------------------------

@app.route('/contacts', methods = ["GET", "POST"])
@login_required
def contacts():
    form = ContactsForm()

    if form.validate_on_submit():
        # Get the data from the form
        first_name = form.first_name.data
        last_name = form.last_name.data
        phone = form.phone.data
        address = form.address.data

        existing_contact = db.session.execute(db.select(Address_book).where( (Address_book.first_name==first_name) | (Address_book.phone==phone))).scalar()
        if existing_contact:
            flash("Contact already exists with the same information", "danger")
            return redirect(url_for('contacts'))
        
        
        new_contact = Address_book(first_name = first_name, last_name = last_name, phone = phone, address = address)

        db.session.add(new_contact)
        db.session.commit()


        flash("Contact added successfully", "success")
                # redirect back to the home page
        return redirect(url_for('index'))
    
    return render_template('contacts.html', form = form)

# ----------------------------------------------------------------------------------------------------------------

@app.route('/address_book')
def address_book():
    address_book = Address_book.query.all()
    return render_template('address_book.html', address_book = address_book)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/signup', methods = ["GET", "POST"])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Get the data from the form
        username = form.username.data
        email = form.email.data
        password = form.password.data
        check_user = db.session.execute(db.select(User).where( (User.username==username) | (User.email==email) )).scalar()
        if check_user:
            flash('A user with that username/password already exists')
            return redirect(url_for('signup'))

        new_user = User(username = username, email = email)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()
        flash(f'{new_user.username} has been created')

        login_user(new_user)      

                # redirect back to the home page
        return redirect(url_for('index'))
    elif form.is_submitted():
        flash("Your passwords do not match")
        return redirect(url_for('signup'))
                        
    return render_template('signup.html', form = form)


@app.route('/logout')
def logout():
    logout_user()
    flash("You have successfully logged out")
    return redirect(url_for('index'))