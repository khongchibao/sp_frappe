import frappe
from frappe.tests import IntegrationTestCase

from sp_frappe.tests.utils import make_tooling

IGNORE_TEST_RECORD_DEPENDENCIES = ["Customer"]


class TestSPTooling(IntegrationTestCase):
	def test_naming_by_type(self):
		self.assertTrue(make_tooling("Khuôn bế").name.startswith("KB-"))
		self.assertTrue(make_tooling("Bản in").name.startswith("BI-"))
		self.assertTrue(make_tooling("Anilox").name.startswith("AN-"))

	def test_life_percent(self):
		doc = make_tooling("Khuôn bế", max_life=1000, usage_count=250)
		self.assertEqual(doc.life_percent, 25)

	def test_expires_at_100_percent(self):
		doc = make_tooling("Bản in", max_life=100, usage_count=100)
		self.assertEqual(doc.status, "Hết hạn")

	def test_no_max_life_means_zero_percent(self):
		doc = make_tooling("Anilox", max_life=0, usage_count=5)
		self.assertEqual(doc.life_percent, 0)

	def test_negative_rejected(self):
		doc = frappe.get_doc({"doctype": "SP Tooling", "tooling_type": "Anilox", "max_life": -1})
		self.assertRaises(frappe.ValidationError, doc.insert)
