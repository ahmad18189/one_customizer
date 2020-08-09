# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import date_diff, add_months, today, getdate, add_days, flt, get_last_day, get_first_day, cint, get_link_to_form, rounded


def create_salary_slips():
	
	start_date = get_first_day(add_months(today(), -1))
	end_date = get_last_day(start_date)
	posting_date = add_days(end_date,1)
	default_company = frappe.db.get_single_value('Global Defaults', 'default_company')
	
	emp_list =  [d.employee for d in get_emp_list(default_company,end_date)]
	
	if emp_list:
		args = frappe._dict({
			"salary_slip_based_on_attendance": 1,
			"payroll_frequency": "Monthly",
			"start_date": start_date,
			"end_date": end_date,
			"company": default_company,
			"posting_date": posting_date,
		})
		if len(emp_list) > 30:
			frappe.enqueue(create_salary_slips_for_employees, timeout=600, employees=emp_list, args=args)
		else:
			create_salary_slips_for_employees(emp_list, args, publish_progress=False)

def create_salary_slips_for_employees(employees, args, publish_progress=True):
	from erpnext.hr.doctype.payroll_entry.payroll_entry import get_existing_salary_slips

	salary_slips_exists_for = get_existing_salary_slips(employees, args)
	count=0
	for emp in employees:
		if emp not in salary_slips_exists_for:
			args.update({
				"doctype": "Salary Slip",
				"employee": emp
			})
			ss = frappe.get_doc(args)
			ss.submit()

		

def get_emp_list(company,end_date):
	sal_struct = frappe.db.sql_list("""
			select
				name from `tabSalary Structure`
			where
				docstatus = 1 and
				is_active = 'Yes'
				and company = %(company)s """,
			{"company": company})
	if sal_struct:
		cond=""
		cond += "and t2.salary_structure IN %(sal_struct)s "
		cond += "and %(from_date)s >= t2.from_date"
		emp_list = frappe.db.sql("""
			select
				distinct t1.name as employee, t1.employee_name, t1.department, t1.designation
			from
				`tabEmployee` t1, `tabSalary Structure Assignment` t2
			where
				t1.name = t2.employee
				and t2.docstatus = 1
		%s order by t2.from_date desc
		""" % cond, {"sal_struct": tuple(sal_struct), "from_date": end_date}, as_dict=True)
		return emp_list

