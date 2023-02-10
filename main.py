from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)
db = SQLAlchemy()
db.init_app(app)


# TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        dictionary = {}
        for col in self.__table__.columns:
            dictionary[col.name] = getattr(self, col.name)
        return dictionary


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random")
def get_random_cafe():
    all_cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(all_cafes)
    # return jsonify(cafe={
    #     "name": random_cafe.name,
    #     "amenities": {
    #         "has_sockets": random_cafe.has_sockets,
    #         "has_wifi": random_cafe.has_wifi,
    #         "has_toilet": random_cafe.has_toilet,
    #         "can_take_calls": random_cafe.can_take_calls
    #     },
    #     "location": random_cafe.location,
    #     "map_url": random_cafe.map_url,
    #     "img_url": random_cafe.img_url,
    #     "seats": random_cafe.seats,
    #     "coffee_price": random_cafe.coffee_price
    #
    # })
    return jsonify(cafe=random_cafe.to_dict())


@app.route("/all")
def get_all_cafes():
    all_cafes = db.session.query(Cafe).all()
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])


@app.route("/search")
def find_cafes_in_location():
    loc = request.args.get('loc')
    all_cafes = db.session.query(Cafe).all()
    result = [cafe.to_dict() for cafe in all_cafes if cafe.location == loc.title()]
    if result:
        return jsonify(cafes=result)
    else:
        return jsonify(error=f"Sorry no cafes found in {loc.title()}")


# HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def add_cafe():
    try:
        new_cafe = Cafe(
            name=request.form.get("name"),
            map_url=request.form.get("map_url"),
            img_url=request.form.get("img_url"),
            location=request.form.get("loc"),
            has_sockets=bool(request.form.get("sockets")),
            has_toilet=bool(request.form.get("toilet")),
            has_wifi=bool(request.form.get("wifi")),
            can_take_calls=bool(request.form.get("calls")),
            seats=request.form.get("seats"),
            coffee_price=request.form.get("coffee_price"),
        )
        db.session.add(new_cafe)
        db.session.commit()
    except Exception as e:
        return jsonify(status={"error": e})
    return jsonify(success="You have successfully added new cafe to the database")


# HTTP PUT/PATCH - Update Record

@app.route("/update-price/<cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    cafe = db.session.query(Cafe).filter_by(id=cafe_id).first()
    if cafe:
        cafe.coffee_price = request.args.get('new_price')
        db.session.commit()
        return jsonify(success="New price successfully updated")
    else:
        return jsonify(error='Unable to update price. Cafe not found. '), 404


# HTTP DELETE - Delete Record
@app.route("/delete-cafe/<cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    if request.args.get("api_key") == "myTopSecretApiKey":
        cafe = db.session.query(Cafe).filter_by(id=cafe_id).first()
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(success="Cafe record successfully deleted")

        else:
            return jsonify(error='Unable to delete record from the database. Cafe not found. '), 404
    else:
        return jsonify(error="This request is unauthorised. You need a valid API key"), 403

if __name__ == '__main__':
    app.run(debug=True, port=5001)
