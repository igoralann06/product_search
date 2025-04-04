from flask import Flask, jsonify, request, render_template
import os
import subprocess
from typing import Dict, List, Tuple
import json
from dotenv import load_dotenv
import sqlite3
from datetime import datetime

load_dotenv()

app = Flask(__name__)

SCRIPTS_DIR = "scripts"
PRODUCTS_DIR = "products"

# Define script directories and their descriptions
SCRIPT_DIRS = {
    'caller_script': 'Scripts for calling other scripts',
    'google_shopping_api': 'Google Shopping API integration scripts',
    'instacart_walmart': 'Walmart and Instacart integration scripts',
    'product_search': 'Product search and comparison scripts'
}

# Define script details
SCRIPT_DETAILS = {
    1: ("instacart_aldi", "aldi.py", "Scrapes instacart-aldi."),
    2: ("instacart_bjs", "bjs.py", "Scrapes instacart-bjs."),
    3: ("instacart_costco", "costco.py", "Scrapes instacart-costco."),
    4: ("instacart_milams", "milams.py", "Scrapes instacart-milams."),
    5: ("instacart_publix", "publix.py", "Scrapes instacart-publix."),
    6: ("instacart_resdept", "restaurant_depot.py", "Scrapes instacart-resdept."),
    7: ("instacart_sabor_tropical", "sabor_tropical.py", "Scrapes instacart-sabor_tropical."),
    8: ("instacart_sams", "sams.py", "Scrapes instacart-sams."),
    9: ("instacart_target", "target.py", "Scrapes instacart-target."),
    10: ("instacart_walmart", "walmart.py", "Scrapes instacart-walmart.")
}

def get_script_details() -> List[Dict]:
    """Returns a list of available scripts with their details."""
    return [
        {
            "id": num,
            "name": script[0],
            "description": script[2]
        }
        for num, script in SCRIPT_DETAILS.items()
    ]

def run_script(script_number: int, script_type: str) -> Dict:
    """Runs the specified script and returns the result."""
    if script_number in SCRIPT_DETAILS:
        script_info = SCRIPT_DETAILS[script_number]
        script_path = os.path.join(SCRIPTS_DIR, script_info[0], script_info[1])

        if os.path.exists(script_path):
            try:
                # Add script type as an argument
                command = f"cd {SCRIPTS_DIR}/{script_info[0]} && python {script_info[1]} {script_type}"
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = process.communicate()
                
                # Get the latest products from the database using the script's folder
                latest_products = get_latest_products(script_info[0])
                
                # Try to parse the output as JSON if it contains image URLs
                try:
                    output_data = json.loads(stdout)
                    return {
                        "success": process.returncode == 0,
                        "images": latest_products,
                        "error": stderr
                    }
                except json.JSONDecodeError:
                    # If not JSON, return as regular output with latest products
                    return {
                        "success": process.returncode == 0,
                        "output": stdout,
                        "images": latest_products,
                        "error": stderr
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }
        else:
            return {
                "success": False,
                "error": f"Script '{script_path}' not found."
            }
    else:
        return {
            "success": False,
            "error": f"Invalid script number '{script_number}'."
        }

def get_product_images() -> List[Dict]:
    """Returns a list of product images from the products directory."""
    images = []
    if os.path.exists(PRODUCTS_DIR):
        for filename in os.listdir(PRODUCTS_DIR):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                # Extract product name from filename (assuming format: product_name.jpg)
                product_name = os.path.splitext(filename)[0]
                images.append({
                    "url": f"/static/products/{filename}",
                    "product_name": product_name
                })
    return images

def search_images(product_name: str, search_type: str) -> List[str]:
    """Search for images based on product name and type."""
    if search_type == 'google':
        # Run Google image search script
        script_folder = "google_images"
        script_file = "main.py"
        command = f"cd {SCRIPTS_DIR}/{script_folder} && python {script_file} {product_name}"
    else:  # walmart
        # Run Walmart image search script
        script_folder = "walmart_images"
        script_file = "main.py"
        command = f"cd {SCRIPTS_DIR}/{script_folder} && python {script_file} {product_name}"

    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        
        try:
            output_data = json.loads(stdout)
            return output_data.get("images", [])
        except json.JSONDecodeError:
            return []
    except Exception as e:
        print(f"Error searching images: {str(e)}")
        return []

def get_latest_products(script_folder: str = None):
    """Fetch the latest products from the SQLite database"""
    try:
        # Construct database path based on script folder
        if script_folder:
            db_path = os.path.join(SCRIPTS_DIR, script_folder, 'product_search.db')
        else:
            db_path = 'product_search.db'
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get the latest timestamp from the database
        cursor.execute("SELECT * FROM google_store_data")
        latest_timestamp = cursor.fetchone()[0]
        
        if not latest_timestamp:
            return []
            
        # Fetch products with the latest timestamp
        cursor.execute("""
            SELECT id, product_name, image_file_names, price, store_name, category
            FROM google_store_data 
            WHERE timestamp = ?
            ORDER BY id DESC
            LIMIT 50
        """, (latest_timestamp,))
        
        products = []
        for row in cursor.fetchall():
            product = {
                'id': row[0],
                'product_name': row[1],
                'image_url': f"/products/{latest_timestamp}/images/{row[2]}" if row[2] else None,
                'price': row[3],
                'store_name': row[4],
                'category': row[5]
            }
            products.append(product)
            
        conn.close()
        return products
    except Exception as e:
        print(f"Error fetching products: {str(e)}")
        return []

@app.route('/')
def index():
    """Serve the web UI."""
    return render_template('index.html', scripts=get_script_details())

@app.route('/api/scripts', methods=['GET'])
def list_scripts():
    """API endpoint to list all available scripts."""
    return jsonify({
        "scripts": get_script_details()
    })

@app.route('/api/scripts/<int:script_number>/run', methods=['POST'])
def execute_script(script_number):
    """API endpoint to run a specific script."""
    script_type = request.json.get('type', '')
    result = run_script(script_number, script_type)
    return jsonify(result)

@app.route('/api/health', methods=['GET'])
def health_check():
    """API endpoint for health check."""
    return jsonify({
        "status": "healthy",
        "scripts_available": len(SCRIPT_DETAILS)
    })

@app.route('/api/products/images', methods=['GET'])
def get_images():
    """API endpoint to get product images."""
    images = get_product_images()
    return jsonify({
        "success": True,
        "images": images
    })

@app.route('/api/search/images', methods=['POST'])
def search_images_endpoint():
    """API endpoint to search for images."""
    data = request.json
    product_name = data.get('product', '')
    search_type = data.get('type', '')
    
    if not product_name or not search_type:
        return jsonify({
            "success": False,
            "error": "Product name and search type are required"
        })
    
    images = search_images(product_name, search_type)
    return jsonify({
        "success": True,
        "images": images
    })

@app.route('/api/products/latest', methods=['GET'])
def get_latest_products_endpoint():
    """API endpoint to get the latest products from the SQLite database."""
    products = get_latest_products()
    return jsonify({
        "success": True,
        "products": products
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)