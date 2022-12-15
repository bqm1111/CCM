import os

from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "one_to_many_example.db"))

app.config['DEBUG'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = database_file

db = SQLAlchemy(app)

# 
class Customer(db.Model):
    '''Customer table'''

    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(25))
    customer_email = db.Column(db.String(100), nullable=True)
    order_id = db.relationship('Order', cascade='all, delete', backref='customer', lazy=True)

    def __init__(self, customer_name, customer_email):
        self.customer_name = customer_name
        self. customer_email = customer_email

    def __repr__(self):
        return f'<Customer: {self.id} {self.customer_name}>'


class Order(db.Model):
    '''Order table'''

    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime, default=datetime.now)
    # Use datetime to generate a random 6 digit number from milliseconds.
    order_number = db.Column(db.Integer, default=datetime.now().strftime("%f"))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))

    def __repr__(self):
        return f'<OrderID: {self.id}>'


if __name__ == '__main__':
    app.run(debug=True)
