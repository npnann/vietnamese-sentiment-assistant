from typing import Tuple

def validate_input(text: str) -> Tuple[bool, str]:
    if not text or not text.strip():
        return False, "Vui lòng nhập nội dung"
    
    stripped_text = text.strip()
    
    if len(stripped_text) < 5:
        return False, "Câu quá ngắn (tối thiểu 5 ký tự)"
    
    if len(stripped_text) > 50:
        return False, "Câu quá dài (tối đa 50 ký tự)"
    
    return True, ""