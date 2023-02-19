
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
		self.issue_token_update(is_issued=1)

	def on_cancel(self):
		self.issue_token_update(is_issued=0)

	def issue_token_update(self, is_issued):

		for d in self.issue_tokens:
			token = frappe.get_doc('Paint Token', d.token_tracer)
			token.update_token(issue_token=self, is_issued=is_issued, update=True, update_modified=True)
			token.validate_redeemed_unissuance()
			d.db_set('is_issued', is_issued)
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
