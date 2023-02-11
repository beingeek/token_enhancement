frappe.provide('token_enhancement')


frappe.pages['generate-tokens'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Generate Tokens',
		single_column: true
	});

	new token_enhancement.GenerateTokensTool(page);
}

token_enhancement.GenerateTokensTool = class GenerateTokensTool {
	constructor(page) {
		this.page = page;
		this.make_form();
		this.prepare_actions();
	}

	make_form() {
		this.form = new frappe.ui.FieldGroup({
			fields: [
				{
					label: __('Number of Tokens'),
					fieldname: 'number_of_tokens',
					fieldtype: 'Int',
					reqd: 1,
				},
				{
					label: __('Token Value'),
					fieldname: 'token_value',
					fieldtype: 'Select',
					options: [50, 300, 400, 1200],
					reqd: 1,
				},
				{
					label: __('Production Batch'),
					fieldname: 'production_batch',
					fieldtype: 'Link',
					options: 'Batch',
					reqd: 1,
				},
				{
					fieldtype: 'Column Break'
				},
				{
					label: __('Notes'),
					fieldname: 'notes',
					fieldtype: 'Small Text',
				},
				{
					fieldtype: 'Column Break'
				},
				{
					label: __('Creation Date'),
					fieldname: 'creation_date',
					fieldtype: 'Date',
					reqd: 1,
					read_only: 1,
					default: frappe.datetime.now_date()
				},
				{
					label: __('Created By'),
					fieldname: 'created_by',
					fieldtype: 'Link',
					options: 'User',
					reqd: 1,
					read_only: 1,
					default: frappe.session.user
				}

			],
			body: this.page.body
		});
		this.form.make();
	}
	prepare_actions() {
		var me = this;
		this.page.clear_inner_toolbar();

		this.page.add_inner_button(__("Generate Tokens"), function () {
			me.generate_tokens();
		});
	}

	generate_tokens() {
		let { number_of_tokens, token_value, production_batch, creation_date, created_by, notes} = this.form.get_values();
		if (number_of_tokens && token_value && production_batch && creation_date && created_by) {
			frappe.call({
				method: "token_enhancement.token_enhancement.page.generate_tokens.generate_tokens.generate_tokens",
				args: {
					number_of_tokens,
					token_value,
					production_batch,
					creation_date,
					created_by,
					notes
				},
				callback: function(r, rt) {
					if(r.message) {
						callback(r.message.account)
					}
				}
			})
			frappe.msgprint('Token Generated Successfully');
		} else {
			frappe.throw(__('Missing values'))
		}
	}
}
