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
