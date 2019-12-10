# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable', Field('myfield', 'string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
#       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.

# after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

import datetime

def get_user_email():
    return None if auth.user is None else auth.user.email

def get_current_time():
    return datetime.datetime.utcnow()

def get_first_name():
    return None if auth.user is None else auth.user.first_name

def get_last_name():
    return None if auth.user is None else auth.user.last_name

# Products
db.define_table('products',
                Field('author', 'string', default=get_user_email()),
                Field('name', 'string'),
                Field('description', 'text'),
                Field('price', 'decimal(18,2)'),
                Field('quantity', 'integer', default=0),
                Field('thetime', 'datetime', default=get_current_time()),
                )

# Reviews
db.define_table('reviews',
                Field('user_email', default=get_user_email()),
                Field('product_id', 'reference products'),
                Field('review', 'text'),
                Field('rating', 'integer', default=None), # The star rating.
                Field('first_name', default=get_first_name()),
                Field('last_name', default=get_last_name())
                )

db.define_table('shopping_cart',
                Field('user_email', default=get_user_email()),  
                #Field('product_id', 'reference products'),
                #Field('amount', 'integer'),
                Field('cart', 'text'), # This stores json, just like localstorage
                )

db.products.id.readable = False
db.products.author.readable = False
db.products.thetime.readable = False
db.products.author.writable = False
db.products.thetime.writable = False
db.products.price.represent = lambda v, r : "$" + str(v)