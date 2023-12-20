from flask import Flask, jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid
import jwt
import datetime
from functools import wraps
import os


app = Flask(__name__)

app.config['SECRET_KEY']='blahblahblah'
db_path = os.getcwd()+r'\inmar_db.sqlite'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+db_path

db = SQLAlchemy(app)


class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	pub_id = db.Column(db.String(100),)
	name = db.Column(db.String(100), unique=True)
	password = db.Column(db.String(100))	
	admin = db.Column(db.Boolean)

class Location(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100))
	deparment = db.Column(db.String(100))
	category = db.Column(db.String(100))
	sub_category = db.Column(db.String(100))


def token_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		token = None
		if 'x-access-token' in request.headers:
			token = request.headers['x-access-token']
		if not token:
			return jsonify({'message': "Token required!!!!!"})
		try:
			data = jwt.decode(token, app.config['SECRET_KEY'])
			current_user = User.query.filter_by(pub_id=data['pub_id']).first()
		except:
			return jsonify({'message': 'Token is invalid'}), 401
		return f(current_user, *args, **kwargs)
	return decorated


@app.route('/login')
def login():
	auth = request.authorization
	
	if not auth or not auth.username or not auth.password:
		return make_response('Could not verify', 401,{'WWW-Authnticate':'Basic realm="Login required!"'}),

	user = User.query.filter_by(name=auth.username).first()
	if not user:
		return make_response('Could not verify', 401,{'WWW-Authnticate':'Basic realm="Login required!"'})

	if user and auth.password:
		token = jwt.encode({'pub_id':user.pub_id, 
							'exp': datetime.datetime.utcnow()+datetime.timedelta(minutes=120) 
							}, 
							app.config['SECRET_KEY']
				)

		return jsonify({'token': token.decode('UTF-8')})

	return make_response('Could not verify', 401,{'WWW-Authnticate':'Basic realm="Login required!"'})


@app.route('/api/users', methods=['GET'])
@token_required
def get_all_user(current_user):

	if not current_user.admin:
		return jsonify({'message': "Not authorized to fetch data!!"})

	users = User.query.all()
	users_list = []
	for user in users:
		user_data = {}
		user_data['pub_id'] = user.pub_id
		user_data['name'] = user.name
		user_data['admin'] = user.admin
		users_list.append(user_data)
	return jsonify({'Users': users_list})


@app.route('/api/user', methods=['POST'])
def create_user():

	data = request.get_json()
	myuuid = uuid.uuid4()

	new_user = User(pub_id=str(myuuid), name=data['name'], password=data['password'], admin=False)
	db.session.add(new_user)
	db.session.commit()
	return jsonify({'message': 'User created successfully!'})


@app.route('/api/user/<pub_id>', methods=['GET'])
@token_required
def get_user_by_id(current_user, pub_id):

	if not current_user.admin:
		return jsonify({'message': "Not authorized to fetch data!!"})

	user = User.query.filter_by(pub_id=pub_id).first()
	if not user:
		jsonify({'message': 'User not found!'})

	user_list = []
	user_data ={}
	user_data['pub_id'] = user.pub_id
	user_data['name'] = user.name
	user_data['admin'] = user.admin
	user_list.append(user_data)

	return jsonify({'user': user_list})


@app.route('/api/user/<pub_id>', methods=['PUT'])
@token_required
def update_user(current_user, pub_id):

	if not current_user.admin:
		return jsonify({'message': "Not authorized to update data!!"})

	user = User.query.filter_by(pub_id=pub_id).first()
	if not user:
		return jsonify({'message': 'User not found!'})

	user.admin = True
	db.session.commit()
	return jsonify({'message': 'User data updated successfully!'})


@app.route('/api/user/<pub_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, pub_id):

	if not current_user.admin:
		return jsonify({'message': "Not authorized to fetch data!!"})

	user = User.query.filter_by(pub_id=pub_id).first()
	if not user:
		return jsonify({'message': 'User not found!'})
	db.session.delete(user)
	db.session.commit()
	return jsonify({'message': 'Deleted user successfully!'})


@app.route('/api/location', methods=['POST'])
@token_required
def create_location(current_user):

	if not current_user.admin:
		return jsonify({'message': "Not authorized to create location!!"})

	data = request.get_json()

	new_location = Location(name=data['name'], 
							deparment=data['department'], 
							category=data['category'], 
							sub_category=data['sub_category']
					)
	db.session.add(new_location)
	db.session.commit()

	return jsonify({'message': 'Location created successfully!'})


@app.route('/api/locations', methods=['GET'])
# @token_required
def get_locations():

	## checking the authorization to to fetch or not
	# Commented to check the non authiration pull.
	# if not current_user.admin:
	# 	return jsonify({'message': "Not authorized to fetch data!!"})

	locations = Location.query.all()
	if locations:

		location_list = []
		for location in locations:
			location_data = {}
			location_data['id'] = location.id
			location_data['name'] = location.name
			location_data['department'] = location.deparment
			location_data['category'] = location.category
			location_data['sub_category'] = location.sub_category
			location_list.append(location_data)
		return jsonify({'Locations': location_list})

	return jsonify({'Locations': 'No data available!'})


@app.route('/api/location/<id>', methods=['GET'])
# @token_required
def get_locations_by_id(id):

	# if not current_user.admin:
	# 	return jsonify({'message': "Not authorized to fetch data!!"})

	location = Location.query.filter_by(id=id).first()

	if not location:
		jsonify({'message': 'Location not found!'})

	location_list = []
	location_data ={}
	location_data['id'] = location.id
	location_data['name'] = location.name
	location_data['department'] = location.deparment
	location_data['category'] = location.category
	location_data['sub_category'] = location.sub_category
	location_list.append(location_data)

	return jsonify({'Location': location_list})


@app.route('/api/location/<id>', methods=['PUT'])
@token_required
def udpate_location(current_user, id):

	if not current_user.admin:
		return jsonify({'message': "Not authorized to create location!!"})

	data = request.get_json()

	location = Location.query.filter_by(id=id).first()

	if not location:
		jsonify({'message': 'Location not found!'})

	
	if data.get('name'):
		location.name = data['name']
	
	if data.get('department'):
		location.deparment = data['department']

	if data.get('category'):
		location.category = data['category']
		
	if data.get('sub_category'):
		location.sub_category = data['sub_category']

	db.session.commit()
	return jsonify({'message': 'Record updated successfully!!!'})



@app.route('/api/location/<id>', methods=['DELETE'])
@token_required
def delete_location(current_user, id):

	if not current_user.admin:
		return jsonify({'message': "Not authorized to fetch data!!"})

	location = Location.query.filter_by(id=id).first()
	if not user:
		return jsonify({'message': 'Location not found!'})
	db.session.delete(location)
	db.session.commit()
	return jsonify({'message': 'Deleted Location successfully!'})


if __name__ == '__main__':
	app.run(debug=True)