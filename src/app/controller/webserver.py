from bottle import route, static_file, get, request, post, run
import json

HOST = "localhost"
PORT = 8080

appcore = None


def start(_appcore):
    global appcore
    appcore = _appcore
    run(host=HOST, port=PORT, quiet=True)


@get('/static/<filepath:path>')
def static(filepath):
    return static_file(filepath, root=appcore.get_static_root())


@post("/login")
def login():
    params = request.params
    result = appcore.login(params["username"], params["password"])
    return json.dumps({"result": result})


@route("/")
def index():
    return appcore.get_index()
