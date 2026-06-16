// Manejo del estado global de la app
let activeTab = 'text';

document.addEventListener('DOMContentLoaded', () => {
    // Inicializar zona drag-and-drop
    const uploadZone = document.getElementById('upload-zone');
    
    if (uploadZone) {
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                uploadZone.style.borderColor = 'var(--accent)';
                uploadZone.style.background = 'rgba(192, 132, 252, 0.08)';
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                uploadZone.style.borderColor = 'var(--border-glass)';
                uploadZone.style.background = 'rgba(10, 10, 15, 0.4)';
            }, false);
        });

        uploadZone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length > 0) {
                const fileInput = document.getElementById('image-file');
                fileInput.files = files;
                handleFileSelect({ target: { files: files } });
            }
        });
    }
});

// Cambiar de pestaña (Texto / Imagen)
function switchTab(tab) {
    activeTab = tab;
    document.getElementById('current-tab').value = tab;
    
    // Botones de pestañas
    const btnText = document.getElementById('tab-text');
    const btnImage = document.getElementById('tab-image');
    
    // Contenedores del formulario
    const textSection = document.getElementById('text-section');
    const imageSection = document.getElementById('image-section');
    
    // Badge de previsualización
    const badge = document.getElementById('output-badge');
    const presetSelector = document.getElementById('preset-selector-group');

    if (tab === 'text') {
        btnText.classList.add('active');
        btnImage.classList.remove('active');
        textSection.classList.remove('hidden');
        imageSection.classList.add('hidden');
        presetSelector.classList.remove('hidden');
        badge.textContent = 'Silueta de Texto';
    } else {
        btnText.classList.remove('active');
        btnImage.classList.add('active');
        textSection.classList.add('hidden');
        imageSection.classList.remove('hidden');
        badge.textContent = 'Mosaico/Silueta de Imagen';
        toggleImageOptions(); // Actualizar visibilidad de paletas y umbral según el radio
    }
}

// Manejar la selección de archivos
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(event) {
            document.getElementById('upload-img-preview').src = event.target.result;
            document.getElementById('upload-prompt').classList.add('hidden');
            document.getElementById('upload-preview-container').classList.remove('hidden');
        };
        reader.readAsDataURL(file);
    }
}

// Limpiar carga de archivo
function clearUpload(e) {
    e.stopPropagation();
    e.preventDefault();
    document.getElementById('image-file').value = '';
    document.getElementById('upload-img-preview').src = '';
    document.getElementById('upload-prompt').classList.remove('hidden');
    document.getElementById('upload-preview-container').classList.add('hidden');
}

// Conmutar opciones de imagen según el modo seleccionado (Mosaico de Color vs Silueta)
function toggleImageOptions() {
    if (activeTab !== 'image') return;
    
    const mode = document.querySelector('input[name="mode"]:checked').value;
    const thresholdContainer = document.getElementById('threshold-container');
    const presetSelector = document.getElementById('preset-selector-group');
    
    if (mode === 'mosaic') {
        thresholdContainer.classList.add('hidden');
        presetSelector.classList.add('hidden'); // Mosaico usa colores reales de foto
    } else {
        thresholdContainer.classList.remove('hidden');
        presetSelector.classList.remove('hidden'); // Silueta usa paleta de color
    }
}

// Actualizar indicador visual del slider de umbral
function updateSliderVal(val) {
    document.getElementById('threshold-val').textContent = val;
}

// Seleccionar Preset de Color
function selectPreset(id, element) {
    document.getElementById('selected-preset').value = id;
    
    // Quitar active de los demás presets
    const cards = document.querySelectorAll('.preset-card');
    cards.forEach(card => card.classList.remove('active'));
    
    // Agregar active al seleccionado
    element.classList.add('active');
}

// Enviar formulario y generar arte asíncronamente
async function generateArt(event) {
    event.preventDefault();
    
    const form = document.getElementById('art-form');
    const formData = new FormData(form);
    
    const loader = document.getElementById('loader');
    const emptyState = document.getElementById('empty-state');
    const outputImage = document.getElementById('output-image');
    const actionsContainer = document.getElementById('actions-container');
    const submitBtn = document.getElementById('submit-btn');

    // Validar en modo imagen si hay archivo
    if (activeTab === 'image') {
        const fileInput = document.getElementById('image-file');
        if (fileInput.files.length === 0) {
            alert('Por favor, selecciona o arrastra una imagen de referencia primero.');
            return;
        }
    }

    // Configurar estado cargando
    loader.classList.remove('hidden');
    emptyState.classList.add('hidden');
    outputImage.classList.add('hidden');
    actionsContainer.classList.add('hidden');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Generando...';

    const endpoint = activeTab === 'text' ? '/generate' : '/generate_from_image';

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.error || 'Ocurrió un error al procesar la imagen.');
        }

        const blob = await response.blob();
        const imageUrl = URL.createObjectURL(blob);
        
        outputImage.src = imageUrl;
        outputImage.classList.remove('hidden');
        actionsContainer.classList.remove('hidden');
    } catch (error) {
        console.error(error);
        alert('Error: ' + error.message);
        emptyState.classList.remove('hidden');
    } finally {
        loader.classList.add('hidden');
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fa-solid fa-rotate-right"></i> Generar Obra de Arte';
    }
}

// Descargar la obra generada
function downloadImage() {
    const img = document.getElementById('output-image');
    if (img && img.src) {
        const link = document.createElement('a');
        link.href = img.src;
        // Nombre sugerido según el modo y fecha
        const dateStr = new Date().toISOString().slice(0,10);
        link.download = `wordart-${activeTab}-${dateStr}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}
