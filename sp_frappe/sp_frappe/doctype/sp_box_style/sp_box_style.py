from frappe.model.document import Document


class SPBoxStyle(Document):
	def before_naming(self):
		self.style_code = (self.style_code or "").strip().upper()

	def validate(self):
		self.style_code = (self.style_code or "").strip().upper()
