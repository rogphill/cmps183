# Here go your api methods.

@auth.requires_signature(hash_vars=False)
def search():
    s = request.vars.search_string or ''
    res = [t for t in request.vars.product_list if s in t]
    return response.json(dict(strings=res))

@auth.requires_signature()
def add_product():
    product_id = db.products.insert(
        name=request.vars.name,
        description=request.vars.description,
    )
    # We return the id of the new product, so we can insert it along all the others.
    return response.json(dict(product_id=product_id))

@auth.requires_signature()
def add_review():
    result = db.reviews.update_or_insert(
        (db.reviews.product_id == request.vars.product_id) & (db.reviews.user_email == auth.user.email),
        review=request.vars.review,
        product_id=int(request.vars.product_id)
    )
    # We return the id of the new review, so we can insert it along all the others.
    return response.json(dict(review_id=result))

def get_star_average(prid):
    revs = db(db.reviews.product_id == prid).select(db.reviews.ALL)
    starAverage = 0
    count = 0
    for rev in revs:
        if rev.rating != None:
            starAverage = starAverage + rev.rating
            count = count + 1
    if count > 0:
        starAverage = starAverage / count
        return starAverage
    else:
        return 0
        
def get_product_list():
    results = []
    ''' if auth.user is None:
        # Not logged in.
        rows = db().select(db.products.ALL, orderby=~db.products.thetime)
        for row in rows:
            results.append(dict(
                id=row.id,
                name=row.name,
                description=row.description,
                price=row.price,
                author=row.author,
                #like = False, # Anyway not used as the user is not logged in. 
                rating = None if row.user_star.id is None else get_star_average(row.id), # As above
            ))
    else: 
    # Logged in.
    rows = db().select(db.products.ALL, db.reviews.ALL,
                        left=[
                            db.reviews.on((db.reviews.product_id == db.products.id)),
                        ],
                        orderby=~db.products.thetime)'''

    rows = db().select(db.products.ALL)                     
 
    for row in rows:
        results.append(dict(
            id=row.id,
            name=row.name,
            description=row.description,
            price=row.price,
            author=row.author,
            quantity=row.quantity,
            desired_quantity=min(1,row.quantity),
            cart_quantity=0,
            rating = None if row.id is None else get_star_average(row.id) #row.user_star.rating,
        ))
    # For homogeneity, we always return a dictionary.
    return response.json(dict(product_list=results))

def get_review_list():
    results = []
    rows = db().select(db.reviews.ALL)
    for row in rows:
        results.append(dict(
            product_id=row.product_id,
            review=row.review,
            user_email=row.user_email,
            rating=row.rating,
            first_name=row.first_name,
            last_name=row.last_name
        ))
    return response.json(dict(review_list=results))   

def get_reviews():
    """Gets the list of people who reviewed a product."""
    product_id = int(request.vars.product_id)
    results = []
    # We get directly the list of all the users who reviewed the product. 
    rows = db(db.reviews.product_id == product_id).select(db.reviews.ALL)

    for row in rows:
        results.append(dict(
            product_id=row.product_id,
            review=row.review,
            user_email=row.user_email,
            rating=row.rating,
            first_name=row.first_name,
            last_name=row.last_name
        ))
    # We return this list as a dictionary field, to be consistent with all other calls.
    return response.json(dict(reviews=results))

@auth.requires_signature(hash_vars=False)
def set_stars():
    """Sets the star rating of a product."""
    product_id = int(request.vars.product_id)
    rating = int(request.vars.rating)
    db.reviews.update_or_insert(
        (db.reviews.product_id == product_id) & (db.reviews.user_email == auth.user.email),
        product_id = product_id,
        user_email = auth.user.email,
        rating = rating
    )
    return "ok" # Might be useful in debugging.

@auth.requires_signature(hash_vars=False)
def set_cart():
    """Sets the cart for a user of a product."""
    product_id = int(request.vars.product_id)
    quantity = int(request.vars.quantity)
    cart = request.vars.cart
    db.shopping_cart.update_or_insert(
        (db.shopping_cart.product_id == product_id) & (db.shopping_cart.user_email == auth.user.email),
        product_id = product_id,
        quantity = quantity,
        user_email = auth.user.email,
        cart = cart
    )
    return "ok" # Might be useful in debugging.

# priv_folder = os.path.join(request.folder, 'private')
# key_file = os.path.join(priv_folder, 'stripe_keys.json')
# STRIPE_KEY_INFO = json.load(open(key_file))

def purchase():
    """Ajax function called when a customer orders and pays for the cart."""
    if not URL.verify(request, hmac_key=session.hmac_key):
        raise HTTP(500)
    # Creates the charge.
    import stripe
    stripe.set_app_info('Luca de Alfaro teaching site', version="2.0", url="http://www.soe.ucsc.edu/~luca")
    # Your secret key.
    stripe.api_key = STRIPE_KEY_INFO['private_key']
    token = json.loads(request.vars.transaction_token)
    amount = float(request.vars.amount)
    try:
        charge = stripe.Charge.create(
            amount=int(amount * 100),
            currency="usd",
            source=token['id'],
            description="Purchase",
        )
        logger.info("The charge was successful")
    except stripe.error.CardError as e:
        logger.info("The card has been declined.")
        logger.info("%r" % traceback.format_exc())
        return response.json(dict(result="nok"))
    db.customer_order.insert(
        customer_info=request.vars.customer_info,
        transaction_token=json.dumps(token),
        cart=request.vars.cart)
    return response.json(dict(result="ok"))

@auth.requires_login()
def view_orders():
    q = db.customer_order # This queries for all products.
    db.customer_order.customer_info.represent = lambda v, r: nicefy(v)
    db.customer_order.transaction_token.represent = lambda v, r: nicefy(v)
    db.customer_order.cart.represent = lambda v, r: nicefy(v)
    form = SQLFORM.grid(
        q,
        editable=True,
        create=True,
        user_signature=True,
        deletable=True,
        details=True,
    )
    return dict(form=form)
