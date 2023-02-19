# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "token_enhancement"
app_title = "Token Enhancement"
app_publisher = "Createch Global Solutions"
app_description = "Token Enhancement for paint mixing company"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "furqan@createch.solutions"
app_license = "MIT"

required_apps = ["erpnext"]

fixtures = [
    {
        "doctype": "Property Setter",
        "filters": [["name", "in", ("Payment Entry-payment_type-options")]],
    },
]

doctype_js = {
    "Payment Entry" : "overrides/payment_entry_override.js"
}

from erpnext.accounts.doctype.payment_entry.payment_entry import PaymentEntry as _PaymentEntry
from token_enhancement.overrides.payment_entry_override import OverridenPaymentEntry as _OverridenPaymentEntry

_PaymentEntry.setup_party_account_field = _OverridenPaymentEntry.setup_party_account_field
_PaymentEntry.validate = _OverridenPaymentEntry.validate
_PaymentEntry.on_submit = _OverridenPaymentEntry.on_submit
_PaymentEntry.on_cancel = _OverridenPaymentEntry.on_cancel
_PaymentEntry.redeem_token_update = _OverridenPaymentEntry.redeem_token_update
_PaymentEntry.validate_payment_type = _OverridenPaymentEntry.validate_payment_type
_PaymentEntry.validate_bank_accounts = _OverridenPaymentEntry.validate_bank_accounts
_PaymentEntry.set_token_references = _OverridenPaymentEntry.set_token_references
_PaymentEntry.validate_token_references = _OverridenPaymentEntry.validate_token_references
_PaymentEntry.validate_allocated_amount_for_tokens = _OverridenPaymentEntry.validate_allocated_amount_for_tokens
_PaymentEntry.set_amounts_for_tokens = _OverridenPaymentEntry.set_amounts_for_tokens
_PaymentEntry.set_total_allocated_amount_tokens = _OverridenPaymentEntry.set_total_allocated_amount_tokens
_PaymentEntry.set_difference_amount = _OverridenPaymentEntry.set_difference_amount
_PaymentEntry.set_title = _OverridenPaymentEntry.set_title
_PaymentEntry.set_remarks_token_pe = _OverridenPaymentEntry.set_remarks_token_pe
_PaymentEntry.add_party_gl_entries = _OverridenPaymentEntry.add_party_gl_entries
_PaymentEntry.add_bank_gl_entries = _OverridenPaymentEntry.add_bank_gl_entries

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/token_enhancement/css/token_enhancement.css"
# app_include_js = "/assets/token_enhancement/js/token_enhancement.js"

# include js, css files in header of web template
# web_include_css = "/assets/token_enhancement/css/token_enhancement.css"
# web_include_js = "/assets/token_enhancement/js/token_enhancement.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "token_enhancement.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "token_enhancement.install.before_install"
# after_install = "token_enhancement.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "token_enhancement.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"token_enhancement.tasks.all"
# 	],
# 	"daily": [
# 		"token_enhancement.tasks.daily"
# 	],
# 	"hourly": [
# 		"token_enhancement.tasks.hourly"
# 	],
# 	"weekly": [
# 		"token_enhancement.tasks.weekly"
# 	]
# 	"monthly": [
# 		"token_enhancement.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "token_enhancement.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "token_enhancement.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "token_enhancement.task.get_dashboard_data"
# }

