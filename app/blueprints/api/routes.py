from . import api
from app import db
from app.models import Contact, Address_book
from flask import request
from .auth import basic_auth, token_auth


@api.route('/token')
@basic_auth.login_required
def get_token():
    auth_user = basic_auth.current_user()
    token = auth_user.get_token()
    return {
        'token': token,
        'token_expiration': auth_user.token_expiration
    }


@api.route('/contacts')
def get_contacts():
    contacts = db.session.execute(db.select(Address_book)).scalars().all()
    return [contact.to_dict() for contact in contacts]


@api.route('/contacts/<contact_id>')
def get_contact(contact_id):
    contact = db.session.get(Contact, contact_id)
    if contact:
        return contact.to_dict()
    else:
        return {'error': f'Contact with an ID of {contact_id} does not exist'}, 404


@api.route('/contacts', methods=["POST"])
@token_auth.login_required
def create_contact():
    # Check to see that the request body is JSON
    if not request.is_json:
        return {'error': 'Your content-type must be application/json'}, 400
    # Get the data from the request body
    data = request.json
    # Validate incoming data
    required_fields = ['first_name', 'last_name', 'phone', 'address']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body"}, 400
    
    # Get the data from the body
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    phone = data.get('phone')
    address = data.get('address')

    existing_contact_phone = Address_book.query.filter_by(phone=phone).first()
    existing_contact_address = Address_book.query.filter_by(address=address).first()

    if existing_contact_phone:
        return {'error': 'A contact with the same phone number already exists'}, 409
    
    if existing_contact_address:
        return {'error': 'A contact with the same address already exists'}, 409

    current_user = token_auth.current_user()
    # Create a new Contact instance with the data
    new_contact = Address_book(first_name = first_name, last_name = last_name, phone = phone, address = address, user_id = current_user.id)
    # add to the database
    db.session.add(new_contact)
    db.session.commit()

    return new_contact.to_dict(), 201