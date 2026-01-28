document.addEventListener("DOMContentLoaded", function () {

    function getCSRFToken() {
        return document.getElementById("csrf-token").value;
    }

    // ----- LIVE CART COUNT -----
    async function updateCartCount() {
        try {
            const res = await fetch("/cart/count/");
            const data = await res.json();
            const cartBadge = document.querySelector("#cart-count");
            if (cartBadge) cartBadge.textContent = data.count;
        } catch (err) {
            console.error("Failed to update cart count", err);
        }
    }
    updateCartCount();

    // ----- TOAST FUNCTION -----
    function showToast(message) {
        let toast = document.getElementById("toast");
        if (!toast) {
            toast = document.createElement("div");
            toast.id = "toast";
            toast.className = "toast";
            document.body.appendChild(toast);
        }
        toast.textContent = message;
        toast.classList.add("show");
        setTimeout(() => toast.classList.remove("show"), 3000);
    }

    // ----- ADD TO CART -----
    document.querySelectorAll(".add-to-cart-btn").forEach(btn => {
        btn.addEventListener("click", function () {
            const productId = this.dataset.id;

            fetch(`/add-to-cart/${productId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.login_required) {
                    showToast("⚠️ Please login to add items to cart.");
                } else if (data.success) {
                    updateCartCount(); // Update badge immediately
                    showToast("🛒 Added to cart!");
                }
            });
        });
    });

    // ----- WISHLIST TOGGLE (UNCHANGED) -----
    document.querySelectorAll(".toggle-wishlist-btn").forEach(btn => {
        btn.addEventListener("click", function () {
            const productId = this.dataset.id;
            const el = this;

            fetch(`/wishlist/toggle/${productId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.login_required) {
                    alert("Please login to use wishlist.");
                } else {
                    el.innerHTML = data.status === "added"
                        ? '<i class="fa-solid fa-heart"></i>'
                        : '<i class="fa-regular fa-heart"></i>';
                }
            });
        });
    });

});
