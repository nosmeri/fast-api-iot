'use strict';

const toggleButton = document.querySelector('.navbar_toggleBtn');
const menu = document.querySelectorAll('.toggle_menu');
toggleButton.addEventListener('click', () => {
    menu.forEach(v => v.classList.toggle('active'))
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

async function fetchUser(params) {
    const navbar_login = document.querySelector(".navbar_login");
    const navbar_user = document.querySelector(".navbar_user");
    const navbar_username = navbar_user.querySelector(".user_name")
    const navbar_admin_link = document.querySelectorAll(".navbar_admin_link")
    const navbar_manager_link = document.querySelectorAll(".navbar_manager_link")

    const username = document.querySelectorAll(".user_name")

    try {
        const response = await fetch('/me');
        if (!response.ok) {
            navbar_user.remove()
            navbar_login.style = "";
            return;
        }
        const user = await response.json();

        navbar_login.remove();
        navbar_user.style = "";

        if (user.role == "admin") {
            navbar_admin_link.forEach(v => v.style.display = "block");
            navbar_username.style.color = "crimson";
        }
        if (user.role == "manager") {
            navbar_manager_link.forEach(v => v.style.display = "block");
            navbar_username.style.color = "lightgreen";
        }

        username.forEach(v => v.textContent = user.username);
    } catch (error) {
        console.error('요저 정보를 불러오는중 오류 발생:', error);
    }
}

window.addEventListener('DOMContentLoaded', fetchUser);

if ('serviceWorker' in navigator) {
    window.addEventListener('load', async () => {
        try {
            await navigator.serviceWorker.register('/service-worker.js');
        } catch (error) {
            console.error('서비스 워커 등록 실패:', error);
        }
    });
}