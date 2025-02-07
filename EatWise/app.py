from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

PRODUCT_API = "https://world.openfoodfacts.org/api/v2/product/"
SEARCH_API = "https://world.openfoodfacts.org/cgi/search.pl"

# Store user preferences in memory (separated into 6 categories)
user_preferences = {
    "general_health": [],
    "food_sensitivities": [],
    "heart_health": [],
    "nutrition": [],
    "additives": [],
    "environmental": []
}

@app.route('/preferences', methods=['POST'])
def save_preferences():
    """Store user preferences from different pages."""
    data = request.get_json()

    for category in user_preferences.keys():
        if category in data:
            user_preferences[category] = data[category]

    return jsonify({"message": "Preferences saved successfully!"}), 200

@app.route('/home/preferences', methods=['GET'])
def get_preferences():
    """Print stored preferences when reaching home page."""
    print("\n📌 User Preferences:")
    print(user_preferences)
    return jsonify(user_preferences), 200

@app.route('/search', methods=['GET'])
def search_product():
    """Search products by name and return basic details (name, image, barcode, quantity)."""
    name = request.args.get('query')
    if not name:
        return jsonify({"error": "Missing product name"}), 400
    return fetch_products_by_name(name)

@app.route('/product/details', methods=['GET'])
def get_product_details():
    """Fetch full details of a product using barcode."""
    barcode = request.args.get('barcode')
    if not barcode:
        return jsonify({"error": "Missing barcode"}), 400
    return fetch_product_by_barcode(barcode)

def fetch_product_by_barcode(barcode):
    """Retrieve product details by barcode."""
    url = f"{PRODUCT_API}{barcode}.json"
    response = requests.get(url)
    if response.status_code == 200:
        product_data = response.json()
        if "product" not in product_data:
            return jsonify({"error": "Product not found"}), 404
        product = product_data["product"]
        return jsonify(format_product_details(product))
    return jsonify({"error": "Failed to fetch product data"}), response.status_code

def fetch_products_by_name(name):
    """Retrieve a list of products matching the name, showing only name, image, barcode, and quantity."""
    params = {"search_terms": name, "search_simple": 1, "action": "process", "json": 1}
    response = requests.get(SEARCH_API, params=params)
    if response.status_code == 200:
        products = response.json().get("products", [])
        if not products:
            return jsonify({"error": "No products found"}), 404
        return jsonify([
            {
                "name": p.get("product_name", "N/A"),
                "image": p.get("image_url", ""),
                "barcode": p.get("code", "N/A"),
                "quantity": p.get("quantity", "N/A")
            } for p in products[:10]
        ])
    return jsonify({"error": "Failed to fetch product data"}), response.status_code

def format_product_details(product):
    """Format full product details for display."""
    return {
        "name": product.get("product_name", "N/A"),
        "brand": product.get("brands", "N/A"),
        "categories": product.get("categories", "N/A"),
        "quantity": product.get("quantity", "N/A"),
        "ingredients": product.get("ingredients_text", "N/A"),
        "nutri_score": product.get("nutriscore_grade", "N/A"),
        "nova_score": product.get("nova_group", "N/A"),
        "ecoscore": product.get("ecoscore_grade", "N/A"),
        "nutrients": product.get("nutriments", {}),
        "allergens": product.get("allergens", "N/A"),
        "additives": product.get("additives_tags", []),
        "image_url": product.get("image_url", "N/A"),
        "image_nutrition": product.get("image_nutrition_url", "N/A"),
        "image_ingredients": product.get("image_ingredients_url", "N/A"),
        "origin": product.get("origins", "N/A"),
        "stores": product.get("stores", "N/A"),
        "countries_sold": product.get("countries_tags", []),
    }

if __name__ == '__main__':
    app.run(debug=True)
