import pandas as pd

def load_business_data(file_path: str):
    """
    Load business dataset from CSV
    """
    data = pd.read_csv(file_path)

    print("\nData Loaded")
    print("Rows:", data.shape[0])
    print("Columns:", data.shape[1])

    return data