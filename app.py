import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib
import os
import requests
import datetime
import json
import pyotp
import qrcode

# --- Configurations ---
st.set_page_config(
    page_title="EV Analytics & Performance Prediction",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Firebase Configuration
FIREBASE_PROJECT_ID = "ev-project-cdf70"
FIREBASE_API_KEY = "AIzaSyCGDLxj9tipBcgalpzAGUj0qGhBgR2QSA8"

def save_to_firebase(data):
    """Saves data to Firebase Firestore using REST API."""
    url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents/predictions?key={FIREBASE_API_KEY}"
    
    # Firestore REST requires a specific nested JSON structure
    firestore_data = {"fields": {}}
    for key, value in data.items():
        if isinstance(value, str):
            firestore_data["fields"][key] = {"stringValue": value}
        elif isinstance(value, int):
            firestore_data["fields"][key] = {"integerValue": str(value)}
        elif isinstance(value, float):
            firestore_data["fields"][key] = {"doubleValue": value}
            
    try:
        response = requests.post(url, json=firestore_data)
        response.raise_for_status()
        return True, response.json()
    except Exception as e:
        return False, str(e)


# Custom CSS for modern, premium look
st.markdown("""
<style>
    .main {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    h1, h2, h3 {
        color: #00E676;
    }
    .stMetric {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .stSlider > div > div > div > div {
        background: #00E676;
    }
</style>
""", unsafe_allow_html=True)

# --- Load Data & Models ---
@st.cache_data
def load_data():
    data_path = os.path.join(os.path.dirname(__file__), 'ev_data_synthetic.csv')
    if os.path.exists(data_path):
        return pd.read_csv(data_path)
    return pd.DataFrame()

@st.cache_resource
def load_models(version="v2"):
    models_dir = os.path.join(os.path.dirname(__file__), 'models')
    try:
        rf_range = joblib.load(os.path.join(models_dir, 'rf_range_model.pkl'))
        rf_charge = joblib.load(os.path.join(models_dir, 'rf_charge_model.pkl'))
        importances = joblib.load(os.path.join(models_dir, 'feature_importances.pkl'))
        return rf_range, rf_charge, importances
    except FileNotFoundError:
        return None, None, None

df = load_data()
rf_range, rf_charge, importances = load_models(version="v2")

if df.empty:
    st.error("Data not found. Please run the data generator script first.")
    st.stop()

# --- Authentication ---
USERS_FILE = os.path.join(os.path.dirname(__file__), 'users.json')

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def check_password():
    """Returns `True` if the user is authenticated."""
    users = load_users()
    
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
        
    if st.session_state["password_correct"]:
        return True
        
    st.markdown("""
    <style>
        .auth-card {
            background-color: #1E1E1E;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0, 230, 118, 0.2);
            margin: auto;
            text-align: center;
        }
        .auth-title {
            color: #00E676 !important;
            margin-bottom: 20px;
        }
        div.stButton > button {
            width: 100%;
            background-color: #00E676;
            color: #121212;
            border: none;
            border-radius: 8px;
            padding: 10px;
            font-weight: bold;
            transition: all 0.3s ease;
            margin-top: 15px;
        }
        div.stButton > button:hover {
            background-color: #00C853;
            color: white;
            box-shadow: 0 0 10px #00E676;
        }
    </style>
    """, unsafe_allow_html=True)
    
    _, col, _ = st.columns([1, 2, 1])
    
    with col:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.markdown('<h2 class="auth-title">⚡ Welcome to EV Analytics</h2>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            contact = st.text_input("Email or Phone", key="login_contact")
            password = st.text_input("Password", type="password", key="login_pass")
            
            if "awaiting_otp" not in st.session_state:
                st.session_state["awaiting_otp"] = False
                
            if not st.session_state["awaiting_otp"]:
                if st.button("Send OTP"):
                    if contact in users and users[contact].get("password") == password:
                        import random
                        otp = str(random.randint(100000, 999999))
                        st.session_state["expected_otp"] = otp
                        st.session_state["contact_attempt"] = contact
                        st.session_state["awaiting_otp"] = True
                        st.rerun()
                    else:
                        st.error("😕 Account not found or password incorrect")
            else:
                st.info(f"Simulation: OTP sent to {st.session_state.get('contact_attempt')}. Your code is: **{st.session_state.get('expected_otp')}**")
                entered_otp = st.text_input("Enter 6-Digit OTP", key="login_otp")
                
                colA, colB = st.columns(2)
                with colA:
                    if st.button("Verify & Login"):
                        if entered_otp == st.session_state.get("expected_otp"):
                            st.session_state["password_correct"] = True
                            st.session_state["logged_in_user"] = st.session_state.get("contact_attempt")
                            st.session_state["awaiting_otp"] = False
                            st.rerun()
                        else:
                            st.error("😕 Incorrect OTP.")
                with colB:
                    if st.button("Cancel"):
                        st.session_state["awaiting_otp"] = False
                        st.rerun()
                    
        with tab2:
            new_contact = st.text_input("New Email or Phone", key="signup_contact")
            new_pass = st.text_input("New Password", type="password", key="signup_pass")
            confirm_pass = st.text_input("Confirm Password", type="password", key="signup_confirm")
            
            if st.button("Sign Up"):
                if not new_contact or not new_pass:
                    st.error("Please fill in all fields.")
                elif new_contact in users:
                    st.error("Account already exists!")
                elif new_pass != confirm_pass:
                    st.error("Passwords do not match!")
                else:
                    users[new_contact] = {
                        "password": new_pass
                    }
                    save_users(users)
                    st.success("Account created successfully! You can now switch to the Login tab.")
        
        st.markdown('</div><br><br>', unsafe_allow_html=True)

    return False

if not check_password():
    st.stop()

# --- App Layout ---
st.title("⚡ EV Analytics & Performance Prediction")
st.markdown("Explore electric vehicle performance trends, compare technical specifications, and use machine learning to forecast range and charging times.")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Analytics Dashboard", "🔋 Feature Importance", "🔮 Predictive What-If Simulator", "👤 My Profile"])

# --- Tab 1: Analytics Dashboard ---
with tab1:
    st.header("Electric Vehicle Performance Trends")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total EV Models tracked", len(df))
    with col2:
        st.metric("Average Range", f"{df['Range_km'].mean():.0f} km")
    with col3:
        st.metric("Avg Charge Time (10%-80%)", f"{df['Charge_Time_mins'].mean():.0f} mins")

    st.subheader("Compare Brands")
    
    colA, colB = st.columns(2)
    
    with colA:
        # Range vs Battery Capacity
        fig = px.scatter(
            df, 
            x="Battery_Capacity_kWh", 
            y="Range_km", 
            color="Brand",
            hover_data=['Motor_Power_kW', 'Price_USD'],
            title="Battery Capacity vs Range",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig, use_container_width=True)
        
    with colB:
        # Price Distribution by Brand
        fig2 = px.box(
            df, 
            x="Brand", 
            y="Price_USD", 
            color="Brand",
            title="Price Distribution by Brand",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white", showlegend=False)
        fig2.update_xaxes(tickangle=-45)
        st.plotly_chart(fig2, use_container_width=True)

# --- Tab 2: Feature Importance ---
with tab2:
    st.header("What Drives EV Performance?")
    st.markdown("Understanding which technical specifications most influence range and charging speed based on our Random Forest models.")
    
    if importances:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Influences on Range (km)")
            range_imp = pd.DataFrame({
                'Feature': importances['Range'].keys(),
                'Importance': importances['Range'].values()
            }).sort_values('Importance', ascending=True)
            
            fig = px.bar(range_imp, x='Importance', y='Feature', orientation='h', color='Importance', color_continuous_scale='Greens')
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.subheader("Influences on Charge Time (mins)")
            charge_imp = pd.DataFrame({
                'Feature': importances['ChargeTime'].keys(),
                'Importance': importances['ChargeTime'].values()
            }).sort_values('Importance', ascending=True)
            
            fig2 = px.bar(charge_imp, x='Importance', y='Feature', orientation='h', color='Importance', color_continuous_scale='Blues')
            fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("Models not found. Please train models first to see feature importances.")

# --- Tab 3: Predictive Simulator ---
with tab3:
    st.header("What-If Scenario Simulator")
    st.markdown("Adjust the specifications below to instantly predict how modifications affect the Range and Charge Time of a hypothetical EV.")
    
    if rf_range is not None and rf_charge is not None:
        col_input, col_output = st.columns([1, 1])
        
        with col_input:
            st.subheader("Adjust Vehicle Specifications")
            
            brands = sorted(df['Brand'].unique().tolist())
            brand = st.selectbox("Car Brand", brands, index=0)
            
            # Base values (averages)
            base_battery = float(df['Battery_Capacity_kWh'].mean())
            base_power = int(df['Motor_Power_kW'].mean())
            base_weight = int(df['Weight_kg'].mean())
            base_charge_pwr = int(df['Max_Charge_Power_kW'].median())
            base_drag = float(df['Drag_Coefficient'].mean())
            
            battery = st.slider("Battery Capacity (kWh)", 30.0, 150.0, base_battery, 0.5)
            st.caption("Larger battery increases range but also increases weight and charge time.")
            
            power = st.slider("Motor Power (kW)", 100, 1000, base_power, 10)
            st.caption("More power means faster acceleration but may reduce efficiency.")
            
            weight = st.slider("Vehicle Weight (kg)", 1000, 3500, base_weight, 50)
            st.caption("Heavier vehicles require more energy to move, reducing range.")
            
            charge_pwr = st.select_slider("Max Charging Power (kW)", options=[50, 100, 150, 250, 350], value=base_charge_pwr)
            st.caption("Higher rates reduce charging time at fast chargers.")
            
            drag = st.slider("Drag Coefficient (Cd)", 0.15, 0.40, base_drag, 0.01)
            st.caption("Lower drag improves aerodynamic efficiency, boosting highway range.")
            
        with col_output:
            st.subheader("Predicted Outcomes")
            
            # Prepare input data for prediction
            input_df = pd.DataFrame({
                'Brand': [brand],
                'Battery_Capacity_kWh': [battery],
                'Motor_Power_kW': [power],
                'Weight_kg': [weight],
                'Max_Charge_Power_kW': [charge_pwr],
                'Drag_Coefficient': [drag]
            })
            
            # Predict
            pred_range = rf_range.predict(input_df)[0]
            pred_charge = rf_charge.predict(input_df)[0]
            
            st.markdown("---")
            
            col_metric1, col_metric2 = st.columns(2)
            with col_metric1:
                st.metric("🎯 Predicted Range", f"{pred_range:.0f} km")
            with col_metric2:
                st.metric("⏱️ Predicted Charge Time", f"{pred_charge:.0f} mins")
                
            st.markdown("---")
            
            # Show a gauge chart for range
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = pred_range,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Range Potential (km)", 'font': {'color': 'white'}},
                gauge = {
                    'axis': {'range': [None, 1000], 'tickcolor': "white"},
                    'bar': {'color': "#00E676"},
                    'steps': [
                        {'range': [0, 300], 'color': "#ff5252"},
                        {'range': [300, 500], 'color': "#ffd740"},
                        {'range': [500, 1000], 'color': "#69f0ae"}
                    ]
                }
            ))
            fig_gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"}, height=300)
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            st.markdown("---")
            if st.button("💾 Save Simulation to Firebase"):
                with st.spinner("Saving to database..."):
                    sim_data = {
                        "timestamp": datetime.datetime.now().isoformat(),
                        "brand": brand,
                        "battery_kwh": float(battery),
                        "motor_power_kw": int(power),
                        "weight_kg": int(weight),
                        "max_charge_power_kw": int(charge_pwr),
                        "drag_coefficient": float(drag),
                        "predicted_range_km": float(pred_range),
                        "predicted_charge_time_mins": float(pred_charge)
                    }
                    success, result = save_to_firebase(sim_data)
                    if success:
                        st.success("Simulation saved successfully!")
                    else:
                        st.error(f"Failed to save: {result}")
            
    else:
        st.warning("Prediction models are currently unavailable. Please ensure `train_models.py` has been executed.")

# --- Tab 4: User Profile ---
with tab4:
    st.header("👤 My Profile Settings")
    st.markdown("Update your personal and professional details below.")
    
    users_db = load_users()
    current_user = st.session_state.get("logged_in_user")
    
    if current_user and current_user in users_db:
        user_info = users_db[current_user]
        
        with st.form("profile_form"):
            colA, colB = st.columns(2)
            with colA:
                form_name = st.text_input("Full Name", value=user_info.get("full_name", ""))
                form_email = st.text_input("Email", value=user_info.get("email", ""))
            with colB:
                form_company = st.text_input("Company", value=user_info.get("company", ""))
                form_job = st.text_input("Job Title", value=user_info.get("job_title", ""))
                
            submitted = st.form_submit_button("Update Profile")
            if submitted:
                user_info["full_name"] = form_name
                user_info["email"] = form_email
                user_info["company"] = form_company
                user_info["job_title"] = form_job
                
                users_db[current_user] = user_info
                save_users(users_db)
                st.success("✅ Profile successfully updated!")
    else:
        st.error("Error loading user profile. Please try logging out and logging back in.")
