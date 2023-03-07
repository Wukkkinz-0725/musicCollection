from flask import Flask, Response, request, redirect, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from model import db, UserModel, CollectionModel, DBClient, Serializer
import json
import re
import os

# init user app
user_app = Flask(__name__)
CORS(user_app)

# connect to db
rds = DBClient()
user_app.config['SQLALCHEMY_DATABASE_URI'] = rds.get_uri()

# init db
db.init_app(user_app)

# Set up models
with user_app.app_context():
    db.create_all()

# setup bcrypt
bcrypt = Bcrypt(user_app)

# check email format
def check_email(email):
    if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email):
        return False
    else:
        return True

@user_app.route("/users/all", methods=["get"])
def get_all_users():
    # get query parameters
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 20, type=int)

    if (limit < 10 or limit > 50):
        # Use default to prevent client stupid action
        limit = 20
        
    usrs = UserModel.query.offset(offset).limit(limit).all()
    return Response(json.dumps(Serializer.serialize_list(usrs)), status=200, content_type="application.json")


@user_app.route("/users/create", methods=["post"])
def create_user():
    # check request type
    content_type = request.headers.get('Content-Type')
    if (content_type != 'application/json'):
        return Response('Content-Type Not Supported', status=400, content_type="text/plain")
    
    # get request body
    body = request.json

    # check if the request body is valid
    if body["email"] is None or not check_email(body["email"]) or body["password"] is None:
        return Response("Invalid Request", status=400, content_type="text/plain")

    # we should save the password in encrypted form
    body["password"] = bcrypt.generate_password_hash(body["password"])

    # we could determine that all the fields are required, even if the field is None
    usr = UserModel(body['email'], body['username'], body['password'], body['age'], body['description'])
    db.session.add(usr)
    db.session.commit()
    result = usr.id

    if result:
        rsp = Response("Creation is successful", status=200, content_type="application.json")
    else:
        rsp = Response("Creation Failed", status=400, content_type="text/plain")

    return rsp

@user_app.route("/users/query/<uid>", methods=["GET"])
def get_user(uid):
    # email required
    # if not email or not check_email(email):
    #     result = {'result' : 'You need to provide your email!'}
    #     rsp = Response(json.dumps(result), status=400, content_type="application.json")
    #     return rsp

    # uid required
    if not uid:
        result = {'result' : 'You need to provide your user id!'}
        rsp = Response(json.dumps(result), status=400, content_type="application.json")
        return rsp

    # get the result from db
    usr = UserModel.query.filter_by(id=uid).first()

    if usr:
        rsp = Response(json.dumps(usr.serialize()), status=200, content_type="application.json")
    else:
        rsp = Response("Not Found", status=404, content_type="text/plain")

    return rsp


@user_app.route("/users/update/<uid>", methods=["post"])
def update_user(uid):
    # check request type
    content_type = request.headers.get('Content-Type')
    if (content_type != 'application/json'):
        return Response('Content-Type Not Supported', status=400, content_type="text/plain")

    # email required
    # if not email or not check_email(email):
    #     result = {'result' : 'You need to provide your email!'}
    #     rsp = Response(json.dumps(result), status=400, content_type="application.json")
    #     return rsp

    # uid required
    if not uid:
        result = {'result' : 'You need to provide your user id!'}
        rsp = Response(json.dumps(result), status=400, content_type="application.json")
        return rsp
    
    # get request body
    body = request.json

    # check if the request body is valid
    if "email" in body:
        return Response("You cannot change your email", status=400, content_type="text/plain")
    elif "id" in body:
        return Response("You cannot change your user id", status=400, content_type="text/plain")

    # communication with db
    if "password" in body:
        body["password"] = bcrypt.generate_password_hash(body["password"])
    
    result = UserModel.query.filter_by(id=uid).update(body)
    db.session.commit()

    if result:
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
    else:
        rsp = Response("Update Failed", status=400, content_type="text/plain")

    return rsp


