from sanic import Sanic
from sanic.response import text
from sanic_mongodb_ext import MongoDbExtension
from umongo import MotorAsyncIOInstance
import configparser
from sanic_cors import CORS, cross_origin

config = configparser.ConfigParser()
config.read('config/configuration.cfg')

app = Sanic("simple-ecm")
#Configuration for MongoDB and uMongo
app.config.update({
    "MONGODB_DATABASE": config.get('mongodb', 'database',fallback='simpleecm'), # Make ensure that the `app` database is really exists
    "MONGODB_URI": config.get('mongodb', 'uri',fallback='mongodb://localhost:27017'),
    # You can also specify custom connection options.
    # For more details check the official docs: https://api.mongodb.com/python/3.7.0/api/pymongo/mongo_client.html#pymongo.mongo_client.MongoClient
    "MONGODB_CONNECT_OPTIONS": {
        "minPoolSize": 10,
        "maxPoolSize": 50,
    },
    "LAZY_UMONGO": MotorAsyncIOInstance(),
    "REQUEST_MAX_SIZE": 314572800
})


# Extensions
MongoDbExtension(app)

#allow CORS for all domains on all routes
CORS(app)