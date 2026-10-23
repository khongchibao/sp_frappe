import frappe


def after_install():
	ensure_defaults()


def after_migrate():
	ensure_defaults()


def ensure_defaults():
	"""Tạo UOM 'Thùng', nhóm Item mặc định và lưu SP Settings lần đầu (idempotent)."""
	if not frappe.db.exists("UOM", "Thùng"):
		frappe.get_doc({"doctype": "UOM", "uom_name": "Thùng", "must_be_whole_number": 1}).insert(
			ignore_permissions=True
		)
	ensure_item_group("Products")
	settings = frappe.get_single("SP Settings")
	if not settings.item_group:
		settings.item_group = "Products"
	if not settings.stock_uom:
		settings.stock_uom = "Thùng"
	if not settings.revision_lock_fields:
		from sp_frappe.sp_frappe.doctype.sp_settings.sp_settings import DEFAULT_LOCK_FIELDS

		settings.revision_lock_fields = "\n".join(DEFAULT_LOCK_FIELDS)
	settings.save(ignore_permissions=True)
	frappe.db.commit()


def ensure_item_group(name: str) -> str:
	"""Tạo nhóm Item (và nhóm gốc nếu site chưa chạy setup wizard)."""
	if frappe.db.exists("Item Group", name):
		return name
	root = "All Item Groups"
	if not frappe.db.exists("Item Group", root):
		frappe.get_doc({"doctype": "Item Group", "item_group_name": root, "is_group": 1}).insert(
			ignore_permissions=True
		)
	frappe.get_doc(
		{"doctype": "Item Group", "item_group_name": name, "parent_item_group": root, "is_group": 0}
	).insert(ignore_permissions=True)
	return name
