import requests # type:ignore
import json
import os
import numpy as np



def get_prediction_from_api(payload_data):
    """
    Sends data to the prediction API and returns the result.
    
    Args:
        payload_data (dict): A dictionary containing the features for the prediction model.
        
    Returns:
        dict: The JSON response from the API, or None if an error occurs.
    """
    url = "https://sofipremasapi.wandev.site/predict"
    headers = {
        'Content-Type': 'application/json'
    }
    try:
        # Using requests.post is a more direct way to make a POST request
        response = requests.post(url, headers=headers, data=json.dumps(payload_data), timeout=60)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        # In a real application, you would want to log this error
        print(f"An error occurred while calling the prediction API: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Failed to decode JSON response from API. Response text: {response.text}")
        return None
    
def get_fuel_filter_pressure_from_api(device_id):
    """
    Fetches the most recent fuel filter pressure reading for a device.

    The upstream API has no pagination/limit support (query params like
    limit/page_size are ignored) and returns a device's entire reading
    history - tens of MB and growing - as a flat JSON array sorted
    newest-first. To avoid downloading the whole history on every poll,
    the response is streamed and reading stops as soon as the first
    (i.e. latest) record has been decoded.

    Args:
        device_id (str): The device ID for which to retrieve fuel filter pressure data.

    Returns:
        dict: The most recent reading, or None if unavailable or an error occurs.
    """
    token = os.environ.get('IOT_API_TOKEN')
    if not token:
        print("IOT_API_TOKEN is not set; skipping fuel filter pressure request.")
        return None
    url = "https://iot.ums-biroti.id/api/S01/?device_id=" + device_id
    headers = {
        'Authorization': 'Token ' + token
    }
    decoder = json.JSONDecoder()
    try:
        with requests.get(url, headers=headers, stream=True, timeout=15) as response:
            response.raise_for_status()
            response.encoding = 'utf-8'
            buf = ""
            for chunk in response.iter_content(chunk_size=2048, decode_unicode=True):
                if not chunk:
                    continue
                buf += chunk
                stripped = buf.lstrip()
                if not stripped.startswith('['):
                    continue
                try:
                    record, _ = decoder.raw_decode(stripped, 1)
                    return record
                except json.JSONDecodeError:
                    continue  # first record isn't complete yet, keep reading
            return None  # stream ended before a full record was received (e.g. empty list)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while calling the fuel filter pressure API: {e}")
        return None