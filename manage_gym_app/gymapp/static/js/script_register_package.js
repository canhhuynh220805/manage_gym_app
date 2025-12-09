function register_package(userId, packageId) {
    if (confirm('Xác nhận đăng kí gói tập này?')) {
        fetch('/api/register_package', {
            method: 'post',
            body: JSON.stringify({
                "user_id": userId,
                "package_id": packageId,
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(function(res) {
            return res.json();
        }).then(function(data) {
            if (data.status === 200) {
                alert(data.msg);
                location.reload();
            } else {
                alert('Lỗi: ' + data.err_msg);
            }
        }).catch(function(err) {
            console.error(err);
            alert('Đã có lỗi hệ thống xảy ra!');
        });
    }
}
