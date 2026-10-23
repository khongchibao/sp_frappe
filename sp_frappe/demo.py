"""Dữ liệu mẫu để dùng thử và kiểm tra.

    bench --site <site> execute sp_frappe.demo.make_demo_data

Idempotent: chạy lại không tạo trùng. Khách hàng giả có tiền tố [DEMO].
"""

import frappe
from frappe.model.workflow import apply_workflow

from sp_frappe.tests.utils import LAYER_ROLES, ensure_erp_roots

DEMO_PREFIX = "[DEMO]"
CUSTOMERS = ("[DEMO] Công ty TNHH Thực phẩm An Phát", "[DEMO] Công ty CP Điện tử Bình Minh")
PAPERS = [
	("KRF-125", "Kraft", 125, "Nâu"),
	("KRF-150", "Kraft", 150, "Nâu"),
	("TLN-125", "Test liner", 125, "Nâu"),
	("MED-100", "Medium", 100, "Nâu"),
	("MED-125", "Medium", 125, "Nâu"),
	("DPX-250", "Duplex", 250, "Trắng"),
]
GRADES = [  # (ply, flute, [mã giấy theo lớp], ect, bục)
	(3, "B", ["KRF-125", "MED-100", "KRF-125"], 5.5, 900),
	(3, "C", ["KRF-150", "MED-100", "KRF-150"], 6.5, 1100),
	(5, "BC", ["KRF-125", "MED-100", "TLN-125", "MED-100", "KRF-125"], 9.0, 1300),
	(5, "BC", ["KRF-150", "MED-125", "KRF-150", "MED-125", "KRF-150"], 11.0, 1700),
]
FLEXO = {"print_method": "Flexo trực tiếp"}
OFFSET = {"print_method": "Offset bồi"}


def _colors(*specs):
	return [{"ink_code": c, "pantone": p, "coverage_percent": cov, "print_side": "Ngoài"} for c, p, cov in specs]


def make_demo_data() -> dict:
	ensure_erp_roots()
	customers = [_customer(n) for n in CUSTOMERS]
	for code, kind, gsm, color in PAPERS:
		if not frappe.db.exists("SP Paper", code):
			frappe.get_doc(
				{"doctype": "SP Paper", "paper_code": code, "paper_type": kind, "gsm": gsm, "color": color}
			).insert()
	grades = [_grade(*g) for g in GRADES]
	die = _tooling("Khuôn bế", customers[0], 100000, "Kệ K1-03")
	plate = _tooling("Bản in", customers[0], 50000, "Tủ B2-01")
	_tooling("Anilox", None, 200000, "Kệ A1-01")

	if frappe.db.count("SP Product Spec", {"item_name": ["like", f"{DEMO_PREFIX}%"]}) >= 10:
		return summary()

	g3b, g3c, g5a, g5b = grades
	A, B = customers
	K = _colors(("K", "Black C", 100))
	rows = [
		# (khách, kết cấu, kiểu hộp, L, W, H, thêm, trạng thái cuối)
		(A, g3b, "0201", 400, 300, 200, {}, "Nháp"),
		(A, g3b, "0201", 500, 350, 250, {**FLEXO, "colors": _colors(("K", "Black C", 100), ("R", "186 C", 60))}, "Nháp"),
		(B, g3c, "0203", 600, 400, 300, {}, "Nháp"),
		(A, g5a, "0201", 600, 400, 400, {**FLEXO, "colors": _colors(("K", "Black C", 100), ("R", "186 C", 70), ("Y", "116 C", 40))}, "Chờ duyệt mẫu"),
		(B, g5b, "0201", 700, 500, 500, {}, "Chờ duyệt mẫu"),
		(B, g5a, "0203", 550, 350, 300, {**OFFSET, "colors": _colors(("C", "Process Cyan", 80), ("M", "Process Magenta", 60), ("Y", "Process Yellow", 40), ("K", "Black C", 100))}, "Nháp"),
		(A, g3b, "DIECUT", 300, 200, 100, {"blank_l": 880, "blank_w": 520, "cutting_die": die.name, "printing_plate": plate.name, **FLEXO, "colors": K}, "Đã duyệt"),
		(B, g3c, "0427", 280, 180, 80, {"blank_l": 760, "blank_w": 440, "cutting_die": die.name}, "Nháp"),
		(B, g5b, "SHEET", 1200, 800, 50, {"blank_l": 1200, "blank_w": 800}, "Đã duyệt"),
		(A, g3b, "0201", 250, 200, 150, {**OFFSET, "colors": _colors(("C", "Process Cyan", 90), ("M", "Process Magenta", 70), ("Y", "Process Yellow", 50), ("K", "Black C", 100))}, "Nháp"),
	]  # fmt: skip
	for i, (cust, grade, style, L, W, H, extra, target) in enumerate(rows, start=1):
		doc = frappe.get_doc(
			{
				"doctype": "SP Product Spec", "customer": cust, "item_name": f"{DEMO_PREFIX} Thùng carton mẫu {i:02d}",
				"box_style": style, "ply": grade.ply, "flute": grade.flute, "board_grade": grade.name,
				"inner_l": L, "inner_w": W, "inner_h": H, "joint_type": "Dán keo", "print_method": "Không in",
				"qty_per_bundle": 20, "bundles_per_pallet": 12, "ect_min": grade.ect_target, "burst_min": grade.bursting_target,
				"operations": [{"seq": 1, "operation": "Máy sóng"}, {"seq": 2, "operation": "Dán/Ghim"}, {"seq": 3, "operation": "Đóng gói"}],
				**extra,
			}
		)  # fmt: skip
		doc.insert()
		if target != "Nháp":
			doc.update({"artwork_file": f"/files/demo-artwork-{i:02d}.pdf", "approved_sample_date": frappe.utils.today()})
			doc.save()
			apply_workflow(doc, "Gửi duyệt")
			if target == "Đã duyệt":
				doc.reload()
				apply_workflow(doc, "Duyệt")
	frappe.db.commit()
	return summary()


