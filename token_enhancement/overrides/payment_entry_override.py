from frappe import _
import frappe
import erpnext
from frappe.utils import flt
from token_enhancement.token_enhancement.doctype.paint_token.paint_token import get_token_data

class OverridenPaymentEntry:
	def setup_party_account_field(self):
		self.party_account_field = None
		self.party_account = None
		self.party_account_currency = None

		if self.payment_type == "Receive":
			self.party_account_field = "paid_from"
			self.party_account = self.paid_from
			self.party_account_currency = self.paid_from_account_currency

		elif self.payment_type in ["Pay", "Token Payment Entry"]:
			self.party_account_field = "paid_to"
			self.party_account = self.paid_to
			self.party_account_currency = self.paid_to_account_currency

	def validate(self):
		self.setup_party_account_field()
		self.set_missing_values()
		self.validate_payment_type()
		self.validate_party_details()
		self.validate_bank_accounts()
		self.set_exchange_rate()
		self.validate_mandatory()

		# Token Payment Entry
		if self.payment_type == 'Token Payment Entry':
			self.set_token_references()
			self.validate_token_references()
			self.validate_duplicate_token_entries()
			self.set_amounts_for_tokens()
			self.set_title()
			self.validate_allocated_amount_for_tokens()
			self.set_status()

		# other pe types
		else:
			self.validate_reference_documents()
			self.set_amounts()
			self.clear_unallocated_reference_document_rows()
			self.validate_payment_against_negative_invoice()
			self.validate_transaction_reference()
			self.set_title()
			self.set_remarks()
			self.validate_duplicate_entry()
			self.validate_allocated_amount()
			self.validate_paid_invoices()
			self.ensure_supplier_is_not_blocked()
			self.set_status()

	def on_submit(self):
		self.setup_party_account_field()
		if self.difference_amount:
			frappe.throw(_("Difference Amount must be zero"))
		self.make_gl_entries()
		self.update_outstanding_amounts()
		self.update_advance_paid()
		self.update_expense_claim()
		self.update_payment_schedule()
		self.redeem_token_update(is_redeemed=1)
		self.set_status()

	def on_cancel(self):
		self.setup_party_account_field()
		self.make_gl_entries(cancel=1)
		self.update_outstanding_amounts()
		self.update_advance_paid()
		self.update_expense_claim()
		self.delink_advance_entry_references()
		self.update_payment_schedule(cancel=1)
		self.set_payment_req_status()
		self.redeem_token_update(is_redeemed=0)
		self.set_status(update=True)

	def redeem_token_update(self, is_redeemed):
		for d in self.get("token_references"):
			token = frappe.get_doc('Paint Token', d.token_tracer)
			token.update_token(payment_entry=self, is_redeemed=is_redeemed, update=True, update_modified=True)
			token.validate_unissued_redemption()
			d.is_redeemed = is_redeemed
			token.notify_update()

	def validate_payment_type(self):
		if self.payment_type not in ("Receive", "Pay", "Internal Transfer", "Token Payment Entry"):
			frappe.throw(_("Payment Type must be one of Receive, Pay and Internal Transfer"))

	def validate_bank_accounts(self):
		if self.payment_type in ("Pay", "Internal Transfer", "Token Payment Entry"):
			self.validate_account_type(self.paid_from, ["Bank", "Cash"])

		if self.payment_type in ("Receive", "Internal Transfer"):
			self.validate_account_type(self.paid_to, ["Bank", "Cash"])

	def set_token_references(self):
		for d in self.get("token_references"):
			token_data = get_token_data(d.token_key)
			d.token_tracer = token_data.token_tracer
			d.token_value = token_data.token_value
			d.is_issued = token_data.is_issued
			d.is_redeemed = token_data.is_redeemed

	def validate_token_references(self):
		if not self.token_references:
			frappe.throw(_('Please Enter Token keys'))

		for d in self.get("token_references"):
			token_data = get_token_data(d.token_key)
			if not (token_data.is_issued and token_data.issued_to):
				frappe.throw(_('Row# {0} Token {1} not yet issued').format(d.idx, d.token_key))
			if token_data.is_redeemed:
				frappe.throw(_('Row# {0} Token {1} already redeemed').format(d.idx, d.token_key))
			if self.party != token_data.issued_to:
				frappe.throw(_('Row# {0} Token {1} was not issued to {2}').format(d.idx, d.token_key, frappe.get_desk_link('Customer', self.party)))

	def validate_duplicate_token_entries(self):
		reference_names = []
		for d in self.get("token_references"):
			if (d.token_key) in reference_names:
				frappe.throw(_("Row #{0}: Duplicate entry in Token {1}")
					.format(d.idx, d.token_key))
			reference_names.append((d.token_key))

	def validate_allocated_amount_for_tokens(self):
		if self.paid_amount != self.total_allocated_amount:
			frappe.throw(_('Paid amount {0} is not equal to {1} sum of token values').format(self.paid_amount, self.total_allocated_amount))

	def set_amounts_for_tokens(self):
		self.set_amounts_in_company_currency()
		self.set_total_allocated_amount_tokens()

	def set_total_allocated_amount_tokens(self):
		total_allocated_amount, base_total_allocated_amount = 0, 0
		for d in self.get("token_references"):
			if d.token_value:
				total_allocated_amount += flt(d.token_value)
				base_total_allocated_amount += flt(flt(d.token_value) * flt(self.source_exchange_rate),
					self.precision("base_paid_amount"))

		self.total_allocated_amount = abs(total_allocated_amount)
		self.base_total_allocated_amount = abs(base_total_allocated_amount)

	def set_difference_amount(self):
		base_unallocated_amount = flt(self.unallocated_amount) * (flt(self.source_exchange_rate)
			if self.payment_type == "Receive" else flt(self.target_exchange_rate))

		base_party_amount = flt(self.base_total_allocated_amount) + flt(base_unallocated_amount)

		if self.payment_type == "Receive":
			self.difference_amount = base_party_amount - self.base_received_amount
		elif self.payment_type in ["Pay", "Token Payment Entry"]:
			self.difference_amount = self.base_paid_amount - base_party_amount
		else:
			self.difference_amount = self.base_paid_amount - flt(self.base_received_amount)

		total_deductions = sum([flt(d.amount) for d in self.get("deductions")])

		self.difference_amount = flt(self.difference_amount - total_deductions,
			self.precision("difference_amount"))

	# Paid amount is auto allocated in the reference document by default.
	# Clear the reference document which doesn't have allocated amount on validate so that form can be loaded fast

	def set_title(self):
		if frappe.flags.in_import and self.title:
			# do not set title dynamically if title exists during data import.
			return

		if self.payment_type in ("Receive", "Pay", "Token Payment Entry"):
			self.title = self.party
		else:
			self.title = self.paid_from + " - " + self.paid_to

	def set_remarks_token_pe(self):
		# set remarks for token entry
		pass

	def add_party_gl_entries(self, gl_entries):
		if self.party_account:
			if self.payment_type=="Receive":
				against_account = self.paid_to
			else:
				against_account = self.paid_from

			party_gl_dict = self.get_gl_dict({
				"account": self.party_account,
				"party_type": self.party_type,
				"party": self.party,
				"against": against_account,
				"account_currency": self.party_account_currency,
				"cost_center": self.cost_center
			}, item=self)

			dr_or_cr = "credit" if erpnext.get_party_account_type(self.party_type) == 'Receivable' and self.payment_type!="Token Payment Entry" else "debit"

			if self.payment_type == "Token Payment Entry":
				for d in self.get("token_references"):
					gle = party_gl_dict.copy()
					gle.update({
						"against_voucher_type": "Paint Token",
						"against_voucher": d.token_tracer
					})
					allocated_amount_in_company_currency = flt(flt(d.token_value) * flt(self.source_exchange_rate),
						self.precision("paid_amount"))

					gle.update({
						dr_or_cr + "_in_account_currency": d.token_value,
						dr_or_cr: allocated_amount_in_company_currency
					})

					gl_entries.append(gle)

			else:
				for d in self.get("references"):
					gle = party_gl_dict.copy()
					gle.update({
						"against_voucher_type": d.reference_doctype,
						"against_voucher": d.reference_name
					})

					allocated_amount_in_company_currency = flt(flt(d.allocated_amount) * flt(d.exchange_rate),
						self.precision("paid_amount"))

					gle.update({
						dr_or_cr + "_in_account_currency": d.allocated_amount,
						dr_or_cr: allocated_amount_in_company_currency
					})

					gl_entries.append(gle)

				if self.unallocated_amount:
					base_unallocated_amount = base_unallocated_amount = self.unallocated_amount * \
						(self.source_exchange_rate if self.payment_type=="Receive" else self.target_exchange_rate)

					gle = party_gl_dict.copy()

					gle.update({
						dr_or_cr + "_in_account_currency": self.unallocated_amount,
						dr_or_cr: base_unallocated_amount
					})

					gl_entries.append(gle)

	def add_bank_gl_entries(self, gl_entries):
		if self.payment_type in ("Pay", "Internal Transfer", "Token Payment Entry"):
			gl_entries.append(
				self.get_gl_dict({
					"account": self.paid_from,
					"account_currency": self.paid_from_account_currency,
					"against": self.party if self.payment_type in ["Pay", "Token Payment Entry"] else self.paid_to,
					"credit_in_account_currency": self.paid_amount,
					"credit": self.base_paid_amount,
					"cost_center": self.cost_center
				}, item=self)
			)
		if self.payment_type in ("Receive", "Internal Transfer"):
			gl_entries.append(
				self.get_gl_dict({
					"account": self.paid_to,
					"account_currency": self.paid_to_account_currency,
					"against": self.party if self.payment_type=="Receive" else self.paid_from,
					"debit_in_account_currency": self.received_amount,
					"debit": self.base_received_amount,
					"cost_center": self.cost_center
				}, item=self)
			)
