document.addEventListener("DOMContentLoaded", function () {

    const toggleBtn = document.getElementById("themeToggle");
    if (!toggleBtn) {
        console.error("themeToggle button not found");
        return;
    }

    if (localStorage.getItem("theme") === "dark") {
        document.body.classList.add("dark-mode");
        toggleBtn.innerText = "Light Mode";
    }

    toggleBtn.addEventListener("click", function () {
        document.body.classList.toggle("dark-mode");

        if (document.body.classList.contains("dark-mode")) {
            toggleBtn.innerText = "Light Mode";
            localStorage.setItem("theme", "dark");
        } else {
            toggleBtn.innerText = "Dark Mode";
            localStorage.setItem("theme", "light");
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const bell = document.querySelector(".bi-bell");
    if (!bell) return;

    bell.addEventListener("click", function () {
        fetch("/admin-panel/notifications/read/");
    });
});

{/* <script>
function toggle(id) {
    let el = document.getElementById("cat-" + id);
    el.style.display = el.style.display === "block" ? "none" : "block";
}
</script> */}