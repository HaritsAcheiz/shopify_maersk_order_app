document.addEventListener('DOMContentLoaded', () => {
  const AppBridge = window['app-bridge'];
  const createApp = AppBridge.default;

  // Retrieve shopOrigin from query parameters
  const shopOrigin = new URLSearchParams(window.location.search).get('shop');
  if (!shopOrigin) {
    console.error('Shop parameter is missing!');
    // Optionally redirect to an error page
    return;
  }

  // Initialize Shopify App Bridge
  const app = createApp({
    apiKey: 'bab5bf6827a5f563959611dcfe25a3ba',
    shopOrigin: shopOrigin
  });

  // Initialize Title Bar
  const TitleBar = AppBridge.actions.TitleBar;
  TitleBar.create(app, { title: 'Order Shipping Labels' });

  // Fetch orders initially
  fetchOrders();

  // Function to fetch orders from the server
  function fetchOrders(searchTerm = '') {
    const searchUrl = `/search_orders?search=${searchTerm}`;

    fetch(searchUrl)
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        // Clear any existing error messages
        const errorContainer = document.getElementById('errorContainer');
        errorContainer.style.display = 'none';
        errorContainer.textContent = '';

        // Update the order table with the fetched data
        const orderTableBody = document.getElementById('orderTableBody');
        orderTableBody.innerHTML = '';

        data.orders.forEach(order => {
          const row = document.createElement('tr');
          row.innerHTML = `
            <td>${order.no}</td>
            <td>${order.date}</td>
            <td>${order.customer}</td>
            <td>${order.totalPrice}</td>
            <td>${order.paymentStatus}</td>
            <td>${order.fulfillmentStatus}</td>
            <td>${order.shippingAddress}</td>
            <td><button class="action-button" onclick="viewOrderDetails('${order.no}')">View Details</button></td>
          `;
          orderTableBody.appendChild(row);
        });
      })
      .catch(error => {
        console.error('Error fetching orders:', error);

        // Display an error message to the user
        const errorContainer = document.getElementById('errorContainer');
        errorContainer.style.display = 'block';
        errorContainer.textContent = 'Error fetching orders. Please try again later.';
      });
  }

  // Event listener for the search input
  const searchBox = document.getElementById('searchBox');
  searchBox.addEventListener('input', () => {
    const searchTerm = searchBox.value;
    fetchOrders(searchTerm);
  });

  // Define the viewOrderDetails function outside the event listener
  function viewOrderDetails(orderId) {
    // Redirect to the order details page with the orderId as a query parameter
    window.location.href = `/order-details?order_id=${orderId}`;
  }
});