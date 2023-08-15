import csv
import xml.etree.ElementTree as ET
import app as app
import os

def extract_element_data(element):
    data = {}
    for child in element:
        data[child.tag] = child.text.strip() if child.text else ''
    return data

def extract_class_data(company):
    class_data = []
    classes = company.findall('.//Classes/Class')
    for i, class_elem in enumerate(classes, start=1):
        class_data.append(extract_element_data(class_elem))

    return class_data

def extract_payroll_group_data(company):
    payroll_group_data = []
    payroll_groups = company.findall('.//PayrollGroups/PayrollGroup')
    for i, payroll_group in enumerate(payroll_groups, start=1):
        payroll_group_data.append(extract_element_data(payroll_group))

    return payroll_group_data

def extract_plan_data(company):
    plan_data = []
    plans = company.findall('.//Plans/Plan')
    for i, plan in enumerate(plans, start=1):
        plan_data.append(extract_element_data(plan))

    return plan_data

def c_xml_to_csv(xml_file, csv_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        all_data = [] 

        
        for company in root.iter('Company'):
            company_data = extract_element_data(company)

            class_data = extract_class_data(company)
            for class_row in class_data:
                company_with_class_data = {**company_data, **class_row}

                payroll_group_data = extract_payroll_group_data(company)
                for payroll_group_row in payroll_group_data:
                    company_with_payroll_group_data = {**company_with_class_data, **payroll_group_row}

                    plan_data = extract_plan_data(company)
                    for plan_row in plan_data:
                        all_data.append({**company_with_payroll_group_data, **plan_row})

        fieldnames = set()
        for data in all_data:
            fieldnames.update(data.keys())

        column_order = sorted(fieldnames)

        c_csv_file_path = os.path.splitext(csv_file)[0] + '.csv'

        with open(c_csv_file_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=column_order)
            writer.writeheader()
            writer.writerows(all_data)
        
        return c_csv_file_path
    
    except Exception as e:
        app.logger.error('Error during conversion: %s', str(e))
        raise


# xml_file_path = 'Data_API_20230809_152251_9872 (1).xml'
# csv_file_path = 'largest_companies_test.csv'
# xml_to_csv(xml_file_path, csv_file_path)