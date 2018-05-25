from pymongo import MongoClient
import re
from bson import ObjectId
import json
from app_insta.models.user import MongoUserDao
import random
import datetime

mongo_user_dao = MongoUserDao()

class Image:
    def __init__(self, user_id, image_type, updated_time, image_size, likes, comments, description, url, views):
        self.user_id = user_id
        self.image_type = image_type
        self.updated_time = updated_time
        self.image_size = image_size
        self.likes = likes
        self.comments = comments
        self.description = description
        self.url = url
        self.views = views


class MongoImageDao:
    def __init__(self):
        config = json.load(open('./config.json', 'r'))
        client = MongoClient(config['mongo_host'], config['mongo_port'])
        self.db = client[config['db_name']]

    def save(self, image):
        self.db.images.insert_one(image)

    def search_by_description(self, image_description):
        result_cursor = self.db.images.find({'image_content': re.compile(image_description, re.IGNORECASE)})
        matches = []
        for image in result_cursor:
            matches.append(image)
        return matches

    def delete_by_id(self, _id):
        self.db.images.delete_one({'_id': ObjectId(_id)})

    def update_by_id(self, _id, image):
        self.db.images.update_one({'_id': ObjectId(_id)}, {'$set': image})

    def list_all_images_for_user(self, user_id):
        user = mongo_user_dao.get_by_id(user_id)
        if 'images' in user:
            return user['images']
        else:
            return []

    def find_images_by_type(self, image_type):
        a = 3 if True else 1
        result_cursor = self.db.images.find({'image_type': image_type})
        matches = []
        for image in result_cursor:
            matches.append(image)
        return matches

    def get_by_id(self, _id):
        query = {
            '_id': ObjectId(_id)
        }
        cursor = self.db.images.find(query)
        image = cursor[0] if cursor.count() > 0 else None
        return image

    def get_id_by_image_url(self, url):
        cursor = self.db.images.find({'url': url})
        image_data = cursor[0] if cursor.count() > 0 else None
        if image_data is None:
            return "No images found"
        else:
            matches = []
            for image in cursor:
                matches.append(image)
            return matches[0]['_id']

    def get_comments_by_imageid(self, _id):
        image = self.get_by_id(_id)
        return image['comments']

    def add_images(self):
        k = 0
        users = []
        for i in range(46):
            flag_found = False
            if i % 10 == 0:
                k = 0
            image = dict()
            comments = []
            number_of_comments = random.randint(5,30)
            if i in range(1,9):
                for j in range(0, number_of_comments):
                    comments.append('comments' + str(j) + ' for image: image' + str(i) + '.png')
            else:
                for j in range(0, number_of_comments):
                    comments.append('comments' + str(j) + ' for image: image' + str(i) + '.jpg')
            _id = mongo_user_dao.get_id_by_username('username' + str(k))
            user = mongo_user_dao.get_by_id(_id)
            for iterated_user in users:
                if iterated_user['_id'] == user['_id']:
                    user = iterated_user
                    flag_found = True
                    break
            if flag_found == False:
                users.append(user)
            image['user_id'] = _id
            image['updated_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            image['image_size'] = str(random.randint(100, 300)) + ' KB'
            image['likes'] = random.randint(20, 100)
            image['comments'] = comments
            image['views'] = random.randint(20, 100)
            if i in range(1,9):
                image['description'] = 'This is the description for the image with name: image' + str(i) + '.png'
                image['url'] = '/images/image' + str(i) + '.png'
            else:
                image['description'] = 'This is the description for the image with name: image' + str(i) + '.jpg'
                image['url'] = '/images/image' + str(i) + '.jpg'

            if self.check_if_image_exists(image['url']) == False:
                self.db.images.insert_one(image)
                user_images = user['images'] if 'images' in user else None
                if user_images is None:
                    user_images = []
                    user['images'] = user_images
                user_images.append(image['_id'])
            k += 1

        for user in users:
            self.db.users.update_one({'_id': user['_id']}, {'$set': user})




    def check_if_image_exists(self, url):
        result_cursor = self.db.images.find({'url': url})
        matches = []
        for image in result_cursor:
            matches.append(image)
        if len(matches) > 0:
            return True
        else:
            return False

    def get_all_images(self):
        return self.db.images.find()
