import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils import cstr, flt, today

from sp_frappe.install import ensure_item_group
from sp_frappe.sp_frappe.doctype.sp_settings.sp_settings import get_lock_fields
from sp_frappe.utils.blank import BlankError, calc_blank
from sp_frappe.utils.naming import derive_customer_code, normalize_customer_code

DRAFT, PENDING, APPROVED, RETIRED = "Nháp", "Chờ duyệt mẫu", "Đã duyệt", "Ngưng"
LOCKED_STATES = (APPROVED, RETIRED)

# Vai trò được sửa toàn bộ thông tin kỹ thuật (khi spec chưa bị khóa)
EDITOR_ROLES = {"SP Kỹ thuật", "SP Quản lý", "System Manager"}
QUALITY_FIELDS = {"ect_min", "bct_min", "burst_min", "moisture_max", "fsc_claim"}
# Trường hệ thống / do workflow điều khiển - ai có quyền write cũng kích hoạt được qua workflow
SYSTEM_FIELDS = {"spec_status", "approved_by", "usage_counted", "erpnext_item"}
_ROW_SKIP = {
	"name", "idx", "creation", "modified", "modified_by", "owner", "parent", "parentfield", "parenttype",
	"docstatus", "doctype",
}  # fmt: skip
_LAYOUT = {"Section Break", "Column Break", "Tab Break", "HTML", "Button"}


