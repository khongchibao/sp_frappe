import frappe
from frappe import _
from frappe.model.document import Document

from sp_frappe.utils.naming import board_grade_name

ROLES = ("Mặt", "Sóng", "Lót giữa", "Đáy")


class SPBoardGrade(Document):
	def autoname(self):
		# autoname chạy trước validate/fetch_from nên đọc gsm trực tiếp từ SP Paper
		gsms = [row.gsm or frappe.db.get_value("SP Paper", row.paper, "gsm") or 0 for row in self.layers]
		base = board_grade_name(self.ply, self.flute, gsms)
		name, n = base, 1
		while frappe.db.exists("SP Board Grade", name):
			n += 1
			name = f"{base}-{n}"
		self.name = name

	def validate(self):
		self.validate_flute()
		self.validate_layers()

	def validate_flute(self):
		flute_ply = frappe.db.get_value("SP Flute", self.flute, "ply")
		if flute_ply and flute_ply != self.ply:
			frappe.throw(
				_("Loại sóng {0} là sóng {1} lớp, không khớp {2} lớp").format(self.flute, flute_ply, self.ply)
			)

	def validate_layers(self):
		ply = int(self.ply)
		if len(self.layers) != ply:
			frappe.throw(
				_("Kết cấu {0} lớp cần đúng {0} dòng lớp giấy (hiện có {1})").format(ply, len(self.layers))
			)
		for idx, row in enumerate(self.layers, start=1):
			row.layer_no = idx
			if not row.gsm:
				row.gsm = frappe.db.get_value("SP Paper", row.paper, "gsm")
		roles = [row.layer_role for row in self.layers]
		if roles[0] != "Mặt" or roles[-1] != "Đáy":
			frappe.throw(_("Lớp đầu phải là 'Mặt' và lớp cuối phải là 'Đáy'"))
		flute_layers = roles.count("Sóng")
		if flute_layers != ply // 2:
			frappe.throw(
				_("Kết cấu {0} lớp cần {1} lớp 'Sóng' (hiện có {2})").format(ply, ply // 2, flute_layers)
			)
		for i, role in enumerate(roles[1:-1], start=2):
			expected = "Sóng" if i % 2 == 0 else "Lót giữa"
			if role != expected:
				frappe.throw(_("Lớp {0} phải là '{1}' (sóng xen kẽ lớp phẳng)").format(i, expected))
