document.addEventListener("DOMContentLoaded", function () {

    const page = document.querySelector(".order-page");

    /* ================================
       MODAL ELEMENTS
    ================================= */
    const modal = document.getElementById("cancelModal");
    const cancelYes = document.getElementById("cancelYes");
    const cancelNo = document.getElementById("cancelNo");

    let selectedCard = null;
    let cancelUrl = null;

    /* ================================
       OPEN CANCEL MODAL
    ================================= */
    page.addEventListener("click", function (e) {

        if (e.target.classList.contains("open-cancel-modal")) {
            e.preventDefault();

            selectedCard = e.target.closest(".order-card");
            cancelUrl = e.target.dataset.url;

            modal.style.display = "flex";
        }

    });

    /* ================================
       CLOSE MODAL
    ================================= */
    cancelNo.addEventListener("click", function () {
        modal.style.display = "none";
    });

    window.addEventListener("click", function (e) {
        if (e.target === modal) {
            modal.style.display = "none";
        }
    });

    /* ================================
       CONFIRM CANCEL (AJAX)
    ================================= */
    cancelYes.addEventListener("click", function (e) {
        e.preventDefault();

        if (!selectedCard || !cancelUrl) return;

        fetch(cancelUrl, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken")
            }
        })
        .then(res => res.json())
        .then(data => {

            if (data.success) {

                selectedCard.dataset.status = "Cancelled";

                const badge = selectedCard.querySelector(".status-badge");
                badge.innerText = "Cancelled";
                badge.className = "status-badge status-cancelled";

                const cancelBtn = selectedCard.querySelector(".open-cancel-modal");
                if (cancelBtn) cancelBtn.remove();

                const trackBtn = selectedCard.querySelector(".track-btn");
                if (trackBtn) trackBtn.remove();

                const invoiceBtn = selectedCard.querySelector(".invoice-btn");
                if (invoiceBtn) invoiceBtn.remove();

            } else {
                alert("Cancel failed");
            }

            modal.style.display = "none";
        });

    });

    /* ================================
       FILTER BUTTONS
    ================================= */
    page.addEventListener("click", function (e) {

        if (e.target.classList.contains("filter-btn")) {

            document.querySelectorAll(".filter-btn")
                .forEach(btn => btn.classList.remove("active"));

            e.target.classList.add("active");

            const status = e.target.dataset.status;

            document.querySelectorAll(".order-card").forEach(card => {

                if (status === "all" || card.dataset.status === status) {
                    card.style.display = "block";
                } else {
                    card.style.display = "none";
                }

            });
        }

    });

    /* ================================
       STAR RATING
    ================================= */
    page.addEventListener("click", function (e) {

        if (e.target.classList.contains("star")) {

            const star = e.target;
            const value = parseInt(star.dataset.value);
            const starsContainer = star.closest(".stars");
            const card = star.closest(".order-card");
            const itemId = card.dataset.itemId;

            starsContainer.dataset.rating = value;

            starsContainer.querySelectorAll(".star").forEach(s => {
                s.classList.toggle("active",
                    parseInt(s.dataset.value) <= value);
            });

            fetch(`/orders/rate/${itemId}/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify({ rating: value })
            });

        }

    });

    /* ================================
       CSRF
    ================================= */
    function getCookie(name) {
        let cookieValue = null;

        document.cookie.split(";").forEach(cookie => {
            const c = cookie.trim();
            if (c.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(
                    c.substring(name.length + 1)
                );
            }
        });

        return cookieValue;
    }

});
