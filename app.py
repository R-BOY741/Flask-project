import hmac
import sqlite3
import datetime

from flask import Flask, request, jsonify
from flask_jwt import JWT, jwt_required, current_identity

from flask_cors import CORS


# Function to help format data from database into dictionary objects
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


def init_user_table():
    conn = sqlite3.connect('online_store.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS user("
                 "user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "first_name TEXT NOT NULL,"
                 "last_name TEXT NOT NULL,"
                 "username TEXT NOT NULL,"
                 "password TEXT NOT NULL)")
    print("user table created successfully")
    conn.close()


# def fetch_users():
#     with sqlite3.connect('online_store.db') as conn:
#         cursor = conn.cursor()
#         cursor.execute("SELECT * FROM user")
#         users = cursor.fetchall()
#
#         new_data = []
#
#         for data in users:
#             new_data.append(User(data[0], data[3], data[4]))
#     return new_data


def init_items_table():
    with sqlite3.connect('online_store.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "name TEXT NOT NULL,"
                     "price TEXT NOT NULL,"
                     "type TEXT NOT NULL,"
                     "description TEXT NOT NULL,"
                     "image TEXT NOT NULL,"
                     "date_created TEXT NOT NULL)")
    print("blog table created successfully.")


init_user_table()
init_items_table()




# users = fetch_users()

# username_table = {u.username: u for u in users}
# userid_table = {u.id: u for u in users}


# def authenticate(username, password):
#     user = username_table.get(username, None)
#     if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
#         return user


# def identity(payload):
#     user_id = payload['identity']
#     return userid_table.get(user_id, None)


app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'

CORS(app)

# jwt = JWT(app, authenticate, identity)


# @app.route('/protected')
# @jwt_required()
# def protected():
#     return '%s' % current_identity


@app.route('/user-registration/', methods=["POST", "PATCH"])
def user_registration():
    response = {}

    if request.method == "POST":
        try:

            first_name = request.json['first_name']
            last_name = request.json['last_name']
            username = request.json['username']
            password = request.json['password']

            with sqlite3.connect("online_store.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO user("
                               "first_name,"
                               "last_name,"
                               "username,"
                               "password) VALUES(?, ?, ?, ?)", (first_name, last_name, username, password))
                conn.commit()
                response["message"] = "success"
                response["status_code"] = 201
        except ValueError:
            response["message"] = "Error in backend"
            response["status_code"] = 400
        return response

    # LOGIN
    if request.method == "PATCH":
        username = request.json["username"]
        password = request.json["password"]

        with sqlite3.connect("online_store.db") as conn:
            conn.row_factory = dict_factory
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user WHERE username=? AND password=?", (username, password))

            user = cursor.fetchone()

        response["status_code"] = 200
        response["data"] = user
        return response


@app.route('/create-items/', methods=["POST"])
# @jwt_required()
def create_items():
    response = {}

    if request.method == "POST":
        name = request.json['name']
        price = request.json['price']
        _type = request.json['type']
        image = request.json['image']
        description = request.json['description']

        date_created = datetime.datetime.now()

        with sqlite3.connect('online_store.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO items("
                           "name,"
                           "price,"
                           "type,"
                           "description,"
                           "image,"
                           "date_created) VALUES(?, ?, ?, ?, ?, ?)", (name, price, _type, description, image, date_created))
            conn.commit()
            response["status_code"] = 201
            response['description'] = "items added succesfully"
        return response


@app.route('/get-items/', methods=["GET"])
def get_items():
    response = {}
    with sqlite3.connect("online_store.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items")

        posts = cursor.fetchall()

        response['status_code'] = 200
        response['data'] = posts
    return response


@app.route("/delete-items/<int:items_id>")
#@jwt_required()
def delete_items(items_id):
    response = {}
    with sqlite3.connect("online_store.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM items WHERE id=" + str(items_id))
        conn.commit()
        response['status_code'] = 200
        response['message'] = "Items deleted successfully."
    return response


@app.route('/edit-items/<int:items_id>/', methods=["PUT"])
#@jwt_required()
def edit_items(items_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('online_Store.db') as conn:
            incoming_data = dict(request.json)
            put_data = {}

            if incoming_data.get("name") is not None:
                put_data["name"] = incoming_data.get("name")
                with sqlite3.connect('online_store.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE items SET name =? WHERE id=?", (put_data["name"], items_id))
                    conn.commit()
                    response['message'] = "Update was successfully added"
                    response['status_code'] = 200
            if incoming_data.get("price") is not None:
                put_data['price'] = incoming_data.get('price')

                with sqlite3.connect('online_store.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE items SET price =? WHERE id=?", (put_data["price"], items_id))
                    conn.commit()

                    response["price"] = "price updated successfully"
                    response["status_code"] = 200
    return response


@app.route('/filter-product/<type>/', methods=["GET"])
def filter_product(type):
    response = {}
    with sqlite3.connect("online_store.db") as conn:
        cursor = conn.cursor()
        # cursor.execute("SELECT * FROM items WHERE type LIKE '%" + type + "%'")
        cursor.execute("SELECT * FROM items")

        posts = cursor.fetchall()

        response['status_code'] = 200
        response['data'] = posts
    return jsonify(response)


@app.route('/get-items/<int:items_id>/', methods=["GET"])
def get_post(items_id):
    response = {}

    with sqlite3.connect("online_store.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items WHERE id=" + str(items_id))

        response["status_code"] = 200
        response["description"] = "items retrieved successfully"
        response["data"] = cursor.fetchone()

    return jsonify(response)


if __name__ == "__main__":
    app.debug = True
    app.run()



