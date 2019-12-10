import datetime

# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------


def index():
    grid = SQLFORM.grid(db.product,
        create=True, editable=True, 
    )
    return dict(grid=grid)

def buy(row):
    if auth.user is not None:
        return A('Buy', _class='btn', _href=URL('default', 'create_order', args=[row.id], user_signature=True))
    else:
        return A('')

def store():
    query = db.product
    links = []

    # Adding buy button:
    links.append(
        dict(header='', body = lambda row : buy(row)
        )
    )

    """Returns the store page, with the list of products to be bought"""
    grid = SQLFORM.grid(
        query,
        field_id = db.product.id,
        fields = [db.product.product_name, db.product.product_quantity, db.product.sales_price],
        links = links,
        details=True,
        create=True, 
        editable=True,
        deletable=False,
        csv=False,
        user_signature=True, 
    )
    return dict(grid=grid)


@auth.requires_login()
def create_order():
    """Page to create an order, accessed from the Buy button."""
    product = db.product(request.args(0))
    user_profile = db(db.user_profile.email == auth.user.email).select().first()

    if user_profile is None:
        redirect(URL('default', 'profile',
                     vars=dict(next=URL('default', 'create_order', args=[product.id]),
                               edit='y')))
    # Ok, here you know the profile exists.
    # Sets the default for the order to be created. 
    db.orders.product_id.default = product.id
    db.orders.email.default = auth.user.email
    db.orders.order_date.default = datetime.datetime.utcnow()
    # Complete.  You have to create a form for inserting an order, and process/return it. 
    form = SQLFORM.factory(
        Field('order_quantity', 'integer', requires=IS_INT_IN_RANGE(1, product.product_quantity + 1))
    )

    if form.process().accepted:
        db.orders.insert(
            quantity=form.vars.order_quantity,
            amount_paid=form.vars.order_quantity * product.sales_price
        )
        redirect(request.vars.next or URL('default', 'store'))
    return dict(form=form, name=product.product_name)

@auth.requires_login()
def profile():
    """Page for creating/editing/viewing a profile. 
    It has two modes: edit/create, and view."""

    # Hide email:
    db.user_profile.email.readable = False
    db.user_profile.email.writable = False
    db.user_profile.id.readable = False
    db.user_profile.id.writable = False

    # This is the email of the user to which the form applies.
    user_email = request.vars.email or auth.user.email
    
    # Get profile:
    user_profile = db.user_profile(db.user_profile.email==user_email)

    if request.vars.edit == 'y':
        # Mode for create/edit. 
        # You need to create a form to create (if there is no profile)
        # or edit (if there is a profile) the profile for the user.
        if user_profile is None:

            # Add profile:
            profStatus = "Add"
            form = SQLFORM.factory(
                Field('name', 'string'),
                Field('street', 'string'),
                Field('city', 'string'),
                Field('zip', 'integer'),
            )

            if form.process().accepted:
                db.user_profile.insert(
                    email=auth.user.email,
                    name=form.vars.name,
                    street=form.vars.street,
                    city=form.vars.city,
                    zip=form.vars.zip,
                )
                redirect(request.vars.next or URL('default', 'index'))
        else:
            # Edit profile:
            profStatus = "Edit"
            form = SQLFORM(db.user_profile, record=user_profile)
            redirect(request.vars.next)
        
    else:
        # Mode for view.
        # You need to read the profile for the user, and return a view form for it, 
        # generated with SQLFORM(db.profile, profile, readonly=True). 
        # You do not need to process the form.
        profStatus = "View"
        form = SQLFORM(db.user_profile, user_profile, readonly=True, formname='View_Profile') # Placeholder.  
    return dict(form=form, profStatus=profStatus)


@auth.requires_login()
def order_list():
    """Page to display the list of orders."""
    query = db.orders
    links = []

    db.orders.product_id.label = 'Product'

    # Fixes visualization of email and product.  I hope this works, it should give you the idea at least.
    db.orders.email.represent = lambda v, r : A(v, _href=URL('default', 'profile', vars=dict(email=v)))
    db.orders.product_id.represent = lambda v, r : A(get_product_name(db.product(v)), _href=URL('default', 'view_product', args=[v]))
    
    grid = SQLFORM.grid(
        query,
        field_id = db.orders.id,
        fields = [db.orders.email, db.orders.product_id, db.orders.quantity, db.orders.order_date, db.orders.amount_paid],
        links = links,
        details=False,
        create=False, 
        editable=False,
        deletable=False,
        csv=False 
        )
    return dict(grid=grid)


def view_product():
    """Controller to view a product."""
    p = db.product(request.args(0))
    if p is None:
        form = P('No such product')
    else:
        form = SQLFORM(db.product, p, readonly=True)
    return dict(form=form)


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


