import unittest

from sp_frappe.utils.blank import BlankError, calc_blank

B = {"length_allowance_mm": 10, "width_allowance_mm": 5, "glue_flap_mm": 35}


class TestCalcBlank(unittest.TestCase):
	def test_rsc_0201(self):
		r = calc_blank("RSC_0201", 400, 300, 200, B)
		self.assertEqual(r.blank_l, 2 * 400 + 2 * 300 + 35 + 10)
		self.assertEqual(r.blank_w, 200 + 300 + 5)
		self.assertEqual(r.area_m2, round(1445 * 505 / 1e6, 4))

	def test_fol_0203_width_uses_two_w(self):
		r = calc_blank("FOL_0203", 400, 300, 200, B)
		self.assertEqual(r.blank_l, 1445)
		self.assertEqual(r.blank_w, 200 + 600 + 5)

	def test_manual_keeps_values(self):
		r = calc_blank("MANUAL", 0, 0, 0, None, manual_l=820.5, manual_w=410)
		self.assertEqual((r.blank_l, r.blank_w), (820.5, 410))
		self.assertEqual(r.area_m2, round(820.5 * 410 / 1e6, 4))

	def test_manual_requires_positive(self):
		for l, w in [(0, 100), (100, 0), (None, 100), (100, None), (-5, 100)]:
			with self.assertRaises(BlankError):
				calc_blank("MANUAL", 1, 1, 1, None, manual_l=l, manual_w=w)

	def test_unknown_formula(self):
		with self.assertRaises(BlankError):
			calc_blank("XYZ", 100, 100, 100, B)

	def test_missing_flute_params(self):
		with self.assertRaises(BlankError):
			calc_blank("RSC_0201", 100, 100, 100, None)

	def test_non_positive_dimensions(self):
		for dims in [(0, 100, 100), (100, 0, 100), (100, 100, 0), (-1, 100, 100)]:
			with self.assertRaises(BlankError):
				calc_blank("RSC_0201", *dims, B)

	def test_non_numeric_dimension(self):
		with self.assertRaises(BlankError):
			calc_blank("RSC_0201", "abc", 100, 100, B)

	def test_negative_allowance_rejected(self):
		with self.assertRaises(BlankError):
			calc_blank("RSC_0201", 100, 100, 100, {**B, "length_allowance_mm": -1})

	def test_zero_allowances_allowed(self):
		r = calc_blank("RSC_0201", 100, 100, 100, {"length_allowance_mm": 0, "width_allowance_mm": 0, "glue_flap_mm": 0})
		self.assertEqual((r.blank_l, r.blank_w), (400, 200))

	def test_string_numbers_from_form(self):
		r = calc_blank("RSC_0201", "400", "300", "200", B)
		self.assertEqual(r.blank_l, 1445)

	def test_minimum_size_boundary(self):
		r = calc_blank("RSC_0201", 50, 50, 50, B)
		self.assertEqual((r.blank_l, r.blank_w), (245, 105))

	def test_large_box_area(self):
		r = calc_blank("RSC_0201", 2500, 2500, 2500, B)
		self.assertEqual(r.blank_l, 10045)
		self.assertAlmostEqual(r.area_m2, 10045 * 5005 / 1e6, places=3)

	def test_rounding_one_decimal(self):
		r = calc_blank("RSC_0201", 100, 100, 100, {"length_allowance_mm": 0.26, "width_allowance_mm": 0.04, "glue_flap_mm": 35})
		self.assertEqual(r.blank_l, 435.3)
		self.assertEqual(r.blank_w, 200.0)

	def test_flute_params_from_flute_differ(self):
		b = calc_blank("RSC_0201", 300, 200, 150, {"length_allowance_mm": 24, "width_allowance_mm": 12, "glue_flap_mm": 35})
		c = calc_blank("RSC_0201", 300, 200, 150, B)
		self.assertGreater(b.blank_l, c.blank_l)
