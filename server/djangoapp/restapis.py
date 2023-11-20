import requests
import json
from .models import CarDealer, DealerReview, CarModel, CarData
from requests.auth import HTTPBasicAuth
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions



# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    # Construct params from kwargs
    api_key= "xK2-SbF9cArNQOnJdufIAKbTGoF6U2U2RM8GCS1RTwOw"
    params = {key: kwargs.get(key) for key in ["text", "version", "features", "return_analyzed_text"]}
    headers = {'Content-Type': 'application/json'}

    # Basic authentication if api_key is provided
    auth = HTTPBasicAuth('apikey', api_key)

    try:
        response = requests.get(url, params=params, headers=headers, auth=auth)
        
    except requests.exceptions.RequestException as e:
        print("Network exception occurred: {}".format(e))
        return None

    status_code = response.status_code
    print("GET from {} with status {}".format(url, status_code))

    try:
        return response.json()
    except ValueError:
        print("Response content is not valid JSON")
        return None

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)

def post_request(url, json_payload, dealer_id, **kwargs):
    try:
        response = requests.post(url, json=json_payload, **kwargs)

        # Check if the request was successful
        if 200 <= response.status_code < 300:
            return "Submission successful", True
        else:
            return f"Failed to submit. Status code: {response.status_code}", False
    except requests.RequestException as e:
        # Handle any exceptions that occur during the request
        return f"An error occurred: {str(e)}", False

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list

def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer (address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results


# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list

def get_dealer_by_id_from_cf(url, dealer_id):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as reviews
        reviews = json_result
        # For each review object
        for review in reviews:
            # Get its content in `doc` object
            review_doc = review
            if review_doc.get("dealership") == dealer_id:
                # Create a DealerReview object with values in `doc` object
                sentiment = analyze_sentiment(review_doc.get("review"))
                review_obj = DealerReview (dealership=review_doc["dealership"], name=review_doc["name"], purchase=review_doc["purchase"],
                            review=review_doc["review"], purchase_date=review_doc["purchase_date"], car_make=review_doc["car_make"],
                            car_model=review_doc["car_model"],
                            car_year=review_doc["car_year"], sentiment=sentiment, id=review_doc["id"])
                results.append(review_obj)
            else:
                continue

    return results


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative


def analyze_sentiment(text):
    # Replace 'your_api_key' and 'your_service_url' with your IBM Watson NLU credentials
    api_key = '64YyezcbQGhvhRs0x2F_5x4YyG6iWZlm4Q33sPigpVfU'
    service_url = 'https://api.au-syd.natural-language-understanding.watson.cloud.ibm.com/instances/40f86668-a223-4aa4-bbce-ee72bffe569b'

    authenticator = IAMAuthenticator(api_key)
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2021-08-01',
        authenticator=authenticator
    )

    natural_language_understanding.set_service_url(service_url)

    try:
        # Analyze the sentiment
        response = natural_language_understanding.analyze(
            text=text,
            features=Features(sentiment=SentimentOptions())
        ).get_result()

        # Extract the sentiment label
        sentiment_label = response['sentiment']['document']['label']
        return sentiment_label
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_cars(dealer_id, url):
    
    json_result = get_request(url)
    dealers = json_result
    
    dealer_name = None
    for dealer in dealers:
        dealer_doc = dealer
        if dealer_doc.get("id") == dealer_id:
            dealer_name = dealer_doc.get("full_name")
              # Break the loop once the matching dealer is found

    results = []
    cars = CarModel.objects.order_by('-name')[:10]
    for car in cars:
        if car.dealer_id == dealer_id:
            car_obj = CarData(name=car.name, car_maker=car.car_maker, year=car.year, dealer_name=dealer_name)
            results.append(car_obj)
        else:
            continue

    return results
