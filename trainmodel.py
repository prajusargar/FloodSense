# Library Imports
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import f1_score, recall_score, precision_score, accuracy_score, confusion_matrix
import joblib
import json


# Step 1: Read Dataset
data = pd.read_csv('flood.csv')  # Adjust the file path as per your dataset location

# Step 1.1: Keep Selected Features
selected_features = [
    'MonsoonIntensity', 'TopographyDrainage', 'RiverManagement', 'ClimateChange', 
    'Siltation', 'DrainageSystems', 'CoastalVulnerability', 'Watersheds', 
    'DeterioratingInfrastructure', 'WetlandLoss', 'FloodProbability'
]
data = data[selected_features]

# data.head(5)

# Step 1.2: Print Min, Max, Mean, Mode, and Median for Each Column
stats = {}
for column in data.columns:
    stats[column] = {
        'min': data[column].min(),
        'max': data[column].max(),
        'mean': data[column].mean(),
        'mode': data[column].mode()[0] if not data[column].mode().empty else None,
        'median': data[column].median()
    }

# Display stats
for column, stat_values in stats.items():
    print(f"{column}:")
    print(f"\t\t\t\tMin: {stat_values['min']} \t Max: {stat_values['max']} \t Mean: {stat_values['mean']}")


#     print(f"  Mode: {stat_values['mode']}")
#     print(f"  Median: {stat_values['median']}")
    print()


# Step 2: Dataset Preprocessing
# Check for missing values
if data.isnull().sum().any():
    # Optionally remove rows with missing values or fill them
    data = data.fillna(data.mean())  # Filling missing values with column mean


# Step 3: Define Features and Target
X = data.drop('FloodProbability', axis=1)  # Features (independent variables)
y = data['FloodProbability']  # Target (dependent variable)



# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)



# Step 4: Declare and Configure Model
# Initialize Random Forest Regressor
rf_model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)



# Step 5: Train the Model
rf_model.fit(X_train, y_train)



import pickle

# Step 6: Save Model and Feature Names using `pickle`
with open("random_forest_flood_model.pkl", "wb") as model_file:
    pickle.dump(rf_model, model_file)  # Saving model

with open("feature_names.pkl", "wb") as feature_file:
    pickle.dump(X.columns.tolist(), feature_file)  # Saving feature names





# Step 8: Test Model Accuracy
y_pred = rf_model.predict(X_test)

# Converting both continuous predictions and true values to binary for classification metrics
y_pred_binary = [1 if x >= 0.5 else 0 for x in y_pred]  # Thresholding predictions
y_test_binary = [1 if x >= 0.5 else 0 for x in y_test]  # Thresholding true values

# Metrics Calculation
f1 = f1_score(y_test_binary, y_pred_binary)
recall = recall_score(y_test_binary, y_pred_binary)
precision = precision_score(y_test_binary, y_pred_binary)
accuracy = accuracy_score(y_test_binary, y_pred_binary)

# Confusion Matrix to calculate specificity
tn, fp, fn, tp = confusion_matrix(y_test_binary, y_pred_binary).ravel()
specificity = tn / (tn + fp)

# Print out the scores
print(f"F1 Score: \t{round(f1, 2)}")
print(f"Recall:   \t{round(recall, 2)}")
print(f"Precision:\t{round(precision, 2)}")
print(f"Accuracy: \t{round(accuracy, 3)}")
print(f"Specificity: \t{round(specificity, 2)}")


from sklearn.metrics import mean_squared_error, r2_score

# Calculate regression metrics
mse = mean_squared_error(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred, squared=False)  # RMSE is the square root of MSE
r2 = r2_score(y_test, y_pred)

print(f"MSE: \t\t{round(mse, 2)}")
print(f"RMSE: \t\t{round(rmse, 2)}")
print(f"R² Score: \t{round(r2, 2)}")




# Step 7: Test the Model with Custom Input
# Assume Custom Input as JSON
custom_input = {
    'MonsoonIntensity': 3, 'TopographyDrainage': 5, 'RiverManagement': 7, 'ClimateChange': 4, 'Siltation': 3,
    'DrainageSystems': 8, 'CoastalVulnerability': 7, 'Watersheds': 5, 'DeterioratingInfrastructure': 4,
    'WetlandLoss': 2
}

# Convert JSON input to a DataFrame for model input
custom_df = pd.DataFrame([custom_input])

# Load the model and predict using `pickle`
with open("random_forest_flood_model.pkl", "rb") as model_file:
    rf_loaded_model = pickle.load(model_file)

prediction = rf_loaded_model.predict(custom_df)
print(f"Flood Probability Prediction for Custom Input: {round(prediction[0]* 100, 2)} %")
