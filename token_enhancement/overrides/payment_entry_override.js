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
