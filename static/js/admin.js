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
            const response = await fetch(`/admin/modify?userid=${id}&attr=${attribute}&value=${value}&type=${type}`, {
                method: 'POST'
            });
            if (response.ok) {
                saveLocalStorage();
                window.location.reload();
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
                const response = await fetch(`/admin/delete?userid=${id}`, {
                    method: 'DELETE'
                });
                if (response.ok) {
                    saveLocalStorage();
                    window.location.reload();
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

function saveLocalStorage() {
    const formData = new FormData(userModifyForm);
    const attribute = formData.get('attribute').trim();
    const value = formData.get('value').trim();
    const type = formData.get('type');
    
    localStorage.setItem('admin_modify_attribute', attribute);
    localStorage.setItem('admin_modify_value', value);
    localStorage.setItem('admin_modify_type', type);
}

window.addEventListener('DOMContentLoaded', () => {
    const attribute = localStorage.getItem('admin_modify_attribute');
    const value = localStorage.getItem('admin_modify_value');
    const type = localStorage.getItem('admin_modify_type');
    if (attribute !== null) userModifyForm.querySelector('input[name="attribute"]').value = attribute;
    if (value !== null) userModifyForm.querySelector('input[name="value"]').value = value;
    if (type !== null) {
        const typeInput = userModifyForm.querySelector(`input[name="type"][value="${type}"]`);
        if (typeInput) typeInput.checked = true;
    }
    // 복원 후 localStorage 값 삭제
    localStorage.removeItem('admin_modify_attribute');
    localStorage.removeItem('admin_modify_value');
    localStorage.removeItem('admin_modify_type');
});