@user_app.route("/users/delete/<uid>", methods=["post"])
def delete_user(uid):
    # email required
    # if not email or not check_email(email):
    #     result = {'result' : 'You need to provide your email!'}
    #     rsp = Response(json.dumps(result), status=400, content_type="application.json")
    #     return rsp

    # uid required
    if not uid:
        result = {'result' : 'You need to provide your user id!'}
        rsp = Response(json.dumps(result), status=400, content_type="application.json")
        return rsp

    # communication with db
    try:
        UserModel.query.filter_by(id=uid).delete()
        db.session.commit()
        rsp = Response("Delete Successfully", status=200, content_type="text/plain")
    except:
        rsp = Response("Delete Failed", status=400, content_type="text/plain")    

    return rsp

@user_app.route("/users/<uid>/collections", methods=["get"])
def get_user_collections(uid):
     # email required
    # if not email or not check_email(email):
    #     result = {'result' : 'You need to provide your email!'}
    #     rsp = Response(json.dumps(result), status=400, content_type="application.json")
    #     return rsp

    # uid required
    if not uid:
        result = {'result' : 'You need to provide your user id!'}
        rsp = Response(json.dumps(result), status=400, content_type="application.json")
        return rsp

    # get query parameters
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 20, type=int)
    
    if (limit < 10 or limit > 50):
        # Use default to prevent client stupid action
        limit = 20

    collectionList = UserModel.query \
        .join(CollectionModel, UserModel.id==CollectionModel.uid) \
        .with_entities(CollectionModel.colid, CollectionModel.sid, CollectionModel.uid, CollectionModel.song_name) \
        .filter(UserModel.id == uid) \
        .distinct() \
        .offset(offset) \
        .limit(limit) \
        .all()

    collectionResult = [dict(collection._mapping) for collection in collectionList]
    rsp = Response(json.dumps(collectionResult), status=200, content_type="application.json")
    return rsp

@user_app.route("/user/<uid>/songs", methods=["get"])
def get_user_songs(uid):
    # uid required
    if not uid:
        result = {'result' : 'You need to provide your user id!'}
        rsp = Response(json.dumps(result), status=400, content_type="application.json")
        return rsp

    # get query parameters
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 20, type=int)

    if (limit < 10 or limit > 50):
        # Use default to prevent client stupid action
        limit = 20
    
    songIdList = UserModel.query \
        .join(CollectionModel, UserModel.id==CollectionModel.uid) \
        .with_entities(CollectionModel.sid) \
        .filter(UserModel.id == uid) \
        .distinct() \
        .offset(offset) \
        .limit(limit) \
        .all()
    
    songIdResult = [dict(songId._mapping) for songId in songIdList]
    rsp = Response(json.dumps(songIdResult), status=200, content_type="application.json")
    return rsp


@user_app.route("/users/<uid>/comments", methods=["get"])
def get_user_comments(uid):
    # email required
    # if not email or not check_email(email):
    #     result = {'result' : 'You need to provide your email!'}
    #     rsp = Response(json.dumps(result), status=400, content_type="application.json")
    #     return rsp

    # uid required
    if not uid:
        result = {'result' : 'You need to provide your user id!'}
        rsp = Response(json.dumps(result), status=400, content_type="application.json")
        return rsp

    # get query parameters
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 10, type=int)

    if (limit < 10 or limit > 50):
        # Use default to prevent client stupid action
        limit = 20

    rsp = redirect("http://test-env.eba-bq3zvah2.us-east-1.elasticbeanstalk.com/comments/query/uid/" + uid + "?offset=" + str(offset) + "&limit=" + str(limit), code=302)
    return rsp

#  ----------------
# | collection API |
#  ----------------

@user_app.route("/collections/create", methods=["POST"])
def create_collection():
    content_type = request.headers.get('Content-Type')
    if (content_type != 'application/json'):
        return Response('Content-Type Not Supported', status=400, content_type="text/plain")
    
    # get request body
    body = request.json

    # we could determine that all the fields are required, even if the field is None
    collection = CollectionModel(body['uid'], body['sid'], body['song_name'])
    db.session.add(collection)
    db.session.commit()
    result = collection.colid

    if result:
        rsp = Response("Creation is successful", status=200, content_type="application.json")
    else:
        rsp = Response("Creation Failed", status=400, content_type="text/plain")
    return rsp

