""" REST views for the data API
"""
import json
import logging
import os

from django.conf import settings
from django.http import Http404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from core_main_app.access_control.api import check_can_write
from core_main_app.access_control.exceptions import AccessControlError
from core_main_app.commons import exceptions
from core_main_app.components.data import api as data_api
from core_main_app.components.data.api import check_xml_file_is_valid
from core_main_app.components.data.models import Data
from core_main_app.components.data.tasks import get_task_progress, get_task_result
from core_main_app.components.user import api as user_api
from core_main_app.components.workspace import api as workspace_api
from core_main_app.rest.data.abstract_views import AbstractExecuteLocalQueryView
from core_main_app.rest.data.abstract_views import AbstractMigrationView
from core_main_app.rest.data.admin_serializers import AdminDataSerializer
from core_main_app.rest.data.serializers import (
    DataSerializer,
    DataWithTemplateInfoSerializer,
)
from core_main_app.rest.mongo_data.serializers import MongoDataSerializer
from core_main_app.settings import MONGODB_INDEXING, MAX_DOCUMENT_LIST
from core_main_app.settings import XML_POST_PROCESSOR, XML_FORCE_LIST
from core_main_app.utils import xml as main_xml_utils
from core_main_app.utils.boolean import to_bool
from core_main_app.utils.databases.mongo.pymongo_database import get_full_text_query
from core_main_app.utils.datetime_tools.utils import datetime_now
from core_main_app.utils.file import get_file_http_response
from core_main_app.utils.pagination.rest_framework_paginator.pagination import (
    StandardResultsSetPagination,
)
from core_main_app.commons.exceptions import XMLError
from core_main_app.utils.xml import get_content_by_xpath, format_content_xml

logger = logging.getLogger(__name__)


