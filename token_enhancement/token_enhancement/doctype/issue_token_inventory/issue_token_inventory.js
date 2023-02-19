// Copyright (c) 2023, Createch Global Solutions and contributors
// For license information, please see license.txt

frappe.ui.form.on('Issue Token Inventory', {
	onload: function(frm) {
		if (frm.is_new() || frm.doc.docstatus == 0) {
			frm.set_value('issued_by', frappe.session.user);
        	frm.set_value('issue_date', frappe.datetime.now_date());
		}
		frm.set_query("token_tracer", "issue_tokens", function() {
			return {
				filters: {
					"is_issued": 0,
					"is_redeemed": 0
				}
			};
		});

	},

    // refresh: function(frm) {

	// }
});
