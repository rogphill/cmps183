# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable', Field('myfield', 'string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
#       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.


db.define_table('product',
    Field('product_name'),
    Field('product_quantity', 'integer'),
    Field('sales_price', 'float'),
)

def get_product_name(p):
    return None if p is None else p.product_name

db.define_table('user_profile',
    Field('email', 'string'),
    Field('name', 'string'),
    Field('street', 'string'),
    Field('city', 'string'),
    Field('zip', 'integer'),
)

db.define_table('orders',
    Field('email', 'string'),
    Field('product_id', 'integer'),
    Field('quantity', 'integer'),
    Field('order_date', 'date'),
    Field('amount_paid', 'float'),
)

db.product.id.readable = False
db.product.product_name.label = 'Name'
db.product.product_quantity.label = 'Quantity'

# after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)