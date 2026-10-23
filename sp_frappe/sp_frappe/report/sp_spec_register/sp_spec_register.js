frappe.query_reports["SP Spec Register"] = {
	filters: [
		{ fieldname: "customer", label: __("Khách hàng"), fieldtype: "Link", options: "Customer" },
		{
			fieldname: "spec_status",
			label: __("Trạng thái"),
			fieldtype: "Select",
			options: "\nNháp\nChờ duyệt mẫu\nĐã duyệt\nNgưng",
		},
		{ fieldname: "box_style", label: __("Kiểu hộp"), fieldtype: "Link", options: "SP Box Style" },
		{ fieldname: "from_date", label: __("Tạo từ ngày"), fieldtype: "Date" },
		{ fieldname: "to_date", label: __("Đến ngày"), fieldtype: "Date" },
	],
};
