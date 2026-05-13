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
document.addEventListener("DOMContentLoaded", () => {

    /* ============================
       ANIMATED COUNTERS
    ============================ */
    document.querySelectorAll(".dash-card").forEach(card => {
        const target = Number(card.dataset.count || 0);
        const counterEl = card.querySelector(".counter");
        const isCurrency = counterEl.textContent.includes("₹");
        let start = 0;
        const duration = 900;
        const startTime = performance.now();

        function animate(time) {
            const progress = Math.min((time - startTime) / duration, 1);
            const value = Math.floor(progress * target);
            counterEl.textContent = isCurrency ? `₹${value}` : value;
            if (progress < 1) requestAnimationFrame(animate);
        }
        requestAnimationFrame(animate);
    });

    /* ============================
       SPARKLINE MINI CHARTS
    ============================ */
    document.querySelectorAll(".sparkline").forEach(canvas => {
        const ctx = canvas.getContext("2d");
        const data = Array.from({ length: 8 }, () => Math.floor(Math.random() * 10) + 2);

        new Chart(ctx, {
            type: "line",
            data: {
                labels: data.map((_, i) => i),
                datasets: [{
                    data,
                    borderWidth: 2,
                    tension: .4,
                    pointRadius: 0,
                    borderColor: "rgba(255,255,255,.9)",
                    backgroundColor: "rgba(255,255,255,.25)",
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false }, tooltip: { enabled: false } },
                scales: { x: { display: false }, y: { display: false } }
            }
        });
    });

    /* ============================
       RIPPLE EFFECT
    ============================ */
    document.querySelectorAll(".ripple").forEach(el => {
        el.addEventListener("click", function (e) {
            const circle = document.createElement("span");
            const diameter = Math.max(this.clientWidth, this.clientHeight);
            const radius = diameter / 2;

            circle.style.width = circle.style.height = `${diameter}px`;
            circle.style.left = `${e.clientX - this.getBoundingClientRect().left - radius}px`;
            circle.style.top = `${e.clientY - this.getBoundingClientRect().top - radius}px`;
            circle.classList.add("ripple-circle");

            const ripple = this.getElementsByClassName("ripple-circle")[0];
            if (ripple) ripple.remove();

            this.appendChild(circle);
        });
    });

});

document.querySelectorAll(".nav-menu a, .cart-icon, .heart-icon, #notif-btn, .account-btn").forEach(btn => {
    btn.addEventListener("click", e => {
        const ripple = document.createElement("span");
        const size = Math.max(btn.offsetWidth, btn.offsetHeight);
        const rect = btn.getBoundingClientRect();
        ripple.style.width = ripple.style.height = size + "px";
        ripple.style.left = e.clientX - rect.left - size / 2 + "px";
        ripple.style.top = e.clientY - rect.top - size / 2 + "px";
        ripple.style.position = "absolute";
        ripple.style.borderRadius = "50%";
        ripple.style.background = "rgba(37,99,235,.35)";
        ripple.style.transform = "scale(0)";
        ripple.style.animation = "ripple .6s linear";
        ripple.style.pointerEvents = "none";
        btn.appendChild(ripple);
        setTimeout(() => ripple.remove(), 600);
    });
});

