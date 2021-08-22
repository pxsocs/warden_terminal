from flask import Blueprint, render_template, url_for, jsonify, request

warden = Blueprint('warden', __name__)


# Welcome Page
@warden.route("/", methods=['GET'])
def warden_page():
    from node_warden import pickle_it
    first_time = pickle_it('load', 'first_time.pkl')
    if first_time == 'file not found':
        return render_template("warden/welcome.html",
                               title="Welcome to the WARden")
    else:
        # pickle_it('save', 'first_time.pkl', False)
        return render_template("warden/main.html", title="Main Dashboard")


@warden.route("/setup", methods=['GET'])
def setup():
    # pickle_it('save', 'first_time.pkl', False)
    # kick off the background setup and node check
    from config import node_finder
    from apscheduler.schedulers.background import BackgroundScheduler
    job_defaults = {'coalesce': False, 'max_instances': 1}
    scheduler = BackgroundScheduler(job_defaults=job_defaults)
    scheduler.add_job(node_finder)
    scheduler.start()
    return render_template("warden/setup.html", title="Initial Setup")


# Main Method to display Pickle Files in real time
# usage: /broadcast?data=block
@warden.route("/broadcast", methods=['GET'])
def broadcast():
    from node_warden import pickle_it
    file = request.args.get("data")
    if file is None:
        return 'file not found'
    broadcaster = pickle_it('load', file + '.pkl')
    return jsonify(broadcaster)
