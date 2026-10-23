import frappe
from frappe.tests import IntegrationTestCase

from sp_frappe.demo import make_demo_data


class TestDemoData(IntegrationTestCase):
	def test_make_demo_data(self):
		result = make_demo_data()
		self.assertEqual(result["specs"], 10)
		self.assertEqual(frappe.db.count("SP Paper", {"paper_code": ["in", ["KRF-125", "DPX-250"]]}), 2)
		statuses = frappe.get_all("SP Product Spec", filters={"item_name": ["like", "[DEMO]%"]}, pluck="spec_status")
		self.assertEqual(sorted(set(statuses)), ["Chờ duyệt mẫu", "Nháp", "Đã duyệt"])
		self.assertEqual({"3", "5"}, set(frappe.get_all("SP Product Spec", filters={"item_name": ["like", "[DEMO]%"]}, pluck="ply")))
		self.assertGreaterEqual(frappe.db.count("SP Tooling"), 3)

	def test_idempotent(self):
		make_demo_data()
		grades, tools = frappe.db.count("SP Board Grade"), frappe.db.count("SP Tooling")
		self.assertEqual(make_demo_data()["specs"], 10)
		self.assertEqual((frappe.db.count("SP Board Grade"), frappe.db.count("SP Tooling")), (grades, tools))
