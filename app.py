import os

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import json

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATA_BASE_URI'] = 'sqlite:////' + os.path.join(basedir, 'data.sqlite')
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

    for day in data[0]["usersDutyList"][0]["dutyDays"]:
        duty_date_db = DutyDate(day=day["day"], day_of_week=day["dayOfWeek"])
        db.session.add(duty_date_db)
    db.session.commit()
    for group in data:
        group_db = Group(group_id=group["groupId"], group_name=group["groupName"],
                         month_number=group["monthNumber"], year=group["year"],
                         month_name=group["monthName"])

        for user in group["usersDutyList"]:
            if not user["isOnDutyThisMonth"]:
                continue
            else:
                user_db = User(user_id=user["userId"], user_name=user["userName"],
                               user_full_name=user["userFullname"], user_email=user["userEmail"],
                               is_on_duty_this_month=user["isOnDutyThisMonth"], user_phone=user["userPhone"],
                               user_ext=user["userExt"], is_owner=user["isOwner"], group=group_db)
                db.session.add(user_db)
                db.session.commit()
                for day in user["dutyDays"]:
                    if day["isDuty"] == 'true':
                        user_db.duty_dates.append(DutyDate.query.filter_by(day=day["day"]).first())
                db.session.commit()

    return render_template("index.html",
                           groups=Group.query.all(),
                           users=User.query.all(),
                           )


@app.route("/<int:group>/<string:day>")
def show_duty(group, day):
    duty_day = DutyDate.query.filter_by(day=day).first()
    users = User.query.filter_by(group_id=group).all()
    for user in users:
        if duty_day in user.duty_dates:
            found_user = user
            break
    return render_template("current_duty.html", user=found_user)


@app.route("/<string:day>")
def show_all_duty(day):
    duty_day = DutyDate.query.filter_by(day=day).first()
    users = User.query.all()
    found_users = []
    for user in users:
        if duty_day in user.duty_dates:
            found_users.append(user)
    return render_template("all_duty.html", users=found_users)


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
