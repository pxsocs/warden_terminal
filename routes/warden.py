from flask import Blueprint, render_template, url_for

warden = Blueprint('warden', __name__)


# Main page for WARden
@warden.route("/", methods=['GET'])
def warden_page():
    from node_warden import pickle_it
    first_time = pickle_it('load', 'first_time.pkl')
    if first_time == 'file not found':
        pickle_it('save', 'first_time.pkl', False)
        return render_template("warden/welcome.html",
                               title="Welcome to the WARden")
    else:
        return ("OK")
