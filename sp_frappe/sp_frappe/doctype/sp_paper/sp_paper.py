import frappe
from frappe import _
from frappe.model.document import Document


class SPPaper(Document):
	def validate(self):
		if not self.gsm or self.gsm <= 0:
			frappe.throw(_("Định lượng (gsm) phải lớn hơn 0"))
