from flask import request, Response, render_template, session, send_from_directory
from app_insta import app
from app_insta.models.product import Product, MongoProductDao
from app_insta.models.user import User, MongoUserDao
from app_insta.models.image import Image, MongoImageDao
import json
from bson import ObjectId
import datetime

mongo_product_dao = MongoProductDao()
mongo_user_dao = MongoUserDao()
mongo_image_dao = MongoImageDao()

product_list = []

@app.route('/health', methods=['GET'])
def health():
    return 'healthy'


@app.route('/api/product', methods=['POST', 'GET'])
def products():
    if request.method == 'GET':
        matches = mongo_product_dao.search_by_name(request.args['name'])
        output_type = request.args.get('output_type', None)
        if output_type == 'html':
            return render_template('results.html', results=matches, query=request.args['name'], user_id=request.args.get('user_id'))
        else:
            return Response(str(matches), mimetype='application/json', status=200)
    elif request.method == 'POST':
        product = dict()
        operation_type  = request.form.get('operation_type', None)
        if operation_type is not None:
            if operation_type == 'add':
                product['_id'] = request.form['_id']
                product['name'] = request.form['name']
                product['description'] = request.form['description']
                product['price'] = request.form['price']
                # p = Product(12, request.form['name'], request.form['description'], request.form['price'])
                mongo_product_dao.save(product)
                return Response(str({'status': 'success'}), mimetype='application/json', status=200)
            elif operation_type == 'delete':
                _id = request.form.get('_id')
                mongo_product_dao.delete_by_id(_id)
                return Response(str({'status': 'success'}), mimetype='application/json', status=200)
            elif operation_type == 'update':
                p = Product(request.form['name'], request.form['description'], request.form['price'])
                mongo_product_dao.update_by_id(request.form['_id'], p)
                return Response(str({'status': 'success'}), mimetype='application/json', status=200)
                db.products.update_one(update={'$set': product}, filter={'name': currentname})
                return Response(str({'status': 'success'}), mimetype='application/json', status=200)


@app.route('/listProducts', methods=['GET'])
def list_all():
    matching_prods = mongo_product_dao.list_all_products()
    matches = []
    for prod in matching_prods:
        matches.append(prod)
    return Response(str(matches), mimetype='application/json', status=200)


@app.route('/addStuff', methods=['GET'])
def add_stuff():
    mongo_product_dao.add_stuff()
    return Response(str({'status': 'success'}), mimetype='application/json', status=200)


@app.route('/api/user/<action>', methods=['GET', 'POST'])
def user_actions(action):
    if action == 'login':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User(username, password, None, None, None, None, None, None, None, None, None, None, None, None, None)
        is_valid = mongo_user_dao.authenticate(user)
        session['user_id'] = str(mongo_user_dao.get_id_by_username(username))
        name = mongo_user_dao.find_user_name_by_credentials(user)
        if is_valid is not None and is_valid:
            return render_template('profile.html', sign_up_msg="Welcome to Facebook", name = name if name is not None else "Anonymous", user_id=mongo_user_dao.get_id_by_username(username))
        else:
            return render_template("index.html", message="Invalid Username/Password")
    elif action == 'signup':
        user = dict()
        user['name'] = request.form.get('name')
        user['email'] = request.form.get('email')
        user['username'] = request.form.get('username')
        user['password'] = request.form.get('password')
        does_user_exist = mongo_user_dao.check_if_user_exists(request.form.get('username'))
        if does_user_exist:
            return render_template("index.html", user_exists_msg="Username exists, please enter a different user name!")
        else:
            mongo_user_dao.save(user)
            session['user_id'] = str(mongo_user_dao.get_id_by_username(user['username']))
            return Response(str({'status' : 'User Added!'}), mimetype='application/json', status=200)

    else:
        status = {
            'status' : 'Invalid Action'
        }
        return Response(str(status), mimetype='application/json', status=400)


@app.route('/listUsers', methods=['GET'])
def list_all_users():
    matching_users = mongo_user_dao.list_all_users()
    matches = []
    if matching_users is not None:
        for user in matching_users:
            matches.append(user)
    return render_template('users.html', results=matches)


@app.route('/addUsers', methods=['GET'])
def add_users():
    mongo_user_dao.add_stuff()
    return Response(str({'status': 'success'}), mimetype='application/json', status=200)

