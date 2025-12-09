const listMember = document.getElementById("assigned-member");
const memberDropdown = document.getElementById("member-dropdown");
const msg = document.getElementById("no-member-msg");

function checkDropdownEmpty() {
    const hasItems = memberDropdown.querySelectorAll("li").length > 0;
    msg.classList.toggle("d-none", hasItems); // có item → ẩn, hết → hiện
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


function togglePlan(checkbox, id, name, description, image) {
    if (checkbox.checked) {
        addToPlan(id, name, description, image);
    } else {
        removeFromPlan(id);
    }
}

function addToPlan(id, name, description, image){
    fetch('/api/workout-exercises',{
        method: "post",
        body: JSON.stringify({
            'id': id,
            'name': name,
            'description': description,
            'image': image
        }),
        headers: {
            "Content-Type": "application/json"
        }
    }).then(res => res.json()).then(data => {
        console.log(data)
        renderTable(data)
    })
}

function renderTable(data){
    const tbody = document.getElementById("exercise-table-body");
    tbody.innerHTML = "";
    let stt = 1;

    for(let ex of data){
        let dayOptions = "";
        for (let d of days) {
            dayOptions += `<option value="${d}">${d}</option>`;
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
    const cb = document.getElementById(`cb-${id}`);
    if (cb) {
        cb.checked = false;
    }
    fetch(`/api/workout-exercises/${id}`, {
        method: "delete"
    })
    .then(res => res.json())
    .then(data => renderTable(data));
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
    }).then(res => res.json())
}

function createWorkoutPlan(){
    if(confirm("Bạn có chắc chắn là tạo kế hoạch này") === true){
        const namePlan = document.getElementById("name-plan").value

        const selectedDivs = document.querySelectorAll("#assigned-member div[data-id]");
        const memberIds = Array.from(selectedDivs).map(div => div.dataset.id);

        if(!namePlan){
            alert("Vui lòng nhập tên kế hoạch!");
            return;
        }

        fetch('/api/workout-plans', {
            method: 'post',
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                "name-plan": namePlan,
                "member_ids": memberIds
            })
        }).then(res => res.json()).then(data => {
            if (data.status === 200) {
                alert("Lưu thành công!");
                location.reload();
            } else {
                alert("Lỗi: " + data.err_msg);
            }
        })

    }
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

function assignPlanToMember(plan_id, member_id){
    if(confirm("Bạn muốn gán kế hoạch này cho hội viên?") === true){
        fetch('/api/assign-existing-plan', {
            method: 'post',
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                "plan_id": plan_id,
                "member_id": member_id
            })
        }).then(res => res.json()).then(data =>{
            if(data.status == 200){
               alert(data.msg);
               location.reload();
            }
            else{
                alert(data.err_msg);
            }
        });

    }
}