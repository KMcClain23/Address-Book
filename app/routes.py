import os
from werkzeug.utils import secure_filename
from app import app, db
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import ContactsForm, RegistrationForm, LoginForm, EditProfileForm, DeleteAccountForm
from app.models import Address_book, User, Contact

basedir = os.path.abspath(os.path.dirname(__file__))
static_folder = os.path.join(basedir, 'static')

UPLOAD_FOLDER = os.path.join(static_folder, 'UserUploads')
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

# Add a route
@app.route('/')
def index():

    return render_template('index.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
print(allowed_file('Jimmy.JPG'))
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

        existing_contact = db.session.query(Address_book).filter((Address_book.user_id == current_user.id) & ((Address_book.first_name == first_name) | (Address_book.phone == phone))).first()

        if existing_contact:
            flash("Contact already exists with the same information", "danger")
            return redirect(url_for('contacts'))
        
        
        new_contact = Address_book(first_name = first_name, last_name = last_name, phone = phone, address = address, user_id = current_user.id)

        db.session.add(new_contact)
        db.session.commit()


        flash("Contact added successfully", "success")
                # redirect back to the home page
        return redirect(url_for('address_book'))
    
    return render_template('contacts.html', form = form)

# ----------------------------------------------------------------------------------------------------------------

@app.route('/address_book')
def address_book():
    address_book = current_user.contacts
    return render_template('address_book.html', address_book = address_book)

# ----------------------------------------------------------------------------------------------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(User.username.ilike(form.username.data)).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
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
            flash('A user with that username/password already exists', 'warning')
            return redirect(url_for('signup'))
        
        new_user = User(username = username, email = email)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()
        flash(f'{new_user.username} has been created', 'success')

        login_user(new_user)      
                # redirect back to the home page
        return redirect(url_for('index'))
    elif form.is_submitted():
        flash("Your passwords do not match", 'warning')
        return redirect(url_for('signup'))
                        
    return render_template('signup.html', form = form)


@app.route('/logout')
def logout():
    logout_user()
    flash("You have successfully logged out", 'success')
    return redirect(url_for('index'))

@app.route('/delete_contact/<int:contact_id>', methods = ['POST'])
@login_required
def delete_contact(contact_id):
    contact = Address_book.query.get(contact_id)
    
    if contact is None:
        flash(f"contact with and id of {contact_id} does not exist", 'danger')
        return redirect (url_for('index'))
    elif contact.user != current_user:
        flash("You do not have permission to delete this contact!", 'danger')
        return redirect (url_for('index'))

    db.session.delete(contact)
    db.session.commit()
    flash(f"{contact.first_name} {contact.last_name} has been deleted from your address book.", 'success')
    return redirect (url_for('address_book'))


@app.route('/delete_account', methods=['GET', 'POST'])
@login_required
def delete_account():
    form = DeleteAccountForm()

    if form.validate_on_submit():
        if current_user.check_password(form.password.data):
            user = User.query.get(current_user.id)
            db.session.delete(user)
            db.session.commit()
            logout_user()
            flash('Your account has been deleted.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Incorrect password. Account not deleted', 'danger')
    
    return render_template('delete_account.html', form=form)


@app.route('/edit_contact/<int:contact_id>', methods=['GET', 'POST'])
@login_required
def edit_contact(contact_id):
    contact = Address_book.query.get(contact_id)

    if contact is None:
        flash(f"Contact with an ID of {contact_id} does not exist", 'danger')
        return redirect(url_for('index'))
    elif contact.user != current_user:
        flash("You do not have permission to edit this contact!", 'danger')
        return redirect(url_for('index'))

    form = ContactsForm(obj=contact)

    if form.validate_on_submit():
        # Update the contact's information based on the form data
        contact.first_name = form.first_name.data
        contact.last_name = form.last_name.data
        contact.phone = form.phone.data
        contact.address = form.address.data
        # Update other fields as needed

        db.session.commit()
        flash(f"{contact.first_name.title()} {contact.last_name.title()}'s information has been updated.", 'success')
        return redirect(url_for('address_book'))

    return render_template('edit_contact.html', form=form, contact=contact)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = EditProfileForm()
        
    if request.method == 'POST' and form.validate_on_submit():
        new_username = form.new_username.data
        new_email = form.new_email.data
        new_password = form.new_password.data
        confirm_password = form.confirm_password.data
        profile_image = form.profile_image.data

        password_update_success = True  # To track password update success

        if new_password:
            if new_password != confirm_password:
                flash('Passwords do not match. Please confirm your new password correctly.', 'danger')
                password_update_success = False
            else:
                current_user.set_password(new_password)
                db.session.commit()
                flash('Password updated successfully!', 'success')

        if profile_image:
            if allowed_file(profile_image.filename):
                filename = secure_filename(profile_image.filename)
                target_path = os.path.join(UPLOAD_FOLDER, filename)
                if not os.path.exists(UPLOAD_FOLDER):
                    os.makedirs(UPLOAD_FOLDER)
                profile_image.save(target_path)
                current_user.profile_image = filename
                db.session.commit()
                flash('Profile image updated successfully!', 'success')
            else:
                flash('Invalid file format. Allowed formats: jpg, jpeg, png, gif', 'danger')

        if password_update_success:
            if new_username != current_user.username or new_email != current_user.email:
                current_user.username = new_username
                current_user.email = new_email
                db.session.commit()
                flash('Username and Email updated successfully!', 'success')
        else:
            print("Password update failed")

    return render_template('profile.html', form=form)