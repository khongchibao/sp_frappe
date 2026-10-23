import frappe
from frappe import _


def execute(filters=None):
	filters = frappe._dict(filters or {})
	return get_columns(), get_data(filters)


def get_columns():
	return [
		{"label": _("Spec"), "fieldname": "name", "fieldtype": "Link", "options": "SP Product Spec", "width": 170},
		{"label": _("Phiên bản"), "fieldname": "revision", "fieldtype": "Int", "width": 80},
		{"label": _("Khách hàng"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 180},
		{"label": _("Sản phẩm"), "fieldname": "item_name", "fieldtype": "Data", "width": 180},
		{"label": _("Kiểu hộp"), "fieldname": "box_style", "fieldtype": "Link", "options": "SP Box Style", "width": 80},
		{"label": _("Kích thước trong (mm)"), "fieldname": "dimensions", "fieldtype": "Data", "width": 140},
		{"label": _("Kết cấu giấy"), "fieldname": "board_grade", "fieldtype": "Link", "options": "SP Board Grade", "width": 160},
		{"label": _("m²/thùng"), "fieldname": "area_per_box_m2", "fieldtype": "Float", "precision": 4, "width": 90},
		{"label": _("Trạng thái"), "fieldname": "spec_status", "fieldtype": "Data", "width": 110},
		{"label": _("Ngày duyệt mẫu"), "fieldname": "approved_sample_date", "fieldtype": "Date", "width": 110},
	]  # fmt: skip


def get_data(filters):
	conditions = {}
	for key in ("customer", "spec_status", "box_style"):
		if filters.get(key):
			conditions[key] = filters[key]
	if filters.get("from_date") and filters.get("to_date"):
		conditions["creation"] = ["between", [f"{filters.from_date} 00:00:00", f"{filters.to_date} 23:59:59"]]
	elif filters.get("from_date"):
		conditions["creation"] = [">=", f"{filters.from_date} 00:00:00"]
	elif filters.get("to_date"):
		conditions["creation"] = ["<=", f"{filters.to_date} 23:59:59"]

	rows = frappe.get_list(
		"SP Product Spec",
		filters=conditions,
		fields=[
			"name", "revision", "customer", "item_name", "box_style", "inner_l", "inner_w", "inner_h",
			"board_grade", "area_per_box_m2", "spec_status", "approved_sample_date",
		],
		order_by="spec_code asc, revision desc",
		limit_page_length=0,
	)  # fmt: skip
	for row in rows:
		row["dimensions"] = f"{row.inner_l} x {row.inner_w} x {row.inner_h}"
	return rows
