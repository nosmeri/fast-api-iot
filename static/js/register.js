const form = document.querySelector('#registerForm');
form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const formData = new FormData(form);
    const username = formData.get('username').trim();
    const password = formData.get('password').trim();
    const data = {
        username: username,
        password: password
    }

    if (!username || !password) {
        event.preventDefault();
        alert('아이디와 비밀번호를 입력해주세요.');
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
        }
    } catch (error) {
        console.error('회원가입 요청 중 오류 발생:', error);
        alert('회원가입 요청 중 오류가 발생했습니다. 나중에 다시 시도해주세요.');
    }
});

// TODO: 추가적인 유효성 검사
// 예: 비밀번호 길이, 특수문자 포함 여부 등