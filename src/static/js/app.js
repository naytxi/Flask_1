// static/js/app.js (CON LÓGICA DE BUCLE CORREGIDA)
document.addEventListener("DOMContentLoaded", function() {
    console.log("DOM Cargado. Buscando carrusel...");
    const carousel = document.querySelector('.carousel');
    if (!carousel) {
        console.error("Elemento .carousel NO encontrado.");
        return;
    }
    // Necesitamos el contenedor para calcular cuántos caben
    const carouselContainer = document.querySelector('.carousel-container');
     if (!carouselContainer) {
        console.error("Elemento .carousel-container NO encontrado.");
        return;
    }

    const carouselItems = carousel.querySelectorAll('.carousel-item');
    if (carouselItems.length === 0) {
         console.error("No se encontraron .carousel-item dentro de .carousel.");
         return;
    }

    const prevButton = document.querySelector('.prev');
    const nextButton = document.querySelector('.next');
    if (!prevButton) console.warn("Botón .prev no encontrado.");
    if (!nextButton) console.warn("Botón .next no encontrado.");

    let currentIndex = 0;
    const totalItems = carouselItems.length;
    let itemWidth = 0;
    let itemsInView = 3; // Valor por defecto si falla el cálculo
    let maxIndex = 0; // Índice máximo al que podemos ir antes de mostrar huecos

    console.log(`Carrusel encontrado con ${totalItems} items.`);

    // Función para calcular cuántos items caben y el índice máximo
    function calculateCarouselParams() {
        if (carouselItems.length > 0 && carouselItems[0].offsetWidth > 0) {
             itemWidth = carouselItems[0].offsetWidth;
             // Calcula cuántos items caben aproximadamente en el contenedor
             // Usamos floor para redondear hacia abajo
             itemsInView = Math.max(1, Math.floor(carouselContainer.clientWidth / itemWidth));
             // Calcula el último índice que permite mostrar un grupo completo
             maxIndex = Math.max(0, totalItems - itemsInView);
             console.log(`Recalculado: itemWidth=${itemWidth}px, itemsInView=${itemsInView}, maxIndex=${maxIndex}`);
        } else {
            console.warn("No se pudo calcular itemWidth o no hay items. Usando valores por defecto.");
            // Si no podemos calcular, evitamos que los botones funcionen mal
             maxIndex = 0; // Solo permite estar en el índice 0
        }
         // Asegurarnos que currentIndex no sea inválido después de recalcular
         if (currentIndex > maxIndex) {
            currentIndex = maxIndex;
         }
    }


    // Función para mover el carrusel
    function moveCarousel(eventName = 'Desconocido') {
        // Usamos el itemWidth calculado previamente
        console.log(`[${eventName}] Moviendo carrusel: currentIndex=${currentIndex}, itemWidth=${itemWidth}px`);

        if (carousel && itemWidth > 0) {
             const newTransform = `translateX(-${currentIndex * itemWidth}px)`;
             console.log(`Aplicando transform: ${newTransform}`);
             carousel.style.transform = newTransform;
        } else if (itemWidth <= 0) {
            console.warn("itemWidth es 0 o inválido. No se aplicará transform.");
        }
    }

    // Botón Anterior
    if (prevButton) {
        prevButton.addEventListener('click', function() {
            console.log("Click en Botón ANTERIOR");
            const oldIndex = currentIndex;
            // Si está en el índice 0, va al último índice válido (maxIndex)
            // Si está en otro índice, simplemente retrocede 1
            currentIndex = (currentIndex > 0) ? currentIndex - 1 : maxIndex;
            console.log(`currentIndex cambiado de ${oldIndex} a ${currentIndex}`);
            moveCarousel('PrevClick');
        });
    }

    // Botón Siguiente
    if (nextButton) {
        nextButton.addEventListener('click', function() {
            console.log("Click en Botón SIGUIENTE");
            const oldIndex = currentIndex;
            // Si está en el último índice válido (maxIndex) o más allá, va al inicio (0)
            // Si está antes, simplemente avanza 1
            currentIndex = (currentIndex < maxIndex) ? currentIndex + 1 : 0;
            console.log(`currentIndex cambiado de ${oldIndex} a ${currentIndex}`);
            moveCarousel('NextClick');
        });
    }

    // Función inicial para configurar y posicionar
    function initializeCarousel() {
        calculateCarouselParams(); // Calcula anchos y límites
        moveCarousel('Initialize');  // Posiciona al inicio
    }

    // Establece la posición inicial DESPUÉS de que todo haya cargado
    window.addEventListener('load', initializeCarousel);

    // Recalcula y reposiciona si cambia el tamaño de la ventana
    window.addEventListener('resize', initializeCarousel);

});