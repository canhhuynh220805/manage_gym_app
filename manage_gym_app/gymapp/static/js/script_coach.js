const listMember = document.getElementById("assigned-member");
const memberDropdown = document.getElementById("member-dropdown");
const msg = document.getElementById("no-member-msg");

function checkDropdownEmpty() {
    const hasItems = memberDropdown.querySelectorAll(".dropdown-item").length > 0;
    msg.classList.toggle("d-none", hasItems);
}

memberDropdown.addEventListener("click", function(event) {
    if (event.target.classList.contains("dropdown-item")) {
        event.preventDefault();

        if (listMember.textContent.includes("chưa có")) {
            listMember.innerHTML = "";
        }

        const name = event.target.dataset.name;
        const id = event.target.dataset.id;

        const div = document.createElement("div")
        div.className = "d-flex align-items-center me-1";
        div.dataset.id = id;


        const span = document.createElement("span");
        span.className = "badge bg-success me-2";
        span.textContent = name;

        const button = document.createElement("button");
        button.className = "btn btn-sm btn-danger";
        button.textContent = "X";

        button.onclick = function () {
            div.remove();

            const li = document.createElement("li");
            const a = document.createElement("a");
            a.href = "#";
            a.className = "dropdown-item";
            a.dataset.name = name;
            a.dataset.id = id;
            a.textContent = name;
            li.appendChild(a);
            memberDropdown.appendChild(li);
            if (listMember.children.length === 0) {
                 listMember.innerHTML = "(chưa có hội viên)";
            }
            checkDropdownEmpty()
        };

        div.appendChild(span);
        div.appendChild(button);
        listMember.appendChild(div);

        event.target.parentElement.remove();
        checkDropdownEmpty()
    }
});

function openListExercise(){
    const listExercise = document.getElementById("list-exercise")
    const warning = document.getElementById("exercise-warning");

    warning.classList.add("d-none");
    listExercise.classList.remove("d-none")
}

function togglePlan(checkbox, id, name) {
    if (checkbox.checked) {
        addToPlan(id, name);
    } else {
        removeFromPlan(id);
    }
}

function addToPlan(id, name){
    fetch('/api/workout-exercises',{
        method: "post",
        body: JSON.stringify({
            'id': id,
            'name': name,
        }),
        headers: {
            "Content-Type": "application/json"
        }
    }).then(res => res.json()).then(data => {
        if(data.status == 200){
            showToast(data.msg, "success")
            renderTable(data.data)
        }
        else
            showToast(data.err_msg, "danger")
    }).catch(err => {
        console.error(err);
        showToast("Đã có lỗi hệ thống xảy ra!", 'danger');
    });
}

function renderTable(data){
    const tbody = document.getElementById("exercise-table-body");
    tbody.innerHTML = "";
    let stt = 1;

    for(let ex of data){
        let dayOptions = "";
        for (let d of days) {
            const isSelected = (ex.days && ex.days.includes(d)) ? "selected" : "";
            dayOptions += `<option value="${d}" ${isSelected}>${d}</option>`;
        }
        tbody.innerHTML += `
        <tr>
            <td>${stt++}</td>
            <td>${ex.name}</td>
            <td><input type="number" class="form-control sets" value="${ex.sets}" onblur="updateExercise(${ex.id}, this)" style="width:70px"></td>
            <td><input type="number" class="form-control reps" value="${ex.reps}" onblur="updateExercise(${ex.id}, this)" style="width:70px"></td>
            <td>
                <select class="form-select days" multiple
                title="Giữ Ctrl (hoặc Cmd trên Mac) để chọn nhiều ngày" onchange="updateExercise(${ex.id}, this)">
                    ${dayOptions}
                </select>
            </td>
            <td>
                <button class="btn btn-sm btn-danger" onclick="removeFromPlan(${ex.id})">Xóa</button>
            </td>
        </tr>
    `;
    }
}

