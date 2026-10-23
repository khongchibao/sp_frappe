import frappe
from frappe.tests import IntegrationTestCase

IGNORE_TEST_RECORD_DEPENDENCIES = ["Customer", "Supplier", "User", "Item", "Item Group", "UOM"]


class TestSPFlute(IntegrationTestCase):
	def test_seven_flutes_seeded(self):
		codes = set(frappe.get_all("SP Flute", pluck="name"))
		self.assertTrue({"A", "B", "C", "E", "BC", "BE", "CE"} <= codes)

	def test_seeded_flutes_are_flagged_as_assumptions(self):
		self.assertEqual(frappe.db.get_value("SP Flute", "B", "is_assumed"), 1)
		self.assertEqual(frappe.db.get_value("SP Flute", "B", "glue_flap_mm"), 35)

	def test_ply_matches_code(self):
		self.assertEqual(frappe.db.get_value("SP Flute", "BC", "ply"), "5")
		self.assertEqual(frappe.db.get_value("SP Flute", "E", "ply"), "3")

	def test_negative_allowance_rejected(self):
		doc = frappe.get_doc({"doctype": "SP Flute", "flute_code": "zz", "ply": "3", "length_allowance_mm": -1})
		self.assertRaises(frappe.ValidationError, doc.insert)

	def test_code_uppercased(self):
		doc = frappe.get_doc({"doctype": "SP Flute", "flute_code": "ab", "ply": "5"})
		doc.insert()
		self.assertEqual(doc.name, "AB")
