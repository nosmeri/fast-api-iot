'use strict';
import { validatePassword } from "./validators.js";
import { handleFormSubmit, validateRequiredFields, validatePasswordConfirmation } from './form-utils.js';

const form = document.querySelector('#changePWForm');

// 비밀번호 변경 유효성 검사 함수
async function validateChangePassword(data) {
    // 필수 필드 검사
    if (!validateRequiredFields(data, ['currentPassword', 'newPassword', 'confirmPassword'])) {
        return false;
    }

    // 새 비밀번호 유효성 검사
    if (!(await validatePassword(data.newPassword))) {
        return false;
    }

    // 비밀번호 확인 검사
    if (!validatePasswordConfirmation(data.newPassword, data.confirmPassword)) {
        return false;
    }

    return true;
}

// 비밀번호 변경 성공 처리 함수
function handleChangePasswordSuccess(response) {
    alert('비밀번호가 성공적으로 변경되었습니다.');
    window.location.href = '/';
}

// 비밀번호 변경 에러 처리 함수
function handleChangePasswordError(response) {
    if (response.status === 400) {
        alert('비밀번호 변경에 실패했습니다. 현재 비밀번호를 확인해주세요.');
    } else {
        alert('비밀번호 변경 요청에 실패했습니다.');
    }
}

form.addEventListener('submit', async (event) => {
    event.preventDefault();
    await handleFormSubmit(
        form,
        '/changepw',
        'PUT',
        validateChangePassword,
        handleChangePasswordSuccess,
        handleChangePasswordError
    );
});