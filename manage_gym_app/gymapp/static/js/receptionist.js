
function preAssignCoach(coachId, coachName, package_id) {
    showConfirmDialog(
        'Xác nhận chọn HLV',
        `Bạn có chắc muốn gán HLV ${coachName} cho hội viên này không?`,
        function() {
            // Đây là "callback": Chỉ chạy khi người dùng bấm Đồng Ý
            assignCoach(coachId, package_id);
        }
    );
}

function assignCoach(coach_id, package_id){
    fetch(`/api/member-packages/${package_id}/assign-coach`,{
        method: 'PATCH',
        headers: {
        'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            'coach_id': coach_id
        })
    }).then(res => {
        if (res.ok) {
            return res.json().then(data => {
                showToast(data.message, 'success');
                setTimeout(() => location.reload(), 1500);
            });
        } else {
            return res.json().then(data => {
                showToast(data.error || 'Có lỗi xảy ra', 'danger');
            });
        }
    }).catch(err => {
        console.error('Lỗi:', err);
        showToast('Mất kết nối đến máy chủ!', 'danger');
    });
}