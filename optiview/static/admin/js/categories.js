document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("deleteModal");
    const cancelBtn = document.getElementById("cancelDelete");
    const deleteForm = document.getElementById("deleteForm");
    const deleteText = document.getElementById("deleteText");

    // Delete button click
    document.querySelectorAll(".btn-delete").forEach(btn => {
        btn.addEventListener("click", () => {
            const id = btn.dataset.id;
            const name = btn.dataset.name;

            deleteText.textContent = `Are you sure you want to delete "${name}"?`;
            deleteForm.action = `/admin-panel/category/delete/${id}/`; // must match urls.py
            modal.style.display = "flex";
        });
    });

    // Cancel modal
    cancelBtn.addEventListener("click", () => {
        modal.style.display = "none";
    });

    // Click outside modal to close
    modal.addEventListener("click", (e) => {
        if (e.target === modal) modal.style.display = "none";
    });
});