function removeFromPlan(id){
    showConfirmDialog(
        "Xóa bài tập",
        "Bạn xác nhận xóa bài tập này khỏi danh sách tạm",
         function(){
            const cb = document.getElementById(`cb-${id}`);
            if (cb) {
                cb.checked = false;
            }
            fetch(`/api/workout-exercises/${id}`, {
                method: "delete"
            })
            .then(res => res.json()).then(data => {
                if(data.status == 200){
                    showToast(data.msg, "success")
                    renderTable(data.data)
                }else{
                    showToast(data.err_msg, 'danger')
                    cb.checked = true
                }
            }).catch(err => {
                console.error(err);
                showToast("Đã có lỗi hệ thống xảy ra!", 'danger');
            });
        }
    )
}

function updateExercise(id, obj){
    const row = obj.closest("tr");
    const sets = row.querySelector(".sets").value;
    const reps = row.querySelector(".reps").value;
    const days = Array.from(row.querySelector(".days").selectedOptions)
                      .map(opt => opt.value);

    fetch(`/api/workout-exercises/${id}`, {
        method: "put",
        headers:{
            "Content-type": "application/json"
        },
        body: JSON.stringify({ sets, reps , days})
    }).then(res => res.json()).then(data => {
        if(data.status == 200){
            showToast(data.msg, "success")
        }
        else{
            showToast(data.err_msg, 'danger')
        }
    }).catch(err => {
        console.error(err);
        showToast("Đã có lỗi hệ thống xảy ra!", 'danger');
    });
}

function createWorkoutPlan(){
    showConfirmDialog(
        "Xác nhận tạo kế hoạch",
        "Bạn có chắc chắn muốn tạo kế hoạch này!!",
        function(){
            const namePlan = document.getElementById("name-plan").value

            const startDate = new Date(document.getElementById("start-date").value);
            const endDate   = new Date(document.getElementById("end-date").value);

            if (startDate >= endDate) {
                showToast("Ngày bắt đầu phải nhỏ hơn ngày kết thúc", "danger");
            }

            const selectedDivs = document.querySelectorAll("#assigned-member div[data-id]");
            const memberIds = Array.from(selectedDivs).map(div => div.dataset.id);

            if (memberIds.length > 0 && !startDate) {
                showToast("Vui lòng chọn ngày bắt đầu cho hội viên!", "danger");
                return;
            }

            fetch('/api/workout-plans', {
                method: 'post',
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    "name-plan": namePlan,
                    "member_ids": memberIds,
                    "startDate": startDate,
                    "endDate": endDate
                })
            }).then(res => res.json()).then(data => {
                if(data.status == 200){
                    showToast(data.msg, "success")
                    setTimeout(() => {
                        location.reload();
                    }, 1500);
                }
                else{
                    showToast(data.err_msg, "danger")
                }
            }).catch(err => {
                console.error(err);
                showToast("Đã có lỗi hệ thống xảy ra!", 'danger');
            });
        }
    )
}

function searchExercise(){
    let kw = document.getElementById("search-input");
    kw = kw.value.toLowerCase();

    let exercises = document.getElementsByClassName('exercise-item');
    for(let i = 0; i < exercises.length; i++){
        let content = exercises[i].innerText.toLowerCase();
        if(content.includes(kw))
            exercises[i].classList.remove('d-none');
        else
            exercises[i].classList.add('d-none');
    }
}

function assignPlanToMember(plan_id, member_id, prefix = ''){
    const startDate = document.getElementById(prefix + "start_date_" + plan_id).value
    const endDate = document.getElementById(prefix + "end_date_" + plan_id).value

    showConfirmDialog(
        "Xác nhận gán kế hoạch",
        "Bạn có chắc chắn muốn gán kế hoạch này??",
        function(){
            fetch('/api/assign-existing-plan', {
                method: 'post',
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    "plan_id": plan_id,
                    "member_id": member_id,
                    "start_date": startDate,
                    "end_date": endDate
                })
            }).then(res => res.json()).then(data =>{
                if(data.status == 200){
                   showToast(data.msg, "success")
                   setTimeout(() => {
                        location.reload();
                   }, 1500);
                }
                else{
                    showToast(data.err_msg, "danger")
                }
            }).catch(err => {
                console.error(err);
                showToast("Đã có lỗi hệ thống xảy ra!", 'danger');
            });
        }
    )
}