import re

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import today

from sp_frappe.sp_frappe.doctype.sp_product_spec.sp_product_spec import create_new_revision
from sp_frappe.tests.utils import (
	approve,
	make_board_grade,
	make_spec,
	make_tooling,
	make_user,
	ready_for_approval,
	run_workflow,
	spec_values,
)

IGNORE_TEST_RECORD_DEPENDENCIES = [
	"Customer",
	"Item",
	"User",
	"SP Tooling",
	"SP Board Grade",
	"Item Group",
	"UOM",
]


class SPTestCase(IntegrationTestCase):
	def setUp(self):
		# IntegrationTestCase chỉ rollback cuối class -> tự rollback sau từng test để các test độc lập
		frappe.set_user("Administrator")
		frappe.db.savepoint("sp_test")
		self.addCleanup(frappe.db.rollback, save_point="sp_test")
		self.addCleanup(frappe.set_user, "Administrator")


class TestNamingAndBlank(SPTestCase):
	def test_naming(self):
		spec = make_spec()
		self.assertRegex(spec.spec_code, r"^KG-[A-Z0-9]+-\d{4}$")
		self.assertEqual(spec.name, f"{spec.spec_code}-R1")
		self.assertEqual(spec.revision, 1)
		self.assertEqual(spec.spec_status, "Nháp")

	def test_customer_code_override(self):
		spec = make_spec(customer_code="abc")
		self.assertTrue(spec.spec_code.startswith("KG-ABC-"))

	def test_sequence_increments(self):
		a, b = make_spec(customer_code="SEQ"), make_spec(customer_code="SEQ")
		self.assertEqual(int(b.spec_code[-4:]), int(a.spec_code[-4:]) + 1)

	def test_blank_rsc_0201(self):
		spec = make_spec()
		self.assertEqual((spec.blank_l, spec.blank_w), (1445, 505))
		self.assertEqual(spec.area_per_box_m2, 0.7297)
		self.assertEqual(spec.blank_formula, "RSC_0201")

	def test_blank_fol_0203(self):
		spec = make_spec(box_style="0203")
		self.assertEqual((spec.blank_l, spec.blank_w), (1445, 805))

	def test_blank_manual(self):
		spec = make_spec(box_style="SHEET", blank_l=1000, blank_w=600)
		self.assertEqual((spec.blank_l, spec.blank_w, spec.area_per_box_m2), (1000, 600, 0.6))

	def test_manual_requires_blank(self):
		with self.assertRaises(frappe.ValidationError):
			make_spec(box_style="SHEET")

	def test_allowances_come_from_flute_master(self):
		frappe.db.set_value("SP Flute", "B", "length_allowance_mm", 20)
		self.assertEqual(make_spec().blank_l, 1455)

	def test_recalculated_on_dimension_change(self):
		spec = make_spec()
		spec.inner_l = 500
		spec.save()
		self.assertEqual(spec.blank_l, 1645)


class TestValidation(SPTestCase):
	def test_ply_must_match_flute(self):
		with self.assertRaises(frappe.ValidationError):
			make_spec(ply="5")

	def test_board_grade_must_match_flute(self):
		other = make_board_grade(3, "C", (150, 100, 150))
		with self.assertRaises(frappe.ValidationError):
			make_spec(board_grade=other.name)

	def test_board_grade_must_match_ply(self):
		five = make_board_grade(5, "BC", (150, 125, 150, 125, 150))
		with self.assertRaises(frappe.ValidationError):
			make_spec(board_grade_doc=five, ply="3", flute="BC")

	def test_dimension_range(self):
		for bad in (49, 2501):
			with self.assertRaises(frappe.ValidationError):
				make_spec(inner_l=bad)
		self.assertEqual(make_spec(inner_l=50).inner_l, 50)
		self.assertEqual(make_spec(inner_h=2500).inner_h, 2500)

	def test_die_required_by_box_style(self):
		with self.assertRaises(frappe.ValidationError):
			make_spec(box_style="DIECUT", blank_l=900, blank_w=500)
		die = make_tooling("Khuôn bế")
		spec = make_spec(box_style="DIECUT", blank_l=900, blank_w=500, cutting_die=die.name)
		self.assertEqual(spec.cutting_die, die.name)

	def test_die_must_be_die_type(self):
		plate = make_tooling("Bản in")
		with self.assertRaises(frappe.ValidationError):
			make_spec(box_style="0427", blank_l=900, blank_w=500, cutting_die=plate.name)

	def test_printing_requires_colors(self):
		with self.assertRaises(frappe.ValidationError):
			make_spec(print_method="Flexo trực tiếp")

	def test_color_count_and_coverage(self):
		colors = [
			{"ink_code": "K", "coverage_percent": 80},
			{"ink_code": "C", "pantone": "300C", "coverage_percent": 40},
		]
		spec = make_spec(print_method="Flexo trực tiếp", colors=colors)
		self.assertEqual(spec.color_count, 2)
		with self.assertRaises(frappe.ValidationError):
			make_spec(print_method="Offset bồi", colors=[{"ink_code": "K", "coverage_percent": 101}])

	def test_no_print_rejects_colors(self):
		with self.assertRaises(frappe.ValidationError):
			make_spec(print_method="Không in", colors=[{"ink_code": "K", "coverage_percent": 50}])

	def test_negative_quality_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			make_spec(ect_min=-1)

	def test_moisture_over_100_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			make_spec(moisture_max=101)


