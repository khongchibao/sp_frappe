import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import make_autoname

PREFIX = {"Khuôn bế": "KB", "Bản in": "BI", "Anilox": "AN"}


class SPTooling(Document):
	def autoname(self):
		self.name = make_autoname(f"{PREFIX[self.tooling_type]}-.####")

	def validate(self):
		if (self.max_life or 0) < 0 or (self.usage_count or 0) < 0:
			frappe.throw(_("Tuổi thọ và số lần dùng không được âm"))
		self.life_percent = round(self.usage_count * 100 / self.max_life, 1) if self.max_life else 0
		if self.max_life and self.life_percent >= 100 and self.status in ("Sẵn sàng", "Đang dùng"):
			self.status = "Hết hạn"
