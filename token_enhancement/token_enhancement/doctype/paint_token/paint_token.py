# -*- coding: utf-8 -*-
# Copyright (c) 2023, Createch Global Solutions and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe import _
import frappe
from frappe.model.document import Document
import io
import os
from pyqrcode import create as qr_create

class PaintToken(Document):
	def validate(self):
		self.validate_token_value()

	def after_insert(self):
		self.db_set('token_tracer', self.name)
		qr_code_generator(self, 'token_key')
		qr_code_generator(self, 'token_tracer')

	def validate_token_value(self):
		token_values = self.meta.get_options("token_value").split('\n')
		token_values = [d for d in token_values if d]
		if self.token_value not in token_values:
			frappe.throw(_('Invalid Token Value'))

	def generate_token_key(self):
		return frappe.generate_hash(length=10)

	def update_token(self, issue_token, is_issued=0, update=False, update_modified=False):
		if issue_token:
			if is_issued:
				self.is_issued = is_issued
				self.issued_to = issue_token.customer
				self.issue_date = issue_token.issue_date
				self.issued_by = issue_token.issued_by

			elif not is_issued:
				self.is_issued = is_issued
				self.issued_to = None
				self.issue_date = None
				self.issued_by = None

		if update:
			self.db_set('is_issued', self.is_issued, update_modified=update_modified)
			self.db_set('issued_to', self.issued_to, update_modified=update_modified)
			self.db_set('issue_date', self.issue_date, update_modified=update_modified)
			self.db_set('issued_by', self.issued_by, update_modified=update_modified)


def qr_code_generator(doc, qr_field):
	qr_field_value = doc.get(qr_field)
	url = qr_create(qr_field_value)
	qr_image = io.BytesIO()
	url.png(qr_image, scale=8, quiet_zone=1)
	name = frappe.generate_hash(doc.name, 5)
	filename = f"QRCode-{name}.png".replace(os.path.sep, "__")

	_file = frappe.get_doc(
		{
			"doctype": "File",
			"file_name": filename,
			"is_private": 0,
			"content": qr_image.getvalue(),
			"attached_to_doctype": doc.get("doctype"),
			"attached_to_name": doc.get("name"),
			"attached_to_field": qr_field,
		}
	)
	_file.save()
	doc.db_set("{0}_qr".format(qr_field), _file.file_url)
	doc.notify_update()
