from datetime import datetime

from cloudipsp import Api, Checkout
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///shop.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)


class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), unique=True, nullable=False, index=True)
    price = db.Column(db.Float)
    isActive = db.Column(db.Boolean(), default=True)
    text = db.Column(db.Text, nullable=False)
    date_added = db.Column(db.DateTime(), default=datetime.now)
    img = db.Column(db.LargeBinary)

    def __repr__(self):
        return f"< ID:{self.id}; Title: {self.title}, Price: {self.price} >"


@app.route('/')
def index():
    items = Item.query.order_by(Item.price).all()
    return render_template("index.html", items=items)


@app.route('/about')
def about():
    return render_template("about.html")


from sqlalchemy.exc import SQLAlchemyError


@app.route('/create', methods=["POST", "GET"])
def create_item():
    if request.method == "POST":
        title = request.form.get('title')
        price = request.form.get('price')
        description = request.form.get('text')

        item = Item(title=title, price=price, text=description)
        try:
            db.session.add(item)
            db.session.commit()
            flash("Item created successfully!")
            return redirect(url_for('create_item'))
        except SQLAlchemyError as e:
            db.session.rollback()
            error_msg = f"Error creating item: {str(e)}"
            flash(error_msg)
            return redirect(url_for('create_item'))
    else:
        return render_template("create.html")


@app.route('/buy/<id>')
def buy(id):
    item = Item.query.get(id)
    api = Api(merchant_id=1396424, secret_key='test')
    checkout = Checkout(api=api)
    data = {
        'currency': 'USD',
        'amount': int(item.price*100)
    }
    url = checkout.url(data).get('checkout_url')
    return redirect(url)


if __name__ == '__main__':
    app.run(debug=True)
