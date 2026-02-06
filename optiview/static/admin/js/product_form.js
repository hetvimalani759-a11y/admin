document.addEventListener("DOMContentLoaded", function () {
  const categorySelect = document.getElementById("categorySelect");
  const subcategorySelect = document.getElementById("subcategorySelect");

  if (!categorySelect || !subcategorySelect) return;

  categorySelect.addEventListener("change", function () {
    const categoryId = this.value;

    subcategorySelect.innerHTML = '<option value="">Loading...</option>';
    subcategorySelect.disabled = true;

    if (!categoryId) {
      subcategorySelect.innerHTML = '<option value="">Select Subcategory</option>';
      subcategorySelect.disabled = true;
      return;
    }

    fetch(`/admin-panel/get-subcategories/${categoryId}/`)
      .then(res => res.json())
      .then(data => {
        subcategorySelect.innerHTML = '<option value="">Select Subcategory</option>';
        data.forEach(subcat => {
          const opt = document.createElement("option");
          opt.value = subcat.id;
          opt.textContent = subcat.name;
          subcategorySelect.appendChild(opt);
        });
        subcategorySelect.disabled = false;
      })
      .catch(() => {
        subcategorySelect.innerHTML = '<option value="">Error loading</option>';
      });
  });
});
