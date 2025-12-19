function processPending(invoiceId) {
    showConfirmDialog(
        "Xác nhận thu tiền",
        "Bạn có chắc chắn muốn thu tiền hóa đơn này không?",
        function() {
            fetch('/api/cashier/process-pending', {
                method: 'POST',
                body: JSON.stringify({
                    'invoice_id': invoiceId
                }),
                headers: {
                    'Content-Type': 'application/json'
                }
            }).then(res => res.json()).then(data => {
                if (data.status === 200) {
                    showToast(data.msg, 'success');
                    setTimeout(() => location.reload(), 1500);
                } else {
                    showToast("Lỗi: " + data.msg, 'danger');
                }
            }).catch(err => {
                console.error(err);
                showToast("Đã có lỗi hệ thống xảy ra!", 'danger');
            });
        }
    );
}
function cancelInvoice(invoiceId) {
    if (confirm("Bạn có chắc chắn muốn hủy hóa đơn này không?")) {
        fetch('/api/cashier/cancel-invoice', {
            method: 'post',
            body: JSON.stringify({ "invoice_id": invoiceId }),
            headers: { 'Content-Type': 'application/json' }
        }).then(res => res.json()).then(data => {
            if (data.status === 200) {
                alert(data.msg);
                location.reload();
            } else {
                alert(data.msg);
            }
        });
    }
}