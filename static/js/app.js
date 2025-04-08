document.addEventListener("DOMContentLoaded", function() {
    const carousel = document.querySelector('.carousel');
    const carouselItems = document.querySelectorAll('.carousel-item');
    let currentIndex = 0;

    // Function to move the carousel
    function moveCarousel() {
        const totalItems = carouselItems.length;
        const itemWidth = carouselItems[0].clientWidth;
        carousel.style.transform = `translateX(-${currentIndex * itemWidth}px)`;
    }

    // Previous button
    document.querySelector('.prev').addEventListener('click', function() {
        if (currentIndex > 0) {
            currentIndex--;
        } else {
            currentIndex = carouselItems.length - 1;
        }
        moveCarousel();
    });

    // Next button
    document.querySelector('.next').addEventListener('click', function() {
        if (currentIndex < carouselItems.length - 1) {
            currentIndex++;
        } else {
            currentIndex = 0;
        }
        moveCarousel();
    });

    // Set the initial position of the carousel
    moveCarousel();
});
