// Flight data fetching and filtering
async function fetchFlights() {
    try {
        const response = await fetch('/api/flights');
        const flights = await response.json();
        
        if (flights.error) {
            console.error(flights.error);
            return;
        }
        
        updateFlightTable(flights);
        updateFlightStats(flights);
    } catch (error) {
        console.error('Error fetching flights:', error);
    }
}

function updateFlightTable(flights) {
    const tableBody = document.getElementById('flight-table');
    if (!tableBody) return;
    
    tableBody.innerHTML = '';
    
    flights.forEach(flight => {
        const isDeparting = flight.status.toLowerCase().includes('depart') || 
                          new Date(flight.departure_time) > new Date();
        const isArriving = flight.status.toLowerCase().includes('arriv') || 
                         new Date(flight.arrival_time) > new Date();
        
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50';
        row.dataset.flight = 'true';
        row.dataset.departing = isDeparting;
        row.dataset.arriving = isArriving;
        
        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                    <div class="flex-shrink-0 h-10 w-10 bg-blue-100 rounded-full flex items-center justify-center">
                        <i class="fas fa-plane text-blue-600"></i>
                    </div>
                    <div class="ml-4">
                        <div class="text-sm font-medium text-gray-900">${flight.flight_number}</div>
                        <div class="text-sm text-gray-500">${flight.airline || 'Unknown'}</div>
                    </div>
                </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium">${flight.origin} → ${flight.destination}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-500">${formatTime(flight.departure_time)} - ${formatTime(flight.arrival_time)}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs font-medium rounded-full ${getStatusClass(flight.status)}">
                    ${flight.status}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button onclick="createAlertForFlight('${flight.flight_id}')" class="text-blue-600 hover:text-blue-900">
                    <i class="fas fa-bell"></i> Alert
                </button>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

function updateFlightStats(flights) {
    const departing = flights.filter(f => 
        f.status.toLowerCase().includes('depart') || 
        new Date(f.departure_time) > new Date()
    ).length;
    
    const arriving = flights.filter(f => 
        f.status.toLowerCase().includes('arriv') || 
        new Date(f.arrival_time) > new Date()
    ).length;
    
    document.getElementById('total-flights').textContent = flights.length;
    document.getElementById('departing-flights').textContent = departing;
    document.getElementById('arriving-flights').textContent = arriving;
}

function formatTime(timeString) {
    if (!timeString) return 'N/A';
    const date = new Date(timeString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function getStatusClass(status) {
    switch((status || '').toLowerCase()) {
        case 'on time': 
        case 'scheduled':
            return 'bg-green-100 text-green-800';
        case 'delayed': 
            return 'bg-yellow-100 text-yellow-800';
        case 'cancelled':
            return 'bg-red-100 text-red-800';
        case 'departed':
            return 'bg-blue-100 text-blue-800';
        case 'arrived':
            return 'bg-purple-100 text-purple-800';
        default: 
            return 'bg-gray-100 text-gray-800';
    }
}

function createAlertForFlight(flightId) {
    document.querySelector('#create-alert-modal select[name="flight_id"]').value = flightId;
    document.getElementById('create-alert-modal').classList.remove('hidden');
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Close buttons for flash messages
    document.querySelectorAll('.close-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            this.parentElement.remove();
        });
    });
    
    // Initialize flight data
    if (document.getElementById('flight-table')) {
        fetchFlights();
        setInterval(fetchFlights, 30000);
    }
});
function editAlert(alertId, flightId, alertType, message, notificationMethod, status, endTime) {
    document.getElementById('flightSelect').value = flightId;
    document.getElementById('alertType').value = alertType;
    document.getElementById('alertMessage').value = message || '';
    document.getElementById('notificationMethod').value = notificationMethod;
    document.getElementById('alertStatus').value = status;
    
    // Format the end time for datetime-local input
    if (endTime) {
        const dt = new Date(endTime);
        const formatted = dt.toISOString().slice(0, 16);
        document.getElementById('alertEndTime').value = formatted;
    }
    
    openModal('edit', alertId);
}
// Auto-refresh flights every 5 minutes
setInterval(() => {
    fetch('/update-flights')
        .then(response => response.json())
        .then(data => {
            if (!data.error) {
                window.location.reload();
            }
        });
}, 300000); // 5 minutes in milliseconds