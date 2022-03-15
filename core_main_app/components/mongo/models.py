""" Mongoengine Data model
"""

import logging

from django.db.models.signals import post_save, post_delete

from core_main_app.commons.exceptions import CoreError
from core_main_app.components.data.models import Data
from core_main_app.components.data.tasks import index_mongo_data, delete_mongo_data
from core_main_app.components.template.models import Template
from core_main_app.components.workspace.models import Workspace
from core_main_app.settings import (
    MONGODB_INDEXING,
    MONGODB_ASYNC_SAVE,
    SEARCHABLE_DATA_OCCURRENCES_LIMIT,
)
from core_main_app.utils import xml as xml_utils

logger = logging.getLogger(__name__)

try:
    if MONGODB_INDEXING:
        from mongoengine import Document, DoesNotExist
        from mongoengine import fields as mongo_fields
        from core_main_app.utils.databases.mongo.pymongo_database import init_text_index

        class AbstractMongoData(Document):
            """Data object stored in MongoDB"""

            data_id = mongo_fields.IntField(primary_key=True)
            title = mongo_fields.StringField()
            dict_content = mongo_fields.DictField()
            creation_date = mongo_fields.DateTimeField()
            last_modification_date = mongo_fields.DateTimeField()
            last_change_date = mongo_fields.DateTimeField()

            meta = {
                "abstract": True,
            }

            def get_dict_content(self):
                """Return dict_content

                Returns:

                """
                return self.dict_content

            @staticmethod
            def post_save_data(sender, instance, **kwargs):
                raise NotImplementedError("post_save_data not implemented")

            @staticmethod
            def post_delete_data(sender, instance, **kwargs):
                raise NotImplementedError("post_delete_data not implemented")

        class MongoData(AbstractMongoData):
            """Data object stored in MongoDB"""

            _template_id = mongo_fields.IntField(db_field="template")
            user_id = mongo_fields.IntField()
            _workspace_id = mongo_fields.IntField(db_field="workspace")
            _xml_content = None

            meta = {
                "indexes": [
                    "title",
                    "_template_id",
                    "user_id",
                    "last_modification_date",
                ],
            }

            @property
            def template(self):
                """Return template object

                Returns:

                """
                return Template.get_by_id(self._template_id)

            @property
            def workspace(self):
                """Return workspace object

                Returns:

                """
                return Workspace.get_by_id(self._workspace_id)

            @property
            def xml_content(self):
                """Get xml content - read from data.

                Returns:

                """
                if not self._xml_content:
                    self._xml_content = Data.get_by_id(self.data_id).xml_content
                return self._xml_content

            @xml_content.setter
            def xml_content(self, value):
                """Set xml content - to be saved as a file.

                Args:
                    value:

                Returns:

                """
                self._xml_content = value

            @staticmethod
            def execute_query(query, order_by_field):
                """Execute a query.

                Args:
                    query:
                    order_by_field: Order by field.

                Returns:

                """
                return MongoData.objects(__raw__=query).order_by(*order_by_field)

            @staticmethod
            def aggregate(pipeline):
                """Execute an aggregate on the Data collection.

                Args:
                    pipeline:

                Returns:

                """
                return MongoData.objects().aggregate(pipeline)

            @staticmethod
            def init_mongo_data(data):
                """Initialize mongo data from data

                Args:
                    data:

                Returns:

                """
                try:
                    # check if data already exists in mongo
                    mongo_data = MongoData.objects.get(pk=data.id)
                except DoesNotExist:
                    # create new mongo data otherwise
                    mongo_data = MongoData()

                # Initialize mongo data fields
                mongo_data.data_id = data.id
                mongo_data.title = data.title
                # transform xml content into a dictionary
                mongo_data.dict_content = xml_utils.raw_xml_to_dict(
                    data.xml_content,
                    xml_utils.post_processor,
                    list_limit=SEARCHABLE_DATA_OCCURRENCES_LIMIT,
                )
                mongo_data._template_id = data.template.id if data.template else None
                mongo_data.user_id = data.user_id if data.user_id else None
                mongo_data._workspace_id = data.workspace.id if data.workspace else None
                mongo_data.creation_date = data.creation_date
                mongo_data.last_modification_date = data.last_modification_date
                mongo_data.last_change_date = data.last_change_date
                return mongo_data

            @staticmethod
            def post_save_data(sender, instance, **kwargs):
                """Method executed after a saving of a Data object.
                Args:
                    sender: Class.
                    instance: Data document.
                    **kwargs: Args.

                """
                if MONGODB_ASYNC_SAVE:
                    index_mongo_data.apply_async((str(instance.id),))
                else:
                    mongo_data = MongoData.init_mongo_data(instance)
                    mongo_data.save()

            @staticmethod
            def post_delete_data(sender, instance, **kwargs):
                """Method executed after a deleting of a Data object.
                Args:
                    sender: Class.
                    instance: Data document.
                    **kwargs: Args.

                """
                if MONGODB_ASYNC_SAVE:
                    delete_mongo_data.apply_async((str(instance.id),))
                else:
                    try:
                        mongo_data = MongoData.objects.get(data_id=instance.id)
                        mongo_data.delete()
                    except DoesNotExist:
                        logger.warning(
                            f"Trying to delete {str(instance.id)} but document was not found."
                        )
                    except Exception as e:
                        logger.error(f"An unexpected error occurred: {str(e)}")

        # Initialize text index
        init_text_index(MongoData)
        # connect sync method to Data post save
        post_save.connect(MongoData.post_save_data, sender=Data)
        # connect sync method to Data post delete
        post_delete.connect(MongoData.post_delete_data, sender=Data)
except ImportError as e:
    raise CoreError(
        "Mongoengine needs to be installed when MongoDB indexing is enabled. "
        "Install required python packages (see requirements.mongo.txt) "
        "or disable MongoDB indexing (MONGODB_INDEXING=False). "
    )