class SPProductSpec(Document):
	# ------------------------------------------------------------ naming
	def autoname(self):
		if not self.spec_code:
			if not self.customer_code:
				self.customer_code = derive_customer_code(frappe.db.get_value("Customer", self.customer, "customer_name") or self.customer)
			self.customer_code = normalize_customer_code(self.customer_code) or "KH"
			self.spec_code = make_autoname(f"KG-{self.customer_code}-.####")
		self.name = f"{self.spec_code}-R{self.revision or 1}"

	# ------------------------------------------------------------ validate
	def validate(self):
		before = self.get_doc_before_save()
		locked = bool(before and before.spec_status in LOCKED_STATES)

		self.enforce_field_scope(before)
		if locked:
			self.enforce_revision_lock(before)
		else:
			self.customer_code = normalize_customer_code(self.customer_code or "") or derive_customer_code(
				frappe.db.get_value("Customer", self.customer, "customer_name") or self.customer
			)
			self.validate_structure(before)
			self.validate_dimensions()
			self.calculate_blank()
			self.validate_printing()
			self.validate_tooling()
		self.validate_numbers()
		self.validate_approval(before)

	def enforce_field_scope(self, before):
		"""SP QC chỉ sửa nhóm Chất lượng; SP Kinh doanh chỉ thao tác workflow. Kỹ thuật/Quản lý sửa tự do."""
		if self.is_new() or before is None:
			return
		roles = set(frappe.get_roles())
		if frappe.session.user == "Administrator" or roles & EDITOR_ROLES:
			return
		allowed = set(SYSTEM_FIELDS)
		if "SP QC" in roles:
			allowed |= QUALITY_FIELDS
		changed = [f for f in self.changed_fields(before) if f not in allowed]
		if changed:
			frappe.throw(
				_("Vai trò của bạn không được sửa: {0}").format(", ".join(self.field_labels(changed))),
				frappe.PermissionError,
			)

	def enforce_revision_lock(self, before):
		changed = [f for f in get_lock_fields() if f in self.changed_fields(before)]
		if changed:
			frappe.throw(
				_("Spec đã duyệt, không được sửa: {0}. Hãy dùng nút 'Tạo phiên bản mới'.").format(
					", ".join(self.field_labels(changed))
				)
			)

	def validate_structure(self, before):
		flute_ply = frappe.db.get_value("SP Flute", self.flute, "ply")
		if flute_ply != self.ply:
			frappe.throw(_("Loại sóng {0} là sóng {1} lớp, không khớp {2} lớp của spec").format(self.flute, flute_ply, self.ply))
		grade = frappe.db.get_value("SP Board Grade", self.board_grade, ["ply", "flute", "active"], as_dict=True)
		if grade.ply != self.ply:
			frappe.throw(_("Kết cấu giấy {0} là {1} lớp, không khớp {2} lớp của spec").format(self.board_grade, grade.ply, self.ply))
		if grade.flute != self.flute:
			frappe.throw(_("Kết cấu giấy {0} dùng sóng {1}, không khớp sóng {2} của spec").format(self.board_grade, grade.flute, self.flute))
		if not grade.active and (before is None or before.board_grade != self.board_grade):
			frappe.throw(_("Kết cấu giấy {0} đã ngưng sử dụng").format(self.board_grade))

	def validate_dimensions(self):
		for field in ("inner_l", "inner_w", "inner_h"):
			value = self.get(field) or 0
			if not 50 <= value <= 2500:
				frappe.throw(_("{0} phải trong khoảng 50-2500 mm").format(self.meta.get_label(field)))

	def calculate_blank(self):
		style = frappe.db.get_value("SP Box Style", self.box_style, ["blank_formula", "requires_die"], as_dict=True)
		self.blank_formula = style.blank_formula
		flute = frappe.db.get_value(
			"SP Flute", self.flute, ["length_allowance_mm", "width_allowance_mm", "glue_flap_mm"], as_dict=True
		)
		try:
			result = calc_blank(
				style.blank_formula, self.inner_l, self.inner_w, self.inner_h, flute, self.blank_l, self.blank_w
			)
		except BlankError as e:
			frappe.throw(_(str(e)))
		self.blank_l, self.blank_w, self.area_per_box_m2 = result.blank_l, result.blank_w, result.area_m2
		self._requires_die = bool(style.requires_die)

	def validate_printing(self):
		if self.print_method == "Không in":
			if self.colors:
				frappe.throw(_("Phương pháp in là 'Không in' nhưng bảng màu đang có dữ liệu"))
			self.color_count = 0
			return
		if not self.colors:
			frappe.throw(_("Có in thì phải khai báo bảng màu"))
		for row in self.colors:
			if not 0 <= flt(row.coverage_percent) <= 100:
				frappe.throw(_("Dòng {0} bảng màu: độ phủ phải trong khoảng 0-100%").format(row.idx))
		self.color_count = len(self.colors)

	def validate_tooling(self):
		if self._requires_die and not self.cutting_die:
			frappe.throw(_("Kiểu hộp {0} bắt buộc phải có khuôn bế").format(self.box_style))
		for field, kind in (("cutting_die", "Khuôn bế"), ("printing_plate", "Bản in")):
			link = self.get(field)
			if link and frappe.db.get_value("SP Tooling", link, "tooling_type") != kind:
				frappe.throw(_("{0} phải là công cụ loại '{1}'").format(self.meta.get_label(field), kind))

	def validate_numbers(self):
		for field in ("ect_min", "bct_min", "burst_min", "moisture_max"):
			if flt(self.get(field)) < 0:
				frappe.throw(_("{0} không được âm").format(self.meta.get_label(field)))
		if (self.moisture_max or 0) > 100:
			frappe.throw(_("Độ ẩm tối đa không được vượt 100%"))
		for field in ("qty_per_bundle", "bundles_per_pallet"):
			if (self.get(field) or 0) < 0:
				frappe.throw(_("{0} phải lớn hơn 0").format(self.meta.get_label(field)))

	def validate_approval(self, before):
		self.flags.approved_now = self.spec_status == APPROVED and (before is None or before.spec_status != APPROVED)
		if not self.flags.approved_now:
			return
		missing = [
			self.meta.get_label(f)
			for f in ("artwork_file", "approved_sample_date", "qty_per_bundle", "bundles_per_pallet")
			if not self.get(f)
		]
		if missing:
			frappe.throw(_("Trước khi duyệt phải có: {0}").format(", ".join(missing)))
		self.approved_by = frappe.session.user

	# ------------------------------------------------------------ after save
	def on_update(self):
		if not self.flags.get("approved_now"):
			return
		self.flags.approved_now = False
		self.retire_previous_revisions()
		self.record_tooling_usage()
		self.sync_item()

	def retire_previous_revisions(self):
		for name in frappe.get_all(
			"SP Product Spec",
			filters={"spec_code": self.spec_code, "spec_status": APPROVED, "name": ["!=", self.name]},
			pluck="name",
		):
			frappe.db.set_value("SP Product Spec", name, "spec_status", RETIRED)

	def record_tooling_usage(self):
		"""Cộng số lần dùng khuôn/bản in khi spec được duyệt lần đầu (mỗi spec_code + công cụ đếm một lần)."""
		if self.usage_counted:
			return
		for field in ("cutting_die", "printing_plate"):
			tool = self.get(field)
			if not tool:
				continue
			already = frappe.db.exists(
				"SP Product Spec",
				{"spec_code": self.spec_code, "usage_counted": 1, field: tool, "name": ["!=", self.name]},
			)
			if already:
				continue
			doc = frappe.get_doc("SP Tooling", tool)
			doc.usage_count = (doc.usage_count or 0) + 1
			doc.last_used_on = today()
			doc.save(ignore_permissions=True)
		self.db_set("usage_counted", 1, update_modified=False)

	def sync_item(self):
		settings = frappe.get_single("SP Settings")
		if not settings.auto_create_item:
			return
		uom = settings.stock_uom or "Thùng"
		group = ensure_item_group(settings.item_group or "Products")
		if not frappe.db.exists("UOM", uom):
			frappe.get_doc({"doctype": "UOM", "uom_name": uom, "must_be_whole_number": 1}).insert(ignore_permissions=True)
		values = {
			"item_name": self.item_name,
			"item_group": group,
			"stock_uom": uom,
			"description": self.item_description(),
		}
		if frappe.db.exists("Item", self.spec_code):
			item = frappe.get_doc("Item", self.spec_code)
			item.update({k: v for k, v in values.items() if k != "stock_uom"})
			item.save(ignore_permissions=True)
		else:
			item = frappe.get_doc({"doctype": "Item", "item_code": self.spec_code, "is_stock_item": 1, **values})
			item.insert(ignore_permissions=True)
		self.db_set("erpnext_item", item.name, update_modified=False)
		self.erpnext_item = item.name

	def item_description(self) -> str:
		return (
			f"Khách hàng: {self.customer}<br>"
			f"Kiểu hộp: {self.box_style} | Kích thước trong: {self.inner_l} x {self.inner_w} x {self.inner_h} mm<br>"
			f"Kết cấu: {self.board_grade} (sóng {self.flute}, {self.ply} lớp)<br>"
			f"Khổ phôi: {self.blank_l} x {self.blank_w} mm ({self.area_per_box_m2} m²) | Phiên bản R{self.revision}"
		)

	# ------------------------------------------------------------ helpers
	def changed_fields(self, before) -> list[str]:
		out = []
		for df in self.meta.fields:
			if df.fieldtype in _LAYOUT:
				continue
			if df.fieldtype in ("Table", "Table MultiSelect"):
				if self._rows(self.get(df.fieldname)) != self._rows(before.get(df.fieldname)):
					out.append(df.fieldname)
			elif not _same(self.get(df.fieldname), before.get(df.fieldname)):
				out.append(df.fieldname)
		return out

	@staticmethod
	def _rows(rows) -> list[tuple]:
		return [
			tuple(sorted((k, _norm(v)) for k, v in row.as_dict(no_nulls=True).items() if k not in _ROW_SKIP))
			for row in rows or []
		]

	def field_labels(self, fieldnames) -> list[str]:
		return [self.meta.get_label(f) for f in fieldnames]


