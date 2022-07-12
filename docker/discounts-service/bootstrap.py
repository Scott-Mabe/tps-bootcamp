from flask import Flask
from models import Discount, DiscountType, Influencer, Tracker, db
import time
import datetime

import random
import os
import sys
import json
import names

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import words

DB_USERNAME = os.environ['POSTGRES_USER']
DB_PASSWORD = os.environ['POSTGRES_PASSWORD']
DB_HOST = os.environ['POSTGRES_HOST']
DB_NAME = os.environ['POSTGRES_DB']

discount_code = ['DATADOG20','GROOVYFRI10','HAPPYDOG15','CYBERDOG35','BULLDOG25','HYPERTUE']
discount_value = [20, 10, 15, 35, 25, 20] 

def create_app():
    """Create a Flask application"""
    app = Flask(__name__)
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://' + DB_USERNAME + ':' + DB_PASSWORD + '@' + DB_HOST + '/' + DB_NAME
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    initialize_database(app, db)
    return app


def initialize_database(app, db):
    """Drop and restore database in a consistent state"""
    with app.app_context():
        db.drop_all()
        db.create_all()

        for i in range(500):
            discount_type = DiscountType(words.get_random(),
                                         'price * %f' % random.random(),
                                         Influencer(names.get_full_name()))
            discount_name = words.get_random(random.randint(2,4))
            num = random.randint(0,5)
            discount = Discount(discount_name,
                                discount_code[num],
                                discount_value[num],
                                discount_type)
            db.session.add(discount)
            # add first Tracker info
            timeNow = datetime.datetime.now()
            first_tracker = Tracker(str(timeNow))
            db.session.add(first_tracker)

        first_discount_type = DiscountType('Save with Sherry', 
                                           'price * .8',
                                           Influencer('Sherry'))
        second_discount_type = DiscountType('Sunday Savings', 
                                           'price * .9',
                                           Influencer('Jerry'))
        third_discount_type = DiscountType('Monday Funday',
                                           'price * .95',
                                           Influencer('Candy'))
        first_discount = Discount('Black Friday', 
                                  'CYBERDOG35', 
                                  35,
                                  first_discount_type)

        second_discount = Discount('SWEET SUNDAY', 
                                   'HAPPYDOG15',
                                   15,
                                   second_discount_type)
        third_discount = Discount('Monday Funday', 
                                  'BULLDOG25', 
                                  25,
                                  third_discount_type)
        db.session.add(first_discount)
        db.session.add(second_discount)
        db.session.add(third_discount)
        db.session.commit()
