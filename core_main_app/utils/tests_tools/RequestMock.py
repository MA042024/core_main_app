""" Mock a Request object.
"""
import json

from django.core.wsgi import get_wsgi_application
from django.http import HttpResponse
from rest_framework import status
from rest_framework.test import APIRequestFactory


class RequestMock(object):
    """ Represent a request.
        Use this class to simulate an HTTP request.
    """

    @staticmethod
    def do_request_get(view, user, data=None, param=None):
        """Execute a GET HTTP request.
        Args:
            view: View method called by the request.
            user: User for the request.
            data: Data.
            param: View method params.

        Returns:
            Response: Request response.

        """
        return RequestMock._do_request("GET", view, user, data, param)

    @staticmethod
    def do_request_post(view, user, data=None, param=None):
        """Execute a POST HTTP request.
        Args:
            view: View method called by the request.
            user: User for the request.
            data: Data.
            param: View method params.

        Returns:
            Response: Request response.
        """
        return RequestMock._do_request("POST", view, user, data, param)

    @staticmethod
    def do_request_put(view, user, data=None, param=None):
        """Execute a PUT HTTP request.
        Args:
            view: View method called by the request.
            user: User for the request.
            data: Data.
            param: View method params.

        Returns:
            Response: Request response.

        """
        return RequestMock._do_request("PUT", view, user, data, param)

    @staticmethod
    def do_request_delete(view, user, data=None, param=None):
        """Execute a DELETE HTTP request.
        Args:
            view: View method called by the request.
            user: User for the request.
            data: Data.
            param: View method params.

        Returns:
            Response: Request response.

        """
        return RequestMock._do_request("DELETE", view, user, data, param)

    @staticmethod
    def do_request_patch(view, user, data=None, param=None):
        """Execute a PATCH HTTP request.
        Args:
            view: View method called by the request.
            user: User for the request.
            data: Data.
            param: View method params.

        Returns:
            Response: Request response.

        """
        return RequestMock._do_request("PATCH", view, user, data, param)

    @staticmethod
    def _do_request(http_method, view, user, data=None, param=None):
        """Execute the http_method request.
        Args:
            http_method: HTTP method.
            view: View method called by the request.
            user: User for the request.
            data: Data.
            param: View method params.

        Returns:
            Response: Request response.

        """
        url = "/dummy_url"
        factory = APIRequestFactory()
        # Request by http_method.
        if http_method == "GET":
            request = factory.get(url, data=data)
        elif http_method == "POST":
            request = factory.post(url, data=json.dumps(data), content_type="application/json")
        elif http_method == "PUT":
            request = factory.put(url, data=json.dumps(data), content_type="application/json")
        elif http_method == "DELETE":
            request = factory.delete(url, data=json.dumps(data), content_type="application/json")
        elif http_method == "PATCH":
            request = factory.patch(url, data=json.dumps(data), content_type="application/json")
        else:
            return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        # Set the user
        request.user = user

        # i18n. Get django validation messages.
        get_wsgi_application()
        # Do not use CSRF checks.
        request._dont_enforce_csrf_checks = True

        if param:
            view_ = view(request, **param)
        else:
            view_ = view(request)

        return view_
