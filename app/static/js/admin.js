'use strict';

async function fetchAndRenderUsers() {
    try {
        const response = await fetch('/admin/user');
        if (!response.ok) throw new Error('관리자 정보를 불러오지 못했습니다.');
        const data = await response.json();
        // 사용자 목록 렌더링
        const userList = document.getElementById('user-list');
        userList.innerHTML = '';
        data.users.forEach(u => {
            const li = document.createElement('li');

            const nameColor = u.role === 'admin' ? 'red' : (u.role === 'manager' ? 'yellow' : 'white');

            li.innerHTML = `
                <button class="modify-button" id="${u.id}">modify</button>
                <button class="delete-button" id="${u.id}">delete</button>
                ${u.id} ${u.username}
                <span style=\"color: ${nameColor};\">${u.role}</span>
            `;
            userList.appendChild(li);
        });
        addEventListenersToButtons();
    } catch (e) {
        alert('관리자/사용자 정보를 불러오지 못했습니다.');
    }
}

window.addEventListener('DOMContentLoaded', fetchAndRenderUsers);

function addEventListenersToButtons() {
    const modifyButtons = document.querySelectorAll('.modify-button');
    const deleteButtons = document.querySelectorAll('.delete-button');
    const userModifyForm = document.querySelector('#userModifyForm');
    modifyButtons.forEach(button => {
        button.addEventListener('click', async (event) => {
            const id = button.getAttribute('id');
            const formData = new FormData(userModifyForm);
            const attribute = formData.get('attribute').trim();
            const value = formData.get('value').trim();
            const type = formData.get('type');
            if (!type) {
                alert('수정할 타입을 선택해주세요.');
                return;
            }
            if (!attribute || !value) {
                alert('수정할 속성과 값을 입력해주세요.');
                return;
            }
            try {
                const response = await fetch(`/admin/user`, {
                    method: 'PUT',
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        "userid": id,
                        "attr": attribute,
                        "attr_type": type,
                        "value": value
                    })

                });
                if (response.ok) {
                    fetchAndRenderUsers();
                } else {
                    alert('수정 요청에 실패했습니다.');
                }
            } catch (error) {
                console.error('수정 요청 중 오류 발생:', error);
                alert('수정 요청 중 오류가 발생했습니다. 나중에 다시 시도해주세요.');
                return;
            }
        });
    });
    deleteButtons.forEach(button => {
        button.addEventListener('click', async (event) => {
            const id = button.getAttribute('id');
            if (confirm('정말로 삭제하시겠습니까?')) {
                try {
                    const response = await fetch(`/admin/user?userid=${id}`, {
                        method: 'DELETE'
                    });
                    if (response.ok) {
                        fetchAndRenderUsers();
                    } else {
                        alert('삭제 요청에 실패했습니다. 나중에 다시 시도해주세요.');
                    }
                } catch (error) {
                    console.error('삭제 요청 중 오류 발생:', error);
                    alert('삭제 요청 중 오류가 발생했습니다. 나중에 다시 시도해주세요.');
                }
            }
        });
    });
}