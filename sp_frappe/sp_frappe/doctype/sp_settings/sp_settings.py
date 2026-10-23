import frappe
from frappe import _
from frappe.model.document import Document

DEFAULT_LOCK_FIELDS = (
	"customer customer_code box_style ply flute board_grade inner_l inner_w inner_h blank_l blank_w "
	"joint_type print_method cutting_die printing_plate colors operations"
).split()


class SPSettings(Document):
	def validate(self):
		meta = frappe.get_meta("SP Product Spec")
		unknown = [f for f in parse_lock_fields(self.revision_lock_fields) if not meta.has_field(f)]
		if unknown:
			frappe.throw(_("Trường không tồn tại trong SP Product Spec: {0}").format(", ".join(unknown)))


def parse_lock_fields(value: str | None) -> list[str]:
	return [p for p in (value or "").replace(",", "\n").split() if p]


def get_lock_fields() -> list[str]:
	value = frappe.db.get_single_value("SP Settings", "revision_lock_fields")
	return parse_lock_fields(value) or list(DEFAULT_LOCK_FIELDS)
