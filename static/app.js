let slideIndex = 0;

function moveSlide(step) {
    const slides = document.querySelectorAll('.carousel-item');
    slideIndex += step;

    if (slideIndex < 0) {
        slideIndex = slides.length - 1;
    }
    if (slideIndex >= slides.length) {
        slideIndex = 0;
    }

    const carousel = document.querySelector('.carousel');
    carousel.style.transform = `translateX(-${slideIndex * 100}%)`;
}

// Inicializa el carrusel en el primer slide
document.addEventListener('DOMContentLoaded', () => {
    moveSlide(0);
});
