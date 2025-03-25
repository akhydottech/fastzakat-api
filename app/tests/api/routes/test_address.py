from fastapi.testclient import TestClient

from app.core.config import settings


def test_search_address_success(client: TestClient) -> None:
    query = "123 Main St"
    response = client.get(
        f"{settings.API_V1_STR}/address/search",
        params={"query": query},
    )
    assert response.status_code == 200
    content = response.json()
    
    # Check top level fields
    assert "type" in content
    assert "version" in content
    assert "features" in content
    assert "attribution" in content
    assert "licence" in content
    assert "query" in content
    assert "limit" in content
    
    # Check features array
    assert isinstance(content["features"], list)
    if content["features"]:
        feature = content["features"][0]
        assert "type" in feature
        assert "geometry" in feature
        assert "properties" in feature
        
        # Check geometry
        geometry = feature["geometry"]
        assert "type" in geometry
        assert "coordinates" in geometry
        assert isinstance(geometry["coordinates"], list)
        assert len(geometry["coordinates"]) == 2  # [longitude, latitude]
        
        # Check properties
        properties = feature["properties"]
        assert "label" in properties
        assert "score" in properties
        assert "id" in properties
        assert "name" in properties
        assert "postcode" in properties
        assert "citycode" in properties
        assert "x" in properties
        assert "y" in properties
        assert "city" in properties
        assert "context" in properties
        assert "type" in properties
        assert "importance" in properties
        assert "banId" in properties
        assert "oldcitycode" in properties
        assert "oldcity" in properties


def test_search_address_no_query(client: TestClient) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/address/search",
    )
    assert response.status_code == 422  # Validation error for missing query parameter
