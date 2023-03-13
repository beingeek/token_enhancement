frappe.provide('token_enhancement');

frappe.pages['sales-order-page'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Order Form',
		single_column: true
	});
	new token_enhancement.SalesOrderPage(page);
}


token_enhancement.SalesOrderPage = class GenerateTokensTool {
	constructor(page) {
		this.page = page;
		this.make_form();
		this.add_item_in_table_with_paint_uom();
		this.hide_company(this.form);
		this.prepare_actions();
	}

	make_form() {
		this.form = new frappe.ui.FieldGroup({
			fields: [
				{
					label: __('Dealer'),
					fieldname: 'customer',
					fieldtype: 'Link',
					options: 'Customer',
					reqd: 1,
				},
				{
					label: __('Company'),
					fieldname: 'company',
					fieldtype: 'Link',
					options: 'Company',
					reqd: 1
				},
				{
					fieldtype: 'Column Break'
				},
				{
					label: __('Order Date'),
					fieldname: 'transaction_date',
					fieldtype: 'Date',
					reqd: 1,
					// read_only: 1,
					default: frappe.datetime.now_date()
				},
				{
					label: __('Delivery Date'),
					fieldname: 'delivery_date',
					fieldtype: 'Date',
					reqd: 1,
					// read_only: 1,
					default: frappe.datetime.now_date()
				},
				{
					fieldtype: 'Section Break'
				},
				{
					label: __('Item Table HTML'),
					fieldname: 'item_table_html',
					fieldtype: 'HTML',
					// read_only: 1
				},
				{
					fieldtype: 'Section Break'
				},
				{
					label: 'Item Table',
					fieldname: 'item_table',
					fieldtype: 'Table',
					data: [],
					read_only: 1,
					hidden: 1,
					fields: [
						{
							fieldtype:'Link',
							fieldname:'item_code',
							label: __('Item'),
							options: 'Item',
							reqd: 1,
							// read_only:1,
							in_list_view:1
						},
						{
							fieldtype:'Float',
							fieldname:'qty',
							label: __('Qty'),
							reqd: 1,
							// read_only: 1,
							in_list_view:1
						}
					]
				}

			],
			body: this.page.body
		});
		this.form.make();
	}
	prepare_actions() {
		var me = this;
		this.page.clear_inner_toolbar();

		this.page.add_inner_button(__("Create Sales Order"), function () {
			me.create_sales_order();
		});
	}

	add_item_in_table_with_paint_uom() {
		var me = this;
		var item_to_order_area = $('<div style="min-height: 300px">').appendTo(me.form.fields_dict.item_table_html.wrapper);
		me.item_to_order_area = new token_enhancement.ItemToOrderEditor(item_to_order_area, me);
	}

	create_sales_order() {
		var me = this;

		let { customer, company, transaction_date, delivery_date, item_table} = this.form.get_values();

		if (customer && company && transaction_date && delivery_date && item_table) {
			frappe.call({
				method: "token_enhancement.token_enhancement.page.sales_order_page.sales_order_page.create_sales_order",
				args: {
					customer,
					company,
					transaction_date,
					delivery_date,
					item_table,
				},
				freeze: true,
				freeze_message: __("Creating Sales Order......"),
				callback: function(r) {
					if(r.message) {
						frappe.msgprint('Sales Order Created Successfully');
						$("input.item-qty").val(null);
						me.form.set_value('customer', null);
						me.form.set_value('transaction_date', null);
						me.form.set_value('delivery_date', null);
						me.form.fields_dict.item_table.df.data = [];
						me.form.fields_dict.item_table.grid.refresh();
					}
				}
			})
		} else {
			frappe.throw(__('Missing values'))
		}
	}

	hide_company(frm) {
		var companies = Object.keys(locals[":Company"] || {});
		if(companies.length === 1) {
			if(!frm.get_value('company')) frm.set_value("company", companies[0]);
			frm.set_df_property('company', 'hidden', 1);
		} else if(erpnext.last_selected_company) {
			if(!frm.get_value('company')) frm.set_value("company", erpnext.last_selected_company);
		}
	}
}

token_enhancement.ItemToOrderEditor = Class.extend({
	init: function(wrapper, frm) {
		var me = this;
		this.frm = frm;
		this.wrapper = wrapper;
		$(wrapper).html('<div class="help">' + __("Loading Item") + '...</div>');
		frappe.call({
			method: 'token_enhancement.token_enhancement.page.sales_order_page.sales_order_page.get_all_paint_uom_items',
			callback: function(r) {
				if (r.message.length) {
					me.item_table = r.message;
					me.show_item_table();
				} else {
					$(wrapper).html('<div class="help">' + __("No Items Found ") + '...</div>');
				}
			}
		});
	},
	show_item_table: function() {
		var me = this;
		$(this.wrapper).empty();

		$.each(this.item_table, function(i, data) {
			var uom = Object.keys(data);
			var items = Object.values(data);

			var items_html = "";
			$.each((items[0] || []), function(i, item) {
				items_html+= repl('<div class="col-md-3">\
				<div style="margin-top:4px">\
					<div style="display:inline;">%(item)s</div>\
					<div class="pull-right" data-item="%(item)s" style="display:inline;">\
						<input class="item-qty" type="text" style="margin-left:1px; font-size: 10px;" >\
					</div>\
				</div>\
				</div>', {item: item});
			});

			$(me.wrapper).append(repl('<div class="paint-uom" style="margin-top:15px;" >\
				<caption>%(uom_display)s</caption>\
				<div class="row">%(items_html)s</div>\
			</div>', {uom_display: __(uom), items_html: items_html}));

		});

		$(this.wrapper).find('input[type="text"]').change(function() {
			me.set_items_in_table();
		});
	},
	set_items_in_table: function() {
		var me = this;
		var opts = this.get_items();
		me.frm.form.fields_dict.item_table.df.data = [];

		$.each(opts.items_with_qty, function(i, item) {
			me.frm.form.fields_dict.item_table.df.data.push({
				'item_code': item.item_code,
				'qty': item.qty
			});

		});
		me.frm.form.fields_dict.item_table.grid.refresh();
	},
	get_items: function() {
		var items_with_qty = [];
		$(this.wrapper).find('[data-item]').each(function() {
			var item_code = $(this).attr('data-item');
			var qty = cint($("[data-item='" + item_code + "']").find('input[type="text"]').val());

			if (qty==0) {
				$("[data-item='" + item_code + "']").find('input[type="text"]').val(null);
			}

			if(qty) {
				items_with_qty.push({item_code: item_code, qty: qty});
			}
		});

		return {
			items_with_qty: items_with_qty
		};
	},
});
