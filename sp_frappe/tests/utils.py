"""Helper tạo dữ liệu cho test và demo. Không chứa test case."""

import frappe

from sp_frappe.install import ensure_item_group

LAYER_ROLES = {
	3: ["Mặt", "Sóng", "Đáy"],
	5: ["Mặt", "Sóng", "Lót giữa", "Sóng", "Đáy"],
	7: ["Mặt", "Sóng", "Lót giữa", "Sóng", "Lót giữa", "Sóng", "Đáy"],
}


def ensure_erp_roots():
	"""Site mới (chưa chạy setup wizard) chưa có nhóm khách hàng / vùng gốc."""
	if not frappe.db.exists("Customer Group", "All Customer Groups"):
		frappe.get_doc(
			{"doctype": "Customer Group", "customer_group_name": "All Customer Groups", "is_group": 1}
		).insert(ignore_permissions=True)
	if not frappe.db.exists("Territory", "All Territories"):
		frappe.get_doc({"doctype": "Territory", "territory_name": "All Territories", "is_group": 1}).insert(
			ignore_permissions=True
		)
	for doctype, field, leaf, parent_field, root in (
		("Customer Group", "customer_group_name", "Commercial", "parent_customer_group", "All Customer Groups"),
		("Territory", "territory_name", "Vietnam", "parent_territory", "All Territories"),
	):
		if not frappe.db.exists(doctype, leaf):
			frappe.get_doc({"doctype": doctype, field: leaf, parent_field: root, "is_group": 0}).insert(
				ignore_permissions=True
			)
	ensure_item_group("Products")


def make_customer(name: str = "SP Test Thực phẩm An Phát") -> str:
	ensure_erp_roots()
	if frappe.db.exists("Customer", {"customer_name": name}):
		return frappe.db.get_value("Customer", {"customer_name": name}, "name")
	doc = frappe.get_doc(
		{
			"doctype": "Customer",
			"customer_name": name,
			"customer_group": "Commercial",
			"territory": "Vietnam",
			"customer_type": "Company",
		}
	)
	doc.insert(ignore_permissions=True)
	return doc.name


def make_paper(code: str, gsm: int, paper_type: str = "Kraft", color: str = "Nâu") -> str:
	if not frappe.db.exists("SP Paper", code):
		frappe.get_doc(
			{"doctype": "SP Paper", "paper_code": code, "paper_type": paper_type, "gsm": gsm, "color": color, "active": 1}
		).insert(ignore_permissions=True)
	return code


def make_board_grade(ply: int = 3, flute: str = "B", gsms=(125, 100, 125), roles=None, **kw):
	roles = roles or LAYER_ROLES[ply]
	layers = []
	for i, (role, gsm) in enumerate(zip(roles, gsms, strict=True), start=1):
		kind = "Medium" if role in ("Sóng", "Lót giữa") else "Kraft"
		layers.append({"layer_no": i, "layer_role": role, "paper": make_paper(f"T-{kind[:3].upper()}-{gsm}", gsm, kind)})
	doc = frappe.get_doc({"doctype": "SP Board Grade", "ply": str(ply), "flute": flute, "layers": layers, **kw})
	doc.insert(ignore_permissions=True)
	return doc


def get_or_make_board_grade(ply: int, flute: str, gsms):
	name = frappe.db.get_value(
		"SP Board Grade", {"ply": str(ply), "flute": flute, "name": ["like", "%-" + "/".join(map(str, gsms))]}
	)
	return frappe.get_doc("SP Board Grade", name) if name else make_board_grade(ply, flute, gsms)


def make_tooling(kind: str = "Khuôn bế", **kw):
	doc = frappe.get_doc({"doctype": "SP Tooling", "tooling_type": kind, "max_life": 100000, **kw})
	doc.insert(ignore_permissions=True)
	return doc


def spec_values(**overrides) -> dict:
	grade = overrides.pop("board_grade_doc", None) or get_or_make_board_grade(3, "B", (125, 100, 125))
	values = {
		"doctype": "SP Product Spec",
		"customer": make_customer(),
		"item_name": "Thùng carton test",
		"box_style": "0201",
		"ply": grade.ply,
		"flute": grade.flute,
		"board_grade": grade.name,
		"inner_l": 400,
		"inner_w": 300,
		"inner_h": 200,
		"joint_type": "Dán keo",
		"print_method": "Không in",
		"qty_per_bundle": 20,
		"bundles_per_pallet": 10,
	}
	values.update(overrides)
	return values


def make_spec(**overrides):
	doc = frappe.get_doc(spec_values(**overrides))
	doc.insert()
	return doc


def make_user(email: str, roles: list[str]):
	if not frappe.db.exists("User", email):
		frappe.get_doc(
			{"doctype": "User", "email": email, "first_name": email.split("@")[0], "send_welcome_email": 0}
		).insert(ignore_permissions=True)
	user = frappe.get_doc("User", email)
	user.add_roles(*roles)
	return user


def ready_for_approval(doc, **kw):
	"""Điền các trường bắt buộc trước khi duyệt."""
	doc.update({"artwork_file": "/files/test-artwork.pdf", "approved_sample_date": "2026-10-01", **kw})
	doc.save()
	return doc


def run_workflow(doc, action: str):
	from frappe.model.workflow import apply_workflow

	return apply_workflow(doc, action)


def approve(doc):
	"""Nháp -> Chờ duyệt mẫu -> Đã duyệt qua workflow (chạy với quyền Administrator)."""
	ready_for_approval(doc)
	run_workflow(doc, "Gửi duyệt")
	doc.reload()
	run_workflow(doc, "Duyệt")
	doc.reload()
	return doc
