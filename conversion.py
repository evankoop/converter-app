import csv
import xml.etree.ElementTree as ET
import app as app
import os
import logging

logging.basicConfig(level=logging.ERROR)


def extract_element_data(element, data=None, excluded_tags=None):
    if data is None:
        data = {}
    
    if excluded_tags is None:
        excluded_tags = set()
    
    current_data = {}

    for child in element:
        if child.tag in excluded_tags:
            continue
        if len(child) > 0:
            child_rows = extract_element_data(child, excluded_tags=excluded_tags)
            if child_rows:
                expanded_rows = []
                for row in child_rows:
                    expanded_row = {**data, **current_data, **row}
                    expanded_rows.append(expanded_row)
                return expanded_rows
        else:
            current_data[child.tag] = child.text.strip() if child.text else ''
    if current_data:
        return [{**data, **current_data}]
    else:
        return []
    
def extract_contact_info(element):
    contact_data = {}

    email_addresses = element.find('.//EmailAddresses')
    if email_addresses:
        for email in email_addresses:
            contact_data[email.tag] = email.text.strip() if email.text else ''
    
    phones = element.find('.//Phones')
    if phones:
        for phone in phones:
            contact_data[phone.tag] = phone.text.strip() if phone.text else ''
    
    return contact_data

def process_company(company):
    default_emp_data = {
        'BusinessUnit':'',
        'Class':'',
        'Department':'',
        'Division':'',
        'Office':'',
        'PayrollGroup':'',
        'Suffix':'',
        'TerminatedOn':'',
        'TerminationReason':''
    }
    company_data = extract_element_data(company, excluded_tags={'Beneficiary', 'Contacts', 'Classes', 'Departments', 'Divisions', 'Offices', 'BusinessUnits', 'PayrollGroups', 'Plans', 'JobClassifications', 'DependentEnrollees', 'Enrollee', 'Riders', 'Rider'})

    employees = company.findall('.//Employee')

    rows = []

    for employee in employees:
        current_emp_data = default_emp_data.copy()

        employee_data = extract_element_data(employee, excluded_tags={'Beneficiary'})

        contact_info = extract_contact_info(employee)

        enrollments = employee.findall('.//Enrollments/Enrollment')

        if not enrollments:
            for row in employee_data:
                rows.append({**company_data[0], **current_emp_data, **row, **contact_info})
        else:
            for enrollment in enrollments:
                enrollment_data = extract_element_data(enrollment, excluded_tags={'Beneficiary', 'DependentEnrollees', 'Riders', 'Rider'})

                for emp_row in employee_data:
                    for enroll_row in enrollment_data:
                        combined_data = {**company_data[0], **current_emp_data, **emp_row, **enroll_row, **contact_info}
                        rows.append(combined_data)
    return rows

def process_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    all_rows = []

    for company in root.findall('.//Company'):
        company_rows = process_company(company)
        all_rows.extend(company_rows)
    return all_rows

def write_to_csv(data, csv_file):
    fieldnames = set()
    
    for row in data:
        fieldnames.update(row.keys())
    
    column_order = sorted(fieldnames)

    csv_file_path = os.path.splitext(csv_file)[0] + '.csv'

    with open(csv_file_path, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=column_order)
        writer.writeheader()
        writer.writerows(data)
    
    return csv_file_path

def xml_to_csv(xml_file, csv_file):
    try:
        data = process_xml(xml_file)
        write_to_csv(data, csv_file)

        print('wrote to csv')

    except Exception as e:
        logging.error('Error during conversion: %s', str(e))
        raise