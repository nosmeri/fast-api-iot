'use strict';

const toggleButton = document.querySelector('.navbar_toggleBtn');
const menu = document.querySelectorAll('.toggle_menu');
toggleButton.addEventListener('click', () => {
    for (let i = 0; i < menu.length; i++) {
        menu[i].classList.toggle('active');
    }
})

const navbarLogoutBtn = document.getElementById('navbarLogoutBtn');
if (navbarLogoutBtn) {
    navbarLogoutBtn.addEventListener('click', async (event) => {
        event.preventDefault();
        try {
            const response = await fetch('/logout', {
                method: 'POST',
                credentials: 'same-origin'
            });
            if (response.ok) {
                window.location.href = '/';
            } else {
                alert('로그아웃에 실패했습니다.');
            }
        } catch (error) {
            alert('로그아웃 중 오류가 발생했습니다.');
        }
    });
}