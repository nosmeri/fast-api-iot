import re
from typing import Dict, List, Tuple

# 유효성 검사 규칙 정의
VALIDATION_RULES = {
    "username": {
        "regex": r"^(?!-)(?!.*--)[A-Za-z0-9-]+(?<!-)$",
        "min_length": 3,
        "max_length": 20,
        "description": "영문, 숫자, 하이픈(-)만 사용 가능하며, 하이픈으로 시작하거나 끝날 수 없고, 연속된 하이픈은 허용되지 않습니다.",
    },
    "password": {
        "min_length": 8,
        "max_length": 100,
        "require_numbers": True,
        "require_alphabets": True,
        "require_special_chars": True,
        "special_chars": '!@#$%^&*(),.?":{}|<>',
        "description": "최소 8자 이상, 숫자, 알파벳, 특수문자를 포함해야 합니다.",
    },
}


def validate_username(username: str) -> Tuple[bool, str]:
    """
    사용자명 유효성 검사

    Args:
        username: 검사할 사용자명

    Returns:
        (is_valid, error_message): 유효성 여부와 에러 메시지
    """
    if not username:
        return False, "사용자명을 입력해주세요."

    username = username.strip()

    # 길이 검사
    if len(username) < VALIDATION_RULES["username"]["min_length"]:
        return (
            False,
            f"사용자명은 최소 {VALIDATION_RULES['username']['min_length']}자 이상이어야 합니다.",
        )

    if len(username) > VALIDATION_RULES["username"]["max_length"]:
        return (
            False,
            f"사용자명은 최대 {VALIDATION_RULES['username']['max_length']}자까지 가능합니다.",
        )

    # 정규식 검사
    if not re.match(VALIDATION_RULES["username"]["regex"], username):
        return False, VALIDATION_RULES["username"]["description"]

    return True, ""


def validate_password(password: str) -> Tuple[bool, str]:
    """
    비밀번호 유효성 검사

    Args:
        password: 검사할 비밀번호

    Returns:
        (is_valid, error_message): 유효성 여부와 에러 메시지
    """
    if not password:
        return False, "비밀번호를 입력해주세요."

    # 길이 검사
    if len(password) < VALIDATION_RULES["password"]["min_length"]:
        return (
            False,
            f"비밀번호는 최소 {VALIDATION_RULES['password']['min_length']}자 이상이어야 합니다.",
        )

    if len(password) > VALIDATION_RULES["password"]["max_length"]:
        return (
            False,
            f"비밀번호는 최대 {VALIDATION_RULES['password']['max_length']}자까지 가능합니다.",
        )

    # 숫자 포함 여부
    if VALIDATION_RULES["password"]["require_numbers"]:
        if not any(char.isdigit() for char in password):
            return False, "비밀번호는 숫자를 포함해야 합니다."

    # 알파벳 포함 여부
    if VALIDATION_RULES["password"]["require_alphabets"]:
        if not any(char.isalpha() for char in password):
            return False, "비밀번호는 알파벳을 포함해야 합니다."

    # 특수문자 포함 여부
    if VALIDATION_RULES["password"]["require_special_chars"]:
        special_chars = VALIDATION_RULES["password"]["special_chars"]
        if not any(char in special_chars for char in password):
            return False, "비밀번호는 특수문자를 포함해야 합니다."

    return True, ""


def validate_user_credentials(username: str, password: str) -> Tuple[bool, List[str]]:
    """
    사용자명과 비밀번호를 함께 검사

    Args:
        username: 사용자명
        password: 비밀번호

    Returns:
        (is_valid, error_messages): 유효성 여부와 에러 메시지 리스트
    """
    errors = []

    username_valid, username_error = validate_username(username)
    if not username_valid:
        errors.append(username_error)

    password_valid, password_error = validate_password(password)
    if not password_valid:
        errors.append(password_error)

    return len(errors) == 0, errors


def get_validation_rules() -> Dict:
    """
    프론트엔드에서 사용할 수 있도록 유효성 검사 규칙을 반환
    """
    return VALIDATION_RULES
