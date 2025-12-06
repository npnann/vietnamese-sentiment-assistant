import re
from typing import Dict

import underthesea


ABBREVIATION_DICT: Dict[str, str] = {
    "ko": "không",
    "k": "không",
    "dc": "được",
    "đc": "được",
    "ntn": "như thế nào",
    "bn": "bao nhiêu",
    "j": "gì",
    "m": "mình",
    "mik": "mình",
    "t": "tôi",
    "tg": "thời gian",
    "vs": "với",
    "ck": "chồng",
    "vk": "vợ",
    "ad": "admin",
    "shop": "cửa hàng",
    "sp": "sản phẩm",
    "sl": "số lượng",
    "ship": "giao hàng",
    "ok": "được",
    "oke": "được",
    "okla": "được",
    "nt": "nhắn tin",
    "ib": "nhắn tin",
    "fix": "sửa",
    "share": "chia sẻ",
    "thanks": "cảm ơn",
    "thx": "cảm ơn",
    "plz": "làm ơn",
    "pls": "làm ơn",
    "nhiu": "nhiều"
}


NON_DIACRITIC_DICT: Dict[str, str] = {
    "khong": "không",
    "duoc": "được",
    "tot": "tốt",
    "rat": "rất",
    "it": "ít",
    "neu": "nếu",
    "biet": "biết",
    "chac": "chắc",
    "giua": "giữa",
    "hoac": "hoặc",
    "luon": "luôn",
    "muon": "muốn",
    "nhu": "như",
    "roi": "rồi",
    "tren": "trên",
    "truoc": "trước",
    "vao": "vào",
    "viec": "việc",
    "hom": "hôm",
    "buon": "buồn"
}

COMBINED_NORMALIZATION_DICT: Dict[str, str] = {**ABBREVIATION_DICT, **NON_DIACRITIC_DICT}


def _word_tokenize(text: str) -> str:
    tokenized = underthesea.word_tokenize(text, format="text")
    return tokenized


def _apply_case_pattern(original: str, replacement: str) -> str:
    if original.isupper():
        return replacement.upper()
    elif original.islower():
        return replacement.lower()
    elif original and original[0].isupper():
        return replacement.capitalize()
    else:
        return replacement


def _normalize_all(text: str) -> str:
    words = text.split()
    result = []
    
    for word in words:
        lower_word = word.lower()
        if lower_word in COMBINED_NORMALIZATION_DICT:
            replacement = COMBINED_NORMALIZATION_DICT[lower_word]
            result.append(_apply_case_pattern(word, replacement))
        else:
            result.append(word)
    
    return " ".join(result)


def _clean_text(text: str) -> str:
    cleaned_text = text.strip()
    
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    
    return cleaned_text


def preprocess(text: str) -> str:
    if not isinstance(text, str):
        raise ValueError("Input text must be a string")
    
    if not text.strip():
        return ""

    processed_text = _clean_text(text)

    processed_text = _normalize_all(processed_text)
    
    processed_text = _word_tokenize(processed_text)
    
    return processed_text