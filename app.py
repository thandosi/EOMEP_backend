# Thandokazi Nkohla

import hmac
import sqlite3


from flask import Flask, request, jsonify
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app, resoures={r"/api/*": {"origins": "*"}})
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'


class User(object):
    def __init__(self, id, username, password, client_email, phone_number, address):
        self.id = id
        self.username = username
        self.password = password
        self.client_email = client_email
        self.phone_number = phone_number
        self.address = address


# Creating register table---------------------------------------------------


def init_user_table():
    conn = sqlite3.connect('reservation.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS borders(user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "client_name TEXT NOT NULL,"
                 "client_surname TEXT NOT NULL,"
                 "client_username TEXT NOT NULL,"
                 "client_password TEXT NOT NULL, address TEXT NOT NULL, "
                 "phone_number INT NOT NULL,"
                 " client_email TEXT NOT NULL,"
                 "id_flight INTEGER,"
                 "FOREIGN KEY (id_flight)REFERENCES boarding_tickets(id_flight))")
    print("user table created")
    conn.close()

# creating admin log ----------------------------------------


def init_admin_table():
    with sqlite3.connect('reservation.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS admin (id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "admin_username TEXT NOT NULL,"
                     "admin_password TEXT NOT NULL)")
    print("Login table created successfully.")


# Creating Login table-------------------------------------------------------


def init_post_table():
    with sqlite3.connect('reservation.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS login (id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "client_username TEXT NOT NULL,"
                     "client_password TEXT NOT NULL,"
                     "login_date TEXT NOT NULL)")
    print("Login table created successfully.")


# Creating flights table----------------------------------------------------


def init_product_table():
    with sqlite3.connect('reservation.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS boarding_tickets(id_flight INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "airline TEXT NOT NULL,"
                     "price TEXT NOT NULL,"
                     "from_where TEXT NOT NULL,"
                     "to_where TEXT NOT NULL,"
                     "duration,"
                     "departure,"
                     "accommodation INTEGER,"
                     "arrival,"
                     "FOREIGN KEY (accommodation)REFERENCES hotels(accommodation))")
    print("flights table created successfully.")

# Table accommodation ----------------------------------------------------


def init_accommodation_table():
    with sqlite3.connect('reservation.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS hotels (accommodation INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "address,"
                     "rooms TEXT NOT NULL,"
                     "price TEXT NOT NULL,"
                     "bathroom TEXT NOT NULL,"
                     "parking,"
                     "image,"
                     "check_in,"
                     "check_out)")
    print("accommodation table created successfully.")

# tables---------------------------------------------------------------


init_product_table()
init_user_table()
init_accommodation_table()
init_post_table()
init_admin_table()


def fetch_users():
    with sqlite3.connect('reservation.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM borders")
        users = cursor.fetchall()

        new_data = []

        for data in users:
            new_data.append(User(data[0], data[3], data[4], data[5], data[6], data[7]))
    return new_data


borders = fetch_users()

username_table = {u.username: u for u in borders}
userid_table = {u.id: u for u in borders}


def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


jwt = JWT(app, authenticate, identity)


@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity

# Client register--------------------------------------------------------------------

@app.route('/client-registration/', methods=["POST"])
@cross_origin()
def user_registration():
    response = {}

    if request.method == "POST":
        first_name = request.form['client_name']
        client_surname = request.form['client_surname']
        username = request.form['client_username']
        password = request.form['client_password']
        address = request.form['address']
        phone_number = request.form['phone_number']
        client_email = request.form['client_email']
        id_flight = request.form['id_flight']
        with sqlite3.connect("reservation.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO borders("
                           "client_name,"
                           "client_surname,"
                           "client_username,"
                           "client_password,"
                           "address,phone_number,"
                           "id_flight,"
                           "client_email) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                           (first_name, client_surname, username, password, address, phone_number, id_flight, client_email
                            ))
            conn.commit()
            response["message"] = "success"
            response["status_code"] = 201

        return response

# creating flights---------------------------------------------------------------------------


@app.route('/create-flights/', methods=["POST"])
# @jwt_required()
def create_products():
    response = {}

    if request.method == "POST":
        airline = request.form['airline']
        price = request.form['price']
        from_where = request.form['from_where']
        to_where = request.form['to_where']
        duration = request.form['duration']
        departure = request.form['departure']
        arrival = request.form['arrival']

        with sqlite3.connect('reservation.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO boarding_tickets("
                           "airline,"
                           "price,"
                           "from_where, to_where, duration, departure, arrival) VALUES(?, ?, ?, ?, ?, ?, ?)", (airline, price, from_where, to_where, duration, departure, arrival))
            conn.commit()
            response["status_code"] = 201
            response['description'] = "flight added successfully"
        return response

# creating accommodation----------------------------------------------------------


