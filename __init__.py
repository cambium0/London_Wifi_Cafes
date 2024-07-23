import flask as fl
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_bootstrap import Bootstrap5
import flask_sqlalchemy as fsql
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, URLField, FileField, ValidationError
from wtforms.validators import DataRequired, URL
from werkzeug.utils import secure_filename
import os
import json

db = SQLAlchemy()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cafes.db"
db.init_app(app)
bootstrap = Bootstrap5(app)
all_cafes = {}
app.secret_key = "2383222l38409304949309903"

bool = False

class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, default=False)
    has_wifi = db.Column(db.Boolean, default=False)
    has_sockets = db.Column(db.Boolean, default=False)
    can_take_calls = db.Column(db.Boolean, default=False)
    coffee_price = db.Column(db.String(250), nullable=True)


class CafeForm(FlaskForm):

    ## CUSTOM VALIDATOR

    def validate_photo(form, field):
        filename = secure_filename(form.photo.data.filename)
        print(f"filename is {filename}")
        if '.' not in filename:
            raise ValidationError("Image name missing required filetype designator (.jpg, .png, .jpeg)")
        parts = filename.split('.')
        print(f"parts[1] is {parts[1]}")
        if parts[1] != 'jpg' and parts[1] != 'jpeg' and parts[1] != 'png':
            raise ValidationError("Image file type not allowed: only .jpg, .jpeg and .png types are allowed.")

    cafe = StringField('Cafe name', validators=[DataRequired()])
    mapUrl = URLField('Map URL', validators=[DataRequired(), URL()])
    # imgUrl = URLField('Image URL', validators=[DataRequired(), URL()])
    photo = FileField("Image", validators=[DataRequired()])
    neighborhood = StringField("Cafe neighborhood", validators=[DataRequired()])
    seats = StringField("Number of seats", validators=[DataRequired()])
    hasToilet = BooleanField("Toilets for customers")
    hasWifi = BooleanField("Customer wifi")
    hasSockets = BooleanField("Power Socket Availability")
    callsAllowed = BooleanField("Customers can use cell phones")
    coffeePrice = StringField("Cost of black coffee cup", validators=[DataRequired()])
    submit = SubmitField('Submit')


with app.app_context():
    db.create_all()

def jsonise(data):
    global all_cafes
    columns = [column.key for column in Cafe.__table__.columns]
    my_data = {"data": []}
    json_data = ""
    for record in data:
        a_record = {}
        for column in columns:
            a_record[column] = eval('record.' + column)
            print(f"a_record[{column}] is {a_record[column]}")
            record_json = json.dumps(a_record)
        my_data["data"].append(a_record)
        json_data = json.dumps(my_data)
        json_data = json.loads(json_data)
    return json_data


def read_csv_into_db():
    lines = []
    with open("cafes.csv", 'r') as f:
        lines = [line.rstrip() for line in f]
    columns = lines[0]
    for i in range(1, len(lines)):
        values = lines[i].split(',')
        true_indices = []
        false_indices = []
        for n in range(1, len(values)):
            if values[n] == '1' or values[n] == 1:
                true_indices.append(n)
        for n in range(1, len(values)):
            if values[n] == '0' or values[n] == 0:
                false_indices.append(n)
        for num in true_indices:
            values[num] = True

        for num in false_indices:
            values[num] = False
        with app.app_context():
            cafe = Cafe(id=values[0], name=values[1], map_url=values[2], img_url=values[3], location=values[4], has_sockets=values[5], has_toilet=values[6],
                has_wifi=values[7], can_take_calls=values[8], seats=values[9], coffee_price=values[10])
            db.session.add(cafe)
            db.session.commit()


@app.route('/')
def home():
    global all_cafes
    all_cafes.clear()
    # one-time only
    # read_csv_into_db()
    with app.app_context():
        result = db.session.execute(db.select(Cafe).order_by(Cafe.id)).scalars()
        all_cafes = jsonise(result.all())
        print(f"all_cafes is {all_cafes}")
        return render_template('index.html', Cafes_string=all_cafes)



@app.route("/add", methods=['GET', 'POST'])
def add():
    print("starting /add")
    form = CafeForm()
    img_path = os.getcwd() + '/flask_3/static/images'
    if form.validate_on_submit():
        with app.app_context():
            cafe = Cafe()
            cafe.name = form['cafe'].data
            cafe.map_url = form['mapUrl'].data
            file = form['photo'].data
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(img_path, filename))
                cafe.img_url = filename
            cafe.location = form['neighborhood'].data
            cafe.seats = form['seats'].data
            cafe.has_toilet = form['hasToilet'].data
            cafe.has_wifi = form['hasWifi'].data
            cafe.has_sockets = form['hasSockets'].data
            cafe.can_take_calls = form['callsAllowed'].data
            cafe.coffee_price = form['coffeePrice'].data
            db.session.add(cafe)
            db.session.commit()
        return redirect("/flask_app_3/")
    print(form.errors)
    return render_template('add.html', form=form)


@app.route("/delete/<this_id>", methods=['GET', 'POST'])
def delete(this_id):
    global all_cafes
    global all_cafes
    form = request.form
    with app.app_context():
        db.session.execute(db.delete(Cafe).where(Cafe.id == this_id))
        db.session.commit()
        return redirect("/flask_app_3/")


if __name__ == "__main__":
    app.run(debug=True)

