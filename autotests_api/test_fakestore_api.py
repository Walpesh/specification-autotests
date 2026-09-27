import pytest
import requests

BASE_URL = "https://fakestoreapi.com"

class TestProductsAPI:
    """Автоматизированные тесты для эндпоинтов Products"""

    def test_get_all_products(self):
        resp = requests.get(f"{BASE_URL}/products", timeout=10)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 20
        # Проверка структуры схемы первого товара
        product = data[0]
        assert "id" in product and isinstance(product["id"], int)
        assert "title" in product and isinstance(product["title"], str)
        assert "price" in product
        assert "category" in product and isinstance(product["category"], str)
        assert "description" in product
        assert "image" in product
        assert "rating" in product
        assert "rate" in product["rating"]
        assert "count" in product["rating"]

    def test_get_single_product(self):
        product_id = 1
        resp = requests.get(f"{BASE_URL}/products/{product_id}", timeout=10)
        assert resp.status_code == 200
        product = resp.json()
        assert product["id"] == product_id
        assert len(product["title"]) > 0
        assert product["price"] > 0
        assert product["image"].startswith("http")

    def test_get_products_limit(self):
        limit = 5
        resp = requests.get(f"{BASE_URL}/products", params={"limit": limit}, timeout=10)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == limit

    def test_get_products_sorted_desc(self):
        resp = requests.get(f"{BASE_URL}/products", params={"sort": "desc"}, timeout=10)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) > 1
        ids = [item["id"] for item in data]
        assert ids == sorted(ids, reverse=True)

    def test_get_all_categories(self):
        resp = requests.get(f"{BASE_URL}/products/categories", timeout=10)
        assert resp.status_code == 200
        categories = resp.json()
        assert isinstance(categories, list)
        expected = ["electronics", "jewelery", "men's clothing", "women's clothing"]
        for cat in expected:
            assert cat in categories

    def test_get_products_by_category(self):
        category = "jewelery"
        resp = requests.get(f"{BASE_URL}/products/category/{category}", timeout=10)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) > 0
        for item in data:
            assert item["category"] == category

    def test_create_product(self):
        payload = {
            "title": "QA Automation Pro Laptop Stand",
            "price": 49.99,
            "description": "Ergonomic aluminum stand for testing laptops",
            "image": "https://i.pravatar.cc/300",
            "category": "electronics"
        }
        resp = requests.post(f"{BASE_URL}/products", json=payload, timeout=10)
        assert resp.status_code in [200, 201]
        data = resp.json()
        assert "id" in data
        assert data["title"] == payload["title"]
        assert data["price"] == payload["price"]
        assert data["category"] == payload["category"]

    def test_update_product_put(self):
        payload = {
            "title": "QA Automation Pro Laptop Stand - Updated",
            "price": 59.99,
            "description": "Updated ultra-durable stand",
            "image": "https://i.pravatar.cc/300",
            "category": "electronics"
        }
        resp = requests.put(f"{BASE_URL}/products/7", json=payload, timeout=10)
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == payload["title"]
        assert data["price"] == payload["price"]

    def test_update_product_patch(self):
        payload = {"price": 39.99}
        resp = requests.patch(f"{BASE_URL}/products/7", json=payload, timeout=10)
        assert resp.status_code == 200
        data = resp.json()
        assert data["price"] == payload["price"]

    def test_delete_product(self):
        product_id = 6
        resp = requests.delete(f"{BASE_URL}/products/{product_id}", timeout=10)
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == product_id

    def test_get_nonexistent_category(self):
        resp = requests.get(f"{BASE_URL}/products/category/non_existing_category_xyz", timeout=10)
        assert resp.status_code == 200
        assert resp.json() == []


class TestCartsAPI:
    """Автоматизированные тесты для эндпоинтов Carts"""

    def test_get_all_carts(self):
        resp = requests.get(f"{BASE_URL}/carts", timeout=10)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) > 0
        cart = data[0]
        assert "id" in cart and isinstance(cart["id"], int)
        assert "userId" in cart and isinstance(cart["userId"], int)
        assert "date" in cart and isinstance(cart["date"], str)
        assert "products" in cart and isinstance(cart["products"], list)

    def test_get_single_cart(self):
        cart_id = 1
        resp = requests.get(f"{BASE_URL}/carts/{cart_id}", timeout=10)
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == cart_id
        assert "userId" in data
        assert isinstance(data["products"], list)

    def test_get_carts_limit(self):
        limit = 3
        resp = requests.get(f"{BASE_URL}/carts", params={"limit": limit}, timeout=10)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == limit

    def test_get_carts_sorted_desc(self):
        resp = requests.get(f"{BASE_URL}/carts", params={"sort": "desc"}, timeout=10)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) > 1
        ids = [c["id"] for c in data]
        assert ids == sorted(ids, reverse=True)

    def test_get_carts_date_range(self):
        params = {"startdate": "2019-12-10", "enddate": "2020-10-10"}
        resp = requests.get(f"{BASE_URL}/carts", params=params, timeout=10)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_user_carts(self):
        user_id = 2
        resp = requests.get(f"{BASE_URL}/carts/user/{user_id}", timeout=10)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        for cart in data:
            assert cart["userId"] == user_id

    def test_create_cart(self):
        payload = {
            "userId": 5,
            "date": "2020-02-03",
            "products": [
                {"productId": 5, "quantity": 1},
                {"productId": 1, "quantity": 5}
            ]
        }
        resp = requests.post(f"{BASE_URL}/carts", json=payload, timeout=10)
        assert resp.status_code in [200, 201]
        data = resp.json()
        assert "id" in data
        assert data["userId"] == payload["userId"]
        assert len(data["products"]) == len(payload["products"])

    def test_update_cart_put(self):
        payload = {
            "userId": 3,
            "date": "2019-12-10",
            "products": [{"productId": 1, "quantity": 3}]
        }
        resp = requests.put(f"{BASE_URL}/carts/7", json=payload, timeout=10)
        assert resp.status_code == 200
        data = resp.json()
        assert data["userId"] == payload["userId"]
        assert data["products"][0]["productId"] == 1

    def test_update_cart_patch(self):
        payload = {"userId": 4}
        resp = requests.patch(f"{BASE_URL}/carts/7", json=payload, timeout=10)
        assert resp.status_code == 200
        data = resp.json()
        assert data["userId"] == payload["userId"]

    def test_delete_cart(self):
        cart_id = 6
        resp = requests.delete(f"{BASE_URL}/carts/{cart_id}", timeout=10)
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == cart_id

    def test_get_nonexistent_user_carts(self):
        resp = requests.get(f"{BASE_URL}/carts/user/9999", timeout=10)
        assert resp.status_code == 200
        assert resp.json() == []
