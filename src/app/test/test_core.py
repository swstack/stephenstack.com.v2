"""Somewhat of a science experiment, but, I want to aim this automated testing
to be as Functional as possible.  Unit-tests are important but not the main focus
here.

The `unittest` dependency and usage is only to aid in good test practice and
paradigm.
"""

from app.controller.router import Router
from app.test.utilities import MockResourceManager
from app.view.templates import TemplateBuilder
from mock import Mock
from wsgi_intercept import add_wsgi_intercept, remove_wsgi_intercept
from wsgi_intercept.urllib2_intercept import install_opener
import unittest
import urllib2


class TestCore(unittest.TestCase):
    def setUp(self):
        self._resource_manager = MockResourceManager()
        self._template_builder = TemplateBuilder(self._resource_manager)
        self._template_builder.start()
        self._router = Router(resource_manager=self._resource_manager,
                              template_builder=self._template_builder,
                              login_manager=Mock())
        self._router.start()
        self._app = self._router.get_wsgi_app()
        install_opener()
        add_wsgi_intercept("localhost", 8080, lambda: self._app)

    def tearDown(self):
        remove_wsgi_intercept("localhost", 8080)
        self._router = None
        self._template_builder = None
        self._resource_manager = None
        self._app = None

    def test_s(self):
        resp = urllib2.urlopen("http://localhost:8080/").read()
        self.assertNotEqual(resp, None)


if __name__ == '__main__':
    unittest.main()
