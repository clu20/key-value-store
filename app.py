from flask import Flask,jsonify, request, make_response, g
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)
newdict = {}

#Connect to database
def get_db():
    db = sqlite3.connect(DATABASE)
    return db

class key_value(Resource):
		conn = get_db()
		cur = conn.cursor()
		value = query_db('select value from dict where key = ?', (key,))
		db_key = query_db('select key from dict where key = ?', (key,))
		if db_key is None:
			conn.close()
			return make_response(jsonify(doesExist=False, error="Key does not exist", message="Error in GET"), 404)
		else:
			conn.close()
			return make_response(jsonify(doesExist=True, message="Retrieved successfully", value=value[0]), 200)

	def put(self, key):
		conn = get_db()
		if len(key) < 50:
			cur = conn.cursor()
			db_key = query_db('select key from dict where key = ?', (key,))
			msg = request.get_json()
			value = msg.get('value')
			if db_key is None: #insert a new key into db
				if value is None:
					conn.close()
					return make_response(jsonify(error="Value is missing",message="Error in PUT"), 400)
				else:
					cur.execute("INSERT INTO dict VALUES(?,?)", (key, value))
					conn.commit()
					conn.close()
					return make_response(jsonify(message="Added successfully",replaced=False), 201)
			else:#update a found key value
				if value is None:
					conn.close()
					return make_response(jsonify(error="Value is missing",message="Error in PUT"), 400)
				else:
					# sql = 'update dict set value = ? where key = ?'
					cur.execute('update dict set value = ? where key = ?', (value, key))
					conn.commit()
					conn.close()
					return make_response(jsonify(message="Updated successfully",replaced=True), 200)
		else:
			conn.close()
			return make_response(jsonify(error="Key is too long", message="Error in PUT"), 400)


	# Query Function
	def query_db(query, args=(), one=False):
    	cur = get_db().execute(query, args)
    	rv = cur.fetchone()
    	cur.close()
    	return (rv[0] if rv else None) if one else rv

	def delete(self, key):
		if newdict.pop(key,None) == None:
			return make_response(jsonify(doesExist=False, error="Key does not exist", message="Error in DELETE"), 404)
		else:
			return make_response(jsonify(doesExist=True, message="Deleted successfully"), 200)

api.add_resource(key_value, '/key-value-store/<key>')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8082)