class TestApproval(SPTestCase):
	def test_needs_artwork_and_sample_date(self):
		spec = make_spec()
		run_workflow(spec, "Gửi duyệt")
		spec.reload()
		with self.assertRaises(frappe.ValidationError):
			run_workflow(spec, "Duyệt")

	def test_needs_packing_to_approve(self):
		spec = make_spec(qty_per_bundle=0, bundles_per_pallet=0)
		ready_for_approval(spec)
		run_workflow(spec, "Gửi duyệt")
		spec.reload()
		with self.assertRaises(frappe.ValidationError):
			run_workflow(spec, "Duyệt")

	def test_approval_creates_item(self):
		spec = approve(make_spec())
		self.assertEqual(spec.spec_status, "Đã duyệt")
		self.assertEqual(spec.approved_by, "Administrator")
		self.assertEqual(spec.erpnext_item, spec.spec_code)
		item = frappe.get_doc("Item", spec.spec_code)
		self.assertEqual(
			(item.item_group, item.stock_uom, item.item_name), ("Products", "Thùng", spec.item_name)
		)
		self.assertIn("400 x 300 x 200", item.description)

	def test_item_creation_can_be_disabled(self):
		frappe.db.set_single_value("SP Settings", "auto_create_item", 0)
		spec = approve(make_spec())
		self.assertFalse(spec.erpnext_item)
		self.assertFalse(frappe.db.exists("Item", spec.spec_code))

	def test_tooling_usage_bumped_once(self):
		die, plate = make_tooling("Khuôn bế"), make_tooling("Bản in")
		spec = make_spec(
			box_style="0427", blank_l=900, blank_w=500, cutting_die=die.name, printing_plate=plate.name,
			print_method="Flexo trực tiếp", colors=[{"ink_code": "K", "coverage_percent": 100}],
		)  # fmt: skip
		approve(spec)
		for name in (die.name, plate.name):
			doc = frappe.get_doc("SP Tooling", name)
			self.assertEqual((doc.usage_count, str(doc.last_used_on)), (1, today()))
		spec.reload()
		self.assertEqual(spec.usage_counted, 1)

	def test_return_to_draft(self):
		spec = make_spec()
		ready_for_approval(spec)
		run_workflow(spec, "Gửi duyệt")
		spec.reload()
		run_workflow(spec, "Trả lại")
		spec.reload()
		self.assertEqual(spec.spec_status, "Nháp")

	def test_retire_after_approval(self):
		spec = approve(make_spec())
		run_workflow(spec, "Ngưng sử dụng")
		spec.reload()
		self.assertEqual(spec.spec_status, "Ngưng")


