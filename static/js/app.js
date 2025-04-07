let slideIndex = 0;
const slides = document.querySelectorAll('.carousel-item');
const totalSlides = slides.length;
const itemsPerSlide = 3; // Mostrar tres elementos a la vez

// Ajusta el ancho del carrusel para que se muestren tres elementos a la vez
document.querySelector('.carousel').style.width = `${itemsPerSlide * 100}%`;

function moveSlide(n) {
    slideIndex += n;

    // Asegura que no se salga del rango
    if (slideIndex < 0) {
        slideIndex = Math.floor(totalSlides / itemsPerSlide) * itemsPerSlide; // Mueve al final del carrusel
    } else if (slideIndex > totalSlides - itemsPerSlide) {
        slideIndex = 0; // Vuelve al principio
    }

    // Mueve el carrusel
    const offset = -(slideIndex * (100 / itemsPerSlide)); // Desplaza en porcentaje
    document.querySelector('.carousel').style.transform = `translateX(${offset}%)`;
}

// Inicializa el carrusel
moveSlide(0);

// Botones de navegación
document.querySelector('.prev').addEventListener('click', () => moveSlide(-1));
document.querySelector('.next').addEventListener('click', () => moveSlide(1));
