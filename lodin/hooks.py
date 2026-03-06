app_name = "lodin"
app_title = "Lodin"
app_publisher = "Lodin"
app_description = "Solution de Paiement pour ERPNext"
app_email = "apps@effyis-partners.ma"
app_license = "mit"
app_version = "1.0.0"
required_apps = ["erpnext"]

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "lodin",
# 		"logo": "/assets/lodin/logo.png",
# 		"title": "Lodin",
# 		"route": "/lodin",
# 		"has_permission": "lodin.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/lodin/css/lodin.css"
# app_include_js = "/assets/lodin/js/lodin.js"

# include js, css files in header of web template
# web_include_css = "/assets/lodin/css/lodin.css"
# web_include_js = "/assets/lodin/js/lodin.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "lodin/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "lodin/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "lodin.utils.jinja_methods",
# 	"filters": "lodin.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "lodin.install.before_install"
# after_install = "lodin.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "lodin.uninstall.before_uninstall"
# after_uninstall = "lodin.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "lodin.utils.before_app_install"
# after_app_install = "lodin.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "lodin.utils.before_app_uninstall"
# after_app_uninstall = "lodin.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "lodin.notifications.get_notification_config"

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

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"lodin.tasks.all"
# 	],
# 	"daily": [
# 		"lodin.tasks.daily"
# 	],
# 	"hourly": [
# 		"lodin.tasks.hourly"
# 	],
# 	"weekly": [
# 		"lodin.tasks.weekly"
# 	],
# 	"monthly": [
# 		"lodin.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "lodin.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "lodin.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "lodin.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["lodin.utils.before_request"]
# after_request = ["lodin.utils.after_request"]

# Job Events
# ----------
# before_job = ["lodin.utils.before_job"]
# after_job = ["lodin.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"lodin.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

after_migrate = "lodin.custom.install_custom_fields.install"
after_install = "lodin.custom.install_custom_fields.install"

doc_events = {
    "Sales Invoice": {
        "on_submit": "lodin.custom.sales_invoice.on_submit",
    }
}

doctype_js = {
    "Sales Invoice": "public/js/sales_invoice_custom.js"
}