@user_app.route("/collections/delete/colid/<colid>", methods=["POST"])
def delete_collection_by_colid(colid):
    if not colid:
        result = {'result' : 'colid is empty! Please provide the collection id.'}
        rsp = Response(json.dumps(result), status=400, content_type="application.json")
        return rsp

    try:
        CollectionModel.query.filter_by(colid=colid).delete()
        db.session.commit()
        rsp = Response("Delete Successfully", status=200, content_type="text/plain")
    except:
        rsp = Response("Delete Failed", status=400, content_type="text/plain")    
    return rsp

@user_app.route("/collections/delete/colid/<uid>", methods=["POST"])
def delete_collection_by_uid(uid):
    if not uid:
        result = {'result' : 'uid is empty! Please provide the collection id.'}
        rsp = Response(json.dumps(result), status=400, content_type="application.json")
        return rsp

    try:
        CollectionModel.query.filter_by(uid=uid).delete()
        db.session.commit()
        rsp = Response("Delete Successfully", status=200, content_type="text/plain")
    except:
        rsp = Response("Delete Failed", status=400, content_type="text/plain")    
    return rsp

@user_app.route("/collections/query/colid/<colid>", methods=["GET"])
def get_collection_by_colid(colid):
    if not colid:
        result = {'result' : 'colid is empty! Please provide the collection id.'}
        rsp = Response(json.dumps(result), status=400, content_type="application.json")
        return rsp
    collection = CollectionModel.query.filter_by(colid=colid).first()
    if collection:
        rsp = Response(json.dumps(collection.serialize()), status=200, content_type="application.json")
    else:
        rsp = Response("Not Found", status=404, content_type="text/plain")
    return rsp

@user_app.route("/collections/query/uid/<uid>", methods=["GET"])
def get_collections_by_uid(uid):
    if not uid:
        result = {'result' : 'uid is empty! Please provide the user id.'}
        rsp = Response(json.dumps(result), status=400, content_type="application.json")
        return rsp
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 20, type=int)

    if (limit < 10 or limit > 50):
        # Use default to prevent client stupid action
        limit = 20
    collections = CollectionModel.query.filter_by(uid=uid).offset(offset).limit(limit).all()
    if collections:
        rsp = Response(json.dumps(Serializer.serialize_list(collections)), status=200, content_type="application.json")
    else:
        rsp = Response("Not Found", status=404, content_type="text/plain")
    return rsp

@user_app.route("/collections/query/sid/<sid>", methods=["GET"])
def get_collections_by_sid(sid):
    if not sid:
        result = {'result' : 'sid is empty! Please provide the song id.'}
        rsp = Response(json.dumps(result), status=400, content_type="application.json")
        return rsp
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 20, type=int)

    if (limit < 10 or limit > 50):
        # Use default to prevent client stupid action
        limit = 20
    collections = CollectionModel.query.filter_by(sid=sid).offset(offset).limit(limit).all()
    if collections:
        rsp = Response(json.dumps(Serializer.serialize_list(collections)), status=200, content_type="application.json")
    else:
        rsp = Response("Not Found", status=404, content_type="text/plain")
    return rsp

@user_app.route("/collections/all", methods=["GET"])
def get_all_collections():
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 20, type=int)

    if (limit < 10 or limit > 50):
        # Use default to prevent client stupid action
        limit = 20
    collections = CollectionModel.query.offset(offset).limit(limit).all()
    if collections:
        rsp = Response(json.dumps(Serializer.serialize_list(collections)), status=200, content_type="application.json")
    else:
        rsp = Response("Not Found", status=404, content_type="text/plain")
    return rsp


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    user_app.run(host="localhost", port=port)