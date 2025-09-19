document.addEventListener('DOMContentLoaded', () => {
    // --- LÓGICA DEL MODAL PRINCIPAL (LISTA) ---
    const mainModal = document.getElementById('alimentos-modal');
    if (!mainModal) return;

    const openBtn = document.getElementById('alimentos-btn');
    const mainCloseBtn = mainModal.querySelector('.close-btn');

    openBtn.addEventListener('click', () => { mainModal.style.display = 'block'; });
    mainCloseBtn.addEventListener('click', () => { mainModal.style.display = 'none'; });
    window.addEventListener('click', (event) => {
        if (event.target == mainModal) mainModal.style.display = 'none';
    });

    // --- LÓGICA DE PAGINACIÓN ---
    // (Tu código de paginación existente va aquí, sin cambios)


    // --- NUEVA LÓGICA PARA MODAL DE DETALLES ---
    const detailsModal = document.getElementById('details-modal');
    const detailsContent = detailsModal.querySelector('.details-content');

    // Función para cerrar el modal de detalles
    const closeDetailsModal = () => {
        detailsModal.style.display = 'none';
        detailsContent.innerHTML = ''; // Limpia el contenido
    };
    
    // Cerrar si se hace clic fuera del contenido
    window.addEventListener('click', (event) => {
        if (event.target == detailsModal) closeDetailsModal();
    });

    // Añadir evento a todos los botones "Ver detalles"
    mainModal.querySelectorAll('.details-btn').forEach(button => {
        button.addEventListener('click', async () => {
            const alimentoId = button.dataset.id;
            
            // Petición al backend para obtener los datos
            try {
                const response = await fetch(`/alimento/detalles/${alimentoId}/`);
                if (!response.ok) throw new Error('Error al cargar los datos.');
                const data = await response.json();
                
                // Construir el HTML del modal con los datos recibidos
                renderDetailsModal(data);
                detailsModal.style.display = 'block';

            } catch (error) {
                console.error("Error:", error);
                alert('No se pudieron cargar los detalles del alimento.');
            }
        });
    });

    // Función que construye el HTML del modal de detalles
    function renderDetailsModal(data) {
        // ... (el código de esta función va en el siguiente bloque)
    }

    // Función para manejar el envío del formulario de despacho
    async function handleDispatchSubmit(event) {
        // ... (el código de esta función va en el siguiente bloque)
    }
});

function renderDetailsModal(data) {
    const detailsContent = document.getElementById('details-modal').querySelector('.details-content');

    // Plantilla HTML del contenido del modal
    detailsContent.innerHTML = `
        <div class="modal-header">
            <h2>${data.nombre}</h2>
            <span class="close-btn" id="details-close-btn">&times;</span>
        </div>
        <hr class="separator">
        <div class="modal-body">
            <div class="details-grid">
                ${data.imagen_url ? `<img src="${data.imagen_url}" alt="Vista previa" class="details-img">` : ''}
                
                <div class="details-section">
                    <h4>Inventario</h4>
                    <p><strong>Ingresado:</strong> <span id="qty-ingresada">${data.cantidad_ingresada}</span> Kg</p>
                    <p><strong>Usado:</strong> <span id="qty-usada">${data.cantidad_usada}</span> Kg</p>
                    <p><strong>Restante:</strong> <span id="qty-restante">${data.cantidad_restante}</span> Kg</p>
                </div>

                <div class="details-section">
                    <h4>Despacho</h4>
                    <form id="dispatch-form" data-id="${data.id}">
                        <div class="dispatch-form">
                            <input type="number" step="0.01" min="0" placeholder="Kg" id="dispatch-qty" required>
                            <button type="submit">Aceptar</button>
                        </div>
                    </form>
                </div>

                <div class="details-section">
                    <h4>Información</h4>
                    <p><strong>Precio:</strong> $${data.precio}</p>
                    <p><strong>Categoría:</strong> ${data.categoria}</p>
                    <p><strong>Proveedor:</strong> ${data.proveedor ? data.proveedor.nombre : 'N/A'} 
                        ${data.proveedor ? '<button class="info-btn">Ver más</button>' : ''}
                    </p>
                    <p><strong>Ubicación:</strong> ${data.ubicacion ? data.ubicacion.nombre : 'N/A'}
                        ${data.ubicacion ? '<button class="info-btn">Ver más</button>' : ''}
                    </p>
                </div>

                <div class="details-section">
                    <h4>Fechas</h4>
                    <p><strong>Compra:</strong> ${data.fecha_compra}</p>
                    <p><strong>Vencimiento:</strong> ${data.fecha_vencimiento}</p>
                </div>
            </div>
        </div>
    `;

    // Añadir evento al nuevo botón de cerrar
    detailsContent.querySelector('#details-close-btn').addEventListener('click', () => {
        document.getElementById('details-modal').style.display = 'none';
    });
    
    // Añadir evento al formulario de despacho
    detailsContent.querySelector('#dispatch-form').addEventListener('submit', handleDispatchSubmit);
}

async function handleDispatchSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const alimentoId = form.dataset.id;
    const cantidad = form.querySelector('#dispatch-qty').value;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value; // Necesario para POST

    try {
        const response = await fetch('/alimento/actualizar_cantidad/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify({
                alimento_id: alimentoId,
                cantidad_a_usar: cantidad
            })
        });

        const result = await response.json();

        if (response.ok) {
            alert(result.message);
            // Actualizar los valores en el modal de detalles al instante
            document.getElementById('qty-usada').textContent = result.nueva_cantidad_usada;
            document.getElementById('qty-restante').textContent = result.nueva_cantidad_restante;
            form.reset(); // Limpiar el input
        } else {
            alert(`Error: ${result.message}`);
        }
    } catch (error) {
        console.error("Error en el despacho:", error);
        alert('Ocurrió un error al intentar actualizar la cantidad.');
    }
}