
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
		self.validate_duplicate_token_entries()

	def on_submit(self):
		self.issue_token_update(is_issued=1)

	def on_cancel(self):
		self.issue_token_update(is_issued=0)

	def issue_token_update(self, is_issued):
		token = frappe._dict({
			'issued_to': self.customer, 'issue_date': self.issue_date, 'issued_by': self.issued_by,
			'issue_doctype': self.doctype, 'issue_token_document': self.name
		})
		for d in self.issue_tokens:
			paint_token = frappe.get_doc('Paint Token', d.token_tracer)
			paint_token.update_token(issue_token=token, is_issued=is_issued, update=True, update_modified=True)
			paint_token.validate_redeemed_unissuance()
			d.db_set('is_issued', is_issued)
			paint_token.notify_update()

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

	def validate_duplicate_token_entries(self):
		reference_names = []
		for d in self.issue_tokens:
			if (d.token_tracer) in reference_names:
				frappe.throw(_("Row #{0}: Duplicate entry in Token {1}")
					.format(d.idx, d.token_tracer))
			reference_names.append((d.token_tracer))
