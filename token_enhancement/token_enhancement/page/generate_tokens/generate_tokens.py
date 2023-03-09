import frappe
from frappe import _
from frappe.utils import cint, cstr

@frappe.whitelist()
def generate_tokens(number_of_tokens, token_value,  work_order, creation_date, created_by, company, notes=None):
	token_list = []
	for token_counter in range(cint(number_of_tokens)):
		doc = frappe.new_doc('Paint Token')

		doc.token_key = doc.generate_token_key()
		doc.work_order = work_order
		doc.creation_date = creation_date
		doc.token_value = token_value
		doc.created_by = created_by
		doc.notes = notes
		doc.company = company
		doc.save()
		token_list.append(doc)
	return token_list