class DataList(APIView):
    """List all user Data, or create a new one."""

    permission_classes = (IsAuthenticated,)
    serializer = DataSerializer

    def get(self, request):
        """Get all user Data

        Url Parameters:

            workspace: workspace_id
            template: template_id
            title: document_title

        Examples:

            ../data/
            ../data?page=2
            ../data?workspace=[workspace_id]
            ../data?template=[template_id]
            ../data?title=[document_title]
            ../data?template=[template_id]&title=[document_title]&page=3

        Args:

            request: HTTP request

        Returns:

            - code: 200
              content: List of data
            - code: 500
              content: Internal server error
        """
        try:
            # Get object
            data_object_list = data_api.get_all_by_user(request.user)

            # Apply filters
            workspace = self.request.query_params.get("workspace", None)
            if workspace is not None:
                data_object_list = data_object_list.filter(workspace=workspace)

            template = self.request.query_params.get("template", None)
            if template is not None:
                data_object_list = data_object_list.filter(template=template)

            title = self.request.query_params.get("title", None)
            if title is not None:
                data_object_list = data_object_list.filter(title=title)

            # Get paginator
            paginator = StandardResultsSetPagination()

            # Get requested page from list of results
            page = paginator.paginate_queryset(data_object_list, self.request)

            # Serialize page
            data_serializer = self.serializer(page, many=True)

            # Return paginated response
            return paginator.get_paginated_response(data_serializer.data)

        except Exception as api_exception:
            content = {"message": str(api_exception)}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """Create a Data

        Parameters:

            {
                "title": "document_title",
                "template": "template_id",
                "workspace": "workspace_id",
                "xml_content": "document_content"
            }

        Args:

            request: HTTP request

        Returns:

            - code: 201
              content: Created data
            - code: 400
              content: Validation error
            - code: 404
              content: Template was not found
            - code: 500
              content: Internal server error
        """
        try:
            # Build serializer
            data_serializer = self.serializer(
                data=request.data, context={"request": request}
            )

            # Validate data
            data_serializer.is_valid(True)
            # Save data
            data_serializer.save()

            # Return the serialized data
            return Response(data_serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as validation_exception:
            content = {"message": validation_exception.detail}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except exceptions.DoesNotExist:
            content = {"message": "Template not found."}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        except Exception as api_exception:
            content = {"message": str(api_exception)}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminDataList(DataList):
    """Admin Data List"""

    permission_classes = (IsAdminUser,)
    serializer = AdminDataSerializer

    def get(self, request):
        """Get all Data

        Url Parameters:

            user: user_id
            workspace: workspace_id
            template: template_id
            title: document_title

        Examples:

            ../data/
            ../data?user=[user_id]
            ../data?workspace=[workspace_id]
            ../data?template=[template_id]
            ../data?title=[document_title]
            ../data?template=[template_id]&title=[document_title]

        Args:

            request: HTTP request

        Returns:

            - code: 200
              content: List of data
            - code: 500
              content: Internal server error
        """
        if not request.user.is_superuser:
            content = {"message": "Only a superuser can use this feature."}
            return Response(content, status=status.HTTP_403_FORBIDDEN)
        try:
            # Get object
            data_object_list = data_api.get_all(request.user)

            # Apply filters
            user = self.request.query_params.get("user", None)
            if user is not None:
                data_object_list = data_object_list.filter(user_id=user)

            workspace = self.request.query_params.get("workspace", None)
            if workspace is not None:
                data_object_list = data_object_list.filter(workspace=workspace)

            template = self.request.query_params.get("template", None)
            if template is not None:
                data_object_list = data_object_list.filter(template=template)

            title = self.request.query_params.get("title", None)
            if title is not None:
                data_object_list = data_object_list.filter(title=title)

            # Serialize object
            data_serializer = self.serializer(data_object_list, many=True)

            # Return response
            return Response(data_serializer.data, status=status.HTTP_200_OK)
        except Exception as api_exception:
            content = {"message": str(api_exception)}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        if not request.user.is_superuser:
            content = {"message": "Only a superuser can use this feature."}
            return Response(content, status=status.HTTP_403_FORBIDDEN)
        return super().post(request)


class DataDetail(APIView):
    """Retrieve, update or delete a Data"""

    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer = DataSerializer

    def get_object(self, request, pk):
        """Get data from db

        Args:

            request: HTTP request
            pk: ObjectId

        Returns:

            Data
        """
        try:
            return data_api.get_by_id(pk, request.user)
        except exceptions.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        """Retrieve a data

        Args:

            request: HTTP request
            pk: ObjectId

        Returns:

            - code: 200
              content: Data
            - code: 404
              content: Object was not found
            - code: 500
              content: Internal server error
        """
        try:
            # Get object
            data_object = self.get_object(request, pk)

            # Serialize object
            serializer = self.serializer(data_object)

            # Return response
            return Response(serializer.data)
        except Http404:
            content = {"message": "Data not found."}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        except AccessControlError as exception:
            content = {"message": str(exception)}
            return Response(content, status=status.HTTP_403_FORBIDDEN)
        except Exception as api_exception:
            content = {"message": str(api_exception)}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        """Delete a Data

        Args:

            request: HTTP request
            pk: ObjectId

        Returns:

            - code: 204
              content: Deletion succeed
            - code: 404
              content: Object was not found
            - code: 500
              content: Internal server error
        """
        try:
            # Get object
            data_object = self.get_object(request, pk)

            # delete object
            data_api.delete(data_object, request.user)

            # Return response
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Http404:
            content = {"message": "Data not found."}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        except AccessControlError as exception:
            content = {"message": str(exception)}
            return Response(content, status=status.HTTP_403_FORBIDDEN)
        except Exception as api_exception:
            content = {"message": str(api_exception)}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, pk):
        """Update a Data

        Parameters:

            {
                "title": "new_title",
                "xml_content": "new_xml_content"
            }

        Args:

            request: HTTP request
            pk: ObjectId

        Returns:

            - code: 200
              content: Updated data
            - code: 400
              content: Validation error
            - code: 404
              content: Object was not found
            - code: 500
              content: Internal server error
        """
        try:
            # Get object
            data_object = self.get_object(request, pk)

            # Build serializer
            data_serializer = self.serializer(
                instance=data_object,
                data=request.data,
                partial=True,
                context={"request": request},
            )

            # Validate data
            data_serializer.is_valid(True)
            # Save data
            data_serializer.save()

            return Response(data_serializer.data, status=status.HTTP_200_OK)
        except ValidationError as validation_exception:
            content = {"message": validation_exception.detail}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except Http404:
            content = {"message": "Data not found."}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        except AccessControlError as exception:
            content = {"message": str(exception)}
            return Response(content, status=status.HTTP_403_FORBIDDEN)
        except Exception as api_exception:
            content = {"message": str(api_exception)}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DataChangeOwner(APIView):
    """Change the Owner of a data"""

    permission_classes = (IsAdminUser,)

    def get_object(self, request, pk):
        """Get data from db

        Args:

            request: HTTP request
            pk: ObjectId

        Returns:

            Data
        """
        try:
            return data_api.get_by_id(pk, request.user)
        except exceptions.DoesNotExist:
            raise Http404

    def get_user(self, user_id):
        """Retrieve a User

        Args:

            user_id: ObjectId

        Returns:

            - code: 404
              content: Object was not found
        """
        try:
            return user_api.get_user_by_id(user_id)
        except exceptions.DoesNotExist:
            raise Http404

    def patch(self, request, pk, user_id):
        """Change the Owner of a data

        Args:

            request: HTTP request
            pk: ObjectId
            user_id: ObjectId

        Returns:

            - code: 200
              content: None
            - code: 403
              content: Authentication error
            - code: 404
              content: Object was not found
            - code: 500
              content: Internal server error
        """
        try:
            # get object
            data_object = self.get_object(request, pk)
            user_object = self.get_user(user_id)

            # change owner
            data_api.change_owner(data_object, user_object, request.user)
            return Response({}, status=status.HTTP_200_OK)
        except Http404:
            content = {"message": "Data or user not found."}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        except AccessControlError as ace:
            content = {"message": str(ace)}
            return Response(content, status=status.HTTP_403_FORBIDDEN)
        except Exception as api_exception:
            content = {"message": str(api_exception)}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DataDownload(APIView):
    """Download XML file in data"""

    def get_object(self, request, pk):
        """Get Data from db

        Args:

            request: HTTP request
            pk: ObjectId

        Returns:

            Data
        """
        try:
            return data_api.get_by_id(pk, request.user)
        except exceptions.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        """Download the XML file from a data

        Args:

            request: HTTP request
            pk: ObjectId

        Examples:

            ../data/download/[data_id]
            ../data/download/[data_id]?pretty_print=true

        Returns:

            - code: 200
              content: XML file
            - code: 404
              content: Object was not found
            - code: 500
              content: Internal server error
        """
        try:
            # Get object
            data_object = self.get_object(request, pk)

            # get xml content
            xml_content = data_object.xml_content

            # get format bool
            format = request.query_params.get("pretty_print", False)

            # format content
            if to_bool(format):
                xml_content = format_content_xml(xml_content)

            return get_file_http_response(
                xml_content, data_object.title, "text/xml", "xml"
            )
        except Http404:
            content = {"message": "Data not found."}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        except XMLError:
            content = {"message": "Content is not well formatted XML."}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except Exception as api_exception:
            content = {"message": str(api_exception)}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# FIXME: Should use in the future an serializer with dynamic fields (init depth with parameter for example)
