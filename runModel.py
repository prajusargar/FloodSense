# Library Imports
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import f1_score, recall_score, precision_score, accuracy_score, confusion_matrix
import pickle, json, time

# Step 9: Inference Code for Custom Data Prediction
def predict_flood_probability(custom_json: dict) -> float:
    """
    Load the model and predict flood probability for custom input data.

    Args:
        custom_json (dict): A dictionary containing the values of all the flood prediction factors.

    Returns:
        float: Predicted flood probability.
    """
    # Load the saved model and feature names using `pickle`
    with open("random_forest_flood_model.pkl", "rb") as model_file:
        model = pickle.load(model_file)

    with open("feature_names.pkl", "rb") as feature_file:
        feature_names = pickle.load(feature_file)

    # Convert JSON input to DataFrame for prediction
    custom_data = pd.DataFrame([custom_json], columns=feature_names)

    # Make prediction
    return round((model.predict(custom_data)[0]) * 100, 2)


# Example usage of the inference function:
custom_input = {
    'MonsoonIntensity': 3, 'TopographyDrainage': 5, 'RiverManagement': 7, 'ClimateChange': 4, 'Siltation': 3,
    'DrainageSystems': 8, 'CoastalVulnerability': 7, 'Watersheds': 5, 'DeterioratingInfrastructure': 4,
    'WetlandLoss': 2
}

start_time = time.time()

# Predict flood probability for custom input
flood_probability = predict_flood_probability(custom_input)
print(f"Predicted Flood Probability for Example Input: {flood_probability} %")

end_time = time.time()

# Calculate elapsed time
elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time:.2f} seconds")