
# -*- coding: utf-8 -*-
# Copyright (c) 2023, Createch Global Solutions and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class IssueTokenInventory(Document):
	def validate(self):
		self.validate_tokens()

	def on_submit(self):
		for d in self.issue_tokens:
			token = frappe.get_doc('Paint Token', d.token_tracer)
			token.update_token(self, is_issued=1, update=True, update_modified=True)
			d.is_issued = 1
			token.notify_update()

	def on_cancel(self):
		for d in self.issue_tokens:
			token = frappe.get_doc('Paint Token', d.token_tracer)
			token.update_token(self, is_issued=0, update=True, update_modified=True)
			d.is_issued = 0
			token.notify_update()


	def validate_tokens(self):
		for d in self.issue_tokens:
			token = frappe.get_doc('Paint Token', d.token_tracer)
			if token.is_issued:
				frappe.throw(
					_('Row# {0}, {1} Already Issues')
					.format(d.idx, frappe.get_desk_link('Paint Token', d.token_tracer))
				)

			if token.is_redeemed:
				frappe.throw(
					_('Row# {0}, {1} Redeemed')
					.format(d.idx, frappe.get_desk_link('Paint Token', d.token_tracer))
				)
