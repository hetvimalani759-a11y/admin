document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("deleteModal");
    const cancelBtn = document.getElementById("cancelDelete");
    const deleteForm = document.getElementById("deleteForm");
    const deleteText = document.getElementById("deleteText");

    document.querySelectorAll(".btn-delete").forEach(btn => {
        btn.addEventListener("click", () => {
            const id = btn.dataset.id;
            const name = btn.dataset.name;

            deleteText.textContent = `Are you sure you want to delete "${name}"?`;
            deleteForm.action = `/admin-panel/categories/${id}/delete/`; // adjust if needed
            modal.style.display = "flex";
        });
    });

    cancelBtn.addEventListener("click", () => {
        modal.style.display = "none";
    });

    modal.addEventListener("click", (e) => {
        if (e.target === modal) modal.style.display = "none";
    });
});
