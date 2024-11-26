# Weather-Daily
## Overview
**Weather-Daily** is an interactive web-based application that provides users with current weather information, forecasts for future dates, and AQI (Air Quality Index) details for their location. It also features small talk functionality, making it more engaging for users who interact with it. The application is built using `Streamlit` and leverages machine learning for text classification to determine user intent.

Deployed at: [Weather-Daily](https://weather-daily.streamlit.app/)

## Features
- **Current Weather**: Get the current weather conditions for any location.
- **Forecasts**: Access weather forecasts for specific days or up to 7 days in the future.
- **Air Quality Index (AQI)**: Find detailed AQI information for supported locations.

## Technology Stack
- **Frontend Framework**: Streamlit
- **Machine Learning Model**: Support Vector Machine (SVM)
- **Text Processing**: `fuzzywuzzy` module used for fuzzy matching of queries making the chatbot user-friendly.
- **Model Training**: Scikit-learn with TF-IDF vectorization and SVM classification
- **Data Handling**: Pandas

## Directory Structure
```
weather-daily/
│
├── .devcontainer/
│   └── devcontainer.json
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml
├── assets/
│   ├── chatbot.png
│   ├── human_chat.txt
│   ├── logo.png
│   ├── person.png
│   ├── svm_model.joblib
│   ├── weather_chat.txt
│   └── world-cities.csv
│
├── __pycache__/
│
├── main.py
├── ml_model.py
├── query_parser.py
├── small_talk.py
├── requirements.txt
├── README.md
├── weather_forecaster.py
└── .gitignore
```

## How to Run Locally
### Prerequisites
Ensure you have Python 3.8 or higher installed on your system. Install the required Python packages by running:
```bash
pip install -r requirements.txt
```

### Setup
1. **Clone the repository**:
    ```bash
    git clone https://github.com/harsheenkohli/weather-daily.git
    cd weather-daily
    ```
2. **API Key:** Create a `.streamlit/secrets.toml` file and add your API key(s) for weather data:
    ```toml
    [API_KEY]
    API_KEY = "your_weather_api_key"
    AQI_KEY = "your_aqi_key"
    ```
    > (this format has been written in accordance with the format used in this repository)
3. **Train the model (Optional)**: If you need to retrain the model, run:
    ```bash
    python ml_model.py
    ```

### Run the Application
To run the Streamlit application locally:
```bash
streamlit run main.py
```

## Model Information
The machine learning model used for text classification is an SVM trained with `TF-IDF` vectorization for feature extraction. It classifies user inputs into `casual` and `weather` categories to determine if the query requires small talk responses or weather data.

### Training the Model
The `ml_model.py` script:
- Loads training data from `assets/human_chat.txt` and `assets/weather_chat.txt`.
- Trains an SVM model with a linear kernel.
- Saves the trained model as `assets/svm_model.joblib`.

## File Descriptions
- **`main.py`**: The main script for the Streamlit application.
- **`ml_model.py`**: Script for training the machine learning model.
- **`query_parser.py`**: Script for finding the weather query type and location in the user input.
- **`small_talk.py`**: Contains predefined responses for small talk interactions.
- **`weather_forecaster.py`**: Script for fetching output with API calls based on parsed query.
- **`assets/`**: Directory containing text data, images, the trained model, and additional resources.

## Deployment
The app is deployed on Streamlit Cloud, making it accessible online at: [Weather-Daily](https://weather-daily.streamlit.app/)

## Future Improvements
- Enhance small talk capabilities for a more natural interaction.
- Add support for more languages.
- Implement additional weather data features like radar and satellite views.

## License
This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for more details.
