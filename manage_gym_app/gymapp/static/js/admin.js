function addBenefitRow() {
    const row = `<div class="row mb-2 benefit-row">
        <div class="col-5"><input type="text" class="form-control form-control-sm b-name" placeholder="Tên quyền lợi"></div>
        <div class="col-6"><input type="text" class="form-control form-control-sm b-detail" placeholder="Chi tiết"></div>
        <div class="col-1"><button class="btn btn-sm btn-outline-danger border-0" onclick="this.parentElement.parentElement.remove()">&times;</button></div>
    </div>`;
    document.getElementById('benefit-container').insertAdjacentHTML('beforeend', row);
}

function savePackage() {
    const name = document.getElementById('pkg_name').value.trim();
    const price = document.getElementById('pkg_price').value;
    const duration = document.getElementById('pkg_duration').value;
    const description = document.getElementById('pkg_desc').value.trim();
    const image = document.getElementById('pkg_image').value.trim();

    if (!name || !price || !duration || !description || !image) {
        showToast("Vui lòng nhập đầy đủ", "danger");
        return;
    }

    const benefits = [];
    document.querySelectorAll('.benefit-row').forEach(row => {
        const bName = row.querySelector('.b-name').value.trim();
        if (bName) benefits.push({ name: bName, detail: row.querySelector('.b-detail').value.trim() });
    });

    showConfirmDialog("Xác nhận lưu", "Bạn chắc chắn muốn thêm gói dịch vụ này?", function() {
        fetch('/api/admin/packages', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, price, duration, description, image, benefits })
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 200) {
                showToast(data.msg, "success");

                if (window.jQuery) { $('.modal.show').modal('hide'); }

                setTimeout(() => location.reload(), 1500);
            } else {
                showToast(data.err_msg, "danger");
            }
        })
        .catch(err => {
            console.error(err);
            showToast("Lỗi hệ thống khi gửi dữ liệu!", "danger");
        });
    });
}

function saveExercise() {
    const name = document.getElementById('ex_name').value.trim();
    const description = document.getElementById('ex_desc').value.trim();
    const image = document.getElementById('ex_image').value.trim();

    if (!name) {
        showToast("Tên bài tập không được để trống!", "danger");
        return;
    }
    if (name.length < 3 || name.length > 100) {
        showToast("Tên bài tập phải từ 3 đến 100 ký tự!", "warning");
        return;
    }

    if (!description) {
        showToast("Vui lòng nhập mô tả kỹ thuật bài tập!", "danger");
        return;
    }
    if (description.length < 10) {
        showToast("Mô tả quá ngắn!", "warning");
        return;
    }

    if (!image) {
        showToast("Vui lòng cung cấp đúng link ảnh minh họa!", "danger");
        return;
    }
    const urlPattern = /^(https?:\/\/.*\.(?:png|jpg|jpeg|gif|webp))$/i;
    if (!urlPattern.test(image)) {
        showToast("Link ảnh không hợp lệ!", "warning");
        return;
    }

    showConfirmDialog(
        "Xác nhận thêm bài tập",
        "Bạn có chắc chắn muốn thêm bài tập mới này không?",
        function() {
            fetch('/api/admin/exercises', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    'name': name,
                    'description': description,
                    'image': image
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 200) {
                    showToast(data.msg, "success");

                    if (typeof $ !== 'undefined') {
                        $('.modal.show').modal('hide');
                    }
                    setTimeout(() => location.reload(), 1500);
                } else {
                    showToast("Lỗi: " + data.err_msg, "danger");
                }
            })
            .catch(err => {
                console.error(err);
                showToast("Đã có lỗi hệ thống xảy ra!", "danger");
            });
        }
    );
}