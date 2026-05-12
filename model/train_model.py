import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib
import os

# Load Dataset
data = pd.read_csv('dataset/creditcard.csv')

# Remove Missing Values
data = data.dropna()

# Features and Target
X = data.drop('Class', axis=1)
y = data['Class']

# Split Dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Train Model
model = RandomForestClassifier(n_estimators=50)

model.fit(X_train, y_train)

# Predictions
predictions = model.predict(X_test)

# Accuracy
accuracy = accuracy_score(y_test, predictions)

print(f"Accuracy: {accuracy * 100:.2f}%")

# Create Folder if Not Exists
os.makedirs("trained_model", exist_ok=True)

# Save Model
joblib.dump(model, 'trained_model/fraud_model.pkl')

print("Model Saved Successfully")