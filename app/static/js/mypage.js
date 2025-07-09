'use strict';

const deleteAccount = document.getElementById('deleteAccount');
deleteAccount.addEventListener('click', async (event) => {
    event.preventDefault();

    if (!confirm('정말 회원탈퇴하시겠습니까?')) {
        return;
    }

    try {
        const response = await fetch('/delete_account', {
            method: 'DELETE'
        });
        if (response.ok) {
            window.location.href = '/';
        } else {
            alert('회원탈퇴에 실패했습니다.');
        }
    } catch (error) {
        console.error('회원탈퇴 중 오류 발생:', error);
        alert('회원탈퇴 중 오류가 발생했습니다. 나중에 다시 시도해주세요.');
    }
});