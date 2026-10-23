import frappe
from frappe.tests import IntegrationTestCase

from sp_frappe.sp_frappe.doctype.sp_settings.sp_settings import get_lock_fields, parse_lock_fields

IGNORE_TEST_RECORD_DEPENDENCIES = ["Item Group", "UOM"]


class TestSPSettings(IntegrationTestCase):
	def test_defaults_after_install(self):
		doc = frappe.get_single("SP Settings")
		self.assertEqual(doc.stock_uom, "Thùng")
		self.assertTrue(doc.auto_create_item)
		self.assertIn("inner_l", get_lock_fields())

	def test_parse_accepts_commas_and_lines(self):
		self.assertEqual(parse_lock_fields("a, b\nc"), ["a", "b", "c"])

	def test_unknown_field_rejected(self):
		doc = frappe.get_single("SP Settings")
		doc.revision_lock_fields = "inner_l\nkhong_ton_tai"
		self.assertRaises(frappe.ValidationError, doc.save)
