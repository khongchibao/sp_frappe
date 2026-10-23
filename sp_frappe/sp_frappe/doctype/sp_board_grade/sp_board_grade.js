frappe.ui.form.on("SP Board Grade", {
	setup(frm) {
		frm.set_query("flute", () => ({ filters: { ply: frm.doc.ply || undefined } }));
		frm.set_query("paper", "layers", () => ({ filters: { active: 1 } }));
	},
	ply(frm) {
		frm.set_value("flute", null);
	},
});
