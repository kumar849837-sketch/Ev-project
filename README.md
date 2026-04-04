# Electric Vehicle Analytics & Performance Prediction

This project is a data-driven web application that analyzes electric vehicle (EV) data and predicts performance metrics using machine learning.

## Features
- **Data Synthesis**: Generates a realistic, synthetic EV dataset since raw data was not provided.
- **Predictive Modeling**: Uses Random Forest Regression to forecast an EV's range and charge time from technical specifications.
- **Interactive Dashboard**: A modern, premium-looking Streamlit application that provides:
  - **Performance Trends**: Visualizing and comparing various EV models.
  - **Feature Importance**: Understanding which technical specifications influence range and charging speed.
  - **"What-If" Simulator**: An interactive tool where users adjust parameters (e.g., battery capacity, vehicle weight) to instantly see the predicted impact on Range and Charge Time.

## Project Structure
- `data_generator.py`: Script that constructs the synthetic dataset (`ev_data_synthetic.csv`).
- `train_models.py`: Script that divides data into training/testing sets, applies Random Forest, extracts feature importance, and saves models as `.pkl` files.
- `app.py`: The Streamlit dashboard.
- `requirements.txt`: Python package dependencies.
- `models/`: Directory where trained `.pkl` models are stored.

## Running the Project

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Generate the dataset:**
   ```bash
   python data_generator.py
   ```

3. **Train the predictive models:**
   ```bash
   python train_models.py
   ```

4. **Run the Streamlit Web Application:**
   ```bash
   python -m streamlit run app.py
   ```

The application will launch on your default web browser at `http://localhost:8501`.
