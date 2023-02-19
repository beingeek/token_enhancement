frappe.ui.form.on('Payment Entry', {
	onload: function(frm) {
		frm.events.hide_unhide_fields(frm);
	},

	payment_type: function(frm) {
		frm.events.hide_unhide_fields(frm);
	},

	hide_unhide_fields: function(frm) {
		if (frm.doc.payment_type == 'Token Payment Entry') {
			frm.set_df_property('unallocated_amount', 'hidden', 1);
			frm.set_df_property('difference_amount', 'hidden', 1);
			frm.set_df_property('deductions_or_loss_section', 'hidden', 1);
		} else {
			frm.set_df_property('unallocated_amount', 'hidden', 0);
			frm.set_df_property('difference_amount', 'hidden', 0);
			frm.set_df_property('deductions_or_loss_section', 'hidden', 0);
		}
	}
});

frappe.ui.form.on('Redeem Token', {
	token_key: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		if (row.token_key) {
			return frappe.call({
				method: "token_enhancement.token_enhancement.doctype.paint_token.paint_token.get_token_data",
				args: {
					token_key: row.token_key,
				},
				callback: function(r) {
					if(r.message) {
						let token_data = r.message;
						frappe.model.set_value(cdt, cdn, 'token_tracer', token_data.token_tracer);
						frappe.model.set_value(cdt, cdn, 'token_value', token_data.token_value);
						frappe.model.set_value(cdt, cdn, 'is_issued', token_data.is_issued);
						frappe.model.set_value(cdt, cdn, 'is_redeemed', token_data.is_redeemed);
					}
				}
			})
		}
	},

})
