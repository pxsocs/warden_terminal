from node_warden import pickle_it
import os
from pathlib import Path

home_path = Path.home()
# make directory to store all private data at /home/warden
# /root/warden/
home_dir = os.path.join(home_path, 'warden')
try:
    os.mkdir(home_dir)
except Exception:
    pass


class Config:
    home_dir = os.path.join(home_path, 'warden')
    basedir = os.path.abspath(os.path.dirname(__file__))

    # You should change this secret key. But make sure it's done before any data
    # is included in the database
    SECRET_KEY = "24feff26632734xscdcjncdjdcjuu212i"

    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
        home_dir, "warden.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    debug_file = os.path.join(home_dir, 'debug.log')

    version_file = os.path.join(basedir, 'version.txt')

    # Used for notifications --- FUTURE FEATURE
    MAIL_SERVER = "smtp.googlemail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("EMAIL_USER")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

    # Pretty print json
    JSONIFY_PRETTYPRINT_REGULAR = True

    # Do not start new job until the last one is done
    SCHEDULER_JOB_DEFAULTS = {'coalesce': False, 'max_instances': 1}
    SCHEDULER_API_ENABLED = True


def node_finder():
    # Will look for nodes in local network
    # node_finder is the broacaster dict that
    # is displayed in realtime
    node_finder = {
        'progress': 0,
        'latest_message': '',
        'success_messages': [],
        'fail_messages': [],
        'finished': False
    }

    pickle_it('save', 'node_finder.pkl', node_finder)

    # --------------------------------------------
    # Check Tor
    # --------------------------------------------
    from connections import test_tor
    # Kick off Message
    node_finder['latest_message'] = 'Checking Tor...'
    pickle_it('save', 'node_finder.pkl', node_finder)
    # Run the test...
    tor = test_tor()
    node_finder['latest_message'] = 'Finished Testing Tor'
    if tor['status']:
        node_finder['success_messages'].append('✅ Tor Connected')
    else:
        node_finder['fail_messages'].append('💥 Tor NOT Connected')
    pickle_it('save', 'node_finder.pkl', node_finder)