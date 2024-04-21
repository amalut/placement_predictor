import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import pickle
import numpy as np
from recommendation import recommend_for_student

# Define the recommendation function


# Load the data
data = pd.read_csv('placement.csv')

# No need to one-hot encode 'Stream' column if not using it as a predictor
stream_dummies = pd.get_dummies(data['Stream'], prefix='Stream')

# Select predictor variables
predictors = data[['Cgpa', 'Communication', 'Aptitude', 'Internships']].join(stream_dummies)

# Target variable
target = data['PlacedOrNot']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(predictors, target, test_size=0.2, random_state=42)

# Create a logistic regression model
model = LogisticRegression(max_iter=1000)

# Train the model
model.fit(X_train, y_train)

# Make predictions on the testing set
predictions = model.predict(X_test)

# Evaluate the model
print("Accuracy:", accuracy_score(y_test, predictions))
print("\nConfusion Matrix:\n", confusion_matrix(y_test, predictions))
print("\nClassification Report:\n", classification_report(y_test, predictions))

# Save the trained model to a file
pickle.dump(model, open('model.pkl', 'wb'))

# Calculate the average values of the predictors from the training data
average_values = {
    'Cgpa': X_train['Cgpa'].mean(),
    'Communication': X_train['Communication'].mean(),
    'Aptitude': X_train['Aptitude'].mean(),
    'Internships': X_train['Internships'].mean()
}

# Predict the placement of a new student
new_student_stream = 'Information Technology'  # Replace with the correct stream
new_student_stream_dummy = stream_dummies.loc[stream_dummies[f'Stream_{new_student_stream}'] == 1].values.tolist()[0]
new_student_features = [7.5, 7, 5, 2] + new_student_stream_dummy  # Add the stream dummy variables

prediction = model.predict([new_student_features])
probability_new_student = model.predict_proba([new_student_features])[0][1]

# Call the recommendation function
recommendations = recommend_for_student(probability_new_student,new_student_features, average_values)
print("Predicted placement:", prediction[0])
print("Predicted probability of getting placed:", probability_new_student * 100, "%")
print(type(recommendations))
for recommendation in recommendations:
    print(recommendation)
