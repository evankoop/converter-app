import csv
import xml.etree.ElementTree as ET
import app as app
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
        data.update(extract_element_data(child))
    return data

def extract_employee_data(employee):
    employee_data = extract_element_data(employee)
    return employee_data


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

def extract_hsa_data(employee):
    hsa_data = []
    hsa_data_items = employee.findall('.//HSAData')
    for item in hsa_data_items:
        hsa_data.append(extract_element_data(item))
    return hsa_data

def extract_cafeteria_data(employee):
    cafeteria_data = []
    cafeteria_data_items = employee.findall('.//CafeteriaData')
    for item in cafeteria_data_items:
        cafeteria_data.append(extract_element_data(item))
    return cafeteria_data


def xml_to_csv(xml_file, csv_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        all_data = []

        for company in root.iter('Company'):
            company_data = extract_element_data(company)

            employees = company.findall('.//Employee')
            for employee in employees:
                employee_data = extract_employee_data(employee)
                employee_enrollments = extract_enrollment_data(employee)
                voluntary_disability_data = extract_voluntary_disability_data(employee)
                voluntary_life_data = extract_voluntary_life_data(employee)
                hsa_data = extract_hsa_data(employee)
                cafeteria_data = extract_cafeteria_data(employee)

                voluntary_disability_benefits = ['Voluntary Short-Term Disability', 'Voluntary Long-Term Disability', 'Short-Term Disability', 'Long-Term Disability']

                voluntary_life_benefits = ['Voluntary AD&D', 'Voluntary Life', 'Life', 'AD&D', 'Critical Illness']

                cafeteria_benefits = ['Flexible Spending Account', 'Dependent Care Spending Account', 'Limited Purpose FSA']

                if not employee_enrollments:
                    all_data.append({**company_data, **employee_data})
                else:
                    for enrollment_data_item in employee_enrollments:

                        combined_data = {**company_data, **employee_data, **enrollment_data_item}
                        
                        if voluntary_disability_data and enrollment_data_item.get('Benefit') in voluntary_disability_benefits:
                            combined_data.update(voluntary_disability_data[0])

                        if voluntary_life_data and enrollment_data_item.get('Benefit') in voluntary_life_benefits:
                            combined_data.update(voluntary_life_data[0])

                        if hsa_data and enrollment_data_item.get('Benefit') == 'Consumer Directed Health':
                            combined_data.update(hsa_data[0])

                        if cafeteria_data and enrollment_data_item.get('Benefit') in cafeteria_benefits:
                            combined_data.update(cafeteria_data[0])

                        all_data.append(combined_data)

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
        
