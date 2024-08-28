import unittest
import tempfile
import os
from app import app, mask_email, mask_credit_card, mask_sin, mask_phone_number, mask_text_data

class DataMaskingAppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = app.test_client()
        cls.app.testing = True

    def setUp(self):
        """Create a temporary file for each test."""
        self.test_file = tempfile.NamedTemporaryFile(delete=False, mode='w', newline='', encoding='utf-8')
        self.test_file.write('John Doe\nEmail: john.doe@example.com\nCredit Card: 1234 5678 9012 3456\nSSN: 123-45-6789\nPhone: 555-123-4567\n')
        self.test_file.close()  # Close the file so it can be read by Flask

    def tearDown(self):
        """Remove the temporary file after the test."""
        if os.path.exists(self.test_file.name):
            os.remove(self.test_file.name)

    def test_index_page_loads(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Data Masking Application', response.data)

    def test_file_upload_and_masking(self):
        with open(self.test_file.name, 'rb') as file:
            data = {
                'file': (file, 'test.txt'),
                'file_type': 'txt'
            }
            response = self.app.post('/upload', data=data, content_type='multipart/form-data')
            self.assertEqual(response.status_code, 302)  # Adjust based on actual redirection or success status

    def test_mask_email(self):
        self.assertEqual(mask_email('john.doe@example.com'), 'j***@example.com')

    def test_mask_credit_card(self):
        self.assertEqual(mask_credit_card('1234 5678 9012 3456'), '1234 **** **** 3456')

    def test_mask_sin(self):
        self.assertEqual(mask_sin('123-45-6789'), '***-**-6789')

    def test_mask_phone_number(self):
        self.assertEqual(mask_phone_number('555-123-4567'), '555*****4567')

    def test_mask_text(self):
        text = "Email: john.doe@example.com and SSN: 123-45-6789"
        masked_text = mask_text_data(text)
        self.assertIn('Email: j***@example.com', masked_text)
        self.assertIn('SSN: ***-**-6789', masked_text)

if __name__ == '__main__':
    unittest.main()
