import streamlit as st
from datetime import date
import requests
import pandas as pd
import plotly.express as px
import math
import json
from streamlit_lottie import st_lottie

st.markdown("""
    <style>
        /* Hide Streamlit header */
        .css-1v3fvcr {
            visibility: hidden;
        }
img[data-testid="stLogo"] {
            height: 10rem;
}
       
        .css-cio0dv {
            visibility: hidden;
        }

        /* Change background color for the whole app */
        .stApp {
            background-color: white; /* Default background color */
        }

        /* Change the background color of all containers */
        .stContainer {
            background-color: white;
        }

        /* Style the title */
        .css-10trblm {
            font-family: 'Arial', sans-serif;
            color: #28527A; /* Text color */
            font-size: 3em;
        }

        /* Style for markdown text */
        .css-1y0tads {
            font-family: 'Verdana', sans-serif;
            font-size: 1.2em;
            color: #28527A; /* Text color */
        }

        /* Customize the button */
        .stButton button {
            background: rgba(62, 132, 168, 0.2);
            border-radius: 16px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(4px);
            -webkit-backdrop-filter: blur(4px);
            color: #28527A; /* Text color */
            border-radius: 12px;
            padding: 8px 20px;
            font-size: 1.1em;
            font-weight: bold;
        }

        .stButton button:hover {
            background-color: #28527A; /* Button hover background */
            color: white; /* Button hover text color */
        }

        /* Input field customization */
        .stDateInput input {
            border: 1px solid rgba(62, 132, 168, 0.1);
            padding: 10px;
            border-radius: 5px;
            background: rgba(62, 132, 168, 0.1);
            color: #28527A; /* Input text color */
        }

        /* Align the footer at the bottom */
        footer {
            visibility: hidden;
        }

        .footer-text {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #3E84A8; /* Footer background color */
            color: white; /* Footer text color */
            text-align: center;
            padding: 10px 0;
        }

        /* Description styling */
        .DES {
            background: rgba(62, 132, 168, 0.22);
            border-radius: 16px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(4px);
            -webkit-backdrop-filter: blur(4px);
            border: 1px solid rgba(62, 132, 168, 0.1);
            padding-top: 25px;
            padding-right: 10px;
            padding-bottom: 25px;
            padding-left: 10px;
            margin-bottom: 10px;
        }

        /* Center the image */
        .center {
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .footer-text a {
        color: #fffb00; /* Link color */
        text-decoration: none; /* Remove underline */
        }
        .footer-text a:hover {
        text-decoration: underline; /* Add underline on hover */
        color: #e8e500; /* Slightly darker color on hover */
        }
    </style>
""", unsafe_allow_html=True)



st.logo(
    "https://i.ibb.co/86dHbxY/Apollo.png",
    size='large',
)

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_hello = load_lottieurl("https://lottie.host/e0ada96f-83a8-4108-9f04-7aee9bada15d/nUgFqcW89Y.json")

st_lottie(
    lottie_hello,
    speed=1,
    reverse=False,
    loop=True,
    quality="low", # medium ; high
    height=544,
    width=390,
    key=None,
)


st.markdown(f'<div class="DES">This app provides an accurate forecast of solar energy production using a custom model. Leveraging historical solar production data, the model makes future predictions to help optimize energy resource management and planning.</div>', unsafe_allow_html=True)

def make_prediction(end_date):
    base_date = date(2023, 6, 30)
    days_between = (end_date - base_date).days
    return days_between

col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input("Select Start Date", min_value=date(2023, 7, 1))
with col2:
    end_date = st.date_input("Select End Date", min_value=date(2023, 7, 1))

if st.button("Predict"):
        if start_date < end_date:
            with st.spinner("Fetching forecast data..."):
                days = make_prediction(end_date)

                api_url = f"https://solarmodel.onrender.com/?d={int(days)}"

                try:
                    response = requests.get(api_url)
                    response.raise_for_status()  # Check for request errors
                    forecast_data = pd.read_json(response.json())

                    # Process the forecast data
                    forecast_data['ds'] = pd.to_datetime(forecast_data['ds'], unit='ms', errors='coerce').dt.strftime('%Y-%m-%d')
                    forecast_data = forecast_data[(forecast_data["ds"] >= str(start_date))]

                    # Plotting the forecast
                    st.subheader("Forecast Plot")
                    fig = px.line(forecast_data, x='ds', y='yhat',
                                                title="Solar Energy Forecast",
                                                labels={"ds": "Date", "yhat": "Forecasted Solar Production"})
                    fig.update_xaxes(rangeslider_visible=True, dtick="M1", tickformat="%Y-%m-%d", ticklabelmode="period")
                    fig.update_traces(hovertemplate='%{x|%Y-%m-%d} <br>Forecasted Solar Production: %{y} MW')
                    st.plotly_chart(fig)

                    # Summary statistics
                    st.subheader("Forecast Summary")
                    avg_production = math.ceil(forecast_data['yhat'].mean())
                    min_production = math.ceil(forecast_data['yhat'].min())
                    max_production = math.ceil(forecast_data['yhat'].max())
                    st.warning(f"From {str(start_date)} to {str(end_date)}: \
                                \n- Average Solar Production: {avg_production} MW \
                                \n- Minimum Solar Production: {min_production} MW \
                                \n- Maximum Solar Production: {max_production} MW")

                except requests.exceptions.RequestException as e:
                    st.error(f"Error fetching data: {e}")
        else:
            st.error("End date must be after start date.")

# Add footer
st.markdown(
    '''
    <div class="footer-text">
        Developed by 
        <a href="https://github.com/abbraar/renewable_energy_forecasting" target="_blank" style="text-decoration: none; color: #0366d6;">
            Apollo Team 🌞
        </a> in Le Wagon 🚗
    </div>
    ''', 
    unsafe_allow_html=True
)
