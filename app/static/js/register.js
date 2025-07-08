'use strict';
import { validateUserCredentials } from './validators.js';
import { handleFormSubmit, validateRequiredFields, validatePasswordConfirmation } from './form-utils.js';

const form = document.querySelector('#registerForm');

// 회원가입 유효성 검사 함수
async function validateRegister(data) {
    // 필수 필드 검사
    if (!validateRequiredFields(data, ['username', 'password', 'confirmPassword'])) {
        return false;
    }

    // 사용자명/비밀번호 유효성 검사
    if (!(await validateUserCredentials(data.username, data.password))) {
        return false;
    }

    // 비밀번호 확인 검사
    if (!validatePasswordConfirmation(data.password, data.confirmPassword)) {
        return false;
    }

    return true;
}

// 회원가입 에러 처리 함수
function handleRegisterError(response) {
    if (response.status === 400) {
        alert('이미 존재하는 아이디입니다. 다른 아이디를 사용해주세요.');
    } else {
        alert('회원가입 요청에 실패했습니다.');
    }
}

form.addEventListener('submit', async (event) => {
    event.preventDefault();
    await handleFormSubmit(
        form,
        '/register',
        'POST',
        validateRegister,
        null,
        handleRegisterError
    );
});
