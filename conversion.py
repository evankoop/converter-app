import csv
import xml.etree.ElementTree as ET
import app as app
from flask import render_template
import os


def extract_element_data(element):
    data = {}
    for child in element:
        if child.tag in data:
            if not isinstance(data[child.tag], list):
                data[child.tag] = [data[child.tag]]
            data[child.tag].append(child.text.strip() if child.text else '')
        else:
            data[child.tag] = child.text.strip() if child.text else ''
    return data


def extract_enrollment_data(employee):
    enrollment_data = []
    enrollments = employee.findall('.//Enrollments/Enrollment')
    for enrollment in enrollments:
        enrollment_data_item = extract_element_data(enrollment)
        all_data = {**enrollment_data_item}
        enrollment_data.append(all_data)

    return enrollment_data


def extract_voluntary_disability_data(employee):
    voluntary_disability_data = []
    voluntary_disabilities = employee.findall('.//VoluntaryDisabilityData')
    for item in voluntary_disabilities:
        voluntary_disability_data.append(extract_element_data(item))
    return voluntary_disability_data


def extract_voluntary_life_data(employee):
    voluntary_life_data = []
    voluntary_life_items = employee.findall('.//VoluntaryLifeData')
    for item in voluntary_life_items:
        voluntary_life_data.append(extract_element_data(item))
    return voluntary_life_data


def remove_redundant_data(all_data):
    filtered_data = []
    for data in all_data:
        if 'Plan' in data:  
            filtered_data.append(data)
    return filtered_data


def xml_to_csv(xml_file, csv_file):
    try:
        print("xml_file:", xml_file)
        print("csv_file:", csv_file)
        tree = ET.parse(xml_file)
        root = tree.getroot()

        all_data = []

        for company in root.iter('Company'):
            company_data = extract_element_data(company)

            employees = company.findall('.//Employee')
            for employee in employees:
                employee_data = extract_element_data(employee)
                employee_enrollments = extract_enrollment_data(employee)
                voluntary_disability_data = extract_voluntary_disability_data(employee)
                voluntary_life_data = extract_voluntary_life_data(employee)

                if not employee_enrollments:
                    all_data.append({**company_data, **employee_data})

                for enrollment_data_item in employee_enrollments:
                    all_data.append({**company_data, **employee_data, **enrollment_data_item})

                for voluntary_disability_item_data in voluntary_disability_data:
                    all_data.append({**employee_data, **voluntary_disability_item_data})

                for voluntary_life_item_data in voluntary_life_data:
                    all_data.append({**employee_data, **voluntary_life_item_data})

        all_data = remove_redundant_data(all_data)

        fieldnames = set()
        for data in all_data:
            fieldnames.update(data.keys())

        column_order = sorted(fieldnames)

        csv_file_path = os.path.splitext(csv_file)[0] + '.csv'

        with open(csv_file_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=column_order)
            writer.writeheader()
            writer.writerows(all_data)
            print('wrote csv file')
        
        return csv_file_path

    except Exception as e:
        app.logger.error('Error during conversion: %s', str(e))
        raise
        
