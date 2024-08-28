from flask import Flask, render_template, request, redirect, url_for, send_file, session
import os
import csv
import re
# import nltk
# from nltk.tokenize import word_tokenize
# from nltk.corpus import stopwords
from masking import mask_data, mask_email, mask_credit_card, mask_sin, mask_phone_number

# nltk.download('punkt')
# nltk.download('stopwords')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.secret_key = 'your_secret_key'

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# File to store the masked data count
MASKED_COUNT_FILE = 'masked_count.txt'


def get_masked_count():
    """Read the count of masked data samples from a file."""
    if os.path.exists(MASKED_COUNT_FILE):
        with open(MASKED_COUNT_FILE, 'r') as file:
            count = file.read()
            return int(count) if count.isdigit() else 0
    return 0

def increment_masked_count(count):
    """Increment the count of masked data samples and save to a file."""
    with open(MASKED_COUNT_FILE, 'w') as file:
        file.write(str(count))

def mask_text_data(text):
    """Mask sensitive information in the text."""
    # Define regex patterns for sensitive information
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    credit_card_pattern = r'\b(?:\d[ -]*?){13,16}\b'
    sin_pattern = r'\b\d{3}-\d{2}-\d{4}\b'  # Corrected SSN pattern
    phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'  # Improved phone number pattern

    # Mask patterns in text
    text = re.sub(email_pattern, lambda x: mask_email(x.group()), text)
    text = re.sub(credit_card_pattern, lambda x: mask_credit_card(x.group()), text)
    text = re.sub(sin_pattern, lambda x: mask_sin(x.group()), text)
    text = re.sub(phone_pattern, lambda x: mask_phone_number(x.group()), text)

    return text

@app.route('/')
def index():
    # Retrieve masked data from session if available
    masked_data = session.get('masked_data', [])
    masked_text = session.get('masked_text', '')

    # Clear the masked data from session
    session.pop('masked_data', None)
    session.pop('masked_text', None)
    # Get the current masked data count
    masked_count = get_masked_count()
    return render_template('index.html', masked_data=masked_data, masked_text=masked_text, masked_count=masked_count)

@app.route('/upload', methods=['POST'])
def upload_file():
    message = ""
    if 'file' not in request.files:
        message = 'No file part'
        return render_template('index.html', message=message)

    file = request.files['file']
    file_type = request.form.get('file_type', 'csv')

    if file.filename == '':
        message = 'No selected file'
        return render_template('index.html', message=message)

    if file_type == 'csv' and file.filename.endswith('.csv'):
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

        # Update the masked data count
        current_count = get_masked_count()
        new_count = current_count + len(masked_data)
        increment_masked_count(new_count)

        # Store masked data in session
        session['masked_data'] = masked_data
        session['masked_filepath'] = masked_filepath

        return redirect(url_for('index'))

    elif file_type == 'txt' and file.filename.endswith('.txt'):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Process the text file and mask the data
        with open(filepath, 'r') as txtfile:
            text_content = txtfile.read()
            masked_text = mask_text_data(text_content)

        # Save the masked text to a new file
        masked_filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'masked_' + file.filename)
        with open(masked_filepath, 'w') as txtfile:
            txtfile.write(masked_text)

        # Update the masked data count
        current_count = get_masked_count()
        new_count = current_count + len(re.findall(r'\b\d+', text_content))  # Example count based on numbers
        increment_masked_count(new_count)

        # Store masked file path in session
        session['masked_filepath'] = masked_filepath
        session['masked_text'] = masked_text

        return redirect(url_for('index'))

    else:
        message = 'Invalid file format. Please upload a valid CSV or TXT file.'
        return render_template('index.html', message=message)

@app.route('/download')
def download_file():
    masked_filepath = session.get('masked_filepath')
    
    if masked_filepath and os.path.exists(masked_filepath):
        response = send_file(masked_filepath, as_attachment=True, download_name=os.path.basename(masked_filepath))
        return response
    
    return "File not found or has been removed."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
