$(document).ready(function() {
    $('#memberSelect').select2({
        placeholder: "Gõ tên hoặc SĐT để tìm...",
        allowClear: true,
        width: '100%'
    });

    $('#packageSelect').select2({
        placeholder: "Chọn gói tập...",
        width: '100%'
    });
});

function pay() {
    const memberId = $('#memberSelect').val();
    const packageId = $('#packageSelect').val();

    if (!memberId || !packageId) {
        alert("Vui lòng chọn đầy đủ HỘI VIÊN và GÓI TẬP!");
        return;
    }

    if (confirm('Xác nhận đăng kí gói tập này?')) {
        fetch('/api/cashier/pay', {
            method: 'post',
            body: JSON.stringify({
                'member_id': memberId,
                'package_id': packageId
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(function(res) {
            return res.json();
        }).then(function(data) {
            if (data.status === 200) {
                alert('Thanh toán thành công!');
                location.reload();
            } else {
                alert('Lỗi: ' + data.err_msg);
            }
        }).catch(function(err) {
            console.error(err);
            alert('Lỗi kết nối server.');
        });
    }
}