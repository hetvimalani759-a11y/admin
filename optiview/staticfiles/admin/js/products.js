document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("deleteModal");
  const cancelBtn = document.getElementById("cancelDelete");
  const deleteText = document.getElementById("deleteText");
  const deleteForm = document.getElementById("deleteForm");

  document.querySelectorAll(".btn-delete").forEach(btn => {
    btn.addEventListener("click", () => {
      const id = btn.dataset.id;
      const name = btn.dataset.name;

      deleteText.textContent = `Are you sure you want to delete "${name}"?`;
      deleteForm.action = `/admin-panel/products/delete/${id}/`; // adjust if your URL differs
      modal.classList.add("active");
    });
  });

  cancelBtn.addEventListener("click", () => {
    modal.classList.remove("active");
  });

  modal.addEventListener("click", e => {
    if (e.target === modal) modal.classList.remove("active");
  });
});