def _norm(value):
	if value in (None, ""):
		return ""
	if isinstance(value, int | float):
		return flt(value)
	return cstr(value)


def _same(a, b) -> bool:
	return _norm(a) == _norm(b)


@frappe.whitelist()
def create_new_revision(source_name: str) -> str:
	"""Tạo phiên bản mới (R+1) từ spec đã duyệt. Bản cũ chuyển 'Ngưng' khi bản mới được duyệt."""
	src = frappe.get_doc("SP Product Spec", source_name)
	src.check_permission("read")
	frappe.has_permission("SP Product Spec", "create", throw=True)
	if src.spec_status != APPROVED:
		frappe.throw(_("Chỉ tạo phiên bản mới từ spec đã duyệt"))
	open_rev = frappe.db.get_value(
		"SP Product Spec", {"spec_code": src.spec_code, "spec_status": ["in", [DRAFT, PENDING]]}, "name"
	)
	if open_rev:
		frappe.throw(_("Đã có phiên bản đang soạn/chờ duyệt: {0}").format(open_rev))
	revisions = frappe.get_all("SP Product Spec", filters={"spec_code": src.spec_code}, pluck="revision")
	last = max(revisions or [src.revision])

	new = frappe.copy_doc(src)
	new.update(
		{
			"spec_code": src.spec_code,
			"customer_code": src.customer_code,
			"revision": last + 1,
			"previous_revision": src.name,
			"spec_status": DRAFT,
			"approved_by": None,
			"approved_sample_date": None,
			"usage_counted": 0,
			"erpnext_item": src.erpnext_item,
		}
	)
	new.insert()
	return new.name
