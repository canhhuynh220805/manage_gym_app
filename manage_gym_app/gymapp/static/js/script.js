


//message - Nội dung thông báo
//type - Loại: 'success' (Xanh), 'danger' (Đỏ), 'warning' (Vàng)

function showToast(message, type = 'success') {
    const toastElement = document.getElementById('liveToast');
    const toastBody = document.getElementById('toast-message');

    // 1. Đặt nội dung
    toastBody.innerText = message;

    // 2. Xóa các class màu cũ và thêm màu mới
    toastElement.className = `toast align-items-center border-0 text-white bg-${type}`;

    // (Optional) Đổi màu nút close cho hợp nền
    // Bootstrap class: text-bg-success, text-bg-danger tự xử lý màu chữ trắng

    // 3. Khởi tạo và hiển thị Toast
    const toast = new bootstrap.Toast(toastElement, {
        delay: 3000,   // Tự tắt sau 3 giây
        animation: true
    });

    toast.show();
}

/**
title - Tiêu đề (VD: Xác nhận gán)
message - Nội dung câu hỏi
callback - Hàm sẽ chạy khi bấm nút Đồng ý
 */
function showConfirmDialog(title, message, callback) {
    // 1. Lấy các element
    const modalEl = document.getElementById('globalConfirmModal');
    const titleEl = document.getElementById('confirmTitle');
    const msgEl = document.getElementById('confirmMessage');
    const btnYes = document.getElementById('btnConfirmYes');

    // 2. Điền thông tin
    titleEl.innerText = title;
    msgEl.innerText = message;

    // 3. Khởi tạo Modal Bootstrap
    const confirmModal = new bootstrap.Modal(modalEl);

    // 4. Xử lý sự kiện bấm nút "Đồng ý"
    // Phải gán onclick mới mỗi lần gọi hàm để tránh chạy chồng chéo các lệnh cũ
    btnYes.onclick = function() {
        callback(); // Chạy hàm hành động được truyền vào
        confirmModal.hide(); // Đóng modal xác nhận
    };

    // 5. Hiện Modal
    confirmModal.show();
}