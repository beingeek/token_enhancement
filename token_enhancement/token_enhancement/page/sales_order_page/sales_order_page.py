import frappe
from frappe import _
from frappe.utils import cint, cstr
import json


@frappe.whitelist()
def get_all_paint_uom_items():
	paint_uoms =  frappe.get_all("UOM", filters={
		"is_paint_uom": 1
	}, order_by="name")

	paint_uoms_item_map = []
	if paint_uoms:
		paint_uoms = [paint_uom.get("name") for paint_uom in paint_uoms]
		for paint_uom in paint_uoms:
			paint_uom_item_row = {}
			items_with_uom = frappe.get_all("Item", filters={"paint_uom": paint_uom}, order_by="name")
			if items_with_uom:
				paint_uom_item_row[paint_uom] = [d.get("name") for d in items_with_uom]
				paint_uoms_item_map.append(paint_uom_item_row)

	return paint_uoms_item_map


@frappe.whitelist()
def create_sales_order(customer, company, transaction_date, delivery_date, item_table):
	item_table = json.loads(item_table)

	so = frappe.new_doc('Sales Order')

	so.customer = customer
	so.company = company
	so.transaction_date = transaction_date
	so.delivery_date = delivery_date

	for item in item_table:
		if item.get('item_code') and item.get('qty'):
			so.append("items", {'item_code':item.get('item_code'), 'qty': item.get('qty')})
		else:
			frappe.throw('Missing Data')

	so.save()

	return so
