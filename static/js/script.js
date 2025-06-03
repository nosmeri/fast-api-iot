'use strict';

const toggleButton = document.querySelector('.navbar_toggleBtn');
const menu = document.querySelectorAll('.toggle_menu');
toggleButton.addEventListener('click', () => {
    for (let i = 0; i < menu.length; i++) {
        menu[i].classList.toggle('active');
    }
})