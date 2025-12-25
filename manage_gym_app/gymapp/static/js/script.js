
function showToast(message, type = 'success') {
    const toastElement = document.getElementById('liveToast');
    const toastBody = document.getElementById('toast-message');

    toastBody.innerText = message;

    toastElement.className = `toast align-items-center border-0 text-white bg-${type}`;

    const toast = new bootstrap.Toast(toastElement, {
        delay: 3000,
        animation: true
    });

    toast.show();
}

function showConfirmDialog(title, message, callback) {
    const modalEl = document.getElementById('globalConfirmModal');
    const titleEl = document.getElementById('confirmTitle');
    const msgEl = document.getElementById('confirmMessage');
    const btnYes = document.getElementById('btnConfirmYes');

    titleEl.innerText = title;
    msgEl.innerText = message;

    const confirmModal = new bootstrap.Modal(modalEl);

    btnYes.onclick = function() {
        callback();
        confirmModal.hide();
    };

    confirmModal.show();
}

