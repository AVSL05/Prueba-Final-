import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_basic_import():
    """Test basic imports work"""
    try:
        from app.models import User, Donor, UserRole, BloodType
        assert User is not None
        assert Donor is not None
        assert UserRole is not None
        assert BloodType is not None
        print("Basic imports successful")
    except Exception as e:
        pytest.fail(f"Import failed: {e}")

def test_password_validation():
    """Test password validation utility"""
    try:
        from app.utils.auth import AuthUtils
        
        # Test valid password
        valid, msg = AuthUtils.validate_password('Password123!')
        assert valid is True
        
        # Test invalid password
        valid, msg = AuthUtils.validate_password('weak')
        assert valid is False
        assert 'caracteres' in msg
        
        print("Password validation works")
    except Exception as e:
        pytest.fail(f"Password validation failed: {e}")

if __name__ == "__main__":
    test_basic_import()
    test_password_validation()
    print("All basic tests passed!")