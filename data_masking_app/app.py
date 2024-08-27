from flask import Flask, render_template, request, redirect, url_for, send_file, session
import os
import csv
from masking import mask_data

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.secret_key = 'your_secret_key'

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    # Retrieve masked data from session if available
    masked_data = session.get('masked_data', [])
    # Clear the masked data from session
    session.pop('masked_data', None)
    session.pop('masked_filepath', None)
    return render_template('index.html', masked_data=masked_data)

@app.route('/upload', methods=['POST'])
def upload_file():
    message = ""
    if 'file' not in request.files:
        message = 'No file part'
        return render_template('index.html', message=message)

    file = request.files['file']

    if file.filename == '':
        message = 'No selected file'
        return render_template('index.html', message=message)

    if file and file.filename.endswith('.csv'):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Process the CSV file and mask the data
        masked_data = []
        with open(filepath, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                masked_row = mask_data(row)
                masked_data.append(masked_row)

        # Save the masked data to a new file
        masked_filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'masked_' + file.filename)
        with open(masked_filepath, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=masked_data[0].keys())
            writer.writeheader()
            writer.writerows(masked_data)

        # Store masked data in session
        session['masked_data'] = masked_data
        session['masked_filepath'] = masked_filepath

        return redirect(url_for('index'))  # Redirect to the index page

    else:
        message = 'Invalid file format. Please upload a CSV file.'
        return render_template('index.html', message=message)

@app.route('/download')
def download_file():
    masked_filepath = session.get('masked_filepath')
    if masked_filepath and os.path.exists(masked_filepath):
        return send_file(masked_filepath, as_attachment=True)
    return "File not found or has been removed."

if __name__ == '__main__':
    app.run(debug=True)
