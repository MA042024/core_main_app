""" Set of functions to define the rules for access control
"""
import logging

import core_main_app.permissions.rights as rights
from core_main_app.access_control.api import has_perm_publish, can_write_in_workspace
from core_main_app.access_control.exceptions import AccessControlError

logger = logging.getLogger(__name__)


def has_perm_publish_blob(user):
    """Does the user have the permission to publish a blob.

    Args:
        user

    Returns
    """
    has_perm_publish(user, rights.publish_blob)


def can_write_blob(func, blob, user):
    """Does the user has permission to write blob.

    Args:
        func:
        blob:
        user:

    Returns:

    """
    if user.is_anonymous:
        raise AccessControlError("Unable to insert blob if not authenticated.")

    return func(blob, user)


def can_write_blob_workspace(func, data, workspace, user):
    """Can user write data in workspace.

    Args:
        func:
        data:
        workspace:
        user:

    Returns:

    """
    return can_write_in_workspace(func, data, workspace, user, rights.publish_blob)
