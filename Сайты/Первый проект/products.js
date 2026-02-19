fetch('products.csv')
  .then(r => r.text())
  .then(data => {
    const lines = data.split('\n');
    const container = document.querySelector('.products');

    lines.slice(1).forEach(line => {
      const [name, price, image] = line.split(';');
      if (!name) return;

      container.innerHTML += `
        <div class="product">
          <a href="product.html?name=${name.trim()}">
            <img src="images/${image.trim()}">
            <h3>${name}</h3>
            <p>${price} ₽</p>
          </a>
        </div>
      `;
    });
  });