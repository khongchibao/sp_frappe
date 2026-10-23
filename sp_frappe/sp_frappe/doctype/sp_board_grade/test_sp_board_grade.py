import frappe
from frappe.tests import IntegrationTestCase

from sp_frappe.tests.utils import make_board_grade, make_paper

IGNORE_TEST_RECORD_DEPENDENCIES = ["Supplier"]


class TestSPBoardGrade(IntegrationTestCase):
	def test_name_pattern_3_ply(self):
		self.assertEqual(make_board_grade(3, "B", (135, 95, 135)).name, "3B-135/95/135")

	def test_name_pattern_5_ply(self):
		doc = make_board_grade(5, "BC", (155, 115, 155, 115, 155))
		self.assertEqual(doc.name, "5BC-155/115/155/115/155")

	def test_duplicate_gets_suffix(self):
		first = make_board_grade(3, "C", (165, 105, 165))
		second = make_board_grade(3, "C", (165, 105, 165))
		self.assertEqual(second.name, first.name + "-2")

	def test_layer_count_must_equal_ply(self):
		doc = frappe.get_doc(
			{
				"doctype": "SP Board Grade", "ply": "5", "flute": "BC",
				"layers": [{"layer_role": "Mặt", "paper": make_paper("T-KRA-125", 125)}] * 3,
			}
		)  # fmt: skip
		self.assertRaises(frappe.ValidationError, doc.insert)

	def test_flute_ply_must_match(self):
		with self.assertRaises(frappe.ValidationError):
			make_board_grade(3, "BC", (125, 100, 125))

	def test_needs_flute_layers(self):
		with self.assertRaises(frappe.ValidationError):
			make_board_grade(3, "B", (125, 100, 125), roles=["Mặt", "Lót giữa", "Đáy"])

	def test_first_and_last_roles(self):
		with self.assertRaises(frappe.ValidationError):
			make_board_grade(3, "B", (125, 100, 125), roles=["Đáy", "Sóng", "Mặt"])

	def test_gsm_fetched_from_paper(self):
		doc = make_board_grade(3, "E", (200, 100, 200))
		self.assertEqual([row.gsm for row in doc.layers], [200, 100, 200])
