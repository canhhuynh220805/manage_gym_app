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

function directPay() {
    const memberId = document.getElementById('memberId').value;
    const packageId = document.getElementById('packageId').value;

    if (!memberId) {
        alert("Vui lòng tìm và chọn khách hàng!");
        return;
    }
    if (!packageId) {
        alert("Vui lòng chọn gói tập!");
        return;
    }

    if (confirm("Xác nhận đăng ký và thu tiền ngay lập tức?") === true) {
        fetch('/api/cashier/direct-pay', {
            method: 'POST',
            body: JSON.stringify({
                'member_id': memberId,
                'package_id': packageId
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(res => res.json()).then(data => {
            if (data.status === 200) {
                alert(data.msg);
                location.reload();
            } else {
                alert("Lỗi: " + data.msg);
            }
        }).catch(err => {
            console.error(err);
            alert("Lỗi hệ thống!");
        });
    }
}

function processPending(invoiceId) {
    if (confirm("Bạn có chắc chắn thu tiền hóa đơn này không?") === true) {
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
                alert(data.msg);
                location.reload();
            } else {
                alert("Lỗi: " + data.msg);
            }
        }).catch(err => console.error(err));
    }
}