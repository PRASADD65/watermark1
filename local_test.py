import json
from lambda_function import lambda_handler  # Import the lambda handler

if __name__ == "__main__":
    with open('test_s3_event.json', 'r') as event_file:
        event = json.load(event_file)
        response = lambda_handler(event, None)
        print(response)

