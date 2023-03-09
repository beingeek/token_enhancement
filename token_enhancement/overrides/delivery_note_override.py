import frappe
from frappe import _
from erpnext.stock.doctype.batch.batch import set_batch_nos
from erpnext.stock.doctype.delivery_note.delivery_note import DeliveryNote

class OverriddenDeliveryNote:
	def validate(self):
		self.validate_posting_time()
		super(DeliveryNote, self).validate()
		self.set_status()
		self.so_required()
		self.validate_proj_cust()
		self.check_sales_order_on_hold_or_close("against_sales_order")
		self.validate_warehouse()
		self.validate_uom_is_integer("stock_uom", "stock_qty")
		self.validate_uom_is_integer("uom", "qty")
		self.validate_with_previous_doc()

		if self._action != 'submit' and not self.is_return:
			set_batch_nos(self, 'warehouse', True)

		from erpnext.stock.doctype.packed_item.packed_item import make_packing_list
		make_packing_list(self)

		self.update_current_stock()

		if not self.installation_status: self.installation_status = 'Not Installed'
		self.validate_tokens()
		self.validate_duplicate_token_entries()

	def on_submit(self):
		self.validate_packed_qty()

		# Check for Approving Authority
		frappe.get_doc('Authorization Control').validate_approving_authority(self.doctype, self.company, self.base_grand_total, self)

		# update delivered qty in sales order
		self.update_prevdoc_status()
		self.update_billing_status()

		if not self.is_return:
			self.check_credit_limit()
		elif self.issue_credit_note:
			self.make_return_invoice()
		# Updating stock ledger should always be called after updating prevdoc status,
		# because updating reserved qty in bin depends upon updated delivered qty in SO
		self.update_stock_ledger()
		self.make_gl_entries()
		self.issue_token_update(is_issued=1)

	def on_cancel(self):
		super(DeliveryNote, self).on_cancel()

		self.check_sales_order_on_hold_or_close("against_sales_order")
		self.check_next_docstatus()

		self.update_prevdoc_status()
		self.update_billing_status()

		# Updating stock ledger should always be called after updating prevdoc status,
		# because updating reserved qty in bin depends upon updated delivered qty in SO
		self.update_stock_ledger()

		self.cancel_packing_slips()

		self.make_gl_entries_on_cancel()

		self.issue_token_update(is_issued=0)

	def issue_token_update(self, is_issued):
		token = frappe._dict({
			'issued_to': self.customer, 'issue_date': self.posting_date, 'issued_by': self.owner,
			'issue_doctype': self.doctype, 'issue_token_document': self.name
		})

		for d in self.tokens:
			paint_token = frappe.get_doc('Paint Token', d.token_tracer)
			paint_token.update_token(issue_token=token, is_issued=is_issued, update=True, update_modified=True)
			paint_token.validate_redeemed_unissuance()
			d.db_set('is_issued', is_issued)
			paint_token.notify_update()
	def validate_tokens(self):
		for d in self.tokens:
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
		for d in self.tokens:
			if (d.token_tracer) in reference_names:
				frappe.throw(_("Row #{0}: Duplicate entry in Token {1}")
					.format(d.idx, d.token_tracer))
			reference_names.append((d.token_tracer))
