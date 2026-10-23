import frappe
from frappe.tests import IntegrationTestCase


class TestSPBoxStyle(IntegrationTestCase):
	def test_six_styles_seeded(self):
		self.assertTrue({"0201", "0203", "0300", "0427", "DIECUT", "SHEET"} <= set(frappe.get_all("SP Box Style", pluck="name")))

	def test_formulas(self):
		self.assertEqual(frappe.db.get_value("SP Box Style", "0201", "blank_formula"), "RSC_0201")
		self.assertEqual(frappe.db.get_value("SP Box Style", "0203", "blank_formula"), "FOL_0203")
		self.assertEqual(frappe.db.get_value("SP Box Style", "DIECUT", "blank_formula"), "MANUAL")

	def test_die_requirement_flags(self):
		self.assertEqual(frappe.db.get_value("SP Box Style", "DIECUT", "requires_die"), 1)
		self.assertEqual(frappe.db.get_value("SP Box Style", "0201", "requires_die"), 0)
