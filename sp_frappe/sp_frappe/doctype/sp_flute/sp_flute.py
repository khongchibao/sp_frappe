import frappe
from frappe import _
from frappe.model.document import Document


class SPFlute(Document):
	def validate(self):
		self.flute_code = (self.flute_code or "").strip().upper()
		for field, label in (
			("thickness_mm", "Độ dày"),
			("length_allowance_mm", "Bù khổ dài"),
			("width_allowance_mm", "Bù khổ rộng"),
			("glue_flap_mm", "Mép dán"),
		):
			if (self.get(field) or 0) < 0:
				frappe.throw(_("{0} không được âm").format(label))
