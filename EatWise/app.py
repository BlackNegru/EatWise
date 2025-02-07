from flask import Flask, jsonify, request, render_template
import requests

app = Flask(__name__, template_folder='C:\\Users\\Admin\\StudioProjects\\EatWise')  # Template folder location

# Open Food Facts API Endpoints
PRODUCT_API = "https://world.openfoodfacts.org/api/v2/product/"
SEARCH_API = "https://world.openfoodfacts.org/cgi/search.pl"

@app.route('/')
def home():
    """Render the home page"""
    return render_template('home.html')  # This will serve home.html when the root URL is accessed

@app.route('/search', methods=['GET'])
def search_product():
    """Handle product search based on barcode or name"""
    barcode = request.args.get('barcode')
    name = request.args.get('name')

    print(f"Received request: Barcode = {barcode}, Name = {name}")  # Debugging line

    if barcode:
        print(f"Fetching product by barcode: {barcode}")  # Debugging line
        return fetch_product_by_barcode(barcode)
    elif name:
        print(f"Fetching products by name: {name}")  # Debugging line
        return fetch_products_by_name(name)
    else:
        print("Error: Missing barcode or name parameter")  # Debugging line
        return jsonify({"error": "Missing barcode or name parameter"}), 400

def format_product_details(product):
    """Format product details into a structured JSON"""
    return {
        "name": product.get("product_name", "N/A"),
        "brand": product.get("brands", "N/A"),
        "categories": product.get("categories", "N/A"),
        "ingredients": product.get("ingredients_text", "N/A"),
        "nutri_score": product.get("nutriscore_grade", "N/A"),
        "nova_score": product.get("nova_group", "N/A"),
        "ecoscore": product.get("ecoscore_grade", "N/A"),
        "nutrients": product.get("nutriments", {}),
        "allergens": product.get("allergens", "N/A"),
        "additives": product.get("additives_tags", []),
        "image_url": product.get("image_url", "N/A"),
        "image_nutrition": product.get("image_nutrition_url", "N/A"),
        "image_ingredients": product.get("image_ingredients_url", "N/A")
    }

def fetch_product_by_barcode(barcode):
    """Fetch product details using barcode"""
    url = f"{PRODUCT_API}{barcode}.json"
    print(f"Sending request to Open Food Facts API for barcode: {barcode}")  # Debugging line
    response = requests.get(url)

    print(f"Received response: {response.status_code}")  # Debugging line

    if response.status_code == 200:
        product_data = response.json()

        if "product" not in product_data:
            print("Error: Product not found")  # Debugging line
            return jsonify({"error": "Product not found"}), 404

        return jsonify(format_product_details(product_data["product"]))
    else:
        print(f"Error: Failed to fetch product data, Status Code: {response.status_code}")  # Debugging line
        return jsonify({"error": "Failed to fetch product data"}), response.status_code

def fetch_products_by_name(name):
    """Fetch multiple product details using product name"""
    params = {
        "search_terms": name,
        "search_simple": 1,
        "action": "process",
        "json": 1
    }
    print(f"Sending request to Open Food Facts API for name search: {name}")  # Debugging line
    response = requests.get(SEARCH_API, params=params)

    print(f"Received response: {response.status_code}")  # Debugging line

    if response.status_code == 200:
        products = response.json().get("products", [])

        if not products:
            print("Error: No products found")  # Debugging line
            return jsonify({"error": "No products found"}), 404

        formatted_products = [format_product_details(p) for p in products[:5]]  # Limit results to 5
        print(f"Returning {len(formatted_products)} products")  # Debugging line
        return jsonify(formatted_products)
    else:
        print(f"Error: Failed to fetch product data, Status Code: {response.status_code}")  # Debugging line
        return jsonify({"error": "Failed to fetch product data"}), response.status_code

if __name__ == '__main__':
    app.run(debug=True)
