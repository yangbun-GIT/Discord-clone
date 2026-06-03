from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.main import app


def auth_headers(user_id: int = 42, username: str = "yangbun") -> dict[str, str]:
    token = create_access_token(subject=str(user_id), claims={"username": username})
    return {"Authorization": f"Bearer {token}"}


def test_store_catalog_requires_auth() -> None:
    client = TestClient(app)

    response = client.get("/api/store/catalog")

    assert response.status_code == 401


def test_store_catalog_returns_catalog_shape() -> None:
    client = TestClient(app)

    response = client.get("/api/store/catalog", headers=auth_headers())

    assert response.status_code == 200
    payload = response.json()
    assert payload["orb_balance"] == 1200
    assert payload["is_nitro_member"] is True
    assert len(payload["collections"]) == 5
    assert len(payload["items"]) == 23
    assert "avatar_decoration" in payload["categories"]
    assert "recently_added" in payload["filters"]["sort_modes"]
    assert all(item["ownership_state"] == "not_owned" for item in payload["items"])


def test_store_catalog_marks_nitro_discount_for_demo_member() -> None:
    client = TestClient(app)

    response = client.get("/api/store/catalog", headers=auth_headers())

    discounted_items = [
        item
        for item in response.json()["items"]
        if item["price"]["nitro_discount_percent"] is not None
    ]
    assert discounted_items
    assert all(item["price"]["is_nitro_discounted"] is True for item in discounted_items)


def test_store_item_detail_returns_related_and_bundle_data() -> None:
    client = TestClient(app)

    response = client.get("/api/store/items/6401", headers=auth_headers())

    assert response.status_code == 200
    payload = response.json()
    assert payload["item"]["type"] == "bundle"
    assert payload["can_purchase"] is True
    assert payload["can_gift"] is True
    assert payload["can_equip"] is False
    assert {item["id"] for item in payload["included_items"]} == {6101, 6201, 6301}
    assert payload["related_items"]


def test_store_item_detail_returns_404_for_unknown_item() -> None:
    client = TestClient(app)

    response = client.get("/api/store/items/999999", headers=auth_headers())

    assert response.status_code == 404
    assert response.json()["detail"] == "store item not found"
