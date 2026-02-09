document.addEventListener("DOMContentLoaded", function () {
    const categorySelect = document.getElementById("category");
    const subcategorySelect = document.getElementById("subcategory");

    categorySelect.addEventListener("change", function () {
        const categoryId = this.value;

        subcategorySelect.innerHTML = "<option value=''>Loading...</option>";

        if (!categoryId) {
            subcategorySelect.innerHTML = "<option value=''>Select Subcategory</option>";
            return;
        }

        fetch(`/admin-panel/ajax/subcategories/${categoryId}/`)
            .then(res => res.json())
            .then(data => {
                let options = "<option value=''>Select Subcategory</option>";
                data.forEach(sub => {
                    options += `<option value="${sub.id}">${sub.name}</option>`;
                });
                subcategorySelect.innerHTML = options;
            })
            .catch(err => {
                console.error("Failed to load subcategories:", err);
                subcategorySelect.innerHTML = "<option value=''>Select Subcategory</option>";
            });
    });
});
