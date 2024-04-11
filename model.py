import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import pickle

# Load the data
data = pd.read_csv('placement.csv')
print(data.head(10))
print("\n")

# No need to one-hot encode 'Stream' column if not using it as a predictor
stream_dummies = pd.get_dummies(data['Stream'], prefix='Stream')
#stream_dummies.to_csv('stream_dummies1.csv', index=False)

# Select predictor variables
predictors = data[['Cgpa', 'Communication', 'Aptitude', 'Internships']].join(stream_dummies)

# Target variable
target = data['PlacedOrNot']
print(predictors.head(10))

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

# Predict the placement of a new student
new_student_stream = 'Information Technology'  # Replace with the correct stream
new_student_stream_dummy = stream_dummies.loc[stream_dummies[f'Stream_{new_student_stream}'] == 1].values.tolist()[0]
print(new_student_stream_dummy)
new_student_features = [8, 8, 2.4, 1] + new_student_stream_dummy  # Add the stream dummy variables
new_student_features = [new_student_features]  # Convert to a 2D array

prediction = model.predict(new_student_features)
probability_new_student = model.predict_proba(new_student_features)
print("Predicted placement:", prediction[0])
print("Predicted probability of getting placed:", probability_new_student[0][1] * 100)
