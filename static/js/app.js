fetch('URL_DE_TU_API')
  .then(response => response.json())
  .then(data => {
    const carouselItemsContainer = document.getElementById('carouselItems');
    // Mezcla las imágenes de forma aleatoria
    const shuffledData = data.sort(() => Math.random() - 0.5);
    shuffledData.forEach((item, index) => {
      const isActive = index === 0 ? 'active' : '';
      const carouselItem = document.createElement('div');
      carouselItem.classList.add('carousel-item', isActive);
      const img = document.createElement('img');
      img.src = item.poster_url; // Asegúrate de que 'poster_url' sea la propiedad correcta
      img.alt = item.title;
      img.classList.add('d-block', 'w-100');
      carouselItem.appendChild(img);
      carouselItemsContainer.appendChild(carouselItem);
    });
  })
  .catch(error => console.error('Error al cargar las imágenes:', error));
  document.addEventListener('DOMContentLoaded', () => {
    new bootstrap.Carousel(document.getElementById('carouselExample'), {
      interval: 2000, // Intervalo de tiempo entre cada imagen (en milisegundos)
      ride: 'carousel' // Inicia el carrusel automáticamente
    });
  });
  