# FIXME: Should avoid the duplicated code with get_by_id
@api_view(["GET"])
def get_by_id_with_template_info(request):
    """Retrieve a Data with template information

    Examples:

        ../data/get-full?id=[data_id]

    Args:

        request: HTTP request

    Returns:

        - code: 200
          content: Data
        - code: 400
          content: Validation error
        - code: 404
          content: Object was not found
        - code: 500
          content: Internal server error
    """
    try:
        # Get parameters
        data_id = request.query_params.get("id", None)

        # Check parameters
        if data_id is None:
            content = {"message": "Expected parameters not provided."}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        # Get object
        data_object = data_api.get_by_id(data_id, request.user)

        # Serialize object
        return_value = DataWithTemplateInfoSerializer(data_object)

        # Return response
        return Response(return_value.data, status=status.HTTP_200_OK)
    except exceptions.DoesNotExist:
        content = {"message": "No data found with the given id."}
        return Response(content, status=status.HTTP_404_NOT_FOUND)
    except exceptions.ModelError:
        content = {"message": "Invalid input."}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        content = {"message": "An unexpected error occurred."}
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExecuteLocalQueryView(AbstractExecuteLocalQueryView):
    """Execute Local Query View"""

    if MONGODB_INDEXING:
        serializer = MongoDataSerializer
    else:
        serializer = DataSerializer

    def post(self, request):
        """Execute a query

        Url Parameters:

            page: page_number

        Parameters:

            # get all results (paginated)
            {"query": {}}
            # get all results
            {"query": {}, "all": "true"}
            # get all results filtered by title
            {"query": {}, "title": "title_string"}
             # get all results filtered by workspaces
            {"query": {}, "workspaces": [{"id":"[workspace_id]"}]}
            # get all results filtered by private workspace
            {"query": {}, "workspaces": [{"id":"None"}]}
            # get all results filtered by templates
            {"query": {}, "templates": [{"id":"[template_id]"}] }
            # get all results that verify a given criteria
            {"query": {"root.element.value": 2}}
            # get values at xpath
            {"query": {}, "xpath": "/ns:root/@element", "namespaces": {"ns": "<namespace_url>"}}
            # get results using multiple options
            {"query": {"root.element.value": 2}, "workspaces": [{"id":"workspace_id"}] , "all": "true"}
            {"query": {"root.element.value": 2}, "templates": [{"id":"template_id"}] , "all": "true"}
            {"query": {"root.element.value": 2}, "templates": [{"id":"template_id"}],
            "workspaces": [{"id":"[workspace_id]"}] ,"all": "true"}

        Examples:

            ../data/query/
            ../data/query/?page=2

        Args:

            request: HTTP request

        Returns:

            - code: 200
              content: List of data
            - code: 400
              content: Bad request
            - code: 500
              content: Internal server error
        """
        return super().post(request)

    def build_response(self, data_list):
        """Build the response.

        Args:

            data_list: List of data

        Returns:

            The response paginated
        """

        xpath = self.request.data.get("xpath", None)
        namespaces = self.request.data.get("namespaces", None)
        if "all" in self.request.data and to_bool(self.request.data["all"]):
            if data_list.count() > MAX_DOCUMENT_LIST:
                content = {"message": "Number of documents is over the limit."}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

            # Select values at xpath if provided
            if xpath:
                for data_object in data_list:
                    data_object.xml_content = get_content_by_xpath(
                        data_object.xml_content, xpath, namespaces=namespaces
                    )
            # Serialize data list
            data_serializer = self.serializer(data_list, many=True)
            # Return response
            return Response(data_serializer.data)
        else:
            # Get paginator
            paginator = StandardResultsSetPagination()

            # Get requested page from list of results
            page = paginator.paginate_queryset(data_list, self.request)

            # Select values at xpath if provided
            if xpath:
                for data_object in page:
                    data_object.xml_content = get_content_by_xpath(
                        data_object.xml_content, xpath, namespaces=namespaces
                    )

            # Serialize page
            data_serializer = self.serializer(page, many=True)

            # Return paginated response
            return paginator.get_paginated_response(data_serializer.data)


