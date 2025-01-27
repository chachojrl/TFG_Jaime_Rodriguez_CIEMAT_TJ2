import requests
from bs4 import BeautifulSoup

def fetch_signal_options(url):
    """
    Fetches the HTML content from the given URL and extracts all options 
    from the <select> element with name="signal01".
    """
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        select_element = soup.find('select', {'name': 'signal01'})
        
        if not select_element:
            raise ValueError("No <select> element with name 'signal01' found in the HTML.")
        
        # Extract all options
        options = [option['value'] for option in select_element.find_all('option') if option['value'].strip()]
        return options
    else:
        raise ValueError(f"Error fetching the page: {response.status_code}")

# URL containing the select element
url = "https://info.fusion.ciemat.es/cgi-bin/TJII_data.cgi"

# Fetch and print the options
try:
    signal_options = fetch_signal_options(url)
    print("Available options for 'signal01':")
    for option in signal_options:
        print(option)
except Exception as e:
    print("Error:", e)

# Save to a file
with open("signal_options.txt", "w") as file:
    file.write("\n".join(signal_options))
    print("Signal options saved to 'signal_options.txt'")
