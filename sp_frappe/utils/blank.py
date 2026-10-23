"""Tính khổ phôi và diện tích phôi. Hàm thuần, không phụ thuộc frappe để test độc lập."""

from collections.abc import Mapping
from dataclasses import dataclass

FORMULAS = ("RSC_0201", "FOL_0203", "MANUAL")


class BlankError(ValueError):
	"""Dữ liệu đầu vào không hợp lệ để tính khổ phôi."""


@dataclass(frozen=True)
class BlankResult:
	blank_l: float
	blank_w: float
	area_m2: float


def _num(value, label: str, *, minimum_exclusive: float | None = None, minimum: float | None = None) -> float:
	try:
		number = float(value)
	except (TypeError, ValueError):
		raise BlankError(f"{label} phải là số") from None
	if minimum_exclusive is not None and number <= minimum_exclusive:
		raise BlankError(f"{label} phải lớn hơn {minimum_exclusive:g}")
	if minimum is not None and number < minimum:
		raise BlankError(f"{label} không được nhỏ hơn {minimum:g}")
	return number


def calc_blank(
	style_formula: str,
	length: float,
	width: float,
	height: float,
	flute_params: Mapping[str, float] | None,
	manual_l: float | None = None,
	manual_w: float | None = None,
) -> BlankResult:
	"""Trả về khổ phôi (mm) và m²/thùng.

	RSC_0201: dài = 2L + 2W + mép dán + bù dài;  rộng = H + W + bù rộng
	FOL_0203: dài như trên;                       rộng = H + 2W + bù rộng
	MANUAL:   giữ nguyên giá trị nhập tay (bắt buộc > 0)

	flute_params cần: length_allowance_mm, width_allowance_mm, glue_flap_mm (lấy từ master SP Flute).
	"""
	if style_formula not in FORMULAS:
		raise BlankError(f"Công thức khổ phôi không hợp lệ: {style_formula}")

	if style_formula == "MANUAL":
		blank_l = _num(manual_l, "Khổ phôi dài", minimum_exclusive=0)
		blank_w = _num(manual_w, "Khổ phôi rộng", minimum_exclusive=0)
	else:
		L = _num(length, "Dài trong", minimum_exclusive=0)
		W = _num(width, "Rộng trong", minimum_exclusive=0)
		H = _num(height, "Cao trong", minimum_exclusive=0)
		if not flute_params:
			raise BlankError("Thiếu hệ số bù khổ của loại sóng")
		len_allow = _num(flute_params.get("length_allowance_mm", 0), "Bù khổ dài", minimum=0)
		wid_allow = _num(flute_params.get("width_allowance_mm", 0), "Bù khổ rộng", minimum=0)
		glue = _num(flute_params.get("glue_flap_mm", 0), "Mép dán", minimum=0)
		blank_l = 2 * L + 2 * W + glue + len_allow
		blank_w = (H + W if style_formula == "RSC_0201" else H + 2 * W) + wid_allow

	blank_l, blank_w = round(blank_l, 1), round(blank_w, 1)
	return BlankResult(blank_l, blank_w, round(blank_l * blank_w / 1_000_000, 4))
