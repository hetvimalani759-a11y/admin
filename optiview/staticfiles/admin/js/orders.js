document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".status-select").forEach(select => {
    select.addEventListener("change", () => {
      select.closest("form").submit();
    });
  });
});
