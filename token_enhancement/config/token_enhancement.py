from __future__ import unicode_literals
from frappe import _
import frappe


def get_data():
	config = [
		{
			"label": _("Token Issue and Redeem"),
			"items": [
				{
					"type": "page",
					"name": "generate-tokens",
					"label": _("Generate Tokens"),
				},
				{
					"type": "doctype",
					"name": "Customer",
					"description": _("Customer")
				},
				{
					"type": "doctype",
					"name": "Paint Token",
					"description": _("Paint Tokens")
				},
				{
					"type": "doctype",
					"name": "Issue Token Inventory",
					"description": _("Issue Token Inventory"),
					"dependencies": ["Paint Token", "Customer"],
				},
				{
					"type": "doctype",
					"name": "Payment Entry",
					"description": _("Payment Entry"),
					"dependencies": ["Paint Token", "Customer"],
				},
			]
		},
	]

	return config