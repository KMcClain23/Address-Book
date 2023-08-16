from app import app, db
from flask import render_template, redirect, url_for, flash
from flask import request
from app.forms import ContactsForm
from app.models import User

# Add a route
@app.route('/')
def index():
    countries = ['United States', 'Canada', 'Mexico', 'France', 'Egypt', 'China']
    return render_template('index.html', first_name='David', countries=countries)

@app.route('/contacts', methods = ["GET", "POST"])
def contacts():
    form = ContactsForm()

    if form.validate_on_submit():
        # Get the data from the form
        first_name = form.first_name.data
        last_name = form.last_name.data
        phone = form.phone.data
        address = form.address.data

        existing_contact = db.session.execute(db.select(User).where( (User.first_name==first_name) | (User.phone==phone))).scalar()
        if existing_contact:
            flash("Contact already exists with the same information", "danger")
            return redirect(url_for('contacts'))
        
        
        new_contact = User(first_name = first_name, last_name = last_name, phone = phone, address = address)

        db.session.add(new_contact)
        db.session.commit()


        flash("Contact added successfully", "success")
                # redirect back to the home page
        return redirect(url_for('index'))
    
    return render_template('contacts.html', form = form)