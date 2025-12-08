
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

        const div = document.createElement("div")
        div.className = "d-flex align-items-center me-1";


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
            a.textContent = name;
            li.appendChild(a);
            memberDropdown.appendChild(li);

            checkDropdownEmpty()
        };

        div.appendChild(span);
        div.appendChild(button);
        listMember.appendChild(div);

        event.target.parentElement.remove();
        checkDropdownEmpty()
    }
});


