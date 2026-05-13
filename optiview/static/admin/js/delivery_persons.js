const deleteButtons = document.querySelectorAll('.btn-delete');
const modal = document.getElementById('deleteModal');
const deleteText = document.getElementById('deleteText');
const cancelBtn = document.getElementById('cancelDelete');
const deleteForm = document.getElementById('deleteForm');

deleteButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        const name = btn.dataset.name;
        const id = btn.dataset.id;
        deleteText.textContent = `Are you sure you want to delete "${name}"?`;
        deleteForm.action = `/delivery/delivery-persons/delete/${id}/`;
        modal.classList.add('active');
    });
});

cancelBtn.addEventListener('click', () => {
    modal.classList.remove('active');
});
