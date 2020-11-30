""" Fixtures file for Templates
"""
from core_main_app.components.template.models import Template
from core_main_app.utils.integration_tests.fixture_interface import FixtureInterface


class AccessControlTemplateFixture(FixtureInterface):
    """Access Control Data fixture"""

    user1_template = None
    user2_template = None
    global_template = None
    template_collection = None

    def insert_data(self):
        """Insert a set of Data.

        Returns:

        """
        # Make a connexion with a mock database
        self.generate_template_collection()

    def generate_template_collection(self):
        """Generate a Template Collections.

        Returns:

        """
        xsd = (
            '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">'
            '<xs:element name="tag"></xs:element></xs:schema>'
        )
        self.user1_template = Template(
            content=xsd,
            hash="user1_template_hash",
            filename="user1_template.xsd",
            user="1",
        ).save()
        self.user2_template = Template(
            content=xsd,
            hash="user2_template_hash",
            filename="user2_template.xsd",
            user="2",
        ).save()
        self.global_template = Template(
            content=xsd,
            hash="global_template_hash",
            filename="global_template.xsd",
            user=None,
        ).save()
        self.template_collection = [
            self.user1_template,
            self.user2_template,
            self.global_template,
        ]
