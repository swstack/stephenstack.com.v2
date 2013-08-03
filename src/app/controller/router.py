from app.controller.login import GAPIException
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.session import UnencryptedCookieSessionFactoryConfig
import json
import logging
import random
import string

logger = logging.getLogger("webserver")


def _json_response(body, status):
    try:
        body = json.dumps(body)
    except TypeError:
        body = ""
        logger.error("Could not serialize to JSON!! -- %s", body)
    finally:
        return Response(body=body,
                        status=status,
                        headers={"Content-Type": "application/json"})


class Router(object):
    #================================================================================
    # Construction
    #================================================================================
    def __init__(self, resource_manager,
                       template_builder,
                       login_manager):
        # Dependencies --------------------------------------------------------------
        self._resource_manager = resource_manager
        self._template_builder = template_builder
        self._login_manager = login_manager

        # Internal state ------------------------------------------------------------
        self._static_root = None
        self._config = None
        self._app = None

    def start(self):
        # Setup Pyramid configurator
        self._config = \
            Configurator(session_factory=UnencryptedCookieSessionFactoryConfig("pwnd"))

        # Route: /static/<file> (:method:static)
        self._config.add_static_view(name="static",
                                     path=self._resource_manager.get_fs_resource_root())

        # Route: /login (:method:login)
        self._config.add_route("login", "/login")
        self._config.add_view(self.login,
                              route_name="login",
                              request_method="POST",
                              permission="read")

        # Route: /logout (:method:logout)
        self._config.add_route("logout", "/logout")
        self._config.add_view(self.login,
                              route_name="logout",
                              request_method="POST",
                              permission="read")

        # Route: /admin (:method:admin)
        self._config.add_route("admin", "/admin")
        self._config.add_view(self.admin,
                              route_name="admin",
                              request_method="GET",
                              permission="read")

        # Route: /upload/resume (:method:upload_resume)
        self._config.add_route("upload-resume", "/upload/resume")
        self._config.add_view(self.upload_resume,
                              route_name="upload-resume",
                              request_method="POST",
                              permission="read")

        # Route: /index (:method:index)
        self._config.add_route("index", "/")
        self._config.add_view(self.index,
                              route_name="index",
                              request_method="GET",
                              permission="read")

        # Make WSGI application object
        self._app = self._config.make_wsgi_app()

    #================================================================================
    # Internal
    #================================================================================
    def _get_static_root(self):
        """Return path to static assets/resources"""
        if not self._static_root:
            self._static_root = self._resource_manager.get_fs_resource_root()
        return self._static_root

    #================================================================================
    # Public
    #================================================================================
    def get_wsgi_app(self):
        """Return standard wsgi application,
                        http://www.python.org/dev/peps/pep-0333/
        """
        return self._app

    #================================================================================
    # Routes
    #================================================================================
    def logout(self, request):
        """Revoke current user's token and reset their session."""
        session = request.session
        self._login_manager.logout(session)
        return _json_response("Successfully disconnected", 200)

    def index(self, request):
        """Dat index"""
        session = request.session
        state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                            for _ in xrange(32))
        session['state'] = state
        template_vars = {
              "resume": "",
              "STATE": unicode(state)
        }
        return Response(self._template_builder.get_index(template_vars))

    def login(self, request):
        """Ensure that the request is not a forgery and that the user sending
        this connect request is the expected user.

        This ``POST`` request is expected to have a `state` and `auth_code`
        encoded as json in the HTTP body.
        """
        unencoded_json = json.loads(request.body)

        state = unencoded_json.get("state")
        if not state:
            return _json_response("Missing `POST` data: `state`", 401)

        auth_code = unencoded_json.get("auth_code")
        if not auth_code:
            return _json_response("Missing 'POST` data: `auth_code`", 401)

        try:
            result = self._login_manager.login(request.session, state, auth_code)
        except GAPIException, e:
            return _json_response(e.msg, e.status_code)
        else:
            return _json_response(result, 200)

    def upload_resume(self, request):
        import cgi
        form = cgi.FieldStorage()
        if form.has_key("filename"):
            item = form["filename"]
            if item.file:
                data = item.file.read()
                print cgi.escape(data)

        return Response("pewp")

    def admin(self, request):
        return Response(self._template_builder.get_admin({}))
