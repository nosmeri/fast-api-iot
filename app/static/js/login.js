'use strict';
import { handleFormSubmit, validateRequiredFields } from './form-utils.js';

const form = document.querySelector('#loginForm');

// 로그인 유효성 검사 함수
async function validateLogin(data) {
    return validateRequiredFields(data, ['username', 'password']);
}

// 로그인 에러 처리 함수
function handleLoginError(response) {
    if (response.status === 400) {
        alert('로그인 실패. 아이디와 비밀번호를 확인해주세요.');
    } else {
        alert('로그인 요청에 실패했습니다.');
    }
}

form.addEventListener('submit', async (event) => {
    event.preventDefault();
    await handleFormSubmit(
        form,
        '/login',
        'POST',
        validateLogin,
        null,
        handleLoginError
    );
});