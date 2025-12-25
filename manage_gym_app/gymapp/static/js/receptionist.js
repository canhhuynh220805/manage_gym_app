
function assignCoach(coach_id, package_id){
    showConfirmDialog(
        'Xác nhận chọn HLV',
        'Bạn có chắc muốn gán HLV này cho hội viên này không?',
        function(){
            fetch(`/api/member-packages/${package_id}/assign-coach`,{
                method: 'PATCH',
                headers: {
                'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'coach_id': coach_id
                })
            }).then(res => res.json()).then(data => {
                if(data.status == 200){
                    showToast(data.msg, 'success')
                    setTimeout(() => {
                        location.reload();
                    }, 1500);
                }else
                    showToast(data.err_msg, 'danger')
            }).catch(err => {
                console.error('Lỗi:', err);
                showToast('Mất kết nối đến máy chủ!', 'danger');
            });
        }
    )
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

function updatePackageForDisPlay() {
    const packageSelect = document.getElementById('packageSelect');
    const nameDisplay = document.getElementById('package-name-display');
    const priceDisplay = document.getElementById('price-package');
    const totalDisplay = document.getElementById('total-price');

    const selectedOption = packageSelect.options[packageSelect.selectedIndex];

    const name = selectedOption.getAttribute('data-name');
    const price = selectedOption.getAttribute('data-price');

    if (name && price) {
        const formattedPrice = new Intl.NumberFormat('vi-VN', {
            style: 'currency', currency: 'VND'
        }).format(price);

        nameDisplay.textContent = name;

        priceDisplay.textContent = formattedPrice;
        totalDisplay.textContent = formattedPrice;
    } else {
        nameDisplay.textContent = "Gói tập";
        nameDisplay.classList.add("text-muted");
        nameDisplay.classList.remove("fw-bold", "text-dark");

        priceDisplay.textContent = "0 VND";
        totalDisplay.textContent = "0 đ";
    }
}
document.addEventListener('DOMContentLoaded', function () {
    updatePackageForDisPlay();
    setupAvatarPreview('avatar', 'avatarPreview');
});
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

function submitRegistrationForm(event) {
    event.preventDefault();
    const form = document.getElementById('registrationForm');

    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        showToast("Vui lòng điền đầy đủ thông tin bắt buộc!", "warning");
        return;
    }

    showConfirmDialog(
        "Xác nhận đăng ký",
        "Bạn có chắc chắn muốn tạo tài khoản và lập hóa đơn cho khách hàng này không?",
        function() {

            const formData = new FormData(form);

            fetch('/api/receptionist/issue_an_invoice_receptionist', {
                method: 'POST',
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 200) {
                    form.reset();
                    showToast(data.msg);
                } else {
                    showToast((data.err_msg || "Có lỗi xảy ra"), 'danger');
                }
            })
            .catch(err => {
                console.error(err);
                showToast("Lỗi hệ thống!", 'danger');
            });
        }
    );
}