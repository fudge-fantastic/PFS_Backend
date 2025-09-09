#!/usr/bin/env python3
"""
Test script to verify category name is properly returned in product APIs
"""
import requests
import json

def test_products_api():
    """Test the products API to see if category_name is included"""
    try:
        # Test list products endpoint
        response = requests.get("http://localhost:8000/products/?skip=0&limit=2")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Products API Response:")
            print(f"Success: {data.get('success', False)}")
            print(f"Message: {data.get('message', 'N/A')}")
            print(f"Total products returned: {len(data.get('data', []))}")
            print()
            
            for i, product in enumerate(data.get('data', [])[:2]):
                print(f"Product {i+1}:")
                print(f"  ID: {product.get('id')}")
                print(f"  Title: {product.get('title')}")
                print(f"  Category ID: {product.get('category_id')}")
                print(f"  Category Name: {product.get('category_name', 'MISSING ❌')}")
                print(f"  Price: ${product.get('price')}")
                print()
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Testing PixelForge Products API - Category Name Fix")
    print("=" * 60)
    test_products_api()