class TestRevisionLock(SPTestCase):
	def test_locked_fields_cannot_change(self):
		spec = approve(make_spec())
		spec.inner_l = 500
		with self.assertRaises(frappe.ValidationError):
			spec.save()

	def test_locked_tables_cannot_change(self):
		spec = approve(make_spec())
		spec.append("operations", {"seq": 1, "operation": "Bế"})
		with self.assertRaises(frappe.ValidationError):
			spec.save()

	def test_resave_unchanged_is_allowed(self):
		spec = approve(make_spec(ect_min=6.5, bct_min=1200))
		spec.reload()
		spec.save()

	def test_quality_fields_stay_editable(self):
		spec = approve(make_spec())
		spec.ect_min = 7
		spec.save()
		self.assertEqual(frappe.db.get_value("SP Product Spec", spec.name, "ect_min"), 7)

	def test_lock_list_comes_from_settings(self):
		frappe.db.set_single_value("SP Settings", "revision_lock_fields", "item_name")
		spec = approve(make_spec())
		spec.inner_l = 450
		spec.save()  # không còn bị khóa
		spec.item_name = "Tên khác"
		with self.assertRaises(frappe.ValidationError):
			spec.save()

	def test_new_revision(self):
		spec = approve(make_spec(ect_min=6))
		new_name = create_new_revision(spec.name)
		new = frappe.get_doc("SP Product Spec", new_name)
		self.assertEqual((new.revision, new.previous_revision, new.spec_status), (2, spec.name, "Nháp"))
		self.assertEqual(new.spec_code, spec.spec_code)
		self.assertTrue(new.name.endswith("-R2"))
		self.assertEqual((new.inner_l, new.ect_min, new.approved_by), (400, 6, None))

	def test_cannot_open_two_revisions(self):
		spec = approve(make_spec())
		create_new_revision(spec.name)
		with self.assertRaises(frappe.ValidationError):
			create_new_revision(spec.name)

	def test_revision_only_from_approved(self):
		spec = make_spec()
		with self.assertRaises(frappe.ValidationError):
			create_new_revision(spec.name)

	def test_approving_new_revision_retires_old(self):
		r1 = approve(make_spec())
		r2 = frappe.get_doc("SP Product Spec", create_new_revision(r1.name))
		r2.inner_l = 450
		r2.save()
		approve(r2)
		self.assertEqual(frappe.db.get_value("SP Product Spec", r1.name, "spec_status"), "Ngưng")
		self.assertEqual(r2.spec_status, "Đã duyệt")
		self.assertEqual(r2.erpnext_item, r1.erpnext_item)
		self.assertIn("450 x 300 x 200", frappe.db.get_value("Item", r2.spec_code, "description"))

	def test_tooling_not_double_counted_across_revisions(self):
		die = make_tooling("Khuôn bế")
		r1 = approve(make_spec(box_style="DIECUT", blank_l=900, blank_w=500, cutting_die=die.name))
		approve(frappe.get_doc("SP Product Spec", create_new_revision(r1.name)))
		self.assertEqual(frappe.db.get_value("SP Tooling", die.name, "usage_count"), 1)


class TestRolesAndWorkflow(SPTestCase):
	def setUp(self):
		super().setUp()
		self.kt = make_user("sp.kythuat@example.com", ["SP Kỹ thuật"]).name
		self.kd = make_user("sp.kinhdoanh@example.com", ["SP Kinh doanh"]).name
		self.qc = make_user("sp.qc@example.com", ["SP QC"]).name
		self.ql = make_user("sp.quanly@example.com", ["SP Quản lý"]).name

	def test_engineer_submits_but_cannot_approve(self):
		frappe.set_user(self.kt)
		spec = make_spec()
		ready_for_approval(spec)
		run_workflow(spec, "Gửi duyệt")
		spec.reload()
		with self.assertRaises(frappe.ValidationError):
			run_workflow(spec, "Duyệt")

	def test_sales_approves(self):
		frappe.set_user(self.kt)
		spec = make_spec()
		ready_for_approval(spec)
		run_workflow(spec, "Gửi duyệt")
		frappe.set_user(self.kd)
		spec.reload()
		run_workflow(spec, "Duyệt")
		spec.reload()
		self.assertEqual((spec.spec_status, spec.approved_by), ("Đã duyệt", self.kd))

	def test_sales_cannot_edit_technical_fields(self):
		spec = make_spec()
		frappe.set_user(self.kd)
		spec.reload()
		spec.item_name = "Sửa lén"
		with self.assertRaises(frappe.PermissionError):
			spec.save()

	def test_qc_edits_only_quality_group(self):
		spec = approve(make_spec())
		frappe.set_user(self.qc)
		spec.reload()
		spec.bct_min = 1500
		spec.save()
		spec.inner_w = 310
		with self.assertRaises(frappe.PermissionError):
			spec.save()

	def test_only_manager_retires(self):
		spec = approve(make_spec())
		frappe.set_user(self.kt)
		spec.reload()
		with self.assertRaises(frappe.ValidationError):
			run_workflow(spec, "Ngưng sử dụng")
		frappe.set_user(self.ql)
		spec.reload()
		run_workflow(spec, "Ngưng sử dụng")
		spec.reload()
		self.assertEqual(spec.spec_status, "Ngưng")

	def test_engineer_can_create_revision(self):
		spec = approve(make_spec())
		frappe.set_user(self.kt)
		self.assertTrue(re.search(r"-R2$", create_new_revision(spec.name)))
