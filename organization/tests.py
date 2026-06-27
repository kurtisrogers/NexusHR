from django.test import TestCase

from hrms.test_utils import create_company, create_department


class OrganizationModelTests(TestCase):
    def test_company_str(self):
        company = create_company(name="Nexus Industries")
        self.assertEqual(str(company), "Nexus Industries")

    def test_department_str(self):
        company = create_company()
        department = create_department(company, name="Finance")
        self.assertEqual(str(department), "Finance")
