import streamlit as st
import urllib3
from ai_parser import parse_user_input_with_ai
from data_fetcher import generate_url, fetch_data, extract_data_points
from plotter import plot_data_per_signal
from config_loader import load_keywords, load_signal_options
import requests

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://info.fusion.ciemat.es/cgi-bin/TJII_data.cgi"

def ask_api(question):
    """Sends a question to the external API."""
    response = requests.post("http://localhost:8000/ask", json={"question": question})
    return response.json() if response.status_code == 200 else None

def main():
    st.title("Unified TJ-II Chatbot")
    user_input = st.text_input("Ask a question or request a plot:")
    
    keywords = load_keywords()
    valid_signals = load_signal_options()

    if st.button("Submit"):
        if any(keyword in user_input.lower() for keyword in keywords):
            parsed_data = parse_user_input_with_ai(user_input)

            if parsed_data and "shot" in parsed_data:
                shot = parsed_data["shot"]
                tstart = parsed_data.get("tstart", 0)
                tstop = parsed_data.get("tstop", 2000)
                signals = [sig for sig in parsed_data.get("signals", []) if sig in valid_signals]

                if signals:
                    url = generate_url(BASE_URL, shot, len(signals), signals, ["1.00"] * len(signals), tstart, tstop)
                    html_content = fetch_data(url)
                    if html_content:
                        data_points_dict = extract_data_points(html_content, signals)
                        plot_data_per_signal(data_points_dict)
                    else:
                        st.error("No data retrieved.")
                else:
                    st.error("No valid signals found.")
            else:
                st.error("Failed to interpret request.")
        else:
            response = ask_api(user_input)
            st.write(response if response else "No response.")

if __name__ == "__main__":
    main()
