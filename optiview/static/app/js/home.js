document.addEventListener("DOMContentLoaded", function() {
    const slides = document.querySelectorAll('.hero-slide');
    let slideIndex = 0;
    const interval = 4000; // 4 seconds

    if (slides.length === 0) return;

    // show first slide
    slides[0].classList.add('show');

    setInterval(() => {
        slides[slideIndex].classList.remove('show');
        slideIndex = (slideIndex + 1) % slides.length;
        slides[slideIndex].classList.add('show');
    }, interval);
});
