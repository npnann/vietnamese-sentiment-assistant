import pytest

from modules.preprocessing import (
    preprocess,
    _word_tokenize,
    _normalize_abbreviations,
    _normalize_non_diacritic,
    _clean_text,
    ABBREVIATION_DICT,
    NON_DIACRITIC_DICT
)


class TestWordTokenization:

    def test_basic_tokenization(self):
        text = "Tôi thích học tiếng Việt"
        result = _word_tokenize(text)
        assert "Tôi" in result
        assert "thích" in result
        assert "học" in result
        assert "tiếng" in result
        assert "Việt" in result

    def test_empty_text(self):
        result = _word_tokenize("")
        assert result == ""

    def test_tokenization_with_punctuation(self):
        text = "Rất tốt! Tôi rất thích."
        result = _word_tokenize(text)
        assert "Rất" in result
        assert "tốt" in result
        assert "Tôi" in result
        assert "rất" in result
        assert "thích" in result


class TestAbbreviationNormalization:

    def test_common_abbreviations(self):
        text = "ko dc ntn bn"
        result = _normalize_abbreviations(text)
        assert "không" in result
        assert "được" in result
        assert "như thế nào" in result
        assert "bao nhiêu" in result

    def test_mixed_case_abbreviations(self):
        text = "KO DC K"
        result = _normalize_abbreviations(text)
        assert "không" in result
        assert "được" in result
        assert "không" in result

    def test_no_abbreviations(self):
        text = "Tôi thích học tiếng Việt"
        result = _normalize_abbreviations(text)
        assert result == text

    def test_partial_word_abbreviations(self):
        text = "tokyo kodak"
        result = _normalize_abbreviations(text)
        assert "tokyo" in result
        assert "kodak" in result


class TestNonDiacriticNormalization:

    def test_basic_normalization(self):
        text = "khong duoc tot rat"
        result = _normalize_non_diacritic(text)
        assert "không" in result
        assert "được" in result
        assert "tốt" in result
        assert "rất" in result

    def test_mixed_case_normalization(self):
        text = "KHONG DUOC TOT RAT"
        result = _normalize_non_diacritic(text)
        assert "KHÔNG" in result or "không" in result
        assert "ĐƯỢC" in result or "được" in result
        assert "TỐT" in result or "tốt" in result
        assert "RẤT" in result or "rất" in result

    def test_no_normalization_needed(self):
        text = "không được tốt rất"
        result = _normalize_non_diacritic(text)
        assert result == text

    def test_partial_word_normalization(self):
        text = "tokyo totoro"
        result = _normalize_non_diacritic(text)
        assert "tokyo" in result
        assert "totoro" in result


class TestTextCleaning:

    def test_lowercase_conversion(self):
        text = "TÔI THÍCH HỌC TIẾNG VIỆT"
        result = _clean_text(text)
        assert result.islower()

    def test_whitespace_trimming(self):
        text = "   Tôi thích học tiếng Việt   "
        result = _clean_text(text)
        assert not result.startswith(" ")
        assert not result.endswith(" ")

    def test_multiple_whitespace_normalization(self):
        text = "Tôi    thích     học    tiếng   Việt"
        result = _clean_text(text)
        assert "  " not in result
        assert "tôi thích học tiếng việt" == result

    def test_emoji_preservation(self):
        text = "Tôi thích học 😊👍"
        result = _clean_text(text)
        assert "😊" in result
        assert "👍" in result

    def test_empty_text(self):
        result = _clean_text("")
        assert result == ""

    def test_whitespace_only_text(self):
        result = _clean_text("   \t\n   ")
        assert result == ""


class TestMainPreprocessFunction:

    def test_complete_pipeline(self):
        text = "KO dc tot rat! 😊"
        result = preprocess(text)
        assert "không" in result
        assert "được" in result
        assert "tốt" in result
        assert "rất" in result
        assert "😊" in result
        assert result.islower()

    def test_empty_string(self):
        result = preprocess("")
        assert result == ""

    def test_whitespace_only(self):
        result = preprocess("   \t\n   ")
        assert result == ""

    def test_already_processed_text(self):
        text = "không được tốt rất"
        result = preprocess(text)
        assert "không" in result
        assert "được" in result
        assert "tốt" in result
        assert "rất" in result

    def test_invalid_input_type(self):
        with pytest.raises(ValueError):
            preprocess(123)
        with pytest.raises(ValueError):
            preprocess(None)
        with pytest.raises(ValueError):
            preprocess(["text"])

    def test_complex_vietnamese_text(self):
        text = "Ko bn ntn? Mình k dc đi chơi vs bn dc ko? Thx nhiu! 😢"
        result = preprocess(text)
        assert "không" in result
        assert "bao nhiêu" in result
        assert "như thế nào" in result
        assert "được" in result
        assert "cảm ơn" in result or "thx" in result
        assert "😢" in result


class TestDictionaryContent:

    def test_abbreviation_dict_size(self):
        assert len(ABBREVIATION_DICT) >= 20
        assert len(ABBREVIATION_DICT) <= 35

    def test_non_diacritic_dict_size(self):
        assert len(NON_DIACRITIC_DICT) >= 15
        assert len(NON_DIACRITIC_DICT) <= 30

    def test_common_abbreviations_present(self):
        common_abbrs = ["ko", "k", "dc", "ntn", "bn", "j", "m", "t"]
        for abbr in common_abbrs:
            assert abbr in ABBREVIATION_DICT

    def test_common_non_diacritics_present(self):
        common_words = ["khong", "duoc", "tot", "rat", "it"]
        for word in common_words:
            assert word in NON_DIACRITIC_DICT

    def test_abbreviation_values_are_valid(self):
        for key, value in ABBREVIATION_DICT.items():
            assert isinstance(value, str)
            assert len(value) > 0
            assert any(char in value for char in "àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ") or value.isascii()

    def test_non_diacritic_values_are_valid(self):
        for key, value in NON_DIACRITIC_DICT.items():
            assert isinstance(value, str)
            assert len(value) > 0
            assert any(char in value for char in "àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ")


class TestEdgeCases:

    def test_very_long_text(self):
        long_text = "ko " * 1000
        result = preprocess(long_text)
        assert "không" in result
        assert len(result) > 0

    def test_special_characters(self):
        text = "ko dc! @#$%^&*()_+-=[]{}|;':\",./<>?"
        result = preprocess(text)
        assert "không" in result
        assert "được" in result

    def test_numbers_in_text(self):
        text = "ko dc 123 tot rat 456"
        result = preprocess(text)
        assert "không" in result
        assert "được" in result
        assert "tốt" in result
        assert "rất" in result
        assert "123" in result
        assert "456" in result

    def test_mixed_languages(self):
        text = "ko dc tot rat hello world"
        result = preprocess(text)
        assert "không" in result
        assert "được" in result
        assert "tốt" in result
        assert "rất" in result
        assert "hello" in result
        assert "world" in result