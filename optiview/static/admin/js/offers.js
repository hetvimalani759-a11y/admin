document.addEventListener("DOMContentLoaded", function () {

    const modal = document.getElementById("deleteModal");
    const deleteText = document.getElementById("deleteText");
    const deleteForm = document.getElementById("deleteForm");
    const cancelBtn = document.getElementById("cancelDelete");

    document.querySelectorAll(".btn-delete").forEach(btn => {
        btn.addEventListener("click", function () {
            const id = this.dataset.id;
            const name = this.dataset.name;

            deleteText.textContent = `Are you sure you want to delete "${name}"?`;
            deleteForm.action = `/admin-panel/offers/delete/${id}/`; // ✅ adjust if needed

            modal.style.display = "flex";
        });
    });

    cancelBtn.addEventListener("click", function () {
        modal.style.display = "none";
    });

});
