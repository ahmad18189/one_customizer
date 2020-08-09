# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _
from datetime import date, timedelta
import random
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee
from frappe.utils import cstr



def make_attendance():
	# ~ get employees data 
	employees = frappe.get_list("Employee",fields= ['name','employee_name','company'])
	if employees:
		for employee in employees:
			print(employee)
	
	
			d1 = date(2020, 7, 1)
			d2 = date(2020, 7, 30)
			delta = d2 - d1
			for i in range(delta.days + 1):
				print(d1 + timedelta(days=i))
				hours_rand = round(random.uniform(5.9, 8.1), 2)
				print(hours_rand)
				
				h =get_holidays_for_employee(employee["name"],d1,d2)
				print (h)
				if not cstr(d1 + timedelta(days=i)) in h :
					print ("HIT")
					attendance = frappe.get_doc({
						'doctype': 'Attendance',
						'employee': employee["name"],
						'attendance_date': d1 + timedelta(days=i),
						'status': "Present",
						'working_hours': hours_rand,
						'company': employee["company"],
					})
					attendance.flags.ignore_validate = True
					attendance.insert()
					attendance.submit()


def get_holidays_for_employee(employee, start_date, end_date):
		holiday_list = get_holiday_list_for_employee(employee)
		holidays = frappe.db.sql_list('''select holiday_date from `tabHoliday`
			where
				parent=%(holiday_list)s
				and holiday_date >= %(start_date)s
				and holiday_date <= %(end_date)s''', {
					"holiday_list": holiday_list,
					"start_date": start_date,
					"end_date": end_date
				})

		holidays = [cstr(i) for i in holidays]

		return holidays


	
def reset_validation_salary_slip(doc, method):
	from erpnext.hr.doctype.salary_slip.salary_slip import SalarySlip
	# ~ SalarySlip.validate = validate



def get_emp_and_leave_details(self):
	pass
	# ~ '''First time, load all the components from salary structure'''
	# ~ if self.employee:
		# ~ self.set("earnings", [])
		# ~ self.set("deductions", [])

		# ~ if not self.salary_slip_based_on_timesheet:
			# ~ self.get_date_details()
		# ~ self.validate_dates()
		# ~ joining_date, relieving_date = frappe.get_cached_value("Employee", self.employee,
			# ~ ["date_of_joining", "relieving_date"])

		# ~ self.get_leave_details(joining_date, relieving_date)
		# ~ struct = self.check_sal_struct(joining_date, relieving_date)

		# ~ if struct:
			# ~ self._salary_structure_doc = frappe.get_doc('Salary Structure', struct)
			# ~ self.salary_slip_based_on_timesheet = self._salary_structure_doc.salary_slip_based_on_timesheet or 0
			# ~ self.set_time_sheet()
			# ~ self.pull_sal_struct()
