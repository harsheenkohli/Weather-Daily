"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""


import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Load and label the data


def load_data():
    with open('./assets/human_chat.txt', 'r', encoding='utf-8') as f:
        casual_chats = [(line.strip(), 'casual') for line in f]
    with open('./assets/weather_chat.txt', 'r', encoding='utf-8') as f:
        weather_chats = [(line.strip(), 'weather') for line in f]

    # Combine and split data into texts and labels
    data = casual_chats + weather_chats
    texts, labels = zip(*data)
    return texts, labels

# Train the SVM model


def train_model():
    texts, labels = load_data()
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.25, random_state=42)

    # Create a pipeline with TF-IDF and SVM
    model = make_pipeline(TfidfVectorizer(), SVC(
        kernel='linear', probability=True))
    model.fit(X_train, y_train)

    # Test the model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model accuracy: {accuracy:.2f}")

    # Save the trained model
    joblib.dump(model, './assets/svm_model.joblib')
    print("Model saved as './assets/svm_model.joblib'")


if __name__ == "__main__":
    train_model()
