document.addEventListener('DOMContentLoaded', () => {
    const AppBridge = window['app-bridge'];
    const createApp = AppBridge.default;

    async function initializeAppBridge() {
        try {
            const response = await fetch(`/api/init?shop=${shop}`);
            const data = await response.json();
            if (response.ok) {
                const app = createApp({
                    apiKey: data.apiKey,
                    host: btoa(`${data.shopOrigin}/admin`),
                });

            const Toast = AppBridge.actions.Toast;
            const toast = Toast.create(app, {
                message: 'Welcome to your Shopify App!',
                duration: 3000
            });
            toast.dispatch(Toast.Action.SHOW);

            // Update the title bar for order details
            const TitleBar = actions.TitleBar;
            TitleBar.update(app, { title: 'Order Details' });

            return app;
            } else {
                console.error('Failed to initialize App Bridge:', data.error);
            }
        } catch (error) {
            console.error('Error fetching API key:', error);
        }
    }

    // Initialize App Bridge
    initializeAppBridge();

    const modal = document.getElementById('labelModal');

    // Get the print button
    const printBtn = document.querySelector('.action-button');

    // Get the close button
    const closeBtn = document.querySelector('.close');

    // When print button is clicked, show modal
    printBtn.addEventListener('click', function() {
        // Fetch shipping label data from your backend
        // Replace this with your actual API endpoint
        fetch(`/get-label/${order_data.id}`)
            .then(response => response.json())
            .then(data => {
                // Update modal content with shipping label data
                document.getElementById('dateCreated').textContent = data.date_created;
                document.getElementById('orderNumber').textContent = data.order_number;
                document.getElementById('carrier').textContent = data.carrier;
                document.getElementById('weight').textContent = data.weight;
                document.getElementById('trackingNumber').textContent = data.tracking_number;

                // Add the barcode SVG to the modal
                const barcodeContainer = document.getElementById('barcode');
                barcodeContainer.innerHTML = data.barcode_svg;

                // Show the modal
                modal.style.display = 'block';
                document.body.style.overflow = 'hidden'; // Prevent scrolling
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to load shipping label');
            });
    });

    // Close modal when clicking (x)
    closeBtn.addEventListener('click', function() {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto'; // Re-enable scrolling
    });

    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto'; // Re-enable scrolling
        }
    });
});

function showLabel(orderId) {
    fetch(`/get-label/${orderId}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('dateCreated').textContent = data.date_created;
            document.getElementById('orderNumber').textContent = data.order_number;
            document.getElementById('carrier').textContent = data.carrier;
            document.getElementById('weight').textContent = data.weight;
            document.getElementById('trackingNumber').textContent = data.tracking_number;

            // Add the barcode SVG to the modal
            const barcodeContainer = document.getElementById('barcode');
            barcodeContainer.innerHTML = data.barcode_svg;

            document.getElementById('labelModal').style.display = 'block';
        });
}

// Close modal when clicking the X
document.querySelector('.close').onclick = function() {
    document.getElementById('labelModal').style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function(event) {
    if (event.target == document.getElementById('labelModal')) {
        document.getElementById('labelModal').style.display = 'none';
    }
}

// Print label function
function printLabel() {
    window.print();
}

// Print label function
function printLabel() {
    // Create a new window for printing the shipping label
    const printWindow = window.open('', '', 'height=600,width=800');
    printWindow.document.write(`
        <html>
        <head>
            <title>Shipping Label</title>
            <style>
                /* Add any necessary styles for the print view */
                body { font-family: Arial, sans-serif; }
                .label-content { padding: 20px; }
            </style>
        </head>
        <body onload="window.print(); setTimeout(function() { window.close(); }, 1000);">
            <div class="label-content">
                <h2>SHOPIFY - MAERSK E-DELIVERY</h2>
                <p>Date created: ${document.getElementById('dateCreated').textContent}</p>
                <p>Order #${document.getElementById('orderNumber').textContent}</p>
                <p>Carrier: ${document.getElementById('carrier').textContent}</p>
                <div>${document.getElementById('barcode').innerHTML}</div>
                <p>Weight: ${document.getElementById('weight').textContent}</p>
                <p>TYPNumber: ${document.getElementById('trackingNumber').textContent}</p>
            </div>
        </body>
        </html>
    `);
    printWindow.document.close();
}

function fetchShippingOptions() {
    let zipcode = document.getElementById("originZipcode").value || "91710"; // Default ZIP code

    fetch(`/get-shipping-options?zipcode=${zipcode}`)
        .then(response => response.json())
        .then(data => {
            let shippingSection = document.getElementById("shippingOptionsSection");
            let shippingTable = document.getElementById("shippingOptionsTable");
            shippingTable.innerHTML = ""; // Clear existing data

            if (data.length > 0) {
                shippingSection.style.display = "block"; // Show the section

                data.forEach(service => {
                    let row = `<tr>
                        <td>${service.DisplayService}</td>
                        <td>$${service.TotalQuote.toFixed(2)}</td>
                        <td>${service.DeliveryDate.split('T')[0]}</td>
                        <td><button onclick="showLabel('${service.LinkForShipping}')" class="shipnow-button">Ship Now</button></td>
                    </tr>`;
                    shippingTable.innerHTML += row;
                });
            } else {
                shippingSection.style.display = "none"; // Hide if no results
            }
        })
        .catch(error => {
            console.error("Error fetching shipping options:", error);
            document.getElementById("shippingOptionsSection").style.display = "none";
        });
}