def summary() -> dict:
	out = {
		"customers": len(CUSTOMERS),
		"papers": len(PAPERS),
		"board_grades": len(GRADES),
		"tooling": frappe.db.count("SP Tooling"),
		"specs": frappe.db.count("SP Product Spec", {"item_name": ["like", f"{DEMO_PREFIX}%"]}),
	}
	print("Demo data:", out)
	return out


def _customer(name: str) -> str:
	existing = frappe.db.get_value("Customer", {"customer_name": name})
	if existing:
		return existing
	doc = frappe.get_doc(
		{"doctype": "Customer", "customer_name": name, "customer_group": "Commercial", "territory": "Vietnam", "customer_type": "Company"}
	)  # fmt: skip
	doc.insert()
	return doc.name


def _grade(ply, flute, papers, ect, burst):
	gsms = [frappe.db.get_value("SP Paper", p, "gsm") for p in papers]
	name = f"{ply}{flute}-" + "/".join(str(g) for g in gsms)
	if frappe.db.exists("SP Board Grade", name):
		return frappe.get_doc("SP Board Grade", name)
	layers = [{"layer_role": role, "paper": paper} for role, paper in zip(LAYER_ROLES[ply], papers, strict=True)]
	doc = frappe.get_doc(
		{"doctype": "SP Board Grade", "ply": str(ply), "flute": flute, "ect_target": ect, "bursting_target": burst, "layers": layers}
	)  # fmt: skip
	doc.insert()
	return doc


def _tooling(kind, customer, max_life, location):
	existing = frappe.db.get_value("SP Tooling", {"tooling_type": kind, "storage_location": location})
	if existing:
		return frappe.get_doc("SP Tooling", existing)
	doc = frappe.get_doc(
		{"doctype": "SP Tooling", "tooling_type": kind, "customer": customer, "max_life": max_life, "storage_location": location, "notes": f"{DEMO_PREFIX} dữ liệu mẫu"}
	)  # fmt: skip
	doc.insert()
	return doc
