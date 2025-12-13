
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

function setupAvatarPreview() {
    const avatarInput = document.getElementById('avatar');
    const avatarPreview = document.getElementById('avatarPreview');

    if (!avatarInput || !avatarPreview)
        return;

    const defaultImageSrc = avatarPreview.src;

    avatarInput.addEventListener('change', function (event) {
        const file = event.target.files[0];

        if (file) {
            if (!file.type.startsWith('image/')) {
                alert('Vui lòng chỉ chọn file hình ảnh!');
                avatarInput.value = '';
                return;
            }
            const reader = new FileReader();
            reader.onload = function (e) {
                avatarPreview.src = e.target.result;
            };
            reader.readAsDataURL(file);
        } else {
            avatarPreview.src = defaultImageSrc;
        }
    });
}

document.addEventListener('DOMContentLoaded', function () {
    setupAvatarPreview('avatar', 'avatarPreview');
});