class ExecuteLocalKeywordQueryView(ExecuteLocalQueryView):
    """Execute Local Keyword Query View"""

    def build_query(
        self, query, workspaces=None, templates=None, options=None, title=None
    ):
        """Build the raw query
        Prepare the query for a keyword search

        Args:

            query: ObjectId
            workspaces: ObjectId
            templates: ObjectId
            options: Query options
            title: title filter

        Returns:

            The raw query
        """
        # build query builder
        query = json.dumps(get_full_text_query(query))
        return super().build_query(
            query=str(query),
            workspaces=workspaces,
            templates=templates,
            options=options,
            title=title,
        )


class DataAssign(APIView):
    """Assign a Data to a Workspace."""

    permission_classes = (IsAuthenticated,)

    def get_object(self, request, pk):
        """Get data from db

        Args:

            request: HTTP request
            pk: ObjectId

        Returns:

            Data
        """
        try:
            return data_api.get_by_id(pk, request.user)
        except exceptions.DoesNotExist:
            raise Http404

    def get_workspace(self, workspace_id):
        """Retrieve a Workspace

        Args:

            workspace_id: ObjectId

        Returns:

            - code: 404
              content: Object was not found
        """
        try:
            return workspace_api.get_by_id(workspace_id)
        except exceptions.DoesNotExist:
            raise Http404

    def patch(self, request, pk, workspace_id):
        """Assign Data to a Workspace

        Args:

            request: HTTP request
            pk: ObjectId
            workspace_id: ObjectId

        Returns:

            - code: 200
              content: None
            - code: 403
              content: Authentication error
            - code: 404
              content: Object was not found
            - code: 500
              content: Internal server error
        """
        try:
            # Get object
            data_object = self.get_object(request, pk)
            workspace_object = self.get_workspace(workspace_id)

            # Assign data to workspace
            data_api.assign(data_object, workspace_object, request.user)
            return Response({}, status=status.HTTP_200_OK)
        except Http404:
            content = {"message": "Data or workspace not found."}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        except AccessControlError as ace:
            content = {"message": str(ace)}
            return Response(content, status=status.HTTP_403_FORBIDDEN)
        except Exception as api_exception:
            content = {"message": str(api_exception)}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DataListByWorkspace(APIView):
    """List all Data by workspace."""

    permission_classes = (IsAuthenticated,)
    serializer = DataSerializer

    def get(self, request, workspace_id):
        """Get all workspace Data

        Examples:

            ../workspace/id/data


        Args:

            request: HTTP request

        Returns:

            - code: 200
              content: List of data
            - code: 500
              content: Internal server error
        """
        try:
            # Get object
            data_object_list = data_api.get_all_by_workspace(workspace_id, request.user)

            # Serialize object
            data_serializer = self.serializer(data_object_list, many=True)

            # Return response
            return Response(data_serializer.data, status=status.HTTP_200_OK)
        except Exception as api_exception:
            content = {"message": str(api_exception)}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DataPermissions(APIView):
    """
    Get the permissions of the data according to the client user
    """

    def get(self, request):
        """GET requests"""
        return self.process_request(request)

    def post(self, request):
        """POST requests"""
        return self.process_request(request)

    def get_object(self, request, pk):
        """Get data from db

        Args:

            request: HTTP request
            pk: ObjectId

        Returns:

            Data
        """
        try:
            return data_api.get_by_id(pk, request.user)
        except exceptions.DoesNotExist:
            raise Http404

    def process_request(self, request):
        """Give the user permissions for a list of data ids

        Parameters:

            [
                "data_id1"
                "data_id2"
                "data_id3"
                ...
            ]

        Args:

            request: HTTP request

        Returns:

            - code: 200
              content: JSON Array [ <data_id>: <boolean> ]
            - code: 400
              content: Validation error
            - code: 404
              content: Template was not found
            - code: 500
              content: Internal server error
        """
        try:
            # Build serializer
            data_ids = json.loads(request.query_params["ids"])
            results = {}

            for id in data_ids:
                results[id] = self.can_write_data(request, id)

            return Response(results, status.HTTP_200_OK)

        except ValidationError as validation_exception:
            content = {"message": validation_exception.detail}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except Http404:
            content = {"message": "Data not found."}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        except Exception as api_exception:
            content = {"message": str(api_exception)}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def can_write_data(self, request, id):
        """Get the data permissions of a data

        Args:

            request: http request
            id: data id

        Returns:

            - Boolean
            - raise: Http404
              content: Data was not found
            - raise: Exception
              content: Unknown error
        """
        try:
            # Get object
            data_object = self.get_object(request, id)

            if not request.user.is_superuser:
                check_can_write(data_object, request.user)
            return True
        except AccessControlError:
            return False
        except Exception as exception:
            raise exception


class Validation(AbstractMigrationView):
    """Check for a set of data if the migration is possible for the given target template"""

    def post(self, request, pk):
        """Check if a migration if possible for the given template id

        Parameters:

            {
                "data || template": [
                    "id1",
                    "id2",
                    "id3"
                ]
            }

        Args:

            request: HTTP request
            pk: Target template id

        Returns:

            - code: 200
              content: Migration done
            - code: 400
              content: Bad request
            - code: 403
              content: Access denied
            - code: 500
              content: Internal server error
        """
        return super().post(request=request, template_id=pk, migrate=False)


class Migration(AbstractMigrationView):
    """Data template migration"""

    def post(self, request, pk):
        """Migrate data to the given template id

        Parameters:

            {
                "data || template": [
                    "id1",
                    "id2",
                    "id3"
                ]
            }

        Args:

            request: HTTP request
            pk: Target template id

        Returns:

            - code: 200
              content: Migration done
            - code: 400
              content: Bad request
            - code: 403
              content: Access denied
            - code: 500
              content: Internal server error
        """
        return super().post(request=request, template_id=pk, migrate=True)


@api_view(["GET"])
def get_progress(request, task_id):
    """Get the progress of the migration / validation async task

    Args:
        request:
        task_id:

    Return:
        {
            'state': PENDING | PROGRESS | SUCCESS,
            'details': result (for SUCCESS) | null (for PENDING) | { PROGRESS info }
        }
    """
    result = get_task_progress(task_id)
    return Response(result, content_type="application/json")


