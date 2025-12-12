



function assignCoach(coach_id, package_id, member_id){
    if(confirm("Bạn có chắc chắn muốn chọn HLV này") === true){
        fetch(`/api/member-packages/${package_id}/assign-coach`,{
            method: 'PATCH',
            headers: {
            'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                'coach_id': coach_id,
                'member_id': member_id
            })
        }).then(res => res.json()).then(data => {
            if (data.error) {
                alert('Có lỗi xảy ra: ' + data.error);
            } else {
                alert(data.message);
                location.reload();
        }
        }).catch(err => {
            console.error('Lỗi:', err);
            alert('Lỗi kết nối server!');
        });
    }
}