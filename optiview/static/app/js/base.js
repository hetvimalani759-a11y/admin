document.addEventListener("DOMContentLoaded", function () {
    const accountBtn = document.getElementById("accountBtn");
    const accountDropdown = document.getElementById("accountDropdown");

    accountBtn.addEventListener("click", () => {
        accountDropdown.classList.toggle("show");
    });

    // Optional: close dropdown if clicked outside
    document.addEventListener("click", (e) => {
        if (!accountBtn.contains(e.target) && !accountDropdown.contains(e.target)) {
            accountDropdown.classList.remove("show");
        }
    });

    


    /* ================= NOTIFICATIONS ================= */
    const notifWrapper = document.querySelector(".notif-wrapper");
    const notifBtn = document.querySelector(".notif-btn");
    const notifBox = document.querySelector(".notif-box");
    const notifCount = document.querySelector(".notif-count");
    const notifItems = document.getElementById("notif-items");

    if (notifWrapper && notifBtn && notifBox && notifItems) {
        // Fetch notifications dynamically
        fetch('/notifications/')
            .then(res => res.json())
            .then(data => {
                const notifications = data.notifications;
                if (notifications.length > 0) {
                    notifWrapper.style.display = "block";
                    notifCount.style.display = "inline-block";
                    notifCount.innerText = notifications.length;

                    notifications.forEach(n => {
                        const div = document.createElement("div");
                        div.classList.add("notif-item");
                        div.innerHTML = `<p><strong>${n.title}</strong></p><p>${n.message}</p>`;

                        notifItems.appendChild(div);
                    });
                }
            });

        // Toggle notification dropdown
        notifBtn.addEventListener("click", function (e) {
            e.stopPropagation();
            accountDropdown?.classList.remove("show");
            notifBox.classList.toggle("show");
        });

        document.addEventListener("click", function () {
            notifBox.classList.remove("show");
        });
    }

    /* ================= ACTIVE LINK UNDERLINE ================= */
    const links = document.querySelectorAll(".nav-link, .main-footer a");
    links.forEach(link => {
        if (link.href === window.location.href) {
            link.classList.add("active");
        }
        // Optional: change active on click
        link.addEventListener("click", function() {
            links.forEach(l => l.classList.remove("active"));
            link.classList.add("active");
        });
    });
});
