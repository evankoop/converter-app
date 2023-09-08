import csv
import xml.etree.ElementTree as ET
import app as app
import os

def extract_element_data(element):
    data = {}
    for child in element:
        data[child.tag] = child.text.strip() if child.text else ''
    return data


def extract_dependent_data(employee):
    dependent_data = []
    dependents = employee.findall('.//Dependent')
    for dependent in dependents:
        dependent_data.append(extract_element_data(dependent))
    return dependent_data


def extract_enrollment_data(employee, dependent_data):
    enrollment_data = []
    enrollments = employee.findall('.//Enrollments/Enrollment')
    for enrollment in enrollments:
        enrollment_data_item = extract_element_data(enrollment)
        dependent_enrollees = enrollment.findall('.//DependentEnrollees/Enrollee')
        for dependent_enrollee in dependent_enrollees:
            dependent_enrollee_data = extract_element_data(dependent_enrollee)
            dependent_index = int(dependent_enrollee.findtext('.//SequenceNumber')) - 1
            if 0 <= dependent_index < len(dependent_data):
                dependent = dependent_data[dependent_index]
                all_data = {**enrollment_data_item, **dependent_enrollee_data, **dependent}
                all_data['SSN_Dependent'] = dependent.get('SSN', '')
                all_data['Relationship'] = dependent.get('Relationship', '')
                all_data['SSN_Employee'] = employee.findtext('.//SSN')
                enrollment_data.append(all_data)

    return enrollment_data


def d_xml_to_csv(xml_file, csv_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        all_data = []  

        for company in root.iter('Company'):
            employees = company.findall('.//Employee')
            for employee in employees:
                dependent_data = extract_dependent_data(employee)
                dependent_enrollments = extract_enrollment_data(employee, dependent_data)
                all_data.extend(dependent_enrollments)

        fieldnames = set()
        for data in all_data:
            fieldnames.update(data.keys())

        column_order = sorted(fieldnames)

        d_csv_file_path = os.path.splitext(csv_file)[0] + '.csv'

        with open(d_csv_file_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=column_order)
            writer.writeheader()
            writer.writerows(all_data)

        return d_csv_file_path
    
    except Exception as e:
        app.logger.error('Error during conversion: %s', str(e))
        raise

