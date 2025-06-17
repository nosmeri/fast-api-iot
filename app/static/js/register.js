import { validateUsername, validatePassword } from './validators.js';

const form = document.querySelector('#registerForm');
const submitButton = form.querySelector('button[type="submit"]');

form.addEventListener('submit', async (event) => {
    event.preventDefault();
    submitButton.disabled = true;

    const formData = new FormData(form);
    const username = formData.get('username').trim();
    const password = formData.get('password').trim();
    const confirmPassword = formData.get('confirmPassword').trim();
    const data = {
        username: username,
        password: password
    }

    if (!username || !password) {
        alert('아이디와 비밀번호를 입력해주세요.');
        submitButton.disabled = false;
        return;
    }

    if (!validateUsername(username)) {
        alert('아이디는 영문, 숫자, 하이픈(-)만 사용할 수 있으며, 하이픈으로 시작하거나 끝날 수 없습니다.');
        submitButton.disabled = false;
        return;
    }
    if (!validatePassword(password)) {

        submitButton.disabled = false;
        return;
    }

    if (password !== confirmPassword) {
        alert('비밀번호와 확인 비밀번호가 일치하지 않습니다.');
        submitButton.disabled = false;
        return;
    }
    
    try {
        const response = await fetch('/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
        });

        if (response.ok) {
        window.location.href = '/';
        } else {
        alert('이미 존재하는 아이디입니다. 다른 아이디를 사용해주세요.');
        submitButton.disabled = false;
        }
    } catch (error) {
        console.error('회원가입 요청 중 오류 발생:', error);
        alert('회원가입 요청 중 오류가 발생했습니다. 나중에 다시 시도해주세요.');
        submitButton.disabled = false;
    }
});
