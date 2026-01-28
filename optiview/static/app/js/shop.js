document.addEventListener("DOMContentLoaded", () => {

    const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]")?.value
        || document.getElementById("csrf-token")?.value;

    /* ---------- TOAST ---------- */
    let toastEl = null;
    let hideTimer = null;

    function showToast(message, type = "success") {
        if (!toastEl) {
            toastEl = document.createElement("div");
            toastEl.style.position = "fixed";
            toastEl.style.top = "20px";
            toastEl.style.right = "20px";
            toastEl.style.zIndex = "9999";
            document.body.appendChild(toastEl);
        }

        toastEl.innerHTML = `
            <div style="
                background:${type === "success" ? "#5ec8ec" : "#dc3545"};
                color:white;
                padding:10px 16px;
                border-radius:6px;
                box-shadow:0 4px 10px rgba(0,0,0,.15);
                margin-bottom:8px;
            ">${message}</div>
        `;

        clearTimeout(hideTimer);
        hideTimer = setTimeout(() => {
            toastEl.innerHTML = "";
        }, 2500);
    }

    /* ---------- CART COUNT ---------- */
    async function updateCartCount() {
        try {
            const res = await fetch("/cart/count/");
            const data = await res.json();
            const badge = document.getElementById("cart-count");
            if (badge) badge.textContent = data.count;
        } catch (e) {}
    }

    /* ---------- CLICK HANDLER ---------- */
    document.body.addEventListener("click", async (e) => {

        /* ===== ADD TO CART ===== */
        const cartBtn = e.target.closest(".add-to-cart-btn");
        if (cartBtn) {
            e.preventDefault();
            e.stopPropagation();

            if (cartBtn.dataset.loading === "true") return;
            cartBtn.dataset.loading = "true";

            const productId = cartBtn.dataset.id;

            try {
                const res = await fetch(`/add-to-cart/${productId}/`, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrfToken,
                        "X-Requested-With": "XMLHttpRequest"
                    }
                });
                const data = await res.json();

                if (data.success) {
                    updateCartCount();
                    showToast("🛒 Added to cart");
                } else {
                    showToast(data.error || "Failed", "error");
                }
            } catch (err) {
                showToast("Please register or login before adding to cart", "error");
            } finally {
                cartBtn.dataset.loading = "false";
            }
            return;
        }

        /* ===== WISHLIST ===== */
        const wishBtn = e.target.closest(".toggle-wishlist-btn");
        if (wishBtn) {
            e.preventDefault();
            e.stopPropagation();

            const productId = wishBtn.dataset.id;
            const icon = wishBtn.querySelector("i");

            try {
                const res = await fetch(`/wishlist/toggle/${productId}/`, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrfToken,
                        "X-Requested-With": "XMLHttpRequest"
                    }
                });
                const data = await res.json();

                if (data.status === "added") {
                    icon.classList.remove("fa-regular");
                    icon.classList.add("fa-solid", "text-danger");
                    showToast("💖 Added to wishlist");
                } else if (data.status === "removed") {
                    icon.classList.remove("fa-solid", "text-danger");
                    icon.classList.add("fa-regular");
                    showToast("💔 Removed from wishlist");
                }
            } catch (err) {
                showToast("Please register or login before adding to wishlist", "error");
            }
        }

    });

    updateCartCount();
});
