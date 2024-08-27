import pandas as pd


def validate_csv(filepath):
    try:
        df = pd.read_csv(filepath)

        if df.empty:
            return False, "CSV file is empty"

        # Define column keywords for sensitive data
        sensitive_data_keywords = ['email', 'phone', 'contact']

        # Check if any of the sensitive data keywords are present in the columns
        columns = df.columns.str.lower()  # Normalize column names to lowercase for comparison
        if not any(keyword in columns for keyword in sensitive_data_keywords):
            return False, "CSV file does not contain required columns for sensitive data"

        return True, ""

    except Exception as e:
        return False, str(e)

