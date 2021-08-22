from flask import Blueprint

warden = Blueprint('warden', __name__)


# Main page for WARden
@warden.route("/", methods=['GET'])
def warden_page():
    return ("Running...")
