# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt


# ~ Override Salary Structerfunction 
def pull_sal_struct(self,doc =None,method= None):
	from erpnext.hr.doctype.salary_structure.salary_structure import make_salary_slip
	self.total_working_hours = 0.0
	if self.salary_slip_based_on_timesheet:
		self.salary_structure = self._salary_structure_doc.name
		self.hour_rate = self._salary_structure_doc.hour_rate
		self.total_working_hours += sum([d.working_hours or 0.0 for d in self.timesheets]) or 0.0
		wages_amount = self.hour_rate * self.total_working_hours

		self.add_earning_for_hourly_wages(self, self._salary_structure_doc.salary_component, wages_amount)
	
	if self.salary_slip_based_on_attendance:
		attendances = frappe.db.sql(""" select sum(working_hours) as total from `tabAttendance` where employee = %(employee)s and attendance_date BETWEEN %(start_date)s AND %(end_date)s and status = 'Present' 
		and docstatus = 1""", {'employee': self.employee, 'start_date': self.start_date, 'end_date': self.end_date}, as_dict=1)
		print (attendances)
		self.salary_structure = self._salary_structure_doc.name
		self.hour_rate = self._salary_structure_doc.hour_rate
		
		self.total_working_hours += attendances[0]["total"] or 0.0
		wages_amount = self.hour_rate * self.total_working_hours

		self.add_earning_for_hourly_wages(self, self._salary_structure_doc.salary_component, wages_amount)

	make_salary_slip(self._salary_structure_doc.name, self)

@frappe.whitelist()
def validate_salary_slip(doc ,method):
	if doc.salary_slip_based_on_attendance:
		doc.get_emp_and_leave_details()


@frappe.whitelist()
def customize_salary_slip(doc =None,method= None):
	from erpnext.hr.doctype.salary_slip.salary_slip import SalarySlip
	SalarySlip.pull_sal_struct = pull_sal_struct



# ~ Create Journal Entry for Salary Slip Functions 
@frappe.whitelist()
def make_accrual_jv_entry(salary_slip):
	doc = frappe.get_doc("Salary Slip",salary_slip)
	earnings = doc.get("earnings") or {}
	deductions = doc.get("deductions") or {}
	default_payroll_payable_account = frappe.get_cached_value('Company',
		{"company_name": doc.company},  "default_payroll_payable_account")

	if not default_payroll_payable_account:
		frappe.throw(_("Please set Default Payroll Payable Account in Company {0}")
			.format(self.company))
			
	loan_details = doc.get("loans") or {}
	jv_name = ""
	precision = frappe.get_precision("Journal Entry Account", "debit_in_account_currency")

	if earnings or deductions:
		journal_entry = frappe.new_doc('Journal Entry')
		journal_entry.voucher_type = 'Journal Entry'
		journal_entry.user_remark = _('Accrual Journal Entry for salaries from {0} to {1}')\
			.format(doc.start_date, doc.end_date)
		journal_entry.company = doc.company
		journal_entry.posting_date = doc.posting_date

		accounts = []
		payable_amount = 0
		
		# Earnings
		for earning in earnings:
			account = get_salary_component_account(earning.salary_component,doc.company)
			earning.account = account
			payable_amount += flt(earning.amount, precision)
			accounts.append({
					"account": earning.account,
					"debit_in_account_currency": flt(earning.amount, precision),
					"party_type": '',
					"cost_center": doc.cost_center,
					"project": doc.project
				})
		
		# Deductions
		for deduction in deductions:
			account = get_salary_component_account(deduction.salary_component,doc.company)
			deduction.account = account
			payable_amount -= flt(deduction.amount, precision)
			accounts.append({
					"account": deduction.account,
					"debit_in_account_currency": flt(deduction.amount, precision),
					"party_type": '',
					"cost_center": doc.cost_center,
					"project": doc.project
				})


		# Loan
		for data in loan_details:
			accounts.append({
					"account": data.loan_account,
					"credit_in_account_currency": data.principal_amount,
					"party_type": "Employee",
					"party": data.employee
				})

			if data.interest_amount and not data.interest_income_account:
				frappe.throw(_("Select interest income account in loan {0}").format(data.loan))

			if data.interest_income_account and data.interest_amount:
				accounts.append({
					"account": data.interest_income_account,
					"credit_in_account_currency": data.interest_amount,
					"cost_center": doc.cost_center,
					"project": doc.project,
					"party_type": "Employee",
					"party": data.employee
				})
			payable_amount -= flt(data.total_payment, precision)

		# Payable amount
		accounts.append({
			"account": default_payroll_payable_account,
			"credit_in_account_currency": flt(payable_amount, precision),
			"party_type": '',
		})

		journal_entry.set("accounts", accounts)
		journal_entry.title = default_payroll_payable_account
		journal_entry.save()

		try:
			journal_entry.submit()
			jv_name = journal_entry.name
			frappe.db.set_value("Salary Slip", doc.name, "journal_entry", jv_name)
			
		except Exception as e:
			frappe.msgprint(e)

	return jv_name

@frappe.whitelist()
def create_bank_entry(salary_slip):
	doc = frappe.get_doc("Salary Slip",salary_slip)
	default_payroll_payable_account = frappe.get_cached_value('Company',
			{"company_name": doc.company},  "default_payroll_payable_account")

	if not default_payroll_payable_account:
		frappe.throw(_("Please set Default Payroll Payable Account in Company {0}")
			.format(doc.company))
				
	precision = frappe.get_precision("Journal Entry Account", "debit_in_account_currency")
	user_remark = doc.name
	journal_entry = frappe.new_doc('Journal Entry')
	journal_entry.voucher_type = 'Bank Entry'
	journal_entry.user_remark = _('Payment of {0} from {1} to {2}')\
		.format(user_remark, doc.start_date, doc.end_date)
	journal_entry.company = doc.company
	journal_entry.posting_date = doc.posting_date

	payment_amount = flt(doc.net_pay, precision)
	

	journal_entry.set("accounts", [
		{
			"account": doc.payment_account,
			"credit_in_account_currency": payment_amount
		},
		{
			"account": default_payroll_payable_account,
			"debit_in_account_currency": payment_amount,
			"reference_type": "Journal Entry",
			"reference_name": doc.journal_entry
		}
	])
	journal_entry.save(ignore_permissions = True)
	
	
def get_salary_component_account(salary_component,company):
		account = frappe.db.get_value("Salary Component Account",
			{"parent": salary_component, "company": company}, "default_account")

		if not account:
			frappe.throw(_("Please set default account in Salary Component {0}")
				.format(salary_component))

		return account
