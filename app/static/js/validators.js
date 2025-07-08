'use strict';

// 서버에서 유효성 검사 규칙을 가져오는 함수
async function fetchValidationRules() {
    try {
        const response = await fetch('/validation-rules');
        if (response.ok) {
            return await response.json();
        }
    } catch (error) {
        console.error('유효성 검사 규칙을 가져오는데 실패했습니다:', error);
        alert('유효성 검사 규칙을 가져오는데 실패했습니다.');
        return null;
    }
}

// 유효성 검사 규칙을 캐시
let cachedValidationRules = null;

// 유효성 검사 규칙을 가져오는 함수 (캐시 사용)
async function getValidationRules() {
    if (!cachedValidationRules) {
        cachedValidationRules = await fetchValidationRules();
    }
    return cachedValidationRules;
}

export async function validateUsername(username) {
    const rules = await getValidationRules();

    username = username.trim();

    if (!username) {
        alert('사용자명을 입력해주세요.');
        return false;
    }

    // 길이 검사
    if (username.length < rules.username.min_length) {
        alert(`사용자명은 최소 ${rules.username.min_length}자 이상이어야 합니다.`);
        return false;
    }

    if (username.length > rules.username.max_length) {
        alert(`사용자명은 최대 ${rules.username.max_length}자까지 가능합니다.`);
        return false;
    }

    // 정규식 검사
    const regex = new RegExp(rules.username.regex);
    if (!regex.test(username)) {
        alert(rules.username.description);
        return false;
    }

    return true;
}

export async function validatePassword(password) {
    const rules = await getValidationRules();

    if (!password) {
        alert('비밀번호를 입력해주세요.');
        return false;
    }

    // 길이 검사
    if (password.length < rules.password.min_length) {
        alert(`비밀번호는 최소 ${rules.password.min_length}자 이상이어야 합니다.`);
        return false;
    }

    if (password.length > rules.password.max_length) {
        alert(`비밀번호는 최대 ${rules.password.max_length}자까지 가능합니다.`);
        return false;
    }

    // 숫자 포함 여부
    if (rules.password.require_numbers) {
        if (!/[0-9]/.test(password)) {
            alert(rules.password.description);
            return false;
        }
    }

    // 알파벳 포함 여부
    if (rules.password.require_alphabets) {
        if (!/[a-zA-Z]/.test(password)) {
            alert(rules.password.description);
            return false;
        }
    }

    // 특수문자 포함 여부
    if (rules.password.require_special_chars) {
        const specialCharsRegex = new RegExp(`[${rules.password.special_chars.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}]`);
        if (!specialCharsRegex.test(password)) {
            alert(rules.password.description);
            return false;
        }
    }

    return true;
}

export async function validateUserCredentials(username, password) {
    const usernameValid = await validateUsername(username);
    const passwordValid = await validatePassword(password);

    return usernameValid && passwordValid;
}