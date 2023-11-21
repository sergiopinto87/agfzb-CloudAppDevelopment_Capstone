from cloudant.client import Cloudant
from cloudant.query import Query
from flask import Flask, jsonify, request
import atexit

#Add your Cloudant service credentials here
cloudant_username = "e6e4172f-40ce-4983-b95e-dafcdf47019e-bluemix"
cloudant_api_key = "xK2-SbF9cArNQOnJdufIAKbTGoF6U2U2RM8GCS1RTwOw"
cloudant_url = "https://e6e4172f-40ce-4983-b95e-dafcdf47019e-bluemix.cloudantnosqldb.appdomain.cloud"
client = Cloudant.iam(cloudant_username, cloudant_api_key, connect=True, url=cloudant_url)

session = client.session()
print('Databases:', client.all_dbs())

db = client['reviews']

app = Flask(__name__)

@app.route('/reviews/get', methods=['GET'])
def get():
    dealership_id = request.args.get('id')

    # Check if "id" parameter is missing
    if dealership_id is None:
        return jsonify({"error": "Missing 'id' parameter in the URL"}), 400

    # Convert the "id" parameter to an integer (assuming "id" should be an integer)
    try:
        dealership_id = int(dealership_id)
    except ValueError:
        return jsonify({"error": "'id' parameter must be an integer"}), 400

    # Define the query based on the 'dealership' ID
    selector = {
        'dealership': dealership_id
    }

    # Execute the query using the query method
    result = db.get_query_result(selector)

    # Create a list to store the documents
    data_list = []

    # Iterate through the results and add documents to the list
    for doc in result:
        data_list.append(doc)

    # Return the data as JSON
    return jsonify(data_list)


@app.route('/reviews/post', methods=['POST'])
def post():
    if not request.is_json:
        logging.error("Invalid or missing JSON data in request")
        abort(400, description='Invalid or missing JSON data')

    review_data = request.get_json()

    required_fields = ['name', 'dealership', 'review', 'purchase', 'purchase_date', 'car_make', 'car_model', 'car_year']
    for field in required_fields:
        if field not in review_data:
            logging.error(f"Missing required field: {field}")
            abort(400, description=f'Missing required field: {field}')

    # Save the review data as a new document in the Cloudant database
    try:
        db.create_document(review_data)
    except Exception as e:
        logging.error(f"Error in saving document: {e}")
        abort(500, description='Error in saving document')

    return jsonify({"message": "Review posted successfully"}), 201

if __name__ == '__main__':
    app.run(debug=True)