const params = new URLSearchParams(window.location.search);
const productName = params.get('name');
const container = document.querySelector('.product-page');

fetch('products.csv')
  .then(r => r.text())
  .then(data => {
    const lines = data.split('\n');
    let found = false;

    lines.slice(1).forEach(line => {
      const [name, price, image] = line.split(';');

      if (name && name.trim() === productName) {
        found = true;
        container.innerHTML = `
          <h1>${name}</h1>
          <img src="images/${image.trim()}" width="200">
          <p>${price} ₽</p>
        `;
      }
    });

    if (!found) {
      container.textContent = 'Товар не найден';
    }
  });