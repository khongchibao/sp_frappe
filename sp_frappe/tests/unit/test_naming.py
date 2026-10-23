import unittest

from sp_frappe.utils.naming import board_grade_name, derive_customer_code, normalize_customer_code


class TestNaming(unittest.TestCase):
	def test_derive_strips_generic_words_and_accents(self):
		self.assertEqual(derive_customer_code("Công ty TNHH Thực phẩm An Phát"), "TPAP")

	def test_derive_handles_d_bar(self):
		self.assertEqual(derive_customer_code("Điện máy Đại Nam"), "DMDN")

	def test_derive_empty_falls_back(self):
		self.assertEqual(derive_customer_code(""), "KH")
		self.assertEqual(derive_customer_code("***"), "KH")

	def test_derive_only_generic_words(self):
		self.assertEqual(derive_customer_code("Công ty TNHH"), "CTT")

	def test_derive_max_len(self):
		self.assertEqual(len(derive_customer_code("Alpha Beta Gamma Delta Epsilon")), 4)

	def test_normalize(self):
		self.assertEqual(normalize_customer_code(" t-p ạp "), "TPAP")

	def test_board_grade_name(self):
		self.assertEqual(board_grade_name(3, "B", [125, 100, 125]), "3B-125/100/125")
		self.assertEqual(board_grade_name("5", "BC", [150, 125, 150, 125, 150]), "5BC-150/125/150/125/150")
