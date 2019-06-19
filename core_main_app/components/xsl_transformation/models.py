""" XslTransformation model
"""
from django_mongoengine import fields, Document
from mongoengine import errors as mongoengine_errors

from core_main_app.commons import exceptions
from core_main_app.commons.regex import NOT_EMPTY_OR_WHITESPACES


class XslTransformation(Document):
    """ XslTransformation object
    """
    name = fields.StringField(blank=False, unique=True, regex=NOT_EMPTY_OR_WHITESPACES)
    filename = fields.StringField(blank=False, regex=NOT_EMPTY_OR_WHITESPACES)
    content = fields.StringField(blank=False)

    meta = {'allow_inheritance': True}

    def __str__(self):
        """ String representation of an object.

        Returns:
            String representation

        """
        return self.name

    @staticmethod
    def get_all():
        """ Get all XSL Transformations.

        Returns:

        """
        return XslTransformation.objects.all()

    @staticmethod
    def get_by_name(xslt_name):
        """ Get XSL Transformation by name.

        Args:
            xslt_name:

        Returns:

        """
        try:
            return XslTransformation.objects.get(name=xslt_name)
        except mongoengine_errors.DoesNotExist as e:
            raise exceptions.DoesNotExist(str(e))
        except Exception as e:
            raise exceptions.ModelError(str(e))

    @staticmethod
    def get_by_id(xslt_id):
        """ Get an XSLT document by its id.

        Args:
            xslt_id: Id.

        Returns:
            XslTransformation object.

        """
        try:
            return XslTransformation.objects.get(pk=str(xslt_id))
        except mongoengine_errors.DoesNotExist as e:
            raise exceptions.DoesNotExist(str(e))
        except Exception as ex:
            raise exceptions.ModelError(str(ex))

    def save_object(self):
        """ Custom save.

        Returns:
            Saved Instance.

        """
        try:
            return self.save()
        except mongoengine_errors.NotUniqueError as e:
            raise exceptions.NotUniqueError(str(e))
        except Exception as ex:
            raise exceptions.ModelError(str(ex))

    def clean(self):
        """ Clean is called before saving

        Returns:

        """
        self.name = self.name.strip()
        self.filename = self.filename.strip()

