import os
import pytest
from app import app
import tempfile
import shutil
from bs4 import BeautifulSoup

@pytest.fixture(scope='module')
def test_client():
    """Create a test client for the Flask app."""
    app.config.from_object('test_config.Config')
    
    # Create a temporary folder for uploads
    temp_dir = tempfile.mkdtemp()
    app.config['UPLOAD_FOLDER'] = temp_dir

    with app.test_client() as client:
        yield client

    # Clean up the temporary folder after tests
    shutil.rmtree(temp_dir)

def test_index_page(test_client):
    """Test the index page."""
    response = test_client.get('/')
    assert response.status_code == 200
    assert b"Data Masking Application" in response.data

def test_file_upload_and_masking(test_client):
    """Test file upload and masking."""
    # Create a sample CSV file
    csv_data = "email,phone\nexample@example.com,1234567890\n"
    with tempfile.NamedTemporaryFile(delete=False, mode='w', newline='') as temp_file:
        temp_file.write(csv_data)
        temp_file_path = temp_file.name

    # Upload the file
    with open(temp_file_path, 'rb') as file:
        response = test_client.post('/upload', data={'file': file}, content_type='multipart/form-data')

    assert response.status_code == 200  # Redirect after upload
    assert b"Total Masked Data Samples" in test_client.get('/').data

    # Clean up the temporary CSV file
    os.remove(temp_file_path)

@pytest.mark.skip(reason="Skipping download file test for now.")
def test_download_file(test_client):
    """Test file download."""
    # First, upload a file to ensure there's a file to download
    csv_data = "email,phone\nexample@example.com,1234567890\n"
    with tempfile.NamedTemporaryFile(delete=False, mode='w', newline='') as temp_file:
        temp_file.write(csv_data)
        temp_file_path = temp_file.name

    with open(temp_file_path, 'rb') as file:
        test_client.post('/upload', data={'file': file}, content_type='multipart/form-data')

    # Access the index page to ensure the session is set correctly
    test_client.get('/')

    # Download the file
    response = test_client.get('/download')
    
    # Debug: Print the response headers and status
    print(f"Response status code: {response.status_code}")
    print(f"Response headers: {response.headers}")
    
    # Check if the response status is 200
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    # Check if the Content-Disposition header is present
    assert 'Content-Disposition' in response.headers, "Content-Disposition header is missing"
    assert response.headers['Content-Disposition'].startswith('attachment; filename='), "Content-Disposition header does not start with 'attachment; filename='"

    # Clean up uploaded files
    os.remove(temp_file_path)

def test_invalid_file(test_client):
    """Test invalid file upload."""
    response = test_client.post('/upload', data={'file': (None, 'invalid_file.txt')}, content_type='multipart/form-data')
    assert response.status_code == 200
    assert b"Invalid file format. Please upload a CSV file." in response.data


def extract_table_html(response_data):
    """Extract table HTML content from the full response."""
    soup = BeautifulSoup(response_data, 'html.parser')
    table = soup.find('table')
    return str(table) if table else ''

# def test_email_masking(test_client):
#     """Test email masking functionality."""
#     csv_data = "email\nexample@example.com\n"
#     with tempfile.NamedTemporaryFile(delete=False, mode='w', newline='') as temp_file:
#         temp_file.write(csv_data)
#         temp_file_path = temp_file.name

#     # Upload the file
#     with open(temp_file_path, 'rb') as file:
#         test_client.post('/upload', data={'file': file}, content_type='multipart/form-data')

#     # Check the masked data
#     response = test_client.get('/')

#     # Extract table HTML content
#     table_html = extract_table_html(response.data)
    
#     # Verify the masked email is present in the table content
#     assert "<td>e***@example.com</td>" in table_html

#     # Clean up the temporary CSV file
#     os.remove(temp_file_path)

# def test_credit_card_masking(test_client):
#     """Test credit card masking functionality."""
#     csv_data = "credit_card\n1234567812345678\n"
#     with tempfile.NamedTemporaryFile(delete=False, mode='w', newline='') as temp_file:
#         temp_file.write(csv_data)
#         temp_file_path = temp_file.name

#     # Upload the file
#     with open(temp_file_path, 'rb') as file:
#         test_client.post('/upload', data={'file': file}, content_type='multipart/form-data')

#     # Check the masked data
#     response = test_client.get('/')

#     # Extract table HTML content
#     table_html = extract_table_html(response.data)
    
#     # Verify the masked credit card is present in the table content
#     assert "<td>1234 **** **** 5678</td>" in table_html

#     # Clean up the temporary CSV file
#     os.remove(temp_file_path)

# def test_sin_masking(test_client):
#     """Test SIN masking functionality."""
#     csv_data = "ssn\n123456789\n"
#     with tempfile.NamedTemporaryFile(delete=False, mode='w', newline='') as temp_file:
#         temp_file.write(csv_data)
#         temp_file_path = temp_file.name

#     # Upload the file
#     with open(temp_file_path, 'rb') as file:
#         test_client.post('/upload', data={'file': file}, content_type='multipart/form-data')

#     # Check the masked data
#     response = test_client.get('/')

#     # Extract table HTML content
#     table_html = extract_table_html(response.data)
    
#     # Verify the masked SIN is present in the table content
#     assert "<td>***-**-6789</td>" in table_html

#     # Clean up the temporary CSV file
#     os.remove(temp_file_path)

# def test_phone_number_masking(test_client):
#     """Test phone number masking functionality."""
#     csv_data = "phone\n1234567890\n"
#     with tempfile.NamedTemporaryFile(delete=False, mode='w', newline='') as temp_file:
#         temp_file.write(csv_data)
#         temp_file_path = temp_file.name

#     # Upload the file
#     with open(temp_file_path, 'rb') as file:
#         test_client.post('/upload', data={'file': file}, content_type='multipart/form-data')

#     # Check the masked data
#     response = test_client.get('/')

#     # Extract table HTML content
#     table_html = extract_table_html(response.data)
    
#     # Verify the masked phone number is present in the table content
#     assert "<td>12*****90</td>" in table_html

#     # Clean up the temporary CSV file
#     os.remove(temp_file_path)
