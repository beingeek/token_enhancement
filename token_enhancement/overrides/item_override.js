frappe.ui.form.on('Item', {
	onload: function(frm) {
		frm.set_query("paint_uom", function() {
			return{
				filters: {
					"is_paint_uom": ["=", 1],
				}
			}
		});
	}
});
