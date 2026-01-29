document.addEventListener('DOMContentLoaded', function () {

    const buttons = document.querySelectorAll('.filter-btn');
    const cards = document.querySelectorAll('.shop-card');

    buttons.forEach(btn => {
        btn.addEventListener('click', () => {

            buttons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const filter = btn.dataset.filter;

            cards.forEach(card => {
                card.style.display =
                    (filter === 'all' || card.dataset.category === filter)
                        ? 'flex' : 'none';
            });
        });
    });

});