@app.route('/creating-hotels/', methods=["POST"])
def user_hotels():
    response = {}

    if request.method == "POST":
        address = request.form['address']
        rooms = request.form['rooms']
        price = request.form['price']
        bathroom = request.form['bathroom']
        parking = request.form['parking']
        image = request.form['image']
        check_in = request.form['check_in']
        check_out = request.form['check_out']

        with sqlite3.connect("reservation.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO hotels("
                           "address,"
                           "rooms,"
                           "price,"
                           "bathroom,"
                           "parking,"
                           "image,"
                           "check_in,"
                           "check_out) VALUES(?, ?, ?, ?, ?, ?,?, ?)",
                           (address, rooms, price, bathroom, parking, image, check_in, check_out))
            conn.commit()
            response["message"] = "success"
            response["status_code"] = 201

        return response

# Getting users


@app.route('/get-borders/', methods=["GET"])
def get_users():
    response = {}
    with sqlite3.connect("reservation.db") as conn:
        cursor = conn.cursor()
        cursor.row_factory = sqlite3.Row

        cursor.execute("SELECT * FROM borders")

        posts = cursor.fetchall()
        accumulator = []

        for i in posts:
            accumulator.append({k: i[k] for k in i.keys()})

    response['status_code'] = 200
    response['data'] = tuple(accumulator)
    return jsonify(response)

# get flights


@app.route('/get-flight/', methods=["GET"])
@cross_origin()
def get_point_of_sales():
    response = {}
    with sqlite3.connect("reservation.db") as conn:
        cursor = conn.cursor()
        cursor.row_factory = sqlite3.Row
        cursor.execute("SELECT * FROM boarding_tickets ")

        posts = cursor.fetchall()

        accumulator = []

        for i in posts:
            accumulator.append({k: i[k] for k in i.keys()})

    response['status_code'] = 200
    response['data'] = tuple(accumulator)
    return jsonify(response)

# get hotels


@app.route('/get-hotels/', methods=["GET"])
@cross_origin()
def get_hotels():
    response = {}
    with sqlite3.connect("reservation.db") as conn:
        cursor = conn.cursor()
        cursor.row_factory = sqlite3.Row
        cursor.execute("SELECT * FROM hotels ")

        posts = cursor.fetchall()

        accumulator = []

        for i in posts:
            accumulator.append({k: i[k] for k in i.keys()})

    response['status_code'] = 200
    response['data'] = tuple(accumulator)
    return jsonify(response)

# Updating flights


@app.route('/update-flights/<int:post_id>/', methods=["PUT"])
# @jwt_required()
def edit_post(post_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('reservation.db') as conn:
            incoming_data = dict(request.form)
            put_data = {}

            if incoming_data.get("airline") is not None:
                put_data["airline"] = incoming_data.get("airline")
                with sqlite3.connect('reservation.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET airline =? WHERE id=?", (put_data["airline"], post_id))
                    conn.commit()
                    response['message'] = "Update was successfully"
                    response['status_code'] = 200
            if incoming_data.get("price") is not None:
                put_data['price'] = incoming_data.get('price')
                with sqlite3.connect('reservation.db') as conn:
                    cursor = conn.cursor()
                    conn.commit()
                    cursor.execute("UPDATE product SET price =? WHERE id=?", (put_data["price"], post_id))

                    response["price"] = "price was updated successfully"
                    response["status_code"] = 200

            if incoming_data.get("from_where") is not None:
                put_data['from_where'] = incoming_data.get('from_where')

                with sqlite3.connect('reservation.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET from_where =? WHERE id=?", (put_data["from_from"], post_id))
                    conn.commit()

                    response["description"] = "description was updated successfully"
                    response["status_code"] = 200

                    if incoming_data.get("to_where") is not None:
                        put_data['to_where'] = incoming_data.get('to_where')

                        with sqlite3.connect('reservation.db') as conn:
                            cursor = conn.cursor()
                            cursor.execute("UPDATE product SET to_where =? WHERE id=?",
                                           (put_data["to_from"], post_id))
                            conn.commit()

                            response["description"] = "destination was updated successfully"
                            response["status_code"] = 200

                            if incoming_data.get("departure") is not None:
                                put_data['departure'] = incoming_data.get('departure')

                                with sqlite3.connect('reservation.db') as conn:
                                    cursor = conn.cursor()
                                    cursor.execute("UPDATE product SET departure =? WHERE id=?",
                                                   (put_data["departure"], post_id))
                                    conn.commit()

                                    response["description"] = "departure was updated successfully"
                                    response["status_code"] = 200

                                    if incoming_data.get("arrival") is not None:
                                        put_data['arrival'] = incoming_data.get('arrival')

                                        with sqlite3.connect('reservation.db') as conn:
                                            cursor = conn.cursor()
                                            cursor.execute("UPDATE product SET arrival =? WHERE id=?",
                                                           (put_data["arrival"], post_id))
                                            conn.commit()

                                            response["description"] = "arrival was updated successfully"
                                            response["status_code"] = 200
    return response

# deleting


@app.route("/delete-products/<int:accommodation>/", methods=["PUT"])
# @jwt_required()
def delete_post(accommodation):
    response = {}
    if request.method == "PUT":
        with sqlite3.connect("reservation.db") as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM hotels WHERE accommodation=" + str(accommodation))
            conn.commit()
            response['status_code'] = 200
            response['message'] = "deleted successfully."
    return response


if __name__ == '__main__':
    app.run(debug=True)
