from frappe.model.document import Document


class SPBoxStyle(Document):
	def validate(self):
		self.style_code = (self.style_code or "").strip().upper()
