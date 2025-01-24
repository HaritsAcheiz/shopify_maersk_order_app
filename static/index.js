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
});

// Define the viewOrderDetails function outside the event listener
function viewOrderDetails(orderId) {
    // Redirect to the order details page with the orderId as a query parameter
    window.location.href = `/order-details?order_id=${orderId}`;
}