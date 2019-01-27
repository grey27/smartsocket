from flask import Flask, render_template, g, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
import paho.mqtt.client as mqtt
import datetime
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    "mysql+pymysql://root:zhanghui@39.108.210.212:3306/switch"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SCHEDULER_API_ENABLED'] = True
db = SQLAlchemy(app)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()
client = mqtt.Client()


def switch(state):
    print(state)
    client.connect("39.108.210.212", 1883, 60)
    client.publish("switch", state)
    db.session.add(Log(state))
    db.session.commit()


class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time = db.Column(db.DateTime, default=datetime.datetime.now)
    state = db.Column(db.String(5))

    def __init__(self, state):
        self.state = state


@app.route('/')
def index():
    log = Log.query.order_by(Log.time.desc()).first()
    g.state = log.state
    return render_template('index.html', state=g.state)


@app.route('/post/', methods=['POST'])
def post():
    state = request.form.get('state')
    date = request.form.get('date', default=None)
    trigger = request.form.get('trigger', default=None)
    if date:
        id = date + '-' + state
        hour, minute = date.split(':')
        if trigger == 'date':
            t = datetime.datetime.now()
            day = t.day
            if (str(t.hour) + ":" + str(t.minute)) > date:
                day += 1
            scheduler.add_job(id=id, func=__name__ + ':switch', trigger='date', args=[state],
                              run_date=datetime.datetime(t.year, t.month, day, int(hour), int(minute)))
        else:
            scheduler.add_job(id=id, func=__name__ + ':switch', trigger='cron', args=[state], hour=hour, minute=minute)
    else:
        switch(state)
    return jsonify({'msg': 'ok'})


@app.route('/delete/')
def delete():
    id = request.args.get("id")
    scheduler.delete_job(id)
    return ''


@app.route('/task/')
def task():
    task_dict = {}
    task_list = scheduler.get_jobs()
    for t in task_list:
        if str(t).find('date') != -1:
            task_dict[str(t).split(' ')[0]] = 'date'
        else:
            task_dict[str(t).split(' ')[0]] = 'cron'
    return jsonify(task_dict)


if __name__ == '__main__':
    app.run()
