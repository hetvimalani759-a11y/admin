document.addEventListener("DOMContentLoaded", function () {

  /* ===============================
     ELEMENTS
  =============================== */

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

  let targetItemId = null;
  let isAddressSaved = false;

  const FREE_DELIVERY_LIMIT = 999;
  const DELIVERY_CHARGE = 50;
  const MAX_QTY = 5;
  const stateSelect = document.getElementById("state");
  const citySelect = document.getElementById("city");

 

  // const cities = {
  //   Gujarat: ["Ahmedabad", "Surat", "Vadodara", "Rajkot"],
  //   Maharashtra: ["Mumbai", "Pune", "Nagpur"],
  //   Delhi: ["New Delhi", "Dwarka", "Rohini"],
  //   Karnataka: ["Bangalore", "Mysore", "Hubli"],
  //   Rajasthan: ["Jaipur", "Udaipur", "Jodhpur"]
  // };

  // if (stateSelect && citySelect) {
  //   const selectedCity = citySelect.dataset.selected || "";
  //   stateSelect.addEventListener("change", function () {
  //     const state = this.value;
  //     citySelect.innerHTML = `<option value="">Select City</option>`;
  //     if (cities[state]) {
  //       cities[state].forEach(city => {
  //         const option = document.createElement("option");
  //         option.value = city;
  //         option.textContent = city;
  //         if (city === selectedCity) option.selected = true;
  //         citySelect.appendChild(option);
  //       });
  //     }
  //   });
  //   if (stateSelect.value) stateSelect.dispatchEvent(new Event("change"));
  // }

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

  /* ===============================
     MODALS
  =============================== */

  function openConfirm(id) {
    targetItemId = id;
    confirmModal.style.display = "flex";
  }

  function closeConfirm() {
    confirmModal.style.display = "none";
    targetItemId = null;
  }

  function openStock(msg) {
    stockText.innerText = msg;
    stockModal.style.display = "flex";
  }

  function closeStock() {
    stockModal.style.display = "none";
  }

  confirmNo?.addEventListener("click", closeConfirm);
  stockOk?.addEventListener("click", closeStock);

  /* ===============================
     ADDRESS VALIDATION
  =============================== */

  function validateAddress() {

    const fullName = document.getElementById("full_name").value.trim();
    const phone = document.getElementById("phone").value.trim();
    const address = document.getElementById("address").value.trim();
    const state = document.getElementById("state").value;
    const city = document.getElementById("city").value;
    const pincode = document.getElementById("pincode").value.trim();

    if (!fullName || !phone || !address || !state || !city || !pincode) {
      alert("Please fill all address fields");
      return false;
    }

    if (!/^\d{10}$/.test(phone)) {
      alert("Enter valid 10 digit phone number");
      return false;
    }

    if (!/^\d{6}$/.test(pincode)) {
      alert("Enter valid 6 digit pincode");
      return false;
    }

    return true;
  }

  function renderPreview() {

    const fullName = document.getElementById("full_name").value;
    const phone = document.getElementById("phone").value;
    const address = document.getElementById("address").value;
    const city = document.getElementById("city").value;
    const state = document.getElementById("state").value;
    const pincode = document.getElementById("pincode").value;

    addressPreview.innerHTML = `
      <strong>${fullName}</strong><br>
      📍 ${address}<br>
      ${city}, ${state} - ${pincode}<br>
      📞 ${phone}<br><br>
      <button type="button" id="editAddressBtnPreview" class="btn btn-secondary">
        Edit Address
      </button>
    `;

    document
      .getElementById("editAddressBtnPreview")
      ?.addEventListener("click", () => editBtn.click());
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
  });

  editBtn?.addEventListener("click", function () {

    addressBox.classList.remove("hidden");
    addressPreview.classList.add("hidden");

    saveBtn.style.display = "inline-block";
    editBtn.style.display = "none";

    paymentSection.classList.add("disabled");
    reviewSection.classList.add("disabled");

    isAddressSaved = false;

    updateSummary();
  });

  /* ===============================
     SUMMARY CALCULATION
  =============================== */

  function updateSummary() {

    let items = 0;
    let originalTotal = 0;
    let finalTotal = 0;

    document.querySelectorAll(".checkout-item").forEach(row => {

      const qty = parseInt(row.querySelector(".qty-number").innerText);
      const original = parseFloat(row.dataset.original);
      const final = parseFloat(row.dataset.final);

      items += qty;
      originalTotal += original * qty;
      finalTotal += final * qty;
    });

    const delivery = finalTotal >= FREE_DELIVERY_LIMIT ? 0 : DELIVERY_CHARGE;
    const discount = originalTotal - finalTotal;
    const total = finalTotal + delivery;

    summaryItems.innerText = items;
    summaryOriginal.innerText = originalTotal.toFixed(0);
    summaryDiscount.innerText = discount.toFixed(0);

    summaryDelivery.innerHTML =
      delivery === 0
        ? `<span style="color:green;font-weight:600;">Free 🎉</span>`
        : `₹${delivery}`;

    summaryTotal.innerText = total.toFixed(0);

    if (discount > 0) {
      savedBanner.style.display = "block";
      savedBanner.innerText = `🎉 You saved ₹${discount.toFixed(0)}!`;
    } else {
      savedBanner.style.display = "none";
    }

    placeOrderBtn.disabled = (items === 0 || !isAddressSaved);
  }

  updateSummary();

  /* ===============================
     CART API HELPER
  =============================== */

  const post = url =>
    fetch(url, {
      method: "POST",
      headers: {
        "X-CSRFToken":
          document.cookie
            .split("; ")
            .find(r => r.startsWith("csrftoken="))
            ?.split("=")[1],
        "X-Requested-With": "XMLHttpRequest"
      }
    }).then(res => res.json());

  /* ===============================
     QUANTITY INCREASE
  =============================== */

  document.querySelectorAll(".plus-btn").forEach(btn => {

    btn.addEventListener("click", function () {

      const row = this.closest(".checkout-item");
      const qtyEl = row.querySelector(".qty-number");
      const itemId = row.dataset.id;

      const qty = parseInt(qtyEl.innerText);

      if (qty >= MAX_QTY) {
        openStock(`⚠ Max ${MAX_QTY} items allowed.`);
        return;
      }

      post(`/cart/increase/${itemId}/`).then(data => {

        if (!data.success) {
          openStock(data.message || "Out of stock");
          return;
        }

        qtyEl.innerText = data.quantity;
        updateSummary();
      });
    });
  });

  /* ===============================
     QUANTITY DECREASE
  =============================== */

  document.querySelectorAll(".minus-btn").forEach(btn => {

    btn.addEventListener("click", function () {

      const row = this.closest(".checkout-item");
      const qtyEl = row.querySelector(".qty-number");
      const itemId = row.dataset.id;

      const qty = parseInt(qtyEl.innerText);

      if (qty === 1) {
        openConfirm(itemId);
        return;
      }

      post(`/cart/decrease/${itemId}/`).then(data => {

        if (!data.success) {
          openStock(data.message || "Cannot decrease");
          return;
        }

        qtyEl.innerText = data.quantity;
        updateSummary();
      });
    });
  });

  /* ===============================
     REMOVE ITEM
  =============================== */

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

      if (!document.querySelector(".checkout-item")) {
        location.reload();
      }
    });
  });

  /* ===============================
     PLACE ORDER CHECK
  =============================== */

  placeOrderBtn?.addEventListener("click", function (e) {

    if (!isAddressSaved) {
      e.preventDefault();
      alert("Please save your address first.");
    }
  });

});