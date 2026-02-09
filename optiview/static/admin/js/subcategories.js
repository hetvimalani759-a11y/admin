document.addEventListener("DOMContentLoaded", function () {
  const deleteButtons = document.querySelectorAll(".btn-delete");
  const modal = document.getElementById("deleteModal");
  const deleteText = document.getElementById("deleteText");
  const deleteForm = document.getElementById("deleteForm");
  const cancelBtn = document.getElementById("cancelDelete");

  deleteButtons.forEach(btn => {
    btn.addEventListener("click", function () {
      const subId = this.dataset.id;
      const subName = this.dataset.name;

      deleteText.textContent = `Are you sure you want to delete "${subName}"?`;
      deleteForm.action = `/admin-panel/subcategories/delete/${subId}/`;

      modal.style.display = "flex";
    });
  });

  cancelBtn.addEventListener("click", function () {
    modal.style.display = "none";
  });
});
