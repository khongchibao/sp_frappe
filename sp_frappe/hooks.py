app_name = "sp_frappe"
app_title = "SP Frappe"
app_publisher = "King Group"
app_description = "Spec sản phẩm carton (Technical Data Sheet) cho King Group"
app_email = "dev@kinggroup.vn"
app_license = "mit"

required_apps = ["erpnext"]

after_install = "sp_frappe.install.after_install"
after_migrate = "sp_frappe.install.after_migrate"

# Thứ tự quan trọng: Role / Workflow State / Action Master phải có trước Workflow.
fixtures = [
	{"dt": "Role", "filters": [["name", "in", ["SP Kỹ thuật", "SP Kinh doanh", "SP QC", "SP Quản lý"]]]},
	{"dt": "Workflow State", "filters": [["name", "in", ["Nháp", "Chờ duyệt mẫu", "Đã duyệt", "Ngưng"]]]},
	{
		"dt": "Workflow Action Master",
		"filters": [["name", "in", ["Gửi duyệt", "Duyệt", "Trả lại", "Ngưng sử dụng"]]],
	},
	{"dt": "UOM", "filters": [["name", "=", "Thùng"]]},
	"SP Flute",
	"SP Box Style",
	{"dt": "Workflow", "filters": [["name", "=", "SP Product Spec Approval"]]},
]
