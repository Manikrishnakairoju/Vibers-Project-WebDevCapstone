#homepage.py
import streamlit as st
import requests

# Set page config
st.set_page_config(layout="wide", page_title="Vibers")

# Base URL for the Flask backend
BASE_URL = "http://127.0.0.1:5000"

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = None

# Navigation bar
selected = st.sidebar.selectbox("Main Menu", ["Flights", "My Trips", "Web Scraping", "Login", "Sign Up"])

# Add logout button in sidebar if user is logged in
if st.session_state.logged_in:
    st.sidebar.write(f"Logged in as: {st.session_state.user_email}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_email = None
        st.rerun()

if selected == "Flights":
    st.title("Vibers")
    st.header("Search Flights")

    # Flight search form
    trip_type = st.radio("Trip Type:", ["Round Trip", "One Way"])
    col1, col2 = st.columns(2)
    from_city = col1.text_input("Where from?")
    to_city = col2.text_input("Where to?")
    departure_date = st.date_input("Departure")
    return_date = st.date_input("Return") if trip_type == "Round Trip" else None

    if st.button("Search for Flights"):
        # Prepare data for the backend
        params = {
            'origin': from_city,
            'destination': to_city,
            'departure_date': departure_date.isoformat()
        }
        try:
            # Make the API request to Flask to scrape flight data
            response = requests.get(f"{BASE_URL}/api/scrape-flights", params=params)
            response.raise_for_status()

            flight_data = response.json()

            if flight_data:
                st.success("Flights found!")
                for flight in flight_data:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**{flight['flight_name']}**")
                        st.write(f"Date: {flight['flight_date']}")
                    with col2:
                        st.write(f"Departure: {flight['departure_time']}")
                        st.write(f"Arrival: {flight['arrival_time']}")
                    with col3:
                        st.write(f"**Price: {flight['fare']}**")
                        if st.button(f"Book Flight", key=f"book_{flight['flight_name']}"):
                            if st.session_state.logged_in:
                                booking_data = {
                                    "user_email": st.session_state.user_email,
                                    "flight_name": flight["flight_name"],
                                    "flight_date": flight["flight_date"],
                                    "fare": flight["fare"]
                                }
                                try:
                                    booking_response = requests.post(f"{BASE_URL}/api/book-flight", json=booking_data)
                                    booking_response.raise_for_status()
                                    if booking_response.status_code == 201:
                                        st.success(f"Flight {flight['flight_name']} booked successfully!")
                                    else:
                                        st.error(f"Failed to book flight {flight['flight_name']}. Please try again later.")
                                except requests.exceptions.RequestException as e:
                                    st.error(f"An error occurred while booking: {str(e)}")
                            else:
                                st.warning("Please log in to book a flight.")
            else:
                st.info("No flight data available.")
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to fetch flight data: {str(e)}")


elif selected == "My Trips":
    if st.session_state.logged_in:
        st.title("Flight History")
        try:
            response = requests.get(f"{BASE_URL}/api/flight-history")
            response.raise_for_status()
            flight_history = response.json()
            if flight_history:
                st.table(flight_history)
            else:
                st.info("No flight history available.")
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to fetch flight history: {str(e)}")
    else:
        st.warning("Please log in to view your trips.")

elif selected == "Web Scraping":
    st.title("Web Scraping")
    st.header("Scraped Flight Data")
    st.info("Use the 'Search for Flights' section to initiate flight data scraping.")

elif selected == "Login":
    st.title("Login")
    st.header("Sign In to Your Account")

    with st.form(key="login_form"):
        email = st.text_input("Email address")
        password = st.text_input("Password", type="password")
        sign_in = st.form_submit_button("SIGN IN")

        if sign_in:
            try:
                response = requests.post(f"{BASE_URL}/api/login", json={
                    "email": email,
                    "password": password
                })
                response.raise_for_status()
                if response.status_code == 200:
                    st.success("Logged in successfully!")
                    st.session_state.logged_in = True
                    st.session_state.user_email = email
                    st.rerun()
                else:
                    st.error(response.json().get("error", "Login failed"))
            except requests.exceptions.RequestException as e:
                st.error(f"An error occurred during login: {str(e)}")

elif selected == "Sign Up":
    st.title("Sign Up")
    st.header("Create a New Account")

    with st.form(key="signup_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        agree_terms = st.checkbox("I agree to the Terms of Service")
        register = st.form_submit_button("REGISTER")

        if register:
            if password != confirm_password:
                st.error("Passwords do not match!")
            elif not agree_terms:
                st.error("Please agree to the Terms of Service.")
            else:
                try:
                    response = requests.post(f"{BASE_URL}/api/register", json={
                        "name": name,
                        "email": email,
                        "password": password
                    })
                    response.raise_for_status()
                    if response.status_code == 201:
                        user_details = response.json().get("user_details")
                        st.success(f"Registration successful! User details: {user_details}")
                    else:
                        error_message = response.json().get("error", "Registration failed.")
                        st.error(f"Registration failed: {error_message}")
                except requests.exceptions.RequestException as e:
                    st.error(f"An error occurred during registration: {str(e)}")
                except ValueError:
                    st.error("Received an invalid response from the server.")
