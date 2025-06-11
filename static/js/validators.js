export function validateUsername(username) {
    const regex = /^(?!-)(?!.*--)[A-Za-z0-9-]+(?<!-)$/;
    return regex.test(username);
}

export function validatePassword(password) {
    if (password.length < 8) {
        alert('비밀번호는 최소 8자 이상이어야 합니다.');
        return false;
    }
    
    const hasNumber = /[0-9]/.test(password);
    const hasAlphabet = /[a-zA-Z]/.test(password);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

    if (!hasNumber || !hasAlphabet || !hasSpecialChar) {
        alert('비밀번호는 숫자, 알파벳, 특수문자를 포함해야 합니다.');
        return false;
    }

    return true;
}