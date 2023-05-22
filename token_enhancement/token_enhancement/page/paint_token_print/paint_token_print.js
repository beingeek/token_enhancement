frappe.provide('token_enhancement')

frappe.pages['paint-token-print'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Print Tokens',
		single_column: true
	});

	new token_enhancement.PrintTokens(page);
}

token_enhancement.PrintTokens = class PrintTokens {
	constructor(page) {
		this.page = page;
		this.make_form();
		this.get_tokens_html()
		this.prepare_actions();
	}

	make_form() {
		this.form = new frappe.ui.FieldGroup({
			fields: [
				{
					fieldtype: 'Section Break'
				},
				{
					label: __('Paint Token'),
					fieldname: 'paint_token',
					fieldtype: 'HTML',
					read_only: 1,
					options: ''
				},
				{
					fieldtype: 'Section Break'
				},
				{
					label: 'Token Table',
					fieldname: 'token_table',
					fieldtype: 'Table',
					read_only: 0,
					hidden: 0,
					fields: [
						{
							fieldtype:'Link',
							fieldname:'token',
							label: __('Token'),
							options: 'Paint Token',
							reqd: 1,
							read_only:1,
							in_list_view:1
						}
					]
				}
			],
			body: this.page.body
		});
		this.form.make();
	}

	get_tokens_html() {
			var me = this;
			var paint_token_area = $('<div style="min-height: 300px">').appendTo(me.form.fields_dict.paint_token.wrapper);
			me.paint_token_area = new token_enhancement.PaintTokenTable(paint_token_area, me);
	}

	prepare_actions() {
			var me = this;
			this.page.clear_inner_toolbar();
			this.page.add_inner_button(__("Print"), function () {
				me.print_tokens();
			});
	}

	prepare_actions() {
			var me = this;
			this.page.clear_inner_toolbar();

			this.page.set_primary_action(__('Print'), () => {
				me.print_tokens();
			});

//			this.page.add_inner_button(__("Print"), function () {
//				me.print_tokens();
//			});
	}

	print_tokens() {
		var me = this;
		let tokens = me.form.get_value('token_table');
		if (tokens.length) {
			var w = window.open(
				frappe.urllib.get_full_url("/api/method/token_enhancement.token_enhancement.page.paint_token_print.paint_token_print.print_tokens?" + "tokens=" + JSON.stringify(tokens))
			);
			if (!w) {
				frappe.msgprint(__("Please enable pop-ups")); return;
			}

		} else {
			frappe.throw(__('Selected Tokens and Sticker type'))
		}

//		if (tokens.length) {
//			let url = "/api/method/token_enhancement.token_enhancement.page.paint_token_print.paint_token_print.print_tokens";
//			open_url_post(url, {"tokens": tokens}, true);
//		} else {
//			frappe.throw(__('Selected Tokens and Sticker type'))
//		}

//		if (tokens.length) {
//			frappe.call({
//				method: "token_enhancement.token_enhancement.page.paint_token_print.paint_token_print.print_tokens",
//				args: {
//					tokens
//				},
//				freeze: true,
//				freeze_message: __("Generating Print Format......"),
//				callback: function(r) {
//					if(r.message) {
//						// w = window.open('https://google.com/');
//						var w = window.open();
//
//						w.document.write(r.message);
//						w.document.close();
//						// setTimeout(function () {
//						// 	w.print();
//						// 	w.close();
//						// }, 1000);
//						// 	frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
//						// 		+ "doctype=" + encodeURIComponent(me.frm.doc.doctype)
//						// 		+ "&name=" + encodeURIComponent(me.frm.doc.name)
//						// 		+ "&format=" + encodeURIComponent(me.selected_format())
//						// 		+ "&no_letterhead=" + (me.with_letterhead() ? "0" : "1")
//						// 		+ (me.lang_code ? ("&_lang=" + me.lang_code) : ""))
//						// );
//						if (!w) {
//							frappe.msgprint(__("Please enable pop-ups")); return;
//						}
//					}
//				}
//			})
//		} else {
//			frappe.throw(__('Selected Tokens and Sticker type'))
//		}

	}
}

token_enhancement.PaintTokenTable = Class.extend({
	init: function(wrapper, frm) {
		var me = this;
		this.frm = frm;
		this.wrapper = wrapper;
		$(wrapper).html('<div class="help">' + __("Loading Token") + '...</div>');
		frappe.call({
			method: 'token_enhancement.token_enhancement.page.paint_token_print.paint_token_print.get_paint_tokens',
			callback: function(r) {
				if (r.message.length) {
					me.tokens = r.message;
					me.show_tokens();
				} else {
					$(wrapper).html('<div class="help">' + __("No Tokens Found ") + '...</div>');
				}
			}
		});
	},
	show_tokens: function() {
		var me = this;
		$(this.wrapper).empty();
		var tokens_html = "";
		$.each(this.tokens, function(i, token) {
			let idx = "cbx_" + i;
			tokens_html+= repl(
				'<div class="col-md-3 ptc" style="cursor: pointer; border: 1px solid #d1d8dd; border-radius: 4px;" >\
					<div style="margin-top:4px">\
						<div>%(token)s</div>\
						<div>%(token_key)s</div>\
						<div>%(token_tracer)s</div>\
						<div>%(token_value)s</div>\
						<input data-token="%(token)s" id=%(idx)s type="checkbox" style="margin-left:1px; font-size: 10px;" >\
					</div>\
				</div>', {idx:idx, token: token.name, token_key: token.token_key, token_tracer: token.token_tracer, token_value: token.token_value});
		});

		$(me.wrapper).append(repl('<div class="paint-uom" style="margin-top:15px;" >\
			<div class="row">%(tokens_html)s</div>\
		</div>', {tokens_html: tokens_html}));

		// $.each(this.tokens, function(i, token) {
		// 	let idx = "cbx_" + i;
		// 	console.log(idx);
		// });

		// $('div.ptc').click(function() {
		// 	$n = event.target.nodeName;
		// 	if ($n != 'INPUT') {
		// 		$b2 = !$('#cbx').prop("checked");
		// 		$('#cbx').prop("checked", $b2);
		// 		//if change to true
		// 		//submit event
		// 		//else
		// 		//no submit event
		// 	}
		// })

		$(this.wrapper).find('input[type="checkbox"]').change(function() {
			me.set_tokens_in_table();
		});

	},
	set_tokens_in_table: function() {
		var me = this;
		var opts = this.get_tokens();

		me.frm.form.fields_dict.token_table.df.data = [];

		$.each(opts.tokens, function(i, d) {
			me.frm.form.fields_dict.token_table.df.data.push({
				'token': d.token
			});

		});
		me.frm.form.fields_dict.token_table.grid.refresh();
	},
	get_tokens: function() {
		var tokens = [];
		$(this.wrapper).find('[data-token]').each(function() {
			// debugger;
			var token = $(this).attr('data-token');
			if(token && $(this).prop("checked") == true) {
				tokens.push({token: token});
			}
		});

		return {
			tokens: tokens
		};
	},
});
