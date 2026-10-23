"""Quy tắc đặt mã. Hàm thuần, không phụ thuộc frappe."""

import re
import unicodedata

_STOP_WORDS = {
	"cong", "ty", "tnhh", "cp", "co", "phan", "mtv", "ltd", "jsc", "company", "limited", "corp", "the",
	"dn", "dntn", "hkd", "san", "xuat", "thuong", "mai", "dich", "vu", "va",
}  # fmt: skip


def strip_accents(text: str) -> str:
	text = (text or "").replace("đ", "d").replace("Đ", "D")
	return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))


def derive_customer_code(customer_name: str, max_len: int = 4) -> str:
	"""Viết tắt từ tên khách hàng: bỏ dấu, bỏ từ chung (Công ty, TNHH...), lấy chữ cái đầu.

	"Công ty TNHH Thực phẩm An Phát" -> "TPAP"; nếu rỗng trả về "KH".
	"""
	words = re.findall(r"[A-Za-z0-9]+", strip_accents(customer_name))
	words = [w for w in words if w.lower() not in _STOP_WORDS] or words
	code = "".join(w[0] for w in words[:max_len]).upper()
	return code or "KH"


def normalize_customer_code(code: str) -> str:
	"""Chuẩn hóa mã khách hàng nhập tay: bỏ dấu, chỉ giữ A-Z0-9, in hoa."""
	return re.sub(r"[^A-Z0-9]", "", strip_accents(code).upper())


def board_grade_name(ply: str | int, flute: str, gsms: list[int]) -> str:
	"""Tên kết cấu giấy: <số lớp><sóng>-<gsm lớp 1>/<gsm lớp 2>/..., ví dụ 3B-125/100/125."""
	return f"{ply}{flute}-" + "/".join(str(int(g)) for g in gsms)
