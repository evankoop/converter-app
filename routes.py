from flask import Blueprint, request, render_template, send_file, current_app, url_for, send_from_directory
import os
from conversion import xml_to_csv
import datetime

print('test')

upload_routes = Blueprint('uploads', __name__)

print('After upload routes')

@upload_routes.route('/', methods=['GET', 'POST'])
def upload_file():
    csv_generated = False
    csv_file = None
    csv_file_url = None
    error_message = None  # Define the error_message variable

    if request.method == 'POST':
        uploaded_file = request.files['file']

        if uploaded_file:
            current_datetime = datetime.datetime.now().strftime('%Y-%m-%d')
            csv_filename = f'{current_datetime}_employee.csv'
            csv_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], csv_filename)
            xml_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], uploaded_file.filename)
            uploaded_file.save(xml_filepath)

            try:
                csv_filepath = xml_to_csv(xml_filepath, csv_file_path)
                print("csv_filepath:", csv_filepath)
                if os.path.exists(csv_filepath):
                  print('check two')
                  os.rename(csv_filepath, csv_file_path)
                  print('check three')   
                  csv_generated = True  
                  csv_file = csv_file_path  
                  csv_file_url = url_for('uploads.download_csv', filename=csv_filename)
                  
                
            except Exception as e:
                # Handle the exception silently, without displaying to users
                current_app.logger.error("Error during conversion: %s", str(e))

                # Set user-friendly error message
                csv_generated = False
                error_message = "An error occurred during conversion. Please try again later."

    return render_template('index.html', csv_generated=csv_generated, csv_file=csv_file, csv_file_url=csv_file_url, error_message=error_message)



@upload_routes.route('/download/<filename>')
def download_csv(filename):
        return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename, as_attachment=True)



    