"""
Test suite for Calculator module

Run with: pytest test_calculator.py -v
"""

import pytest
from calculator import Calculator, AdvancedCalculator


# ============================================
# FIXTURES
# ============================================

@pytest.fixture
def calc():
    """Create a Calculator instance for tests"""
    return Calculator()


@pytest.fixture
def adv_calc():
    """Create an AdvancedCalculator instance"""
    return AdvancedCalculator(precision=4)


# ============================================
# BASIC TESTS
# ============================================

class TestCalculatorBasic:
    """Basic calculator operation tests"""
    
    def test_add_integers(self, calc):
        """Test addition with integers"""
        assert calc.add(2, 3) == 5
    
    def test_add_floats(self, calc):
        """Test addition with floats"""
        assert calc.add(2.5, 3.5) == 6.0
    
    def test_add_negative(self, calc):
        """Test addition with negative numbers"""
        assert calc.add(-1, 1) == 0
        assert calc.add(-1, -1) == -2
    
    def test_subtract(self, calc):
        """Test subtraction"""
        assert calc.subtract(10, 4) == 6
        assert calc.subtract(4, 10) == -6
    
    def test_multiply(self, calc):
        """Test multiplication"""
        assert calc.multiply(3, 4) == 12
        assert calc.multiply(-2, 3) == -6
        assert calc.multiply(0, 100) == 0
    
    def test_divide(self, calc):
        """Test division"""
        assert calc.divide(10, 2) == 5.0
        assert calc.divide(7, 2) == 3.5
    
    def test_divide_by_zero(self, calc):
        """Test division by zero raises error"""
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            calc.divide(10, 0)


# ============================================
# PARAMETERIZED TESTS
# ============================================

class TestParameterized:
    """Parameterized test examples"""
    
    @pytest.mark.parametrize("a,b,expected", [
        (1, 1, 2),
        (0, 0, 0),
        (-1, 1, 0),
        (100, 200, 300),
        (1.5, 2.5, 4.0),
    ])
    def test_add_various(self, calc, a, b, expected):
        """Test addition with various inputs"""
        assert calc.add(a, b) == expected
    
    @pytest.mark.parametrize("base,exp,expected", [
        (2, 3, 8),
        (5, 2, 25),
        (10, 0, 1),
        (2, 10, 1024),
    ])
    def test_power(self, calc, base, exp, expected):
        """Test power function"""
        assert calc.power(base, exp) == expected


# ============================================
# ADVANCED CALCULATOR TESTS
# ============================================

class TestAdvancedCalculator:
    """Tests for AdvancedCalculator"""
    
    def test_sqrt(self, adv_calc):
        """Test square root"""
        assert adv_calc.sqrt(4) == 2.0
        assert adv_calc.sqrt(2) == pytest.approx(1.4142, rel=1e-3)
    
    def test_sqrt_negative(self, adv_calc):
        """Test sqrt of negative raises error"""
        with pytest.raises(ValueError):
            adv_calc.sqrt(-1)
    
    def test_factorial(self, adv_calc):
        """Test factorial"""
        assert adv_calc.factorial(0) == 1
        assert adv_calc.factorial(5) == 120
        assert adv_calc.factorial(10) == 3628800
    
    def test_factorial_negative(self, adv_calc):
        """Test factorial of negative raises error"""
        with pytest.raises(ValueError):
            adv_calc.factorial(-1)
    
    def test_factorial_non_integer(self, adv_calc):
        """Test factorial of non-integer raises error"""
        with pytest.raises(TypeError):
            adv_calc.factorial(3.5)


# ============================================
# HISTORY TESTS
# ============================================

class TestHistory:
    """Tests for operation history"""
    
    def test_history_recorded(self, calc):
        """Test that operations are recorded"""
        calc.add(1, 2)
        calc.multiply(3, 4)
        
        assert len(calc.history) == 2
        assert "1 + 2 = 3" in calc.history[0]
    
    def test_clear_history(self, calc):
        """Test clearing history"""
        calc.add(1, 2)
        calc.subtract(5, 3)
        calc.clear_history()
        
        assert len(calc.history) == 0


# ============================================
# MARKERS
# ============================================

@pytest.mark.slow
def test_large_factorial(adv_calc):
    """Test factorial of large number (marked as slow)"""
    result = adv_calc.factorial(100)
    assert result > 10 ** 100


@pytest.mark.skip(reason="Feature not implemented yet")
def test_future_feature():
    """This test is skipped"""
    pass


@pytest.mark.skipif(
    True,  # Replace with actual condition
    reason="Condition not met"
)
def test_conditional_skip():
    """This test is conditionally skipped"""
    pass


# ============================================
# FIXTURES WITH YIELD (SETUP/TEARDOWN)
# ============================================

@pytest.fixture
def calc_with_history():
    """Fixture with setup and teardown"""
    # Setup
    calc = Calculator()
    calc.add(1, 2)
    calc.add(3, 4)
    
    yield calc
    
    # Teardown
    calc.clear_history()


def test_fixture_with_yield(calc_with_history):
    """Test using fixture with yield"""
    assert len(calc_with_history.history) == 2


# ============================================
# CONFTEST EXAMPLE (would be in conftest.py)
# ============================================
"""
# conftest.py - shared fixtures
import pytest

@pytest.fixture(scope="module")
def shared_calculator():
    '''Shared calculator for entire module'''
    return Calculator()

@pytest.fixture(scope="session")
def database_connection():
    '''Shared across all tests'''
    conn = create_connection()
    yield conn
    conn.close()
"""


# ============================================
# RUN TESTS
# ============================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
