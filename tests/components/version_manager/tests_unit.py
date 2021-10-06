"""
Version Manager unit tests
"""
from unittest.case import TestCase

import mock
from mock.mock import Mock, patch

from core_main_app.commons import exceptions
from core_main_app.commons.exceptions import DoesNotExist
from core_main_app.components.template.models import Template
from core_main_app.components.template_version_manager import (
    api as template_version_manager_api,
)
from core_main_app.components.template_version_manager.models import (
    TemplateVersionManager,
)
from core_main_app.components.version_manager import api as version_manager_api
from core_main_app.components.version_manager.models import VersionManager
from core_main_app.utils.tests_tools.MockUser import create_mock_user
from core_main_app.utils.tests_tools.RequestMock import create_mock_request


class TestVersionManagerDisableVersion(TestCase):
    def test_version_manager_disable_version_raises_exception_if_object_does_not_exist(
        self,
    ):
        # Arrange
        mock_user = create_mock_user("1", is_superuser=True)
        mock_request = create_mock_request(mock_user)
        mock_absent = _create_mock_object()

        # Act + Assert
        with self.assertRaises(exceptions.ApiError):
            version_manager_api.disable_version(mock_absent, request=mock_request)

    def test_version_manager_disable_current_version_throws_exception(self):
        # Arrange
        mock_user = create_mock_user("1", is_superuser=True)
        mock_request = create_mock_request(mock_user)
        mock_version_manager = _create_mock_version_manager()
        mock_current = _create_mock_object()
        mock_version_manager.versions.append(str(mock_current.id))
        mock_version_manager.current = str(mock_current.id)

        # Act + Assert
        with self.assertRaises(exceptions.ApiError):
            version_manager_api.disable_version(mock_current, request=mock_request)

    @patch.object(TemplateVersionManager, "version_set", new_callable=mock.PropertyMock)
    def test_version_manager_disable_version_raises_exception_if_new_current_does_not_exist(
        self, mock_versions
    ):
        # Arrange
        mock_user = create_mock_user("1", is_superuser=True)
        mock_request = create_mock_request(mock_user)
        mock_version_manager = _create_version_manager()
        mock_absent = _create_mock_object()
        mock_current = _get_template()
        mock_current.is_current = True
        mock_current.version_manager = mock_version_manager
        mock_versions.return_value = [mock_current]

        # Act + Assert
        with self.assertRaises(exceptions.ApiError):
            version_manager_api.disable_version(
                mock_current, request=mock_request, new_current=mock_absent
            )


class TestVersionManagerSetCurrent(TestCase):
    def test_version_manager_set_current_raises_api_error_if_disabled(self):
        # Arrange
        mock_user = create_mock_user("1", is_superuser=True)
        mock_request = create_mock_request(mock_user)
        to_disable = _create_mock_object()

        # Act + Assert
        with self.assertRaises(exceptions.ApiError):
            version_manager_api.set_current(to_disable, request=mock_request)


class TestVersionManagerGetActiveGlobalVersionManagerByTitle(TestCase):
    @patch.object(TemplateVersionManager, "get_active_global_version_manager_by_title")
    def test_version_manager_get_returns_version_manager(self, mock_get_active_global):
        # Arrange
        mock_user = create_mock_user("1", is_superuser=True)
        mock_request = create_mock_request(mock_user)
        title = "Schema"
        mock_version_manager = _create_mock_version_manager(title=title)

        mock_get_active_global.return_value = mock_version_manager

        # Act
        result = (
            template_version_manager_api.get_active_global_version_manager_by_title(
                title, request=mock_request
            )
        )

        # Assert
        self.assertIsInstance(result, VersionManager)

    @patch.object(TemplateVersionManager, "get_active_global_version_manager_by_title")
    def test_version_manager_get_raises_exception_if_object_does_not_exist(
        self, mock_get_active_global
    ):
        # Arrange
        mock_user = create_mock_user("1", is_superuser=True)
        mock_request = create_mock_request(mock_user)
        mock_absent_title = "Schema"
        mock_get_active_global.side_effect = DoesNotExist("")

        # Act + Assert
        with self.assertRaises(DoesNotExist):
            template_version_manager_api.get_active_global_version_manager_by_title(
                mock_absent_title, request=mock_request
            )


class TestVersionManagerGetVersionByNumber(TestCase):
    @patch.object(TemplateVersionManager, "version_set", new_callable=mock.PropertyMock)
    def test_version_manager_get_returns_version(self, mock_versions):
        # Arrange
        mock_user = create_mock_user("1", is_superuser=True)
        mock_request = create_mock_request(user=mock_user)
        version = _get_template()
        mock_versions.return_value = [version]
        version_manager = _create_version_manager("Schema1", [version])

        # Act
        result = version_manager_api.get_version_by_number(
            version_manager, 1, request=mock_request
        )

        # Assert
        self.assertEquals(result, str(version.id))

    def test_version_manager_get_raises_exception_if_object_does_not_exist(self):
        # Arrange
        mock_user = create_mock_user("1", is_superuser=True)
        mock_request = create_mock_request(user=mock_user)
        version_manager = _create_version_manager("Schema1", [_get_template()])

        # Act + Assert
        with self.assertRaises(IndexError):
            version_manager_api.get_version_by_number(
                version_manager, 2, request=mock_request
            )


class TestVersionManagerGetVersionNumber(TestCase):
    @patch.object(TemplateVersionManager, "version_set", new_callable=mock.PropertyMock)
    def test_version_manager_get_returns_number(self, mock_versions):
        # Arrange
        mock_user = create_mock_user("1", is_superuser=True)
        mock_request = create_mock_request(user=mock_user)
        version = _get_template()
        mock_versions.return_value = [version]
        version_manager = _create_version_manager("Schema1", [version])

        # Act
        result = version_manager_api.get_version_number(
            version_manager, version.id, request=mock_request
        )

        # Assert
        self.assertEquals(result, 1)

    def test_version_manager_get_raises_exception_if_object_does_not_exist(self):
        # Arrange
        mock_user = create_mock_user("1", is_superuser=True)
        mock_request = create_mock_request(user=mock_user)
        # version = 1
        absent_version = -1
        version_manager = _create_version_manager("Schema1", [_get_template()])

        # Act + Assert
        with self.assertRaises(ValueError):
            version_manager_api.get_version_number(
                version_manager, absent_version, request=mock_request
            )


def _create_mock_version_manager(title=""):
    """
    Create a mock version manager
    :param title:
    :return:
    """
    mock_vm = Mock(spec=VersionManager)
    mock_vm.title = title
    mock_vm.current = 1
    mock_vm.versions = [str(mock_vm.current)]
    mock_vm.id = 1
    return mock_vm


def _create_mock_object():
    """
    Create a mock object
    :return:
    """
    mock_object = Mock()
    mock_object.id = 1
    return mock_object


def _create_version_manager(title="", versions=[]):
    """
    Returns a templates version manager
    :param title:
    :return:
    """
    tvm = TemplateVersionManager(
        id=1,
        title=title,
    )
    for template in versions:
        template.version_manager = tvm
    return tvm


def _get_template():
    template = Template()
    template.id = 1
    xsd = (
        "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'>"
        "<xs:element name='tag'></xs:element></xs:schema>"
    )
    template.content = xsd
    return template
