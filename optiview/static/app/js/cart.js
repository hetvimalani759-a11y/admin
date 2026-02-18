document.addEventListener("DOMContentLoaded", () => {

  // ================= MODAL ELEMENTS =================
  const confirmModal = document.getElementById("confirm-modal");
  const confirmYes = document.getElementById("confirm-yes");
  const confirmNo = document.getElementById("confirm-no");

  const stockModal = document.getElementById("stock-modal");
  const stockText = document.getElementById("stock-text");
  const stockOk = document.getElementById("stock-ok");

  let targetItemId = null;

  // ================= CSRF TOKEN =================
  function getCSRFToken() {
    return document.cookie
      .split("; ")
      .find(row => row.startsWith("csrftoken="))
      ?.split("=")[1];
  }

  // ================= MODAL FUNCTIONS =================
  function openConfirm(itemId) {
    targetItemId = itemId;
    confirmModal.style.display = "flex";
  }

  function closeConfirm() {
    confirmModal.style.display = "none";
    targetItemId = null;
  }

  function openStock(message) {
    stockText.textContent = message;
    stockModal.style.display = "flex";
  }

  function closeStock() {
    stockModal.style.display = "none";
  }

  confirmNo?.addEventListener("click", closeConfirm);
  stockOk?.addEventListener("click", closeStock);

  // ================= AJAX HELPER =================
  async function post(url) {
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCSRFToken(),
          "X-Requested-With": "XMLHttpRequest",
        },
      });

      return await response.json();
    } catch (error) {
      console.error("Request failed:", error);
      openStock("Something went wrong. Please try again.");
    }
  }

  // ================= UPDATE SUMMARY =================
  function updateSummary(summary) {
    if (!summary) return;

    document.getElementById("summaryItems").innerText = summary.items_count;
    document.getElementById("summaryOriginal").innerText = summary.original_total;
    document.getElementById("summaryDiscount").innerText = summary.discount_total;

    document.getElementById("summaryDelivery").innerText =
      summary.delivery_charge === 0 ? "Free 🎉" : summary.delivery_charge;

    document.getElementById("summaryTotal").innerText = summary.grand_total;

    const savedBanner = document.getElementById("saved-banner");
    if (savedBanner && summary.total_saved > 0) {
      savedBanner.style.display = "block";
      savedBanner.innerText = `🎉 You saved ₹${summary.total_saved}!`;
    }
  }

  // ================= QUANTITY INCREASE =================
  document.querySelectorAll(".plus-btn").forEach(btn => {
    btn.addEventListener("click", async function () {
      const row = this.closest(".cart-row");
      const itemId = row.dataset.id;
      const stock = parseInt(this.dataset.stock);
      const qtyEl = row.querySelector(".qty-number");
      const currentQty = parseInt(qtyEl.innerText);

      if (currentQty >= stock) {
        openStock(`⚠ Only ${stock} items available in stock.`);
        return;
      }

      const data = await post(`/cart/increase/${itemId}/`);
      if (!data?.success) {
        openStock(data?.message || "Cannot increase quantity.");
        return;
      }

      qtyEl.innerText = data.quantity;
      updateSummary(data.summary);
    });
  });

  // ================= QUANTITY DECREASE =================
  document.querySelectorAll(".minus-btn").forEach(btn => {
    btn.addEventListener("click", async function () {
      const row = this.closest(".cart-row");
      const itemId = row.dataset.id;
      const qtyEl = row.querySelector(".qty-number");
      const currentQty = parseInt(qtyEl.innerText);

      if (currentQty === 1) {
        openConfirm(itemId);
        return;
      }

      const data = await post(`/cart/decrease/${itemId}/`);
      if (!data?.success) return;

      qtyEl.innerText = data.quantity;
      updateSummary(data.summary);
    });
  });

  // ================= REMOVE BUTTON =================
  document.querySelectorAll(".remove-btn").forEach(btn => {
    btn.addEventListener("click", function () {
      const row = this.closest(".cart-row");
      const itemId = row.dataset.id;
      openConfirm(itemId);
    });
  });

  // ================= CONFIRM REMOVE =================
  confirmYes?.addEventListener("click", async () => {
    if (!targetItemId) return;

    const data = await post(`/cart/remove/${targetItemId}/`);
    const row = document.querySelector(`.cart-row[data-id='${targetItemId}']`);

    if (row) {
      row.classList.add("removing");
      setTimeout(() => row.remove(), 300);
    }

    if (data?.summary) {
      updateSummary(data.summary);

      if (data.summary.items_count === 0) {
        location.reload();
      }
    } else {
      openStock(data?.error || "Failed to update cart.");
    }

    closeConfirm();
  });

});
