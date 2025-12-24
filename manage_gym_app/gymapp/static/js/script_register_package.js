function register_package(userId, packageId) {
    showConfirmDialog(
        "Xác nhận đăng kí gói này",
        "Bạn có chắc chắn đăng kí gói này không?",
        function() {
            fetch('/api/register_package', {
                method: 'POST',
                body: JSON.stringify({
                     "user_id": userId,
                     "package_id": packageId,
                }),
                headers: {
                    'Content-Type': 'application/json'
                }
            }).then(res => res.json()).then(data => {
                if (data.status === 200) {
                    showToast(data.msg, 'success');
                    setTimeout(() => location.reload(), 1500);
                } else {
                    showToast("Lỗi: " + data.err_msg, 'danger');
                }
            }).catch(err => {
                console.error(err);
                showToast("Đã có lỗi hệ thống xảy ra!", 'danger');
            });
        }
    );
}