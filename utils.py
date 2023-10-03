import datetime
import requests

def get_now_timestamp():
  now = datetime.datetime.now()
  timestamp = int(now.timestamp())
  return timestamp


def post_prediction(endpoint_url, timestamp, name):
    try:
        data = {
            "timestamp": timestamp,
            "name": name
        }

        response = requests.post(endpoint_url, json=data)

        if response.status_code == 201:
            print ("Prediction saved successfully!")
        else:
            print("Failed to save prediction. Status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print("Error occurred during the request: {str(e)}")