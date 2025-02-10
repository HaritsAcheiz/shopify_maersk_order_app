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

// function showLabel(optionIndex) {
//     let originZipcode = document.getElementById("originZipcode").value || "91710";
//     // Read the JSON from the hidden script tag
//     const orderData = JSON.parse(document.getElementById('order-data').textContent);

//     // Get the selected shipping option data
//     const selectedOption = window.shippingOptionsData[optionIndex];

//     // Define the payload
//     const payload = {
//         Rating: {
//             LocationID: '',
//             Shipper: {
//                 Zipcode: originZipcode
//             },
//             Consignee: {
//                 Zipcode: orderData.detailAddress.zip
//             },
//             LineItems: getLineItems(orderData),
//             TariffHeaderID: ''
//         },
//         Shipment: {
//             Option: optionIndex, // Use the selected option index
//             PackageType: 'PALLET',
//             PayType: '0',
//             IsScreeningConsent: 'false',
//             Shipper: {
//                 Name: 'MAGIC CARS',
//                 Address1: '5151 EUCALYPTUS AVENUE',
//                 Address2: '',
//                 Address3: '',
//                 City: 'CHINO',
//                 Owner: 'MAGIC CARS',
//                 Contact: 'SHIPPING',
//                 Phone: '8008285699',
//                 Extension: '',
//                 Email: '',
//                 SendEmail: ''
//             },
//             Consignee: {
//                 Name: orderData.customer.name,
//                 Address1: orderData.detailAddress.address1,
//                 Address2: orderData.detailAddress.address2,
//                 Address3: '',
//                 City: orderData.detailAddress.city,
//                 Owner: orderData.customer.name,
//                 Contact: orderData.customer.name,
//                 Phone: orderData.customer.phone,
//                 Extension: '',
//                 Email: orderData.customer.email,
//                 SendEmail: ''
//             }
//         }
//     };

//     // Send a POST request to the /get-label endpoint
//     fetch(`/get-label`, {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json'
//         },
//         body: JSON.stringify(payload)
//     })
//         .then(response => response.json())
//         .then(data => {
//             const modalContent = document.querySelector('.modal-content');
//             modalContent.innerHTML = '';

//             const jsonContainer = document.createElement('pre');
//             jsonContainer.style.whiteSpace = 'pre-wrap';
//             jsonContainer.textContent = JSON.stringify(data, null, 2);

//             const closeButton = document.createElement('span');
//             closeButton.className = 'close';
//             closeButton.innerHTML = '&times;';
//             closeButton.onclick = function () {
//                 document.getElementById('labelModal').style.display = 'none';
//             };

//             modalContent.appendChild(closeButton);
//             modalContent.appendChild(jsonContainer);
//             document.getElementById('labelModal').style.display = 'block';
//         })
//         .catch(error => {
//             console.error('Error fetching label data:', error);
//             alert('Failed to load shipping label data');
//         });
// }

function showLabel(optionIndex) {
    let originZipcode = document.getElementById("originZipcode").value || "91710";
    const orderData = JSON.parse(document.getElementById('order-data').textContent);
    const selectedOption = window.shippingOptionsData[optionIndex];

    const payload = {
        Rating: {
            LocationID: '',
            Shipper: {
                Zipcode: originZipcode
            },
            Consignee: {
                Zipcode: orderData.detailAddress.zip
            },
            LineItems: getLineItems(orderData),
            TariffHeaderID: ''
        },
        Shipment: {
            Option: optionIndex,
            PackageType: 'PALLET',
            PayType: '0',
            IsScreeningConsent: 'false',
            Shipper: {
                Name: 'MAGIC CARS',
                Address1: '5151 EUCALYPTUS AVENUE',
                Address2: '',
                Address3: '',
                City: 'CHINO',
                Owner: 'MAGIC CARS',
                Contact: 'SHIPPING',
                Phone: '8008285699',
                Extension: '',
                Email: '',
                SendEmail: ''
            },
            Consignee: {
                Name: orderData.customer.name,
                Address1: orderData.detailAddress.address1,
                Address2: orderData.detailAddress.address2,
                Address3: '',
                City: orderData.detailAddress.city,
                Owner: orderData.customer.name,
                Contact: orderData.customer.name,
                Phone: orderData.customer.phone,
                Extension: '',
                Email: orderData.customer.email,
                SendEmail: ''
            }
        }
    };

    fetch(`/get-label`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.text())
    .then(data => {
        // Parse the XML string
        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(data, "text/xml");

        // Get the base64 PDF data
        const base64Data = xmlDoc.querySelector('DataStream_Byte').textContent;
        console.log(base64Data);

        // Convert base64 to blob
        const binaryData = atob(base64Data);
        const array = new Uint8Array(binaryData.length);
        for (let i = 0; i < binaryData.length; i++) {
            array[i] = binaryData.charCodeAt(i);
        }
        const pdfBlob = new Blob([array], { type: 'application/pdf' });

        // Create object URL
        const pdfUrl = URL.createObjectURL(pdfBlob);

        // Update modal content
        const modalContent = document.querySelector('.modal-content');
        modalContent.innerHTML = `
            <span class="close">&times;</span>
            <iframe src="${pdfUrl}" width="100%" height="600px" style="border: none;"></iframe>
        `;

        // Set up close button functionality
        const closeButton = modalContent.querySelector('.close');
        closeButton.onclick = function() {
            document.getElementById('labelModal').style.display = 'none';
            // Clean up the object URL when closing
            URL.revokeObjectURL(pdfUrl);
        };

        // Show the modal
        document.getElementById('labelModal').style.display = 'block';
    })
    // .catch(error => {
    //     console.error('Error fetching label data:', error);
    //     alert('Failed to load shipping label data');
    // });
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
    let zipcode = document.getElementById("originZipcode").value || "91710";
    let ordername = document.getElementById("orderName").textContent;
    fetch(`/get-shipping-options?zipcode=${zipcode}&ordername=${ordername}`)
        .then(response => response.json())
        .then(data => {
            console.log(data);
            let shippingSection = document.getElementById("shippingOptionsSection");
            let shippingTable = document.getElementById("shippingOptionsTable");
            shippingTable.innerHTML = ""; // Clear existing data
            if (data.length > 0) {
                shippingSection.style.display = "block"; // Show the section
                data.forEach((service, index) => {
                    let row = `<tr>
                        <td>${service.DisplayService}</td>
                        <td>$${service.TotalQuote.toFixed(2)}</td>
                        <td>${service.DeliveryDate.split('T')[0]}</td>
                        <td><button onclick="showLabel(${index})" class="shipnow-button">Ship Now</button></td>
                    </tr>`;
                    shippingTable.innerHTML += row;
                });
                // Store the shipping options data in a global variable for later access
                window.shippingOptionsData = data;
            } else {
                shippingSection.style.display = "none"; // Hide if no results
            }
        })
        .catch(error => {
            console.error("Error fetching shipping options:", error);
            document.getElementById("shippingOptionsSection").style.display = "none";
        });
}

function getLineItems(orderData) {
    let lineItems = [];

    if (!orderData._items || orderData._items.length === 0) {
        return lineItems; // Return empty if no items
    }

    orderData._items.forEach(item => {
        let name = item.name;
        let quantity = item.currentQuantity || 1; // Default to 1 if missing
        let weight = 1; // Default weight

        // Extract weight dynamically if available
        try {
            weight = item.product.variants.edges[0].node.inventoryItem.measurement.weight.value || 1;
        } catch (error) {
            console.warn(`Weight not found for item: ${name}, using default 1`);
        }

        // Push to the lineItems array
        lineItems.push({
            Pieces: quantity.toString(),
            Weight: weight.toString(),
            Description: name,
            Length: "61",
            Width: "40",
            Height: "24"
        });
    });

    return lineItems;
}