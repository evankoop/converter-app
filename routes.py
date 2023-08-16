from flask import Blueprint, request, render_template, send_file, current_app, url_for, send_from_directory
import os
from conversion import xml_to_csv
from dependent import d_xml_to_csv
from company import c_xml_to_csv
import datetime

upload_routes = Blueprint('uploads', __name__)

@upload_routes.route('/', methods=['GET', 'POST'])
def upload_file():
    csv_generated = False
    d_csv_generated = False
    c_csv_generated = False
    csv_file = None
    csv_file_url = None
    d_csv_file_url = None
    c_csv_file_url = None
    error_message = None 

    if request.method == 'POST':
        uploaded_file = request.files['file']

        if 'employee_data' in request.form:
            current_datetime = datetime.datetime.now().strftime('%Y-%m-%d')
            csv_filename = f'{current_datetime}_employee.csv'
            csv_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], csv_filename)
            xml_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], uploaded_file.filename)
            uploaded_file.save(xml_filepath)

            try:
                csv_filepath = xml_to_csv(xml_filepath, csv_file_path)
                if os.path.exists(csv_filepath):
                  os.rename(csv_filepath, csv_file_path)   
                  csv_generated = True  
                  csv_file = csv_file_path  
                  csv_file_url = url_for('uploads.download_csv', filename=csv_filename)
                
            except Exception as e:
                current_app.logger.error("Error during conversion: %s", str(e))
                csv_generated = False
                error_message = "An error occurred during conversion. Please try again later."


        elif 'dependent_data' in request.form:
            current_datetime = datetime.datetime.now().strftime('%Y-%m-%d') 
            d_csv_filename = f'{current_datetime}_dependent.csv'
            d_csv_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], d_csv_filename) 
            d_xml_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], uploaded_file.filename)
            uploaded_file.save(d_xml_filepath)
            d_csv_filepath = None

            try:
                d_csv_filepath = d_xml_to_csv(d_xml_filepath, d_csv_file_path)
                if os.path.exists(d_csv_filepath):
                    os.rename(d_csv_filepath, d_csv_file_path)
                    d_csv_generated = True
                    csv_file = d_csv_file_path
                    d_csv_file_url = url_for('uploads.download_csv', filename=d_csv_filename)
            
            except Exception as e:
                current_app.logger.error("Error during conversion: %s", str(e))
                d_csv_generated = False
                error_message = "An error occurred during conversion. Please try again later."
        
        elif 'company_data' in request.form:
            current_datetime = datetime.datetime.now().strftime('%Y-%m-%d')
            c_csv_filename = f'{current_datetime}_company.csv'
            c_csv_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], c_csv_filename) 
            c_xml_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], uploaded_file.filename)
            uploaded_file.save(c_xml_filepath)
            c_csv_filepath = None

            try:
                c_csv_filepath = c_xml_to_csv(c_xml_filepath, c_csv_file_path)
                if os.path.exists(c_csv_filepath):
                   os.rename(c_csv_filepath, c_csv_file_path) 
                   c_csv_generated = True
                   csv_file = c_csv_file_path
                   c_csv_file_url = url_for('uploads.download_csv', filename=c_csv_filename)

            except Exception as e:
                current_app.logger.error("Error during conversion: %s", str(e))
                c_csv_generated = False
                error_message = "An error occured during conversion. Please try again later."
    
                 
    return render_template('index.html', csv_generated=csv_generated, d_csv_generated=d_csv_generated, c_csv_generated=c_csv_generated, csv_file=csv_file, csv_file_url=csv_file_url, c_csv_file_url=c_csv_file_url, d_csv_file_url=d_csv_file_url, error_message=error_message)



@upload_routes.route('/download/<filename>')
def download_csv(filename):
        return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename, as_attachment=True)



    