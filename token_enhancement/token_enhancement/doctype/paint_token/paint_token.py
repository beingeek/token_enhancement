# -*- coding: utf-8 -*-
# Copyright (c) 2023, Createch Global Solutions and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import io
import os
from base64 import b64encode
from pyqrcode import create as qr_create

class PaintToken(Document):
	def validate(self):
		self.validate_token_value()

	def after_insert(self):
		self.db_set('token_tracer', self.name)
		qr_code_generator(self, 'token_key')
		qr_code_generator(self, 'token_tracer')

	def validate_token_value(self):
		#not other then is select dropdown
		pass

	def generate_token_key(self):
		return frappe.generate_hash(length=10)


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
