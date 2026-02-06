document.addEventListener('DOMContentLoaded', () => {
    const productSelect = document.getElementById('productSelect');
    const categorySelect = document.getElementById('categorySelect');
    const discountType = document.querySelector('select[name="discount_type"]');
    const discountValue = document.querySelector('input[name="discount_value"]');

    // Enable only one selection: product OR category
    if (productSelect && categorySelect) {
        productSelect.addEventListener('change', () => {
            categorySelect.disabled = productSelect.value ? true : false;
        });

        categorySelect.addEventListener('change', () => {
            productSelect.disabled = categorySelect.value ? true : false;
        });
    }

    // Create warning element under discount input
    const warning = document.createElement('div');
    warning.className = 'discount-warning';
    warning.style.display = 'none';
    warning.textContent = '⚠️ You cannot enter more than 100%';
    discountValue.parentNode.appendChild(warning);

    // Limit discount value if percentage
    if (discountType && discountValue) {
        discountType.addEventListener('change', () => {
            warning.style.display = 'none'; // hide warning on type change
            if (discountType.value === 'percent') {
                discountValue.max = 100;
            } else {
                discountValue.removeAttribute('max');
            }
        });

        discountValue.addEventListener('input', () => {
            if (discountType.value === 'percent' && discountValue.value > 100) {
                discountValue.value = 100;
                warning.style.display = 'block';
            } else {
                warning.style.display = 'none';
            }
        });
    }
});
