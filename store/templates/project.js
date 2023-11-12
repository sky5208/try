// project.js

// Function to update the stock value and display it
function updateStock() {
    if (product.stock > 0) {
        product.stock -= 1;
        document.getElementById('stockValue').textContent = product.stock;
    } else {
        alert('สินค้าหมดสต็อก');
    }
}

// Add a click event listener to the "เพิ่มสินค้าในตะกร้า" button
document.getElementById('addToCartButton').addEventListener('click', updateStock);
