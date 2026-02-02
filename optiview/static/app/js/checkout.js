document.addEventListener("DOMContentLoaded", function () {

  /* ================= ADDRESS LOGIC (UNCHANGED) ================= */
  const editBtn = document.getElementById("editAddressBtn");
  const preview = document.getElementById("addressPreview");
  const box = document.getElementById("addressBox");
  const payment = document.getElementById("paymentSection");
  const review = document.getElementById("reviewSection");
  const placeBtn = document.getElementById("placeOrderBtn");
  if (preview.dataset.hasAddress === "1") {
  box.classList.add("hidden");
  preview.classList.remove("hidden");
  editBtn.classList.remove("hidden");
  payment.classList.remove("disabled");
  review.classList.remove("disabled");
  placeBtn.disabled = false;
}


  const full_name = document.getElementById("full_name");
  const phone = document.getElementById("phone");
  const address = document.getElementById("address");
  const city = document.getElementById("city");
  const state = document.getElementById("state");
  const pincode = document.getElementById("pincode");
  const saveBtn = document.getElementById("saveAddressBtn");

  const DELIVERY = parseFloat(document.getElementById("summaryDelivery")?.innerText || 0);

  const cities = {
    Gujarat: ["Ahmedabad", "Surat", "Vadodara", "Rajkot"],
    Maharashtra: ["Mumbai", "Pune", "Nagpur"],
    Delhi: ["New Delhi", "Dwarka", "Rohini"],
    Karnataka: ["Bangalore", "Mysore", "Hubli"],
    Rajasthan: ["Jaipur", "Udaipur", "Jodhpur"]
  };

  state.addEventListener("change", function () {
    city.innerHTML = `<option value="">Select City</option>`;
    if (cities[this.value]) {
      cities[this.value].forEach(c => {
        const opt = document.createElement("option");
        opt.value = c;
        opt.textContent = c;
        city.appendChild(opt);
      });
    }
  });

  saveBtn.addEventListener("click", function () {
    if (!full_name.value || !phone.value || !address.value || !city.value || !state.value || !pincode.value) {
      alert("Please fill all address fields");
      return;
    }

    preview.innerHTML = `
      <strong>${full_name.value}</strong><br>
      ${address.value}, ${city.value}, ${state.value} - ${pincode.value}<br>
      📞 +91 ${phone.value}
    `;

    box.classList.add("hidden");
    preview.classList.remove("hidden");
    editBtn.classList.remove("hidden");

    payment.classList.remove("disabled");
    review.classList.remove("disabled");
    placeBtn.disabled = false;
  });

  editBtn.addEventListener("click", function () {
    preview.classList.add("hidden");
    box.classList.remove("hidden");
    editBtn.classList.add("hidden");

    payment.classList.add("disabled");
    review.classList.add("disabled");
    placeBtn.disabled = true;
  });

  /* ================= MODAL ================= */
  const modal = document.getElementById("confirm-modal");
  const modalText = document.getElementById("confirm-text");
  const yesBtn = document.getElementById("confirm-yes");
  const noBtn = document.getElementById("confirm-no");

  let pendingAction = null;

  function openModal(text, action) {
    modalText.innerText = text;
    pendingAction = action;
    modal.style.display = "flex";
  }

  function closeModal() {
    modal.style.display = "none";
    pendingAction = null;
  }

  noBtn.onclick = closeModal;
  yesBtn.onclick = function () {
    if (pendingAction) pendingAction();
    closeModal();
  };

  /* ================= SUMMARY ================= */
  function recalcSummary() {
    let originalTotal = 0;
    let finalTotal = 0;
    let totalItems = 0;

    document.querySelectorAll(".checkout-item").forEach(row => {
      const qty = parseInt(row.querySelector(".qty-number").innerText);
      const original = parseFloat(row.dataset.original);
      const final = parseFloat(row.dataset.final);

      totalItems += qty;
      originalTotal += original * qty;
      finalTotal += final * qty;
    });

    const discount = originalTotal - finalTotal;
    const payable = finalTotal + DELIVERY;

    document.getElementById("summaryItems").innerText = totalItems;
    document.getElementById("summaryOriginal").innerText = Math.round(originalTotal);
    document.getElementById("summaryDiscount").innerText = Math.round(discount);
    document.getElementById("summaryTotal").innerText = Math.round(payable);

    const banner = document.getElementById("saved-banner");
    if (discount > 0) {
      banner.style.display = "flex";
      banner.innerText = `🎉 You saved ₹${Math.round(discount)}!`;
    } else {
      banner.style.display = "none";
    }
  }

  /* ================= REMOVE ================= */
  document.querySelectorAll(".remove-btn").forEach(btn => {
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      const row = this.closest(".checkout-item");
      const url = this.dataset.removeUrl;

      openModal("Remove this item from cart?", function () {
        fetch(url, { method: "GET" })
          .then(() => {
            row.remove();
            recalcSummary();
          });
      });
    });
  });

  /* ================= QUANTITY ================= */
  document.querySelectorAll(".plus-btn").forEach(btn => {
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      const qtyEl = this.previousElementSibling;
      qtyEl.innerText = parseInt(qtyEl.innerText) + 1;
      recalcSummary();
    });
  });

  document.querySelectorAll(".minus-btn").forEach(btn => {
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      const qtyEl = this.nextElementSibling;
      let qty = parseInt(qtyEl.innerText);
      const row = this.closest(".checkout-item");
      const removeBtn = row.querySelector(".remove-btn");
      const url = removeBtn.dataset.removeUrl;

      if (qty === 1) {
        openModal("Quantity is 1. Remove this item?", function () {
          fetch(url, { method: "GET" })
            .then(() => {
              row.remove();
              recalcSummary();
            });
        });
      } else {
        qtyEl.innerText = qty - 1;
        recalcSummary();
      }
    });
  });

  /* Run once */
  recalcSummary();

});
