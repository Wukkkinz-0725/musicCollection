import os
import pathlib

import requests
from datetime import datetime
from flask import Flask, session, abort, redirect, request
from google.oauth2.credentials import Credentials
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
import secrets


app = Flask("Google Login App")
app.secret_key = secrets.token_hex(16)

client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://googleauth-env.eba-6yr79q2j.us-east-2.elasticbeanstalk.com/authorize"
)


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper


@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/authorize")
def authorize():
    flow.fetch_token(authorization_response=request.url)

    # print(session['state'])
    # print(dict(request.args))
    # if not session["state"] == request.args["state"]:
    #     abort(500)  # State does not match!

    auth_code = request.args.get('code')
    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience='942606144781-d1nlf55298ld772qd9d4h093qnebplpd.apps.googleusercontent.com'
    )

    # store user info
    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session["email"] = id_info.get("email")

    # store credential info
    session["token"] = credentials._id_token
    session["refresh_token"] = credentials._refresh_token
    session["scopes"] = credentials._scopes
    session["client_id"] = credentials._client_id
    session["client_secret"] = credentials._client_secret
    session["quota_project_id"] = credentials._quota_project_id
    session["expiry"] = credentials.expiry.strftime("%Y-%m-%dT%H:%M:%S")
    
    return redirect("/protected_area")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/")
def index():
    return "Hello World <a href='/login'><button>Login</button></a>"


@app.route("/protected_area")
@login_is_required
def protected_area():
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    # auth_url, _ = google.auth.web.AuthorizedSession(client_id=CLIENT_ID, client_secret=CLIENT_SECRET).authorization_url(google.auth.web.OOB_CALLBACK_URN, scopes=SCOPES)
    # auth_code = session["auth_code"]
    # creds = google.oauth2.credentials.Credentials.from_authorized_user_info(
    #     code=auth_code, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, scopes=SCOPES)
    # print(creds)
    # flow.fetch_token(authorization_response=request.url)
    print(session)
    credentials = Credentials.from_authorized_user_info({
        "token": session["token"],
        "refresh_token": session["refresh_token"],
        "scopes": session["scopes"],
        "client_id": session["client_id"],
        "client_secret": session["client_secret"],
        "quota_project_id": session["quota_project_id"],
        "expiry": session["expiry"]
    })
    return f"Hello {session['name']}! <br/> <a href='/logout'><button>Logout</button></a>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
