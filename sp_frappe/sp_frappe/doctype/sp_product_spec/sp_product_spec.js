frappe.ui.form.on("SP Product Spec", {
	setup(frm) {
		frm.set_query("flute", () => ({ filters: { ply: frm.doc.ply || undefined } }));
		frm.set_query("board_grade", () => ({
			filters: { active: 1, ply: frm.doc.ply || undefined, flute: frm.doc.flute || undefined },
		}));
		frm.set_query("cutting_die", () => ({ filters: { tooling_type: "Khuôn bế" } }));
		frm.set_query("printing_plate", () => ({ filters: { tooling_type: "Bản in" } }));
	},

	refresh(frm) {
		if (!frm.is_new() && frm.doc.spec_status === "Đã duyệt") {
			frm.add_custom_button(__("Tạo phiên bản mới"), () => {
				frappe.confirm(
					__("Tạo phiên bản R{0} từ spec này?", [(frm.doc.revision || 1) + 1]),
					() =>
						frappe
							.xcall("sp_frappe.sp_frappe.doctype.sp_product_spec.sp_product_spec.create_new_revision", {
								source_name: frm.doc.name,
							})
							.then((name) => frappe.set_route("Form", "SP Product Spec", name))
				);
			});
		}
		if (frm.doc.erpnext_item) {
			frm.add_custom_button(__("Mở Item ERPNext"), () =>
				frappe.set_route("Form", "Item", frm.doc.erpnext_item)
			);
		}
	},

	ply(frm) {
		frm.set_value({ flute: null, board_grade: null });
	},

	flute(frm) {
		if (frm.doc.board_grade) frm.set_value("board_grade", null);
	},
});
