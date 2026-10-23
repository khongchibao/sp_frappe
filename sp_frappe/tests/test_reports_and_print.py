import json

import frappe
from frappe.desk.doctype.number_card.number_card import get_result
from frappe.tests import IntegrationTestCase

from sp_frappe.sp_frappe.report.sp_spec_register.sp_spec_register import execute as spec_register
from sp_frappe.sp_frappe.report.sp_tooling_life.sp_tooling_life import execute as tooling_life
from sp_frappe.tests.utils import approve, make_spec, make_tooling, ready_for_approval, run_workflow

PRINT_FORMAT = "Phiếu Kỹ thuật Sản phẩm"


class TestReportsAndPrint(IntegrationTestCase):
	def setUp(self):
		frappe.set_user("Administrator")
		frappe.db.savepoint("sp_rp")
		self.addCleanup(frappe.db.rollback, save_point="sp_rp")

	def test_spec_register_columns_and_rows(self):
		spec = make_spec(customer_code="REG")
		columns, rows = spec_register({"customer": spec.customer})
		self.assertEqual(len(columns), 10)
		row = next(r for r in rows if r.name == spec.name)
		self.assertEqual(row.dimensions, "400 x 300 x 200")
		self.assertEqual(row.area_per_box_m2, 0.7297)

	def test_spec_register_filters(self):
		draft, done = make_spec(customer_code="REG"), approve(make_spec(customer_code="REG"))
		_, rows = spec_register({"spec_status": "Đã duyệt", "customer": draft.customer})
		names = {r.name for r in rows}
		self.assertIn(done.name, names)
		self.assertNotIn(draft.name, names)
		_, rows = spec_register({"box_style": "0203", "customer": draft.customer})
		self.assertFalse(rows)
		_, rows = spec_register({"from_date": "2999-01-01"})
		self.assertFalse(rows)
		_, rows = spec_register({"to_date": "2000-01-01"})
		self.assertFalse(rows)

	def test_tooling_life_report(self):
		near = make_tooling("Khuôn bế", max_life=100, usage_count=85)
		fresh = make_tooling("Khuôn bế", max_life=100, usage_count=10)
		repair = make_tooling("Bản in", max_life=100, usage_count=1, status="Sửa chữa")
		_, rows = tooling_life({})
		names = {r.name for r in rows}
		self.assertTrue({near.name, repair.name} <= names)
		self.assertNotIn(fresh.name, names)
		_, rows = tooling_life({"tooling_type": "Bản in"})
		self.assertTrue(all(r.tooling_type == "Bản in" for r in rows))

	def test_number_cards(self):
		def count(card):
			doc = frappe.get_doc("Number Card", card)
			return get_result(doc.as_dict(), doc.filters_json)

		before = {
			c: count(c) for c in ("SP Spec Cho Duyet", "SP Spec Duyet Thang Nay", "SP Cong Cu Sap Het Tuoi")
		}
		pending = make_spec()
		ready_for_approval(pending)
		run_workflow(pending, "Gửi duyệt")
		approve(make_spec())
		make_tooling("Anilox", max_life=100, usage_count=90)
		self.assertEqual(count("SP Spec Cho Duyet"), before["SP Spec Cho Duyet"] + 1)
		self.assertEqual(count("SP Spec Duyet Thang Nay"), before["SP Spec Duyet Thang Nay"] + 1)
		self.assertEqual(count("SP Cong Cu Sap Het Tuoi"), before["SP Cong Cu Sap Het Tuoi"] + 1)

	def test_workspace_references_existing_assets(self):
		ws = frappe.get_doc("Workspace", "Spec Sản phẩm")
		for card in ws.number_cards:
			self.assertTrue(frappe.db.exists("Number Card", card.number_card_name))
		for sc in ws.shortcuts:
			self.assertTrue(frappe.db.exists(sc.type, sc.link_to), sc.link_to)
		self.assertTrue(json.loads(ws.content))

	def test_print_format_renders(self):
		spec = make_spec(
			customer_code="PRT", print_method="Flexo trực tiếp",
			colors=[{"ink_code": "K", "pantone": "Black C", "coverage_percent": 100}],
			operations=[{"seq": 1, "operation": "In flexo", "note": "2 màu"}],
		)  # fmt: skip
		# Render thẳng template Jinja: frappe.get_print cần assets đã build (CI dùng --skip-assets)
		html = frappe.render_template(
			frappe.db.get_value("Print Format", PRINT_FORMAT, "html"),
			{"doc": frappe.get_doc("SP Product Spec", spec.name)},
		)
		for text in ("PHIẾU KỸ THUẬT SẢN PHẨM", spec.spec_code, "Rev 1", "400 x 300 x 200", "1445.0 x 505.0",
		             "0.7297", "Black C", "3B-125/100/125", "Lập", "Kiểm tra", "Duyệt"):  # fmt: skip
			self.assertIn(text, html)
