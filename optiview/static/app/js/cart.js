document.addEventListener("DOMContentLoaded", function () {

    const modal = document.getElementById("confirm-modal");
    const modalText = document.getElementById("confirm-text");
    const yesBtn = document.getElementById("confirm-yes");
    const noBtn = document.getElementById("confirm-no");

    let targetUrl = null;

    function openModal(text, url) {
        modalText.textContent = text;
        targetUrl = url;
        modal.style.display = "flex";
    }

    function closeModal() {
        modal.style.display = "none";
        targetUrl = null;
    }

    noBtn.onclick = closeModal;
    yesBtn.onclick = function () {
        if (targetUrl) window.location.href = targetUrl;
    };

    /* ---------- REMOVE BUTTON ---------- */
    document.querySelectorAll(".remove-btn").forEach(function (btn) {
        btn.addEventListener("click", function (e) {
            e.preventDefault();
            openModal("Are you sure you want to remove this item?", btn.href);
        });
    });

    /* ---------- PLUS BUTTON ---------- */
    document.querySelectorAll(".plus-btn").forEach(function (btn) {
        btn.addEventListener("click", function () {
            const row = btn.closest(".cart-row");
            const id = row.dataset.id;
            window.location.href = "/cart/increase/" + id + "/";
        });
    });

    /* ---------- MINUS BUTTON ---------- */
    document.querySelectorAll(".minus-btn").forEach(function (btn) {
        btn.addEventListener("click", function () {
            const row = btn.closest(".cart-row");
            const id = row.dataset.id;
            const qty = parseInt(row.querySelector(".qty-number").textContent);

            if (qty <= 1) {
                openModal("Quantity is 1. Remove this item?", "/cart/remove/" + id + "/");
            } else {
                window.location.href = "/cart/decrease/" + id + "/";
            }
        });
    });

});
