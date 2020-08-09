# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "customizer"
app_title = "Customizer"
app_publisher = "ahmad"
app_description = "Custom for payroll "
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "ahmad18189"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/customizer/css/customizer.css"
# app_include_js = "/assets/customizer/js/customizer.js"

# include js, css files in header of web template
# web_include_css = "/assets/customizer/css/customizer.css"
# web_include_js = "/assets/customizer/js/customizer.js"

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
# get_website_user_home_page = "customizer.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "customizer.install.before_install"
# after_install = "customizer.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "customizer.notifications.get_notification_config"

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
doc_events = {
	"Salary Slip": {
	 	"before_validate":"customizer.customizer.salary_slip_custom.customize_salary_slip",
	 	"validate":"customizer.customizer.salary_slip_custom.validate_salary_slip"
	 }
}
# Scheduled Tasks
# ---------------

scheduler_events = {
"monthly": [
 		"customizer.tasks.monthly.create_salary_slips"
]
}
# scheduler_events = {
# 	"all": [
# 		"customizer.tasks.all"
# 	],
# 	"daily": [
# 		"customizer.tasks.daily"
# 	],
# 	"hourly": [
# 		"customizer.tasks.hourly"
# 	],
# 	"weekly": [
# 		"customizer.tasks.weekly"
# 	]
# 	"monthly": [
# 		"customizer.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "customizer.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "customizer.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "customizer.task.get_dashboard_data"
# }
fixtures = ["Custom Field","Custom Script"]
