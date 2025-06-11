const form = document.querySelector('#loginForm');
form.addEventListener('submit', async (event) => {
    event.preventDefault();
    submitButton.disabled = true;

    const formData = new FormData(form);
    const username = formData.get('username').trim();
    const password = formData.get('password').trim();
    const data = {
        username: username,
        password: password
    }

    if (!username || !password) {
        alert('아이디와 비밀번호를 입력해주세요.');
        submitButton.disabled = false;
        return;
    }

    try {
        const response = await fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
        });

        if (response.ok) {
        window.location.href = '/';
        } else {
        alert('로그인 실패. 아이디와 비밀번호를 확인해주세요.');
        submitButton.disabled = false;
        }
    } catch (error) {
        console.error('로그인 요청 중 오류 발생:', error);
        alert('로그인 요청 중 오류가 발생했습니다. 나중에 다시 시도해주세요.');
        submitButton.disabled = false;
    }
});