
function preAssignCoach(coachId, coachName, package_id) {
    showConfirmDialog(
        'Xác nhận chọn HLV',
        `Bạn có chắc muốn gán HLV ${coachName} cho hội viên này không?`,
        function() {
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
function searchMembers() {
    let kw = document.getElementById("memberSearch").value;

    if (kw.length === 0) {
        document.getElementById("memberResults").style.display = "none";
        return;
    }

    fetch('/api/members', {
        method: "post",
        body: JSON.stringify({
            "kw": kw
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(res => res.json()).then(data => {
        let html = "";
        for (let m of data) {
            let phone = m.phone ? m.phone : "Chưa có SĐT";
            html += `
                <a href="javascript:;" class="dropdown-item" onclick="chooseMember(${m.id}, '${m.name}', '${phone}')">
                    <img src="${m.avatar}" class="rounded-circle me-2" style="width: 30px; height: 30px; object-fit: cover;">
                    ${m.name} - ${phone}
                </a>
            `;
        }
        let d = document.getElementById("memberResults");
        if (html === "") {
            d.innerHTML = '<span class="dropdown-item text-muted">Không tìm thấy</span>';
        } else {
            d.innerHTML = html;
        }
        d.style.display = "block";
    });
}

function chooseMember(id, name, phone) {
    document.getElementById("memberSearch").value = name + " - " + phone;
    document.getElementById("memberId").value = id;
    document.getElementById("memberResults").style.display = "none";
}

function createInvoice() {
    const memberId = document.getElementById('memberId').value;
    const packageId = document.getElementById('packageId').value;

    if (!memberId) {
        showToast("Vui lòng tìm và chọn khách hàng!", "warning");
        return;
    }
    if (!packageId) {
        showToast("Vui lòng chọn gói tập!", "warning");
        return;
    }

    showConfirmDialog(
        "Xác nhận tạo hóa đơn",
        "Bạn có muốn lập hóa đơn đăng ký dịch vụ cho khách hàng này không?",
        function() {
            fetch('/api/register_package', {
                method: 'POST',
                body: JSON.stringify({
                    'user_id': memberId,
                    'package_id': packageId
                }),
                headers: {
                    'Content-Type': 'application/json'
                }
            }).then(res => res.json()).then(data => {
                if (data.status === 200) {
                    showToast("Tạo hóa đơn thành công! Vui lòng báo khách qua quầy thu ngân.", 'success');
                    setTimeout(() => location.reload(), 2000);
                } else {
                    showToast("Lỗi: " + data.err_msg, 'danger');
                }
            }).catch(err => {
                console.error(err);
                showToast("Lỗi hệ thống!", 'danger');
            });
        }
    );
}