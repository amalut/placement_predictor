import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import pickle

# Load the data
data = pd.read_csv('placement.csv')

# Encode the 'Stream' column using one-hot encoding
stream_dummies = pd.get_dummies(data['Stream'], prefix='Stream')
#stream_dummies.to_csv('stream_dummies1.csv', index=False)


# Add the encoded 'Stream' column to the predictors
predictors = data[['Cgpa','Communication','Aptitude','Internships']].join(stream_dummies)
target = data['PlacedOrNot']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(predictors, target, test_size=0.2, random_state=42)

# Create an XGBoost model
model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')

# Train the model
model.fit(X_train, y_train)

# Make predictions on the testing set
predictions = model.predict(X_test)

# Evaluate the model
print("Accuracy:", accuracy_score(y_test, predictions))
print("\nConfusion Matrix:\n", confusion_matrix(y_test, predictions))
print("\nClassification Report:\n", classification_report(y_test, predictions))

pickle.dump(model,open('xgbmodel.pkl','wb'))

# Predict the placement of a new student
new_student_stream = 'Civil'  # Replace with the correct stream
new_student_stream_dummy = stream_dummies.loc[stream_dummies[f'Stream_{new_student_stream}'] == 1].values.tolist()[0]
print(new_student_stream_dummy)
new_student_features = [8, 6, 7, 1] + new_student_stream_dummy  # Add the stream dummy variables
new_student_features = [new_student_features]  # Convert to a 2D array

prediction = model.predict(new_student_features)
probability_new_student = model.predict_proba(new_student_features)
print("Predicted placement:", prediction[0])
print("Predicted probability of getting placed:", probability_new_student[0][1] * 100)