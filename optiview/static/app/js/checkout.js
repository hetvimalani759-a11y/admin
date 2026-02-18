document.addEventListener("DOMContentLoaded", function () {

  /* ==========================================================
     ELEMENTS
  ========================================================== */
  const confirmModal = document.getElementById("confirm-modal");
  const confirmYes = document.getElementById("confirm-yes");
  const confirmNo = document.getElementById("confirm-no");

  const stockModal = document.getElementById("stock-modal");
  const stockText = document.getElementById("stock-text");
  const stockOk = document.getElementById("stock-ok");

  const saveBtn = document.getElementById("saveAddressBtn");
  const editBtn = document.getElementById("editAddressBtn");
  const addressBox = document.getElementById("addressBox");
  const addressPreview = document.getElementById("addressPreview");

  const paymentSection = document.getElementById("paymentSection");
  const reviewSection = document.getElementById("reviewSection");
  const placeOrderBtn = document.getElementById("placeOrderBtn");

  const summaryItems = document.getElementById("summaryItems");
  const summaryOriginal = document.getElementById("summaryOriginal");
  const summaryDiscount = document.getElementById("summaryDiscount");
  const summaryDelivery = document.getElementById("summaryDelivery");
  const summaryTotal = document.getElementById("summaryTotal");
  const savedBanner = document.getElementById("saved-banner");

  const stateSelect = document.getElementById("state");
  const citySelect = document.getElementById("city");

  let targetItemId = null;
  let isAddressSaved = false;

  /* ==========================================================
     STATE → CITY LOGIC
  ========================================================== */
  const cities = {
    Gujarat: ["Ahmedabad", "Surat", "Vadodara", "Rajkot"],
    Maharashtra: ["Mumbai", "Pune", "Nagpur"],
    Delhi: ["New Delhi", "Dwarka", "Rohini"],
    Karnataka: ["Bangalore", "Mysore", "Hubli"],
    Rajasthan: ["Jaipur", "Udaipur", "Jodhpur"]
  };

  if (stateSelect && citySelect) {
    const selectedCity = citySelect.dataset.selected || "";

    stateSelect.addEventListener("change", function () {
      const state = this.value;
      citySelect.innerHTML = `<option value="">Select City</option>`;
      if (cities[state]) {
        cities[state].forEach(city => {
          const option = document.createElement("option");
          option.value = city;
          option.textContent = city;
          if (city === selectedCity) option.selected = true;
          citySelect.appendChild(option);
        });
      }
    });

    if (stateSelect.value) stateSelect.dispatchEvent(new Event("change"));
  }

  /* ==========================================================
     SUMMARY HELPER
  ========================================================== */
  const DELIVERY = parseFloat(summaryDelivery?.innerText || 0);

  function updateSummary() {
    let items = 0, originalTotal = 0, finalTotal = 0;

    document.querySelectorAll(".checkout-item").forEach(row => {
      const qty = parseInt(row.querySelector(".qty-number").innerText);
      const original = parseFloat(row.dataset.original || 0);
      const final = parseFloat(row.dataset.final || 0);
      items += qty;
      originalTotal += original * qty;
      finalTotal += final * qty;
    });

    const discount = originalTotal - finalTotal;
    const grandTotal = finalTotal + DELIVERY;

    summaryItems && (summaryItems.innerText = items);
    summaryOriginal && (summaryOriginal.innerText = originalTotal.toFixed(0));
    summaryDiscount && (summaryDiscount.innerText = discount.toFixed(0));
    summaryTotal && (summaryTotal.innerText = grandTotal.toFixed(0));

    if (savedBanner) {
      savedBanner.style.display = discount > 0 ? "block" : "none";
      savedBanner.innerText = discount > 0 ? `🎉 You saved ₹${discount.toFixed(0)}!` : "";
    }

    placeOrderBtn && (placeOrderBtn.disabled = (items === 0 || !isAddressSaved));
  }

  updateSummary();

  /* ==========================================================
     MODALS
  ========================================================== */
  function openConfirm(itemId) {
    targetItemId = itemId;
    confirmModal && (confirmModal.style.display = "flex");
  }

  function closeConfirm() {
    confirmModal && (confirmModal.style.display = "none");
    targetItemId = null;
  }

  function openStock(message) {
    stockText && (stockText.textContent = message);
    stockModal && (stockModal.style.display = "flex");
  }

  function closeStock() {
    stockModal && (stockModal.style.display = "none");
  }

  confirmNo?.addEventListener("click", closeConfirm);
  stockOk?.addEventListener("click", closeStock);

  /* ==========================================================
     ADDRESS LOGIC
  ========================================================== */
  function validateAddress() {
    const fullName = document.getElementById("full_name")?.value.trim();
    const phone = document.getElementById("phone")?.value.trim();
    const address = document.getElementById("address")?.value.trim();
    const state = stateSelect?.value;
    const city = citySelect?.value;
    const pincode = document.getElementById("pincode")?.value.trim();

    if (!fullName || !phone || !address || !state || !city || !pincode) {
      alert("Please fill all address fields");
      return false;
    }
    if (!/^\d{10}$/.test(phone)) { alert("Enter valid 10 digit mobile number"); return false; }
    if (!/^\d{6}$/.test(pincode)) { alert("Enter valid 6 digit pincode"); return false; }
    return true;
  }

  function renderPreview() {
    const fullName = document.getElementById("full_name").value;
    const phone = document.getElementById("phone").value;
    const address = document.getElementById("address").value;
    const state = stateSelect.value;
    const city = citySelect.value;
    const pincode = document.getElementById("pincode").value;

    if (addressPreview) {
      addressPreview.innerHTML = `
        <strong>${fullName}</strong><br>
        📍 ${address}<br>
        ${city}, ${state} - ${pincode}<br>
        📞 ${phone}<br><br>
        <button type="button" id="editAddressBtnPreview" class="btn btn-secondary">Edit Address</button>
      `;

      const editBtnPreview = document.getElementById("editAddressBtnPreview");
      editBtnPreview?.addEventListener("click", () => {
        editBtn.click(); // trigger the main edit logic
      });
    }
  }

  function showNotification(message) {
    const notif = document.createElement("div");
    notif.innerText = message;
    notif.style.position = "fixed";
    notif.style.top = "20px";
    notif.style.right = "20px";
    notif.style.background = "#4BB543"; // green
    notif.style.color = "white";
    notif.style.padding = "12px 20px";
    notif.style.borderRadius = "8px";
    notif.style.boxShadow = "0 2px 8px rgba(0,0,0,0.2)";
    notif.style.zIndex = 9999;
    document.body.appendChild(notif);
    setTimeout(() => notif.remove(), 3000);
  }

  saveBtn?.addEventListener("click", function () {
    if (!validateAddress()) return;

    renderPreview();

    addressBox.classList.add("hidden");
    addressPreview.classList.remove("hidden");

    saveBtn.style.display = "none";
    editBtn.style.display = "inline-block";

    paymentSection.classList.remove("disabled");
    reviewSection.classList.remove("disabled");

    isAddressSaved = true;
    updateSummary();

    showNotification("✅ Your changes have been saved!");
  });

  editBtn?.addEventListener("click", function () {
    // Prefill form fields from preview
    if (addressPreview) {
      const previewText = addressPreview.innerText.split("\n");
      document.getElementById("full_name").value = previewText[0] || "";
      document.getElementById("address").value = previewText[1] || "";
      
      const cityStateZip = previewText[2]?.split(" - ") || [];
      const cityState = cityStateZip[0]?.split(",") || [];
      stateSelect.value = cityState[1]?.trim() || "";

      // populate cities
      if (stateSelect.value) stateSelect.dispatchEvent(new Event("change"));
      citySelect.value = cityState[0]?.trim() || "";

      document.getElementById("pincode").value = cityStateZip[1]?.trim() || "";
      document.getElementById("phone").value = previewText[3]?.replace("📞", "").trim() || "";
    }

    addressBox.classList.remove("hidden");
    addressPreview.classList.add("hidden");

    editBtn.style.display = "none";
    saveBtn.style.display = "inline-block";

    paymentSection.classList.add("disabled");
    reviewSection.classList.add("disabled");

    isAddressSaved = false;
    updateSummary();
  });

  /* ==========================================================
     PLACE ORDER VALIDATION
  ========================================================== */
  placeOrderBtn?.addEventListener("click", function (e) {
    if (!isAddressSaved) {
      e.preventDefault();
      alert("Please save your address before placing the order.");
    }
  });

  /* ==========================================================
     CART QUANTITY HANDLING
  ========================================================== */
  const post = url => fetch(url, {
    method: "POST",
    headers: {
      "X-CSRFToken": document.cookie.split("; ").find(r => r.startsWith("csrftoken="))?.split("=")[1],
      "X-Requested-With": "XMLHttpRequest"
    }
  }).then(res => res.json());

  document.querySelectorAll(".plus-btn").forEach(btn => {
    btn.addEventListener("click", function () {
      const row = this.closest(".checkout-item");
      const qtyEl = row.querySelector(".qty-number");
      const itemId = row.dataset.id;
      const maxStock = parseInt(this.dataset.stock || 9999);
      const currentQty = parseInt(qtyEl.innerText);

      if (currentQty >= maxStock) { openStock(`⚠ Only ${maxStock} item(s) available.`); return; }

      post(`/cart/increase/${itemId}/`).then(data => {
        if (!data.success) { openStock(data.message || "Out of stock"); return; }
        qtyEl.innerText = data.quantity;
        updateSummary();
      });
    });
  });

  document.querySelectorAll(".minus-btn").forEach(btn => {
    btn.addEventListener("click", function () {
      const row = this.closest(".checkout-item");
      const qtyEl = row.querySelector(".qty-number");
      const itemId = row.dataset.id;
      const currentQty = parseInt(qtyEl.innerText);

      if (currentQty === 1) { openConfirm(itemId); return; }

      post(`/cart/decrease/${itemId}/`).then(data => {
        qtyEl.innerText = data.quantity;
        updateSummary();
      });
    });
  });

  document.querySelectorAll(".remove-btn").forEach(btn => {
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      const row = this.closest(".checkout-item");
      openConfirm(row.dataset.id);
    });
  });

  confirmYes?.addEventListener("click", function () {
    if (!targetItemId) return;

    post(`/cart/remove/${targetItemId}/`).then(() => {
      const row = document.querySelector(`.checkout-item[data-id="${targetItemId}"]`);
      if (row) row.remove();
      closeConfirm();
      updateSummary();
      if (document.querySelectorAll(".checkout-item").length === 0) location.reload();
    });
  });

});
