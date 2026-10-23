"""Nhúng template.html vào JSON của Print Format (Frappe không tự đọc file .html cho format Jinja chuẩn).

Chạy lại sau mỗi lần sửa template:  python scripts/build_print_format.py
"""

import json
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent / "sp_frappe" / "sp_frappe" / "print_format" / "phieu_ky_thuat_san_pham"
NAME = "Phiếu Kỹ thuật Sản phẩm"


def main():
	html = (DIR / "template.html").read_text(encoding="utf-8")
	doc = {
		"align_labels_right": 0,
		"creation": "2026-10-23 14:00:00.000000",
		"custom_format": 1,
		"default_print_language": "vi",
		"disabled": 0,
		"doc_type": "SP Product Spec",
		"docstatus": 0,
		"doctype": "Print Format",
		"font_size": 10,
		"html": html,
		"idx": 0,
		"line_breaks": 0,
		"margin_bottom": 15.0,
		"margin_left": 12.0,
		"margin_right": 12.0,
		"margin_top": 12.0,
		"modified": "2026-10-23 14:00:00.000000",
		"modified_by": "Administrator",
		"module": "SP Frappe",
		"name": NAME,
		"owner": "Administrator",
		"page_number": "Hide",
		"print_format_builder": 0,
		"print_format_builder_beta": 0,
		"print_format_type": "Jinja",
		"raw_printing": 0,
		"show_section_headings": 0,
		"standard": "Yes",
	}
	out = DIR / f"{DIR.name}.json"
	out.write_text(json.dumps(doc, indent=1, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
	print("wrote", out)


if __name__ == "__main__":
	main()
