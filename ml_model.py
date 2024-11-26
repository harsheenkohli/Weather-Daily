import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split, GridSearchCV
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
        texts, labels, test_size=0.25, random_state=42, shuffle=True
    )

    pipeline = make_pipeline(
        TfidfVectorizer(max_features=5000, ngram_range=(1, 2)),
        SVC(kernel='linear', probability=True, random_state=42)
    )

    # Grid search for hyperparameter tuning
    param_grid = {
        'svc__C': [0.1, 1, 10],
        'svc__kernel': ['linear', 'rbf']
    }

    grid_search = GridSearchCV(pipeline, param_grid, cv=3, scoring='accuracy')
    grid_search.fit(X_train, y_train)

    # Test the model
    best_model = grid_search.best_estimator_
    y_pred = best_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model accuracy: {accuracy:.2f}")

    # Save the best model
    joblib.dump(best_model, './assets/svm_model.joblib')
    print("Model saved as './assets/svm_model.joblib'")

if __name__ == "__main__":
    train_model()
