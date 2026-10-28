"""
data_preprocessing.py - Data loading, cleaning, split, and pipeline for customer churn.
"""
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from config import DATA_PATH, TARGET, SEED, BINARY_COLS, NOMINAL_COLS, NUMERIC_COLS

def load_data(path=DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    df['TotalCharges_clean'] = pd.to_numeric(df['TotalCharges'].replace(' ', '0'), errors='coerce').fillna(0.0)
    df['Churn_binary'] = (df['Churn'] == 'Yes').astype(int)
    return df

def feature_columns(setting="A"):
    if setting == "A":
        # All features including contract, services and billing
        return NUMERIC_COLS + BINARY_COLS + NOMINAL_COLS
    else:
        # Setting B: No contract or tenure (early warning using demographics & basic service)
        return ["MonthlyCharges"] + BINARY_COLS + ["InternetService", "PhoneService"]

def split_data(df: pd.DataFrame, seed=SEED, val_size=0.15, test_size=0.15):
    X = df.drop(columns=['customerID', 'Churn', 'Churn_binary'])
    y = df['Churn_binary'].values
    
    X_tr, X_tmp, y_tr, y_tmp = train_test_split(X, y, test_size=val_size + test_size, stratify=y, random_state=seed)
    X_val, X_te, y_val, y_te = train_test_split(X_tmp, y_tmp, test_size=test_size / (val_size + test_size), stratify=y_tmp, random_state=seed)
    return X_tr, X_val, X_te, y_tr, y_val, y_te

