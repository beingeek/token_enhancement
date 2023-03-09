frappe.ui.form.on('Delivery Note', {
	onload: function(frm) {
		frm.set_query("token_tracer", "tokens", function() {
			return {
				filters: {
					"is_issued": 0,
					"is_redeemed": 0
				}
			};
		});

	},
});
