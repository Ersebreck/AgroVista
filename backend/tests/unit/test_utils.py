"""
Unit tests for utility functions.
"""
from datetime import datetime, timedelta

from app.utils import (
    calculate_days_difference,
    calculate_percentage,
    format_currency,
    format_date,
    generate_summary_text,
    generate_unique_id,
    get_current_date,
    get_status_color,
    is_valid_email,
    sanitize_string,
    validate_date_range,
)


class TestDateUtilities:
    """Test date-related utility functions."""
    
    def test_get_current_date(self):
        """Test getting current date."""
        result = get_current_date()
        assert isinstance(result, str)
        # Check format YYYY-MM-DD
        assert len(result) == 10
        assert result[4] == '-'
        assert result[7] == '-'
    
    def test_format_date(self):
        """Test date formatting."""
        test_date = datetime(2024, 7, 15)
        result = format_date(test_date)
        assert result == "2024-07-15"
        
        # Test with string input
        result = format_date("2024-07-15")
        assert result == "2024-07-15"
    
    def test_calculate_days_difference(self):
        """Test calculating days between dates."""
        date1 = datetime(2024, 7, 1)
        date2 = datetime(2024, 7, 15)
        
        result = calculate_days_difference(date1, date2)
        assert result == 14
        
        # Test with string dates
        result = calculate_days_difference("2024-07-01", "2024-07-15")
        assert result == 14
        
        # Test negative difference
        result = calculate_days_difference(date2, date1)
        assert result == -14
    
    def test_validate_date_range(self):
        """Test date range validation."""
        start_date = "2024-07-01"
        end_date = "2024-07-15"
        
        # Valid range
        assert validate_date_range(start_date, end_date) is True
        
        # Invalid range
        assert validate_date_range(end_date, start_date) is False
        
        # Same dates
        assert validate_date_range(start_date, start_date) is True


class TestStatusUtilities:
    """Test status-related utility functions."""
    
    def test_get_status_color(self):
        """Test getting color for status."""
        assert get_status_color("Completed") == "green"
        assert get_status_color("In Progress") == "yellow"
        assert get_status_color("Planned") == "blue"
        assert get_status_color("Cancelled") == "red"
        assert get_status_color("Unknown") == "gray"  # Default
    
    def test_generate_summary_text(self):
        """Test generating summary text."""
        data = {
            "total": 100,
            "completed": 75,
            "pending": 25
        }
        
        result = generate_summary_text(data)
        assert isinstance(result, str)
        assert "100" in result
        assert "75" in result
        assert "25" in result


class TestNumberUtilities:
    """Test number-related utility functions."""
    
    def test_calculate_percentage(self):
        """Test percentage calculation."""
        assert calculate_percentage(50, 100) == 50.0
        assert calculate_percentage(75, 150) == 50.0
        assert calculate_percentage(0, 100) == 0.0
        
        # Test division by zero
        assert calculate_percentage(50, 0) == 0.0
        
        # Test rounding
        assert calculate_percentage(1, 3) == 33.33
    
    def test_format_currency(self):
        """Test currency formatting."""
        assert format_currency(1000) == "$1,000.00"
        assert format_currency(1234.56) == "$1,234.56"
        assert format_currency(0) == "$0.00"
        assert format_currency(-500) == "-$500.00"


class TestStringUtilities:
    """Test string-related utility functions."""
    
    def test_generate_unique_id(self):
        """Test unique ID generation."""
        id1 = generate_unique_id()
        id2 = generate_unique_id()
        
        assert isinstance(id1, str)
        assert isinstance(id2, str)
        assert id1 != id2  # Should be unique
        assert len(id1) > 0
    
    def test_is_valid_email(self):
        """Test email validation."""
        assert is_valid_email("user@example.com") is True
        assert is_valid_email("test.user@domain.co.uk") is True
        assert is_valid_email("invalid.email") is False
        assert is_valid_email("@example.com") is False
        assert is_valid_email("user@") is False
        assert is_valid_email("") is False
    
    def test_sanitize_string(self):
        """Test string sanitization."""
        assert sanitize_string("  Hello World  ") == "Hello World"
        assert sanitize_string("Test\nString") == "Test String"
        assert sanitize_string("Multiple   Spaces") == "Multiple Spaces"
        assert sanitize_string("") == ""
        assert sanitize_string(None) == ""


class TestActivityUtilities:
    """Test activity-related utility functions."""
    
    def test_calculate_days_without_activity(self):
        """Test calculating days without activity."""
        from app.utils import calculate_days_without_activity
        
        # Activity 5 days ago
        last_activity_date = datetime.now() - timedelta(days=5)
        result = calculate_days_without_activity(last_activity_date)
        assert result == 5
        
        # Activity today
        result = calculate_days_without_activity(datetime.now())
        assert result == 0
        
        # No activity (None)
        result = calculate_days_without_activity(None)
        assert result == -1  # Or whatever default value is used
    
    def test_get_activity_status_icon(self):
        """Test getting icon for activity status."""
        from app.utils import get_activity_status_icon
        
        assert get_activity_status_icon("Completed") == "✓"
        assert get_activity_status_icon("In Progress") == "⚡"
        assert get_activity_status_icon("Planned") == "📅"
        assert get_activity_status_icon("Cancelled") == "✗"
        assert get_activity_status_icon("Unknown") == "?"


class TestDataValidation:
    """Test data validation utilities."""
    
    def test_validate_positive_number(self):
        """Test positive number validation."""
        from app.utils import validate_positive_number
        
        assert validate_positive_number(10) is True
        assert validate_positive_number(0.1) is True
        assert validate_positive_number(0) is False
        assert validate_positive_number(-5) is False
        assert validate_positive_number(None) is False
        assert validate_positive_number("10") is False  # Not a number
    
    def test_validate_percentage(self):
        """Test percentage validation."""
        from app.utils import validate_percentage
        
        assert validate_percentage(50) is True
        assert validate_percentage(0) is True
        assert validate_percentage(100) is True
        assert validate_percentage(101) is False
        assert validate_percentage(-1) is False
        assert validate_percentage(50.5) is True


class TestConversionUtilities:
    """Test data conversion utilities."""
    
    def test_convert_area_units(self):
        """Test area unit conversion."""
        from app.utils import convert_area_units
        
        # Hectares to square meters
        assert convert_area_units(1, "ha", "m2") == 10000
        
        # Square meters to hectares
        assert convert_area_units(10000, "m2", "ha") == 1
        
        # Same unit
        assert convert_area_units(100, "m2", "m2") == 100
    
    def test_convert_weight_units(self):
        """Test weight unit conversion."""
        from app.utils import convert_weight_units
        
        # Kilograms to grams
        assert convert_weight_units(1, "kg", "g") == 1000
        
        # Tons to kilograms
        assert convert_weight_units(1, "t", "kg") == 1000
        
        # Pounds to kilograms (approximate)
        result = convert_weight_units(1, "lb", "kg")
        assert 0.45 < result < 0.46
