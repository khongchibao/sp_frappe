"""Sinh docs/DATA_DICTIONARY.md từ DocType JSON.

python scripts/gen_data_dictionary.py          # ghi file
python scripts/gen_data_dictionary.py --check  # thoát mã 1 nếu file chưa cập nhật (dùng trong CI)
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCTYPE_DIR = ROOT / "sp_frappe" / "sp_frappe" / "doctype"
OUT = ROOT / "docs" / "DATA_DICTIONARY.md"

ORDER = [
	"SP Product Spec", "SP Spec Color", "SP Spec Operation", "SP Board Grade", "SP Board Grade Layer",
	"SP Paper", "SP Flute", "SP Box Style", "SP Tooling", "SP Settings",
]  # fmt: skip
LAYOUT = {"Section Break", "Column Break", "Tab Break"}

# Quy tắc nghiệp vụ nằm trong controller (không thể suy ra từ JSON)
RULES = {
	"SP Product Spec": [
		"Tên document = `{spec_code}-R{revision}`; `spec_code` = `KG-{customer_code}-####`, `customer_code` tự sinh từ tên khách hàng nếu để trống.",
		"`ply` phải khớp loại sóng và kết cấu giấy; kết cấu giấy phải dùng đúng loại sóng của spec.",
		"Kích thước trong 50-2500 mm. Khổ phôi và m²/thùng tự tính từ công thức của kiểu hộp + hệ số bù của loại sóng.",
		"Có in (Flexo/Offset) thì bảng màu không được rỗng, độ phủ 0-100; không in thì bảng màu phải rỗng.",
		"Kiểu hộp đánh dấu `requires_die` thì bắt buộc có khuôn bế; khuôn bế/bản in phải đúng loại công cụ.",
		"Trước khi duyệt: bắt buộc `artwork_file`, `approved_sample_date`, `qty_per_bundle`, `bundles_per_pallet`.",
		"Spec Đã duyệt/Ngưng: các trường trong SP Settings > `revision_lock_fields` không được sửa; dùng 'Tạo phiên bản mới'.",
		"SP QC chỉ sửa nhóm Chất lượng; SP Kinh doanh chỉ thao tác workflow; SP Kỹ thuật/Quản lý sửa tự do khi chưa khóa.",
		"Khi duyệt: tạo/cập nhật Item ERPNext (nếu bật), cộng usage_count khuôn/bản in (một lần cho mỗi spec_code + công cụ), chuyển bản đã duyệt trước đó sang Ngưng.",
	],
	"SP Board Grade": [
		"Tên tự sinh `<số lớp><sóng>-<gsm các lớp>`, ví dụ `3B-125/100/125`; trùng thì thêm hậu tố `-2`, `-3`.",
		"Số dòng lớp = số lớp; lớp đầu là Mặt, lớp cuối là Đáy; số lớp Sóng = số lớp // 2 và xen kẽ lớp phẳng.",
	],
	"SP Tooling": [
		"Tên theo loại: `KB-####` (khuôn bế), `BI-####` (bản in), `AN-####` (anilox).",
		"`life_percent` = usage_count / max_life; đạt 100% thì trạng thái tự chuyển Hết hạn.",
	],
	"SP Flute": ["Hệ số bù khổ và mép dán là [GIẢ ĐỊNH]; sửa trực tiếp ở master, không cần sửa code."],
	"SP Settings": [
		"`revision_lock_fields`: mỗi dòng một fieldname của SP Product Spec; lưu sai tên sẽ báo lỗi."
	],
}

PURPOSE = {
	"spec_code": "Mã định danh spec, giữ nguyên qua các phiên bản",
	"revision": "Số phiên bản (R1, R2...)",
	"spec_status": "Trạng thái do Workflow điều khiển",
	"blank_l": "Khổ phôi dài; tự tính (nhập tay khi công thức MANUAL)",
	"blank_w": "Khổ phôi rộng; tự tính (nhập tay khi công thức MANUAL)",
	"area_per_box_m2": "Diện tích phôi cho một thùng, dùng tính giá/định mức giấy",
	"erpnext_item": "Item ERPNext được tạo khi duyệt",
	"usage_counted": "Cờ nội bộ: đã cộng usage_count cho công cụ",
	"length_allowance_mm": "Hệ số bù khổ dài theo loại sóng [GIẢ ĐỊNH]",
	"width_allowance_mm": "Hệ số bù khổ rộng theo loại sóng [GIẢ ĐỊNH]",
	"glue_flap_mm": "Mép dán/ghim cộng vào chiều dài phôi [GIẢ ĐỊNH]",
	"is_assumed": "Đánh dấu hệ số chưa được xưởng xác nhận",
	"life_percent": "Mức tuổi thọ đã dùng, dùng cho báo cáo SP Tooling Life",
	"revision_lock_fields": "Danh sách trường bị khóa sau khi duyệt",
}


def load():
	docs = {}
	for path in DOCTYPE_DIR.glob("*/*.json"):
		d = json.loads(path.read_text(encoding="utf-8"))
		docs[d["name"]] = d
	return docs


def validation(f):
	parts = []
	ft, opts = f["fieldtype"], f.get("options")
	if ft in ("Link", "Table"):
		parts.append(f"→ {opts}")
	if ft == "Select":
		parts.append("Chọn: " + " / ".join(o for o in opts.split("\n") if o))
	if f.get("unique"):
		parts.append("duy nhất")
	if f.get("default") not in (None, ""):
		parts.append(f"mặc định: {f['default']}")
	if f.get("fetch_from"):
		parts.append(f"lấy từ {f['fetch_from']}")
	if f.get("depends_on"):
		parts.append(f"hiện khi `{f['depends_on']}`")
	if f.get("read_only_depends_on"):
		parts.append(f"chỉ đọc khi `{f['read_only_depends_on']}`")
	if f.get("length"):
		parts.append(f"tối đa {f['length']} ký tự")
	if f.get("precision"):
		parts.append(f"{f['precision']} chữ số thập phân")
	if f.get("no_copy"):
		parts.append("không copy khi nhân bản")
	return "; ".join(parts)


def render(docs):
	lines = [
		"# Từ điển dữ liệu SP Frappe",
		"",
		"> Tệp này sinh tự động bằng `python scripts/gen_data_dictionary.py` - không sửa tay.",
		"",
	]
	names = [n for n in ORDER if n in docs] + sorted(set(docs) - set(ORDER))
	for name in names:
		d = docs[name]
		kind = "Child table" if d.get("istable") else "Single" if d.get("issingle") else "DocType"
		lines += [
			f"## {name}",
			"",
			f"*{kind}*" + (f" - đặt tên: `{d['autoname']}`" if d.get("autoname") else ""),
			"",
		]
		if d.get("permissions"):
			lines += ["**Quyền:** " + "; ".join(
				f"{p['role']} ({'/'.join(k for k in ('read', 'write', 'create', 'delete') if p.get(k))})"
				for p in d["permissions"]
			), ""]  # fmt: skip
		lines += [
			"| fieldname | Nhãn | Kiểu | Bắt buộc | Ràng buộc | Mục đích |",
			"| --- | --- | --- | --- | --- | --- |",
		]
		for f in d["fields"]:
			if f["fieldtype"] in LAYOUT:
				continue
			req = "Có" if f.get("reqd") else ""
			purpose = PURPOSE.get(f["fieldname"]) or f.get("description") or f["label"]
			ro = "; chỉ đọc" if f.get("read_only") else ""
			lines.append(
				f"| `{f['fieldname']}` | {f['label']} | {f['fieldtype']} | {req} | {validation(f)}{ro} | {purpose} |".replace(
					"|  ;", "|"
				)
			)
		if RULES.get(name):
			lines += ["", "**Quy tắc nghiệp vụ**", ""] + [f"- {r}" for r in RULES[name]]
		lines.append("")
	return "\n".join(lines).replace("| ; ", "| ")


def main():
	text = render(load()).rstrip("\n") + "\n"
	if "--check" in sys.argv:
		if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
			print("docs/DATA_DICTIONARY.md chưa cập nhật - chạy python scripts/gen_data_dictionary.py")
			sys.exit(1)
		return
	OUT.parent.mkdir(exist_ok=True)
	OUT.write_text(text, encoding="utf-8")
	print("wrote", OUT)


if __name__ == "__main__":
	main()
