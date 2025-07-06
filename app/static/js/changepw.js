'use strict';
import { validatePassword } from "./validators.js";

const form = document.querySelector('#changePWForm');
const submitButton = form.querySelector('button[type="submit"]');

form.addEventListener('submit', async (event) => {
    event.preventDefault();
    submitButton.disabled = true;

    const formData = new FormData(form);
    const currentPassword = formData.get('currentPassword').trim();
    const newPassword = formData.get('newPassword').trim();
    const confirmPassword = formData.get('confirmPassword').trim();

    if (!currentPassword || !newPassword || !confirmPassword) {
        alert('모든 필드를 입력해주세요.');
        submitButton.disabled = false;
        return;
    }

    if (!validatePassword(newPassword)) {
        submitButton.disabled = false;
        return;
    }


    if (newPassword !== confirmPassword) {
        alert('새 비밀번호와 확인 비밀번호가 일치하지 않습니다.');
        submitButton.disabled = false;
        return;
    }

    try {
        const response = await fetch('/changepw', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                currentPassword: currentPassword,
                newPassword: newPassword
            })
        });

        if (response.ok) {
            alert('비밀번호가 성공적으로 변경되었습니다.');
            window.location.href = '/';
        } else {
            alert('비밀번호 변경에 실패했습니다. 현재 비밀번호를 확인해주세요.');
            submitButton.disabled = false;
        }
    } catch (error) {
        console.error('비밀번호 변경 요청 중 오류 발생:', error);
        alert('비밀번호 변경 요청 중 오류가 발생했습니다. 나중에 다시 시도해주세요.');
        submitButton.disabled = false;
    }
});