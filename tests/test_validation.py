import pytest

from modules.validation import validate_input


class TestValidateInput:

    def test_empty_input(self):
        is_valid, error = validate_input("")
        assert is_valid is False
        assert "Vui lòng nhập nội dung" in error

    def test_whitespace_only(self):
        is_valid, error = validate_input("   ")
        assert is_valid is False
        assert "Vui lòng nhập nội dung" in error

    def test_too_short(self):
        is_valid, error = validate_input("abc")
        assert is_valid is False
        assert "tối thiểu 5 ký tự" in error

    def test_too_long(self):
        is_valid, error = validate_input("a" * 51)
        assert is_valid is False
        assert "tối đa 50 ký tự" in error

    def test_valid_input(self):
        is_valid, error = validate_input("Sản phẩm rất tốt")
        assert is_valid is True
        assert error == ""

    def test_boundary_min(self):
        is_valid, error = validate_input("abcde")
        assert is_valid is True

    def test_boundary_max(self):
        is_valid, error = validate_input("a" * 50)
        assert is_valid is True
