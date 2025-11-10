// Configuración de Socket.IO
const socket = io();

// Estado de la aplicación
let detectionEnabled = true;
let detections = [];

// Elementos del DOM
const videoStream = document.getElementById('video-stream');
const toggleDetectionBtn = document.getElementById('toggle-detection');
const captureBtn = document.getElementById('capture-btn');
const confidenceSlider = document.getElementById('confidence-slider');
const confidenceValue = document.getElementById('confidence-value');
const alertsContainer = document.getElementById('alerts-container');
const detectionsList = document.getElementById('detections-list');
const totalDetectionsEl = document.getElementById('total-detections');
const highAlertsEl = document.getElementById('high-alerts');
const mediumAlertsEl = document.getElementById('medium-alerts');
const clearBtn = document.getElementById('clear-btn');
const exportBtn = document.getElementById('export-btn');
const refreshBtn = document.getElementById('refresh-btn');
const modal = document.getElementById('detection-modal');
const modalBody = document.getElementById('modal-body');
const closeModal = document.querySelector('.close');

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    loadDetections();
    loadStats();
    setupSocketListeners();
    
    // Actualizar estadísticas cada 5 segundos
    setInterval(loadStats, 5000);
});

// Configurar event listeners
function setupEventListeners() {
    toggleDetectionBtn.addEventListener('click', toggleDetection);
    captureBtn.addEventListener('click', captureFrame);
    confidenceSlider.addEventListener('input', updateConfidence);
    clearBtn.addEventListener('click', clearDetections);
    exportBtn.addEventListener('click', exportDetections);
    refreshBtn.addEventListener('click', () => {
        loadDetections();
        loadStats();
    });
    
    // Modal
    closeModal.addEventListener('click', () => {
        modal.style.display = 'none';
    });
    
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
}

// Configurar Socket.IO listeners
function setupSocketListeners() {
    socket.on('connect', () => {
        console.log('Conectado al servidor');
    });
    
    socket.on('weapon_detected', (data) => {
        handleWeaponDetection(data);
    });
    
    socket.on('status', (data) => {
        console.log('Estado:', data.message);
    });
}

// Toggle detección
async function toggleDetection() {
    detectionEnabled = !detectionEnabled;
    
    try {
        const response = await fetch('/api/toggle_detection', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ enabled: detectionEnabled })
        });
        
        const data = await response.json();
        detectionEnabled = data.enabled;
        
        toggleDetectionBtn.textContent = detectionEnabled 
            ? 'Desactivar Detección' 
            : 'Activar Detección';
        toggleDetectionBtn.classList.toggle('btn-secondary', !detectionEnabled);
        toggleDetectionBtn.classList.toggle('btn-primary', detectionEnabled);
    } catch (error) {
        console.error('Error al cambiar estado de detección:', error);
    }
}

// Actualizar umbral de confianza
async function updateConfidence() {
    const value = confidenceSlider.value;
    confidenceValue.textContent = value + '%';
    
    try {
        await fetch('/api/update_confidence', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ confidence: value / 100 })
        });
    } catch (error) {
        console.error('Error al actualizar confianza:', error);
    }
}

// Capturar frame
function captureFrame() {
    // Crear un canvas para capturar el frame del video
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = videoStream.videoWidth || 640;
    canvas.height = videoStream.videoHeight || 480;
    
    ctx.drawImage(videoStream, 0, 0);
    
    canvas.toBlob((blob) => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `capture_${Date.now()}.jpg`;
        a.click();
        URL.revokeObjectURL(url);
    }, 'image/jpeg');
}

// Manejar detección de arma
function handleWeaponDetection(data) {
    // Agregar a la lista de detecciones
    detections.unshift(data);
    if (detections.length > 100) {
        detections.pop();
    }
    
    // Mostrar alerta
    showAlert(data.summary);
    
    // Actualizar lista
    loadDetections();
    loadStats();
}

// Mostrar alerta
function showAlert(summary) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert-item ${summary.alert_level}`;
    
    const time = new Date().toLocaleTimeString();
    alertDiv.innerHTML = `
        <div class="alert-time">${time}</div>
        <div class="alert-message">${summary.message}</div>
    `;
    
    // Remover mensaje de "no hay alertas"
    const noAlerts = alertsContainer.querySelector('.no-alerts');
    if (noAlerts) {
        noAlerts.remove();
    }
    
    alertsContainer.insertBefore(alertDiv, alertsContainer.firstChild);
    
    // Limitar a 10 alertas
    while (alertsContainer.children.length > 10) {
        alertsContainer.removeChild(alertsContainer.lastChild);
    }
}

// Cargar detecciones
async function loadDetections() {
    try {
        const response = await fetch('/api/detections');
        const data = await response.json();
        
        detectionsList.innerHTML = '';
        
        if (data.length === 0) {
            detectionsList.innerHTML = '<p class="no-detections">No hay detecciones aún</p>';
            return;
        }
        
        data.forEach(detection => {
            const item = createDetectionItem(detection);
            detectionsList.appendChild(item);
        });
    } catch (error) {
        console.error('Error al cargar detecciones:', error);
    }
}

// Crear elemento de detección
function createDetectionItem(detection) {
    const item = document.createElement('div');
    item.className = `detection-item ${detection.alert_level}`;
    
    const time = new Date(detection.timestamp).toLocaleString();
    item.innerHTML = `
        <div class="detection-time">${time}</div>
        <div class="detection-message">${detection.weapon_count} arma(s) detectada(s)</div>
        <div class="detection-info">Nivel: ${detection.alert_level.toUpperCase()} | Tipos: ${detection.detection_types || 'N/A'}</div>
    `;
    
    item.addEventListener('click', () => {
        showDetectionDetails(detection.id);
    });
    
    return item;
}

// Mostrar detalles de detección
async function showDetectionDetails(detectionId) {
    try {
        const response = await fetch(`/api/detection/${detectionId}`);
        const detection = await response.json();
        
        modalBody.innerHTML = `
            <div class="detail-row">
                <div class="detail-label">Timestamp</div>
                <div class="detail-value">${new Date(detection.timestamp).toLocaleString()}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Armas Detectadas</div>
                <div class="detail-value">${detection.weapon_count}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Nivel de Alerta</div>
                <div class="detail-value">${detection.alert_level.toUpperCase()}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Tipos de Armas</div>
                <div class="detail-value">${detection.detection_types || 'N/A'}</div>
            </div>
            ${detection.image_path ? `
                <div class="detail-row">
                    <div class="detail-label">Imagen</div>
                    <img src="/${detection.image_path}" alt="Detección" style="max-width: 100%; border-radius: 5px; margin-top: 10px;">
                </div>
            ` : ''}
        `;
        
        modal.style.display = 'block';
    } catch (error) {
        console.error('Error al cargar detalles:', error);
        alert('Error al cargar los detalles de la detección');
    }
}

// Cargar estadísticas
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        
        totalDetectionsEl.textContent = stats.total;
        highAlertsEl.textContent = stats.high_alerts;
        mediumAlertsEl.textContent = stats.medium_alerts;
    } catch (error) {
        console.error('Error al cargar estadísticas:', error);
    }
}

// Limpiar detecciones
function clearDetections() {
    if (confirm('¿Estás seguro de que quieres limpiar la lista de detecciones?')) {
        alertsContainer.innerHTML = '<p class="no-alerts">No hay alertas recientes</p>';
        detectionsList.innerHTML = '<p class="no-detections">No hay detecciones aún</p>';
        detections = [];
    }
}

// Exportar detecciones
async function exportDetections() {
    try {
        const response = await fetch('/api/detections');
        const data = await response.json();
        
        const jsonStr = JSON.stringify(data, null, 2);
        const blob = new Blob([jsonStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `weapon_detections_${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Error al exportar:', error);
        alert('Error al exportar las detecciones');
    }
}

