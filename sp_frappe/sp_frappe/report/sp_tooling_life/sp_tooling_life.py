import frappe
from frappe import _

WARN_PERCENT = 80


def execute(filters=None):
	filters = frappe._dict(filters or {})
	return get_columns(), get_data(filters)


def get_columns():
	return [
		{"label": _("Công cụ"), "fieldname": "name", "fieldtype": "Link", "options": "SP Tooling", "width": 120},
		{"label": _("Loại"), "fieldname": "tooling_type", "fieldtype": "Data", "width": 90},
		{"label": _("Khách hàng"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 180},
		{"label": _("Số lần đã dùng"), "fieldname": "usage_count", "fieldtype": "Int", "width": 110},
		{"label": _("Tuổi thọ tối đa"), "fieldname": "max_life", "fieldtype": "Int", "width": 110},
		{"label": _("Đã dùng (%)"), "fieldname": "life_percent", "fieldtype": "Percent", "width": 100},
		{"label": _("Trạng thái"), "fieldname": "status", "fieldtype": "Data", "width": 100},
		{"label": _("Dùng gần nhất"), "fieldname": "last_used_on", "fieldtype": "Date", "width": 110},
		{"label": _("Vị trí kho"), "fieldname": "storage_location", "fieldtype": "Data", "width": 120},
	]  # fmt: skip


def get_data(filters):
	base = {}
	if filters.get("tooling_type"):
		base["tooling_type"] = filters.tooling_type
	return frappe.get_list(
		"SP Tooling",
		filters=base,
		or_filters=[["life_percent", ">=", WARN_PERCENT], ["status", "in", ["Sửa chữa", "Hết hạn"]]],
		fields=[
			"name", "tooling_type", "customer", "usage_count", "max_life", "life_percent", "status",
			"last_used_on", "storage_location",
		],
		order_by="life_percent desc",
		limit_page_length=0,
	)  # fmt: skip
