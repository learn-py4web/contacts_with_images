"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

import time

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email

url_signer = URLSigner(session)

@action('index')
@action.uses(url_signer, 'index.html')
def index():
    return dict(
        # This is the signed URL for the callback.
        load_contacts_url = URL('load_contacts', signer=url_signer),
        add_contact_url = URL('add_contact', signer=url_signer),
        delete_contact_url = URL('delete_contact', signer=url_signer),
        edit_contact_url = URL('edit_contact', signer=url_signer),
    )

# This is our very first API function.
@action('load_contacts')
@action.uses(url_signer.verify(), db)
def load_contacts():
    rows = db(db.contact).select().as_list()
    return dict(rows=rows)

@action('add_contact', method="POST")
@action.uses(url_signer.verify(), db)
def add_contact():
    id = db.contact.insert(
        first_name=request.json.get('first_name'),
        last_name=request.json.get('last_name'),
    )
    return dict(id=id)

@action('delete_contact')
@action.uses(url_signer.verify(), db)
def delete_contact():
    id = request.params.get('id')
    assert id is not None
    db(db.contact.id == id).delete()
    return "ok"

@action('edit_contact', method="POST")
@action.uses(url_signer.verify(), db)
def edit_contact():
    # Updates the db record.
    id = request.json.get("id")
    field = request.json.get("field")
    value = request.json.get("value")
    db(db.contact.id == id).update(**{field: value})
    time.sleep(1) # debugging
    return "ok"
