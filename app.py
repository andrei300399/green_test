from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////test.db'
db = SQLAlchemy(app)

duty_dates = db.Table('duty_dates',
                      db.Column('duty_date_day', db.String(10), db.ForeignKey('duty_date.day'), primary_key=True),
                      db.Column('user_id', db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
                      )


class Group(db.Model):
    group_id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(80), nullable=False)
    month_number = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    month_name = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return '<Group %r>' % self.group_id


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(80), nullable=False)
    user_full_name = db.Column(db.String(80), nullable=False)
    user_email = db.Column(db.String(80), nullable=False)
    is_on_duty_this_month = db.Column(db.Boolean, nullable=False)
    user_phone = db.Column(db.String(80), nullable=False)
    user_ext = db.Column(db.String(80), nullable=False)
    is_owner = db.Column(db.String(80), nullable=False)

    group_id = db.Column(db.Integer, db.ForeignKey('group.group_id'), nullable=False)
    group = db.relationship('Group', backref=db.backref('users', lazy=True))
    duty_dates = db.relationship('DutyDate', secondary=duty_dates, lazy='subquery',
                                 backref=db.backref('users', lazy=True))

    def __repr__(self):
        return '<User %r>' % self.user_id


class DutyDate(db.Model):
    day = db.Column(db.String(10), primary_key=True)
    day_of_week = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return '<DutyDate %r>' % self.day


@app.route("/")
def index():
    with open('duty.json', encoding='utf-8') as json_file:
        data = json.load(json_file)
    for group in data:
        group_db = Group(group_id=group["groupId"], group_name=group["groupName"],
                         month_number=group["monthNumber"], year=group["year"],
                         month_name=group["monthName"])
        db.session.add(group_db)
        for user in group["usersDutyList"]:
            if not user["isOnDutyThisMonth"]:
                continue
            else:
                user_db = User(user_id=user["userId"], user_name=user["userName"],
                               user_full_name=user["userFullname"], user_email=user["userEmail"],
                               is_on_duty_this_month=user["userId"], user_phone=user["userId"],
                               user_ext=user["userId"], is_owner=user["userId"])

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
