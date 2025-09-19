document.addEventListener('DOMContentLoaded', () => {
    // --- ELEMENTOS PRINCIPALES ---
    const mainModal = document.getElementById('alimentos-modal');
    if (!mainModal) return; // Si el modal principal no existe, detenemos el script.

    const openBtn = document.getElementById('alimentos-btn');
    const mainCloseBtn = mainModal.querySelector('.close-btn');
    const detailsModal = document.getElementById('details-modal');
    const detailsContent = detailsModal.querySelector('.details-content');
    const infoModal = document.getElementById('info-modal');
    const infoContent = infoModal.querySelector('.info-content');

    // --- LÓGICA PARA ABRIR Y CERRAR EL MODAL PRINCIPAL ---
    openBtn.addEventListener('click', () => { mainModal.style.display = 'block'; });
    mainCloseBtn.addEventListener('click', () => { mainModal.style.display = 'none'; });
    
    // --- LÓGICA PARA CERRAR MODALES AL HACER CLIC FUERA ---
    window.addEventListener('click', (event) => {
        if (event.target == mainModal) mainModal.style.display = 'none';
        if (event.target == detailsModal) closeDetailsModal();
        if (event.target == infoModal) closeInfoModal();
    });

    // --- LÓGICA DE PAGINACIÓN ---
    const gridContainer = mainModal.querySelector('.modal-grid');
    const paginationContainer = mainModal.querySelector('.pagination-controls');
    const allItems = Array.from(gridContainer.querySelectorAll('.item-card'));
    let currentPage = 1;
    let itemsPerPage;

    const setItemsPerPage = () => {
        itemsPerPage = (window.innerWidth <= 768) ? 5 : 6;
    };

    const showPage = (page) => {
        currentPage = page;
        const startIndex = (page - 1) * itemsPerPage;
        const endIndex = startIndex + itemsPerPage;

        allItems.forEach((item, index) => {
            // Usamos .toggle() para añadir/quitar la clase de forma más eficiente
            item.classList.toggle('hidden', !(index >= startIndex && index < endIndex));
        });

        paginationContainer.querySelectorAll('.pagination-btn').forEach(button => {
            button.classList.toggle('active', parseInt(button.dataset.page) === currentPage);
        });
    };

    const setupPagination = () => {
        setItemsPerPage();
        paginationContainer.innerHTML = ''; // Limpiar botones existentes
        const pageCount = Math.ceil(allItems.length / itemsPerPage);

        if (pageCount > 1) {
            for (let i = 1; i <= pageCount; i++) {
                const button = document.createElement('button');
                button.className = 'pagination-btn';
                button.innerText = i;
                button.dataset.page = i;
                button.addEventListener('click', () => showPage(i));
                paginationContainer.appendChild(button);
            }
        }
        showPage(1); // Mostrar la primera página por defecto
    };

    if (allItems.length > 0) {
        setupPagination();
    }
    window.addEventListener('resize', () => {
        if (allItems.length > 0) setupPagination();
    });

    // --- FUNCIONES PARA CERRAR MODALES DE DETALLES E INFO ---
    const closeDetailsModal = () => {
        detailsModal.style.display = 'none';
        detailsContent.innerHTML = '';
    };
    const closeInfoModal = () => {
        infoModal.style.display = 'none';
        infoContent.innerHTML = '';
    };

    // --- LÓGICA PARA ABRIR MODAL DE DETALLES ---
    mainModal.querySelectorAll('.details-btn').forEach(button => {
        button.addEventListener('click', async () => {
            const alimentoId = button.dataset.id;
            try {
                const response = await fetch(`/alimento/detalles/${alimentoId}/`);
                if (!response.ok) throw new Error('Error al cargar los datos.');
                const data = await response.json();
                renderDetailsModal(data);
                detailsModal.style.display = 'block';
            } catch (error) {
                console.error("Error:", error);
                alert('No se pudieron cargar los detalles del alimento.');
            }
        });
    });

    // --- FUNCIÓN PARA CONSTRUIR EL MODAL DE DETALLES ---
    function renderDetailsModal(data) {
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
                            ${data.proveedor ? `<button class="info-btn" data-type="proveedor">Ver más</button>` : ''}
                        </p>
                        <p><strong>Ubicación:</strong> ${data.ubicacion ? data.ubicacion.nombre : 'N/A'}
                            ${data.ubicacion ? `<button class="info-btn" data-type="ubicacion">Ver más</button>` : ''}
                        </p>
                    </div>
                    <div class="details-section">
                        <h4>Fechas</h4>
                        <p><strong>Compra:</strong> ${data.fecha_compra}</p>
                        <p><strong>Vencimiento:</strong> ${data.fecha_vencimiento}</p>
                    </div>
                </div>
            </div>`;

        // Añadir eventos a los nuevos elementos del modal
        detailsContent.querySelector('#details-close-btn').addEventListener('click', closeDetailsModal);
        detailsContent.querySelector('#dispatch-form').addEventListener('submit', handleDispatchSubmit);
        
        detailsContent.querySelectorAll('.info-btn').forEach(button => {
            button.addEventListener('click', () => {
                const type = button.dataset.type;
                if (type === 'proveedor') {
                    renderInfoModal('Proveedor', data.proveedor);
                } else if (type === 'ubicacion') {
                    renderInfoModal('Ubicación', data.ubicacion);
                }
            });
        });
    }

    // --- FUNCIÓN PARA CONSTRUIR EL MODAL DE INFO (PROVEEDOR/UBICACIÓN) ---
    function renderInfoModal(title, details) {
        let imageHtml = '';
        // Si hay una URL de imagen, creamos la etiqueta <img>
        if (details.imagen_url) {
            imageHtml = `<img src="${details.imagen_url}" alt="Imagen de ${details.nombre}" class="info-img">`;
        }

        let contentHtml = '';
        if (title === 'Proveedor') {
            contentHtml = `
                ${imageHtml}
                <p><strong>Nombre:</strong> ${details.nombre}</p>
                <p><strong>Local:</strong> ${details.nombre_local || 'N/A'}</p>
                <p><strong>Email:</strong> ${details.correo || 'N/A'}</p>
                <p><strong>Teléfono:</strong> ${details.telefono || 'N/A'}</p>
            `;
        } else if (title === 'Ubicación') {
            contentHtml = `
                ${imageHtml}
                <p><strong>Nombre:</strong> ${details.nombre}</p>
                <p><strong>Barrio:</strong> ${details.barrio || 'N/A'}</p>
                <p><strong>Dirección:</strong> ${details.direccion || 'N/A'}</p>
                <p><strong>Mapa:</strong> ${details.link ? `<a href="${details.link}" target="_blank">Abrir enlace</a>` : 'N/A'}</p>
            `;
        }
        
        infoContent.innerHTML = `
            <div class="modal-header">
                <h2>Detalles de ${title}</h2>
                <span class="close-btn" id="info-close-btn">&times;</span>
            </div>
            <hr class="separator">
            <div class="modal-body">${contentHtml}</div>
        `;
        
        infoModal.style.display = 'block';
        infoContent.querySelector('#info-close-btn').addEventListener('click', closeInfoModal);
    }

    // --- FUNCIÓN PARA MANEJAR EL DESPACHO DE INVENTARIO ---
    async function handleDispatchSubmit(event) {
        event.preventDefault();
        const form = event.target;
        const alimentoId = form.dataset.id;
        const cantidad = form.querySelector('#dispatch-qty').value;
        const csrfToken = document.querySelector('form [name=csrfmiddlewaretoken]').value;

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
                document.getElementById('qty-usada').textContent = result.nueva_cantidad_usada;
                document.getElementById('qty-restante').textContent = result.nueva_cantidad_restante;
                form.reset();
            } else {
                alert(`Error: ${result.message}`);
            }
        } catch (error) {
            console.error("Error en el despacho:", error);
            alert('Ocurrió un error al intentar actualizar la cantidad.');
        }
    }
});