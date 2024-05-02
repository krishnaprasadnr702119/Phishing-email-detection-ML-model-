import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# Path to the dataset
dataset_file = 'Phishing_Email.csv'  

# Load the dataset
mail_data = pd.read_csv(dataset_file)
mail_data = mail_data.dropna() 

# Encode 'Safe Email' as 0 and 'Phishing Email' as 1
mail_data.loc[mail_data['Email Type'] == 'Safe Email', 'Email Type'] = 0
mail_data.loc[mail_data['Email Type'] == 'Phishing Email', 'Email Type'] = 1

# Split data into training and testing sets
X = mail_data['Email Text']
Y = mail_data['Email Type']
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=3)

# Feature extraction using TfidfVectorizer
feature_extraction = TfidfVectorizer(min_df=1, stop_words='english', lowercase=True)
X_train_features = feature_extraction.fit_transform(X_train)
X_test_features = feature_extraction.transform(X_test)

# Convert Y_train and Y_test values to integers
Y_train = Y_train.astype(int)
Y_test = Y_test.astype(int)

# Train the logistic regression model
model = LogisticRegression()
model.fit(X_train_features, Y_train)

# Evaluate the model
training_accuracy = accuracy_score(Y_train, model.predict(X_train_features))
test_accuracy = accuracy_score(Y_test, model.predict(X_test_features))
print(f"Training Accuracy: {training_accuracy}")
print(f"Test Accuracy: {test_accuracy}")

# Save the trained model
joblib.dump(model, 'phishing-model.joblib')

# Save the fitted TfidfVectorizer instance
joblib.dump(feature_extraction, 'tfidf-vectorizer.joblib')
