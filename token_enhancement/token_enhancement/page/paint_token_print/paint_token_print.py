import frappe
from frappe import _
from frappe.utils import cint, cstr
import json
from frappe.utils.pdf import get_pdf
from six import string_types


@frappe.whitelist()
def get_paint_tokens():
	paint_uoms =  frappe.get_all("Paint Token", order_by="name", fields=['name', 'token_key', 'token_tracer', 'token_value'])
	return paint_uoms

@frappe.whitelist()
def print_tokens(tokens):
	if not isinstance(tokens, list):
		tokens = json.loads(tokens)

	tokens_data = {'tokens_details': []}
	for d in tokens:
		fields = ["token_key", "token_key_qr", "token_tracer", "token_tracer_qr", "token_value", "work_order"]
		token_data = frappe.db.get_values("Paint Token", d.get("token"), fields, as_dict=True)
		if token_data:
			if token_data[0].token_value == '50':
				token_data[0]['bkg_color'] = '#8db380'
			elif token_data[0].token_value == '300':
				token_data[0]['bkg_color'] = '#ebd300'
			elif token_data[0].token_value == '400':
				token_data[0]['bkg_color'] = '#d30077'
			elif token_data[0].token_value == '1200':
				token_data[0]['bkg_color'] = '#0194c8'

			tokens_data['tokens_details'].append(token_data[0])

	custom_print_html = frappe.render_template("""
		<style>

		</style>
		<div class="text-center" style="text-align: center;">
		{% for token in doc.tokens_details %}
			<div class="text-center2" style="background-color: {{ token.bkg_color }}; padding: 10px; text-align: center;">
				<p>{{ token.bkg_color }}</p>
				<div class="img-wrap"><img src="{{ token.token_tracer_qr }}" ></div>
				<div class="text-center"><p>Tracer: {{ token.token_tracer }}</p></div>
				<div class=""><p>Work Order: {{ token.work_order }}</p></div>
			</div>
		{% endfor %}
		</div>""", dict(doc=tokens_data))

	frappe.msgprint(cstr(custom_print_html))

	frappe.response.filename = "custom_print_html" + ".pdf"
	frappe.response.filecontent = get_pdf(custom_print_html)
	frappe.response.type = "download"

	# return custom_print_html
