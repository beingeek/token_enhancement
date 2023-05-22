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

			token_data[0]["work_order"] = token_data[0]["work_order"][-5:] if token_data[0].get("work_order") else None
			token_data[0]["token_tracer"] = token_data[0]["token_tracer"][-5:] if token_data[0].get("token_tracer") else None

			tokens_data['tokens_details'].append(token_data[0])

	custom_print_html = frappe.render_template("""
		<style>
		tr {
			height : 96px
		}	

		td {
			width : 196px
		}
		p{
			font-size : 10px
		}
		</style>
			<table>
  <tr>
	{% for token in doc.tokens_details %}
    
      <td colspan="3">
        <div class="text-center2" style="background-color: {{ token.bkg_color }}; padding: 10px; text-align: center;">
          <p>{{ token.bkg_color }}</p>
			<img src="{{ token.token_tracer_qr }}" height = "96px" width="100px"/>
			<div class="text-center"><p>Token Value: {{ token.token_value }}</p></div>
          <div class="text-center"><p>Tracer: {{ token.token_tracer }}</p></div>
          <div class=""><p>WO: {{ token.work_order }}</p></div>
        </div>
      </td>
      
      
      {% if loop.index % 4 == 0 %}
        </tr><tr>
      {% endif %}
    {% endfor %}
  </tr>
</table>""", dict(doc=tokens_data))

	frappe.msgprint(cstr(custom_print_html))

	frappe.response.filename = "custom_print_html" + ".pdf"
	frappe.response.filecontent = get_pdf(custom_print_html)
	frappe.response.type = "download"

	# return custom_print_html