@app.route('/api/cart', methods=['GET','POST'])
def cart():
   if request.args.get('op_type') == 'getcart':
       userId = request.args.get('user_id')
       matched_ids = mongo_user_dao.get_usercart_by_userid(userId)
       matches = mongo_product_dao.get_product_list_from_product_ids(matched_ids)
       return render_template('cart.html', user_id=userId, results=matches)
   elif request.args.get('op_type') == 'addToCart':
       pass
   else:
       user_id = request.args.get('user_id',None)
       product_id = request.args.get('product_id', None)

       user= mongo_user_dao.get_by_id(user_id)
       success = mongo_user_dao.add_to_cart(user_id,product_id)
       user_data = mongo_user_dao.get_by_id(user_id)

       return render_template('profile.html',name=user_data['name'],user_id=user_id)


# @app.route('/admin.html')
# def admin_tasks():
#     return render_template('../../static/admin.html')

@app.route('/app/authenticate', methods=['GET'])
def authenticate():
    username = request.args.get('username')
    password = request.args.get('password')
    user = User(username, password, None, None, None, None, None, None, None, None, None, None, None, None, None)
    is_valid = mongo_user_dao.authenticate(user)
    name = mongo_user_dao.find_user_name_by_credentials(user)
    if is_valid is not None and is_valid:
        _id = mongo_user_dao.get_id_by_username(username)
        data = {
             'status': True,
            '_id':_id
        }
        response = app.response_class(
            response=json.dumps(JSONEncoder().encode(data)),
            status=200,
            mimetype='application/json'
        )
    else:
        data = {
            'status': False,
            'error': 'Invalid Username/Password'
        }
        response = app.response_class(
            response=json.dumps(JSONEncoder().encode(data)),
            status=401,
            mimetype='application/json'
        )
    return response



@app.route('/app/getUserInfo', methods=['GET'])
def get_user_data():
    _id = request.args.get('_id')
    user = mongo_user_dao.get_by_id(_id)
    response = app.response_class(
        response=json.dumps(JSONEncoder().encode(user)),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/app/feed', methods=['POST', 'GET'])
def write_post():
    if request.method == 'POST':
        _id = request.form.get('_id')
        post_content = request.form.get('post')
        post = dict()
        post['post_content'] = post_content
        post['post_type'] = 'text/plain'
        post['updated_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        post['likes'] = 0
        post['comments'] = []
        post['user'] = _id
        post['size'] = len(post_content)
        mongo_user_dao.add_user_post(post, _id)
        success_msg = {'msg' : 'Thanks for posting'}
        response = app.response_class(
            response=json.dumps(JSONEncoder().encode(success_msg)),
            status=200,
            mimetype='application/json'
        )
    elif request.method == 'GET':
        _id = request.args.get('_id')
        posts = mongo_user_dao.get_user_posts(_id)
        if posts is None:
            posts = []
        response = app.response_class(
            response=json.dumps(JSONEncoder().encode(posts)),
            status=200,
            mimetype='application/json'
        )
    return response

@app.route('/addTestImages', methods=['GET'])
def add_test_images():
    mongo_image_dao.add_images()
    return Response(str({'status': 'success'}), mimetype='application/json', status=200)

@app.route('/popular', methods=['POST', 'GET'])
def get_popular_images():
    pm_arr = []
    pm_dict = dict()

    images = mongo_image_dao.get_all_images()
    for image in images:
        pm = calculate_popularity_metric(image)
        pm_dict['pm'] = pm
        pm_dict['image'] = image
        pm_arr.append(pm_dict)
        popular_images = find_top_10(pm_arr)
    response = app.response_class(
        response=json.dumps(JSONEncoder().encode(popular_images)),
        status=200,
        mimetype='application/json'
    )
    return response

def calculate_popularity_metric(image):
    views = image['views']
    number_of_comments = len(image['comments'])
    likes = image['likes']
    views_weightage = 0.2
    comments_weightage = 0.5
    likes_weightage = 0.3

    popularity_metric = number_of_comments * comments_weightage + views * views_weightage + likes * likes_weightage

    return popularity_metric

def find_top_10(pm_arr):
    print(pm_arr.sort(comparator, key=lambda k: k['name']))

def comparator(img1, img2):
    key1 = img1.keys()[0]
    key2 = img2.keys()[0]

    return key1 - key2


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

