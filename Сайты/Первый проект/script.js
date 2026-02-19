fetch('products.csv')
    .then(response => response.text())
    .then(data => {
        const lines = data.split('\n');
        const container = document.querySelector('.products');

        lines.slice(1).forEach(line => {
            const [name, price, image] = line.split(';');

            if (!name) return;

            container.innerHTML += `
            
     <div class="product">
                    <img src="images/${image.trim()}" alt="${name}">
                    <h3>${name}</h3>
                    <strong>${price} ₽</strong>
                </div>
</body>
</html>
               
            `;
        });
    })
    .catch(error => console.error('Ошибка загрузки CSV:', error));
