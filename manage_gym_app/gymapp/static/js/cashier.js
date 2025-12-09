$(document).ready(function() {
    $('#memberSelect').select2({ placeholder: "Tìm hội viên...", allowClear: true });
    $('#packageSelect').select2({ placeholder: "Chọn gói tập..." });
});

function pay() {
    const memberId = $('#memberSelect').val();
    const packageId = $('#packageSelect').val();

    if (!memberId || !packageId) {
        alert("Vui lòng chọn đầy đủ HỘI VIÊN và GÓI TẬP!");
        return;
    }

    if (confirm('Xác nhận lập hóa đơn và thu tiền gói này?')) {
        fetch('/api/cashier/pay', {
            method: 'post',
            body: JSON.stringify({ 'member_id': memberId, 'package_id': packageId }),
            headers: { 'Content-Type': 'application/json' }
        }).then(res => res.json()).then(data => {
            if (data.status === 200) {
                alert('Lập hóa đơn thành công!');
                location.reload();
            } else {
                alert('Lỗi: ' + data.err_msg);
            }
        }).catch(err => {
            console.error(err);
            alert('Lỗi kết nối server.');
        });
    }
}

function showInvoiceDetail(invoiceId) {
    fetch(`/api/invoices/${invoiceId}`)
        .then(res => res.json())
        .then(data => {
            if (data.status === 200) {
                const d = data.data;
                document.getElementById('modal-id').innerText = d.id;
                document.getElementById('modal-date').innerText = d.created_date;
                document.getElementById('modal-staff').innerText = d.staff_name;
                document.getElementById('modal-member').innerText = d.member_name;
                document.getElementById('modal-package').innerText = d.package_name;
                document.getElementById('modal-duration').innerText = d.duration;
                document.getElementById('modal-total').innerText = new Intl.NumberFormat('vi-VN').format(d.total_amount);

                const myModal = new bootstrap.Modal(document.getElementById('invoiceModal'));
                myModal.show();
            } else {
                alert(data.err_msg);
            }
        })
        .catch(err => console.error(err));
}