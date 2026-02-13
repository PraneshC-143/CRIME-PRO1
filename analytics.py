import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


def load_data(file_path):
    """Load dataset from a CSV file."""
    return pd.read_csv(file_path)


def preprocess_data(data):
    """Preprocess the data by handling missing values and encoding categorical features."""
    data = data.dropna()  # Simple missing value handling
    return pd.get_dummies(data)  # Encoding categorical variables


def train_model(X, y):
    """Train a Random Forest model."""
    model = RandomForestClassifier()  
    model.fit(X, y)
    return model


def evaluate_model(model, X_test, y_test):
    """Evaluate the model and return the accuracy score."""
    predictions = model.predict(X_test)
    return accuracy_score(y_test, predictions)  


# Example usage (Uncomment to use)
# if __name__ == '__main__':
#     data = load_data('data.csv')
#     processed_data = preprocess_data(data)
#     X = processed_data.drop('target', axis=1)
#     y = processed_data['target']
#     X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
#     model = train_model(X_train, y_train)
#     accuracy = evaluate_model(model, X_test, y_test)
#     print(f'Model Accuracy: {accuracy}')