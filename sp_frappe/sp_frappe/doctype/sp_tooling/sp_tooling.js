frappe.ui.form.on("SP Tooling", {
	refresh(frm) {
		frm.set_df_property("tooling_type", "read_only", frm.is_new() ? 0 : 1);
	},
});
