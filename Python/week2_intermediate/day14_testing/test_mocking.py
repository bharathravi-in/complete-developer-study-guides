"""
Mocking Examples for Testing

Demonstrates unittest.mock for isolating tests.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, PropertyMock
from typing import Optional
import json


# ============================================
# CODE TO TEST
# ============================================

class DatabaseConnection:
    """Simulated database connection"""
    
    def connect(self):
        # Would actually connect to database
        pass
    
    def query(self, sql: str) -> list:
        # Would actually run query
        pass
    
    def close(self):
        pass


class UserService:
    """Service that uses database"""
    
    def __init__(self, db: DatabaseConnection):
        self.db = db
    
    def get_user(self, user_id: int) -> Optional[dict]:
        result = self.db.query(f"SELECT * FROM users WHERE id = {user_id}")
        if result:
            return result[0]
        return None
    
    def get_user_count(self) -> int:
        result = self.db.query("SELECT COUNT(*) FROM users")
        return result[0]["count"]


def fetch_data(url: str) -> dict:
    """Function that makes HTTP request"""
    import urllib.request
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read())


class ExternalAPIClient:
    """Client for external API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def get_weather(self, city: str) -> dict:
        # Would make actual API call
        pass


# ============================================
# MOCK TESTS
# ============================================

class TestMocking:
    """Mocking examples"""
    
    def test_basic_mock(self):
        """Basic Mock object"""
        mock = Mock()
        
        # Mock can be called with anything
        mock(1, 2, 3)
        mock.some_method("arg")
        mock.nested.attribute.method()
        
        # Assert calls
        mock.assert_called()
        mock.some_method.assert_called_once_with("arg")
    
    def test_mock_return_value(self):
        """Configure mock return value"""
        mock = Mock()
        mock.return_value = 42
        
        assert mock() == 42
        assert mock("ignored", "args") == 42
    
    def test_mock_side_effect(self):
        """Mock with side effects"""
        mock = Mock()
        
        # Return different values on consecutive calls
        mock.side_effect = [1, 2, 3]
        assert mock() == 1
        assert mock() == 2
        assert mock() == 3
        
        # Raise exception
        mock.side_effect = ValueError("Error!")
        with pytest.raises(ValueError):
            mock()
    
    def test_mock_database(self):
        """Mock database connection"""
        # Create mock database
        mock_db = Mock(spec=DatabaseConnection)
        mock_db.query.return_value = [{"id": 1, "name": "Alice"}]
        
        # Use mocked database
        service = UserService(mock_db)
        user = service.get_user(1)
        
        assert user["name"] == "Alice"
        mock_db.query.assert_called_once()
    
    def test_magic_mock(self):
        """MagicMock supports magic methods"""
        mock = MagicMock()
        
        # Magic methods work automatically
        mock.__str__.return_value = "Magic!"
        mock.__len__.return_value = 10
        
        assert str(mock) == "Magic!"
        assert len(mock) == 10


class TestPatch:
    """Using patch decorator and context manager"""
    
    @patch('urllib.request.urlopen')
    def test_patch_decorator(self, mock_urlopen):
        """Patch with decorator"""
        # Configure mock response
        mock_response = Mock()
        mock_response.read.return_value = b'{"data": "test"}'
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response
        
        # Call function
        result = fetch_data("http://example.com")
        
        assert result == {"data": "test"}
        mock_urlopen.assert_called_once_with("http://example.com")
    
    def test_patch_context_manager(self):
        """Patch with context manager"""
        with patch.object(DatabaseConnection, 'query') as mock_query:
            mock_query.return_value = [{"count": 100}]
            
            db = DatabaseConnection()
            service = UserService(db)
            count = service.get_user_count()
            
            assert count == 100
    
    def test_patch_multiple(self):
        """Patch multiple objects"""
        with patch.object(DatabaseConnection, 'connect') as mock_connect, \
             patch.object(DatabaseConnection, 'query') as mock_query:
            
            mock_query.return_value = []
            
            db = DatabaseConnection()
            db.connect()
            service = UserService(db)
            
            mock_connect.assert_called_once()
    
    def test_patch_property(self):
        """Patch a property"""
        class Config:
            @property
            def value(self):
                return "production"
        
        config = Config()
        
        with patch.object(Config, 'value', new_callable=PropertyMock) as mock_value:
            mock_value.return_value = "test"
            assert config.value == "test"


class TestMockAssertions:
    """Mock assertion examples"""
    
    def test_call_assertions(self):
        """Various call assertions"""
        mock = Mock()
        
        mock(1, 2, key="value")
        mock(3, 4)
        mock(5)
        
        # Assert call count
        assert mock.call_count == 3
        
        # Assert specific call
        mock.assert_any_call(3, 4)
        
        # Assert last call
        mock.assert_called_with(5)
        
        # Get all calls
        from unittest.mock import call
        assert mock.call_args_list == [
            call(1, 2, key="value"),
            call(3, 4),
            call(5)
        ]
    
    def test_reset_mock(self):
        """Reset mock state"""
        mock = Mock()
        mock(1)
        mock(2)
        
        assert mock.call_count == 2
        
        mock.reset_mock()
        
        assert mock.call_count == 0
        mock.assert_not_called()


# ============================================
# REAL WORLD EXAMPLE
# ============================================

class TestWeatherService:
    """Test external API client with mocking"""
    
    def test_get_weather(self):
        """Test weather API with mock"""
        client = ExternalAPIClient("test-api-key")
        
        with patch.object(client, 'get_weather') as mock_weather:
            mock_weather.return_value = {
                "city": "NYC",
                "temp": 72,
                "condition": "Sunny"
            }
            
            result = client.get_weather("NYC")
            
            assert result["temp"] == 72
            assert result["condition"] == "Sunny"
            mock_weather.assert_called_once_with("NYC")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