@api_view(["GET"])
def get_result(request, task_id):
    """Get the result of the migration / validation async task

    Args:
        request:
        task_id:

    Return:
        {
                "valid": ["data_id_1", "data_id_2" ...],
                "wrong": ["data_id_3", "data_id_4" ...]
        }
    """
    result = get_task_result(task_id)
    return Response(result, content_type="application/json")


class BulkUploadFolder(APIView):
    """Bulk upload data from folder"""

    permission_classes = (IsAdminUser,)

    @staticmethod
    def _bulk_create(data_list):
        """Bulk insert list of data

        Args:
            data_list:

        Returns:

        """
        try:
            # Bulk insert list of data
            Data.objects.bulk_create(data_list)
        except Exception as exception:
            # Log errors that occurred during bulk insert
            logger.error("Bulk upload failed.")
            logger.error(str(exception))
            # try inserting each data of the batch individually
            for error_data in data_list:
                try:
                    error_data.save()
                except Exception:
                    logger.error(
                        f"Error during bulk upload. Retry loading failed for: {error_data.title}."
                    )

    def put(self, request):
        """Bulk upload a folder.

        Dataset needs to be placed in the MEDIA_ROOT folder.
        The folder parameter is a relative path from the MEDIA_ROOT.

        Parameters:

            {
                "folder": "dataset/folder",
                "template": integer,
                "workspace": integer,
                "batch_size": integer,
                "validate_xml": true|false,
                "clean_title": true|false
            }

        Examples:
            {
                "folder": "dataset/files",
                "template": 1,
                "workspace": 1,
                "batch_size": 10,
                "validate_xml": false
            }

        Args:

            request: HTTP request

        """
        try:
            folder = request.data["folder"]
            template_id = request.data["template"]
            workspace = request.data["workspace"]
            batch_size = request.data.get("batch_size", 10)
            validate_xml = request.data.get("validate_xml", True)
            clean_title = request.data.get("clean_title", True)

            data_list = []

            if not os.path.exists(os.path.join(settings.MEDIA_ROOT, folder)):
                content = {"message": "Folder not found."}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

            for xml_data in os.listdir(os.path.join(settings.MEDIA_ROOT, folder)):
                try:
                    # initialize times
                    now = datetime_now()
                    # Create data
                    instance = Data(
                        template_id=template_id,
                        workspace_id=workspace,
                        user_id=request.user.id,
                        last_change_date=now,
                        creation_date=now,
                        last_modification_date=now,
                    )
                    # Set title
                    instance.title = (
                        xml_data.replace("_", " ").replace(".xml", "")
                        if clean_title
                        else xml_data
                    )
                    # Set XML file
                    instance.xml_file.name = os.path.join(folder, xml_data)
                    # Validate XML
                    if validate_xml:
                        check_xml_file_is_valid(instance, request=request)
                    # Convert to JSON
                    with open(
                        os.path.join(settings.MEDIA_ROOT, folder, xml_data), "rb"
                    ) as xml_file:
                        instance.dict_content = main_xml_utils.raw_xml_to_dict(
                            xml_file,
                            postprocessor=XML_POST_PROCESSOR,
                            force_list=XML_FORCE_LIST,
                        )
                    # Add data to list
                    data_list.append(instance)
                except Exception as exception:
                    logger.error(
                        f"ERROR: Unable to insert {xml_data}: {str(exception)}"
                    )
                # If data list reaches batch size
                if len(data_list) == batch_size:
                    # Bulk insert list of data
                    BulkUploadFolder._bulk_create(data_list)
                    # Clear list of data
                    data_list = list()
            # insert the last batch
            BulkUploadFolder._bulk_create(data_list)

            content = {"message": "Bulk upload is complete. Check the logs for errors."}
            return Response(content, status=status.HTTP_200_OK)

        except Exception as api_exception:
            content = {"message": str(api_exception)}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
