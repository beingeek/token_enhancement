import frappe
from frappe import _
from frappe.utils import cint, cstr

@frappe.whitelist()
def generate_tokens(number_of_tokens, token_value,  production_batch, creation_date, created_by, notes=None):
	for token_counter in range(cint(number_of_tokens)):
		doc = frappe.new_doc('Paint Token')

		doc.token_key = doc.generate_token_key()
		doc.production_batch = production_batch
		doc.creation_date = creation_date
		doc.token_value = token_value
		doc.created_by = created_by
		doc.notes = notes
		doc.token_tracer

		doc.save()
