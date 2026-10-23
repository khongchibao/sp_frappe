import frappe
from frappe.tests import IntegrationTestCase

IGNORE_TEST_RECORD_DEPENDENCIES = ["Supplier"]


class TestSPPaper(IntegrationTestCase):
	def test_gsm_must_be_positive(self):
		doc = frappe.get_doc({"doctype": "SP Paper", "paper_code": "T-BAD", "paper_type": "Kraft", "gsm": 0})
		self.assertRaises(frappe.ValidationError, doc.insert)

	def test_create(self):
		doc = frappe.get_doc({"doctype": "SP Paper", "paper_code": "T-OK", "paper_type": "Test liner", "gsm": 150})
		doc.insert()
		self.assertEqual(doc.color, "Nâu")
		self.assertEqual(doc.active, 1)
