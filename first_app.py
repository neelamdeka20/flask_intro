from flask import Flask
from flask import request
from flask import render_template
from flask import url_for
from flask import redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)
app.app_context().push()

app.config['DEBUG'] = True
app.config['ENV'] = 'development'
app.config['FLASK_ENV'] = 'development'
app.config['SECRET_KEY'] = 'ItShouldBeALongStringOfRandomCharacters'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:sqlrootpwd_123@localhost:3306/new_device_mgmt'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)


class DeviceCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(128))
    devices = db.relationship('Device', backref='devicecategory', lazy=True)


class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(128))
    device_description = db.Column(db.String(512))
    inventory = db.Column(db.Integer)
    device_category = db.Column(db.Integer, db.ForeignKey('device_category.id'), nullable=False)

    def __str__(self):
        return f"{self.device_name} - {self.inventory} in stock at present"


db.create_all()

print(__name__)


@app.route('/')
def hello():
    return '<h1>Welcome to Flask Session!</h1>'


@app.route('/welcome')
def welcome():
    return '<h1>You are at the welcome page</h1>'


@app.route('/about_me')
def about_me():
    return '<h1>You are at about me page</h1>'


@app.route('/user/<string:name>')
def user_with_name(name):
    return f'<H1>Hello {name}. Welcome to the Flask Course.</H1>'


@app.route('/user/<int:sessions>')
def user_with_sessions(sessions):
    return f'<H1>Hello user. You have completed {sessions} sessions of this course.</H1>'


@app.route('/query_string')
def query_string():
    user = request.args.get('user')
    query = request.args.get('query')
    return f'<H1>Query from {user} regarding {query}</H1>'


@app.route('/user_form/<string:name>')
def user_form_with_name(name):
    return render_template("user_form.html", name=name)


@app.route('/accept_user_input', methods=['GET', 'POST'])
def accept_user_input():
    if request.method == 'GET':
        return render_template("accept_user_input.html")
    elif request.method == 'POST':
        strn = url_for("user_form_with_name", name=request.form.get('some_text'))
        print(strn)
        return redirect(strn)


@app.route('/list_devices')
def list_devices():
    result_set = db.session.query(Device).all()
    rows = []
    for row in result_set:
        # print(row.__dict__)
        rows.append(row)
    # print(rows)
    return render_template("list_devices.html", rows=rows, rows_count=len(rows))


@app.route('/add_new_device/<int:device_cat>')
def add_new_device(device_cat):
    valid_device_category = DeviceCategory.query.filter(DeviceCategory.id == device_cat).count()
    if valid_device_category:
        new_device = Device(device_name='A new device', device_description='Description of a new device',
                            inventory=45, device_category=device_cat)
        db.session.add(new_device)
        db.session.commit()
    else:
        return f'<h2>Invalid Device Category {device_cat}</h2>'

    strn = url_for("list_devices")
    return redirect(strn)


@app.route('/delete_a_device/<int:device_id>')
def delete_a_device(device_id):
    device_deleted = Device.query.filter(Device.id == device_id).delete()
    if device_deleted:
        db.session.commit()
    else:
        return f'<h2>Invalid Device ID {device_id}</h2>'

    strn = url_for("list_devices")
    return redirect(strn)


@app.route('/new_device_form', methods=['GET', 'POST'])
def new_device_form():
    if request.method == 'GET':
        return render_template("new_device_form.html")

    elif request.method == 'POST':
        valid_device_category = \
            DeviceCategory.query.filter(DeviceCategory.id == request.form.get('device_category')).count()
        if valid_device_category:
            new_device = Device(device_name=request.form.get('device_name'),
                                device_description=request.form.get('device_description'),
                                inventory=request.form.get('Inventory'),
                                device_category=request.form.get('device_category'))

            db.session.add(new_device)
            db.session.commit()
        else:
            return f"<h2>Invalid Device Category {request.form.get('device_category')}</h2>"

        strn = url_for("list_devices")
        print(strn)
        return redirect(strn)


@app.route('/update_a_device/<int:device_id>')
def update_a_device(device_id):
    valid_device = Device.query.get(device_id)
    device_category = request.args.get('device_cat')
    valid_device_category = 0
    if device_category:
        valid_device_category = DeviceCategory.query.filter(DeviceCategory.id == device_category).count()
    else:
        device_category = valid_device.device_category
        valid_device_category = 1

    print(device_category, valid_device_category)

    if valid_device and valid_device_category:
        device_name = request.args.get('device_name')
        device_description = request.args.get('description')
        inventory = request.args.get('inventory')

        if device_name:
            valid_device.device_name = device_name

        if device_description:
            valid_device.device_description = device_description

        if inventory:
            valid_device.inventory = inventory

        if valid_device_category:
            valid_device.device_category = device_category

        db.session.add(valid_device)
        db.session.commit()
    else:
        return f'<h2>Invalid Device {device_id} or Device Category {device_category}</h2>'

    strn = url_for("list_devices")
    return redirect(strn)


if __name__ == "__main__":
    app.run()
