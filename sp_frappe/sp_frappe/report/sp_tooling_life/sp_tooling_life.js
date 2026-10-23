frappe.query_reports["SP Tooling Life"] = {
	filters: [
		{
			fieldname: "tooling_type",
			label: __("Loại công cụ"),
			fieldtype: "Select",
			options: "\nKhuôn bế\nBản in\nAnilox",
		},
	],
	formatter(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname === "life_percent" && data && data.life_percent >= 100) {
			value = `<span style="color:var(--red-500);font-weight:600">${value}</span>`;
		}
		return value;
	},
};
