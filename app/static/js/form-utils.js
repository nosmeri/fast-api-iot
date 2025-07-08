'use strict';

/**
 * 폼 제출을 처리하는 공통 함수
 * @param {HTMLFormElement} form - 제출할 폼 요소
 * @param {string} url - 요청할 URL
 * @param {string} method - HTTP 메서드 (기본값: 'POST')
 * @param {Function} validator - 유효성 검사 함수 (선택사항)
 * @param {Function} successCallback - 성공 시 콜백 함수 (선택사항)
 * @param {Function} errorCallback - 에러 시 콜백 함수 (선택사항)
 */
export async function handleFormSubmit(
    form,
    url,
    method = 'POST',
    validator = null,
    successCallback = null,
    errorCallback = null
) {
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;

    try {
        // 버튼 비활성화
        submitButton.disabled = true;
        submitButton.textContent = '처리 중...';

        const formData = new FormData(form);
        const data = {};

        // FormData를 객체로 변환
        for (const [key, value] of formData.entries()) {
            data[key] = value.trim();
        }

        // 유효성 검사
        if (validator) {
            const isValid = await validator(data);
            if (!isValid) {
                submitButton.disabled = false;
                submitButton.textContent = originalText;
                return;
            }
        }

        // API 요청
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            if (successCallback) {
                successCallback(response);
            } else {
                // 기본 성공 처리
                window.location.href = '/';
            }
        } else {
            if (errorCallback) {
                errorCallback(response);
            } else {
                // 기본 에러 처리
                const errorData = await response.json().catch(() => ({}));
                alert(errorData.detail || '요청에 실패했습니다.');
            }
        }

    } catch (error) {
        console.error('요청 중 오류 발생:', error);
        if (errorCallback) {
            errorCallback(null, error);
        } else {
            alert('요청 중 오류가 발생했습니다. 나중에 다시 시도해주세요.');
        }
    } finally {
        // 버튼 상태 복원
        submitButton.disabled = false;
        submitButton.textContent = originalText;
    }
}

/**
 * 간단한 필드 유효성 검사
 * @param {Object} data - 검사할 데이터 객체
 * @param {Array} requiredFields - 필수 필드 배열
 * @returns {boolean} 유효성 여부
 */
export function validateRequiredFields(data, requiredFields) {
    for (const field of requiredFields) {
        if (!data[field] || data[field].trim() === '') {
            alert(`${field}을(를) 입력해주세요.`);
            return false;
        }
    }
    return true;
}

/**
 * 비밀번호 확인 검사
 * @param {string} password - 비밀번호
 * @param {string} confirmPassword - 확인 비밀번호
 * @returns {boolean} 일치 여부
 */
export function validatePasswordConfirmation(password, confirmPassword) {
    if (password !== confirmPassword) {
        alert('비밀번호와 확인 비밀번호가 일치하지 않습니다.');
        return false;
    }
    return true;
} 