""" Method's decorators
"""

from functools import wraps
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.models import Group, User
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import resolve_url
from rest_framework import status
from rest_framework.response import Response

from core_main_app.permissions import rights


@receiver(post_save, sender=User)
def add_default_group(sender, **kwargs):
    """
    # Function Name: add_default_group(request)
    # Inputs:        sender, kwargs -
    # Outputs:       -
    # Exceptions:    None
    # Description:   Assigns the user in the default group after its creation
    #                We catch the post_save signal for the User model

    :param sender:
    :param kwargs:
    :return:
    """
    # We retrieve the user
    user = kwargs["instance"]
    # If it's a creation
    if kwargs["created"]:
        group = Group.objects.get(name=rights.DEFAULT_GROUP)
        user.groups.add(group)
        user.save()


def login_or_anonymous_perm_required(
    anonymous_permission,
    function=None,
    redirect_field_name=REDIRECT_FIELD_NAME,
    login_url=None,
):
    """
    # Function Name: login_or_anonymous_perm_required(request)
    # Inputs:        anonymous_permission, function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None -
    # Outputs:       decorator
    # Exceptions:    None
    # Description:   Custom decorator for checking user authentication or anonymous user permission.
    #                Manages the authorisation to execute a function decorated by this decorator.
    #                Conditions: user connected or ANONYMOUS_GROUP assigned with the anonymous_permission in parameter.

    :param anonymous_permission:
    :param function:
    :param redirect_field_name:
    :param login_url:
    :return:
    """

    def _check_group(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            """

            Args:
                request:
                *args:
                **kwargs:

            Returns:

            """
            request.has_anonymous_access = False
            if request.user.is_anonymous:
                access = Group.objects.filter(
                    Q(name=rights.ANONYMOUS_GROUP)
                    & Q(permissions__codename=anonymous_permission)
                )
            else:
                access = request.user.is_authenticated

            if access:
                return view_func(request, *args, **kwargs)
            else:
                path = request.build_absolute_uri()
                resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
                # If the login url is the same scheme and net location then just
                # use the path as the "next" url.
                login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
                current_scheme, current_netloc = urlparse(path)[:2]
                if (not login_scheme or login_scheme == current_scheme) and (
                    not login_netloc or login_netloc == current_netloc
                ):
                    path = request.get_full_path()
                from django.contrib.auth.views import redirect_to_login

                return redirect_to_login(path, resolved_login_url, redirect_field_name)

        return wrapper

    return _check_group


def permission_required(
    content_type,
    permission,
    login_url=None,
    raise_exception=False,
    redirect_field_name=REDIRECT_FIELD_NAME,
):
    """
    # Function Name: permission_required(request)
    # Inputs:        content_type, permission, login_url=None, raise_exception=False,
    #                redirect_field_name=REDIRECT_FIELD_NAME -
    # Outputs:       decorator
    # Exceptions:    None
    # Description:   Check if the user has the required permission given in parameter
    #                If the user is anonymous, check if the ANONYMOUS_GROUP has the required permission

    :param content_type:
    :param permission:
    :param login_url:
    :param raise_exception:
    :param redirect_field_name:
    :return:
    """

    def _check_group(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            """

            Args:
                request:
                *args:
                **kwargs:

            Returns:

            """
            if request.user.is_anonymous:
                # Check in the ANONYMOUS_GROUP
                access = Group.objects.filter(
                    Q(name=rights.ANONYMOUS_GROUP) & Q(permissions__codename=permission)
                )
            else:
                # Check the permission for the current user
                prefixed_permission = "{!s}.{!s}".format(content_type, permission)
                access = request.user.has_perm(prefixed_permission)

            if access:
                return view_func(request, *args, **kwargs)
            else:
                # In case the 403 handler should be called raise the exception
                if raise_exception:
                    raise PermissionDenied
                else:
                    path = request.build_absolute_uri()
                    resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
                    # If the login url is the same scheme and net location then just
                    # use the path as the "next" url.
                    login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
                    current_scheme, current_netloc = urlparse(path)[:2]
                    if (not login_scheme or login_scheme == current_scheme) and (
                        not login_netloc or login_netloc == current_netloc
                    ):
                        path = request.get_full_path()
                    from django.contrib.auth.views import redirect_to_login

                    return redirect_to_login(
                        path, resolved_login_url, redirect_field_name
                    )

        return wrapper

    return _check_group


def api_staff_member_required():
    """
    # Function Name: api_staff_member_required(request)
    # Inputs:        -
    # Outputs:       decorator
    # Exceptions:    None
    # Description:   Check if the user is an admin user. Used by the API

    :return:
    """

    def _check_group(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            """

            Args:
                request:
                *args:
                **kwargs:

            Returns:

            """
            if request.user.is_staff:
                return view_func(request, *args, **kwargs)
            else:
                content = {"message": "Only administrators can use this feature."}
                return Response(content, status=status.HTTP_403_FORBIDDEN)

        return wrapper

    return _check_group


def api_permission_required(content_type, permission, raise_exception=False):
    """
    # Function Name: api_permission_required(request)
    # Inputs:        -
    # Outputs:       decorator
    # Exceptions:    None
    # Description:   Check if the user has the required permission given in parameter.
    #                If the user is anonymous, check if the ANONYMOUS_GROUP has the required permission
    #                Used by the API

    :param content_type:
    :param permission:
    :param raise_exception:
    :return:
    """

    def _check_group(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            """
            Args:
                request:
                *args:
                **kwargs:

            Returns:

            """
            if request.user.is_anonymous:
                access_api = Group.objects.filter(
                    Q(name=rights.ANONYMOUS_GROUP)
                    & Q(permissions__codename=rights.API_ACCESS)
                )
                access = Group.objects.filter(
                    Q(name=rights.ANONYMOUS_GROUP) & Q(permissions__codename=permission)
                )
            else:
                prefixed_api_permission = "{!s}.{!s}".format(
                    rights.API_CONTENT_TYPE, rights.API_ACCESS
                )
                access_api = request.user.has_perm(prefixed_api_permission)
                prefixed_permission = "{!s}.{!s}".format(content_type, permission)
                access = request.user.has_perm(prefixed_permission)

            if access_api and access:
                return view_func(request, *args, **kwargs)
            else:
                # In case the 403 handler should be called raise the exception
                if raise_exception:
                    raise PermissionDenied

                content = {
                    "message": "You don't have enough rights to use this feature."
                }
                return Response(content, status=status.HTTP_403_FORBIDDEN)

        return wrapper

    return _check_group
