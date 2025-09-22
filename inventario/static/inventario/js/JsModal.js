document.addEventListener('DOMContentLoaded', () => {
    const mainModal = document.getElementById('alimentos-modal');
    if (!mainModal) return; 

    const openBtn = document.getElementById('alimentos-btn');
    const mainCloseBtn = mainModal.querySelector('.close-btn');
    const detailsModal = document.getElementById('details-modal');
    const detailsContent = detailsModal.querySelector('.details-content');
    const infoModal = document.getElementById('info-modal');
    const infoContent = infoModal.querySelector('.info-content');

    openBtn.addEventListener('click', () => { mainModal.style.display = 'block'; });
    mainCloseBtn.addEventListener('click', () => { mainModal.style.display = 'none'; });
    window.addEventListener('click', (event) => {
        if (event.target == mainModal) mainModal.style.display = 'none';
        if (event.target == detailsModal) closeDetailsModal();
        if (event.target == infoModal) closeInfoModal();
    });

    const gridContainer = mainModal.querySelector('.modal-grid');
    const paginationContainer = mainModal.querySelector('.pagination-controls');
    const allItems = Array.from(gridContainer.querySelectorAll('.item-card'));
    let currentPage = 1;
    let itemsPerPage;
    const setItemsPerPage = () => { itemsPerPage = (window.innerWidth <= 768) ? 5 : 6; };
    const showPage = (page) => {
        currentPage = page;
        const startIndex = (page - 1) * itemsPerPage;
        const endIndex = startIndex + itemsPerPage;
        allItems.forEach((item, index) => {
            item.classList.toggle('hidden', !(index >= startIndex && index < endIndex));
        });
        paginationContainer.querySelectorAll('.pagination-btn').forEach(button => {
            button.classList.toggle('active', parseInt(button.dataset.page) === currentPage);
        });
    };
    const setupPagination = () => {
        setItemsPerPage();
        paginationContainer.innerHTML = '';
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
        showPage(1);
    };
    if (allItems.length > 0) {
        setupPagination();
    }
    window.addEventListener('resize', () => {
        if (allItems.length > 0) setupPagination();
    });

    const closeDetailsModal = () => { detailsModal.style.display = 'none'; detailsContent.innerHTML = ''; };
    const closeInfoModal = () => { infoModal.style.display = 'none'; infoContent.innerHTML = ''; };

    mainModal.querySelectorAll('.details-btn').forEach(button => {
        button.addEventListener('click', async () => {
            const alimentoId = button.dataset.id;
            try {
                const response = await fetch(`/alimento/detalles/${alimentoId}/`);
                if (!response.ok) throw new Error('Error al cargar datos.');
                const data = await response.json();
                renderDetailsModal(data);
                detailsModal.style.display = 'block';
            } catch (error) {
                console.error("Error:", error);
                alert('No se pudieron cargar los detalles.');
            }
        });
    });

    function renderDetailsModal(data) {
        let etiquetasHtml = data.etiquetas.map(tag => `
            <li class="tag-item">
                ${tag.nombre}
                <button class="remove-tag-btn" data-tag-id="${tag.id}" data-alimento-id="${data.id}">&times;</button>
            </li>`).join('');

        let opcionesEtiquetas = data.todas_las_etiquetas
            .filter(tag => !data.etiquetas.some(assignedTag => assignedTag.id === tag.id))
            .map(tag => `<option value="${tag.id}">${tag.nombre}</option>`).join('');

        detailsContent.innerHTML = `
            <div class="modal-header"><h2>${data.nombre}</h2><span class="close-btn" id="details-close-btn">&times;</span></div>
            <hr class="separator">
            <div class="modal-body"><div class="details-grid">
                ${data.imagen_url ? `<img src="${data.imagen_url}" alt="Vista previa" class="details-img">` : ''}
                <div class="details-section">
                    <h4>Inventario</h4>
                    <p><strong>Ingresado:</strong> <span id="qty-ingresada">${data.cantidad_ingresada}</span> Kg</p>
                    <p><strong>Usado:</strong> <span id="qty-usada">${data.cantidad_usada}</span> Kg</p>
                    <p><strong>Restante:</strong> <span id="qty-restante">${data.cantidad_restante}</span> Kg</p>
                </div>
                <div class="details-section">
                    <h4>Despacho</h4>
                    <form id="dispatch-form" data-id="${data.id}"><div class="dispatch-form">
                        <input type="number" step="0.01" min="0" placeholder="Kg" id="dispatch-qty" required>
                        <button type="submit">Aceptar</button>
                    </div></form>
                </div>
                <div class="details-section">
                    <h4>Información</h4>
                    <p><strong>Precio:</strong> $${data.precio}</p>
                    <p><strong>Categoría:</strong> ${data.categoria}</p>
                    <p><strong>Proveedor:</strong> ${data.proveedor ? data.proveedor.nombre : 'N/A'} ${data.proveedor ? `<button class="info-btn" data-type="proveedor">Ver más</button>` : ''}</p>
                    <p><strong>Ubicación:</strong> ${data.ubicacion ? data.ubicacion.nombre : 'N/A'} ${data.ubicacion ? `<button class="info-btn" data-type="ubicacion">Ver más</button>` : ''}</p>
                </div>
                <div class="details-section">
                    <h4>Fechas</h4>
                    <p><strong>Compra:</strong> ${data.fecha_compra}</p>
                    <p><strong>Vencimiento:</strong> ${data.fecha_vencimiento}</p>
                </div>
                <div class="details-section tags-section">
                    <h4>Etiquetas</h4>
                    <ul class="tag-list" id="tag-list-container">${etiquetasHtml}</ul>
                    <form id="add-tag-form" data-id="${data.id}"><div class="add-tag-form">
                        <select id="tag-select">${opcionesEtiquetas}</select>
                        <button type="submit">Añadir</button>
                    </div></form>
                </div>
            </div></div>`;
        
        detailsContent.querySelector('#details-close-btn').addEventListener('click', closeDetailsModal);
        detailsContent.querySelector('#dispatch-form').addEventListener('submit', handleDispatchSubmit);
        detailsContent.querySelector('#add-tag-form').addEventListener('submit', handleTagManagement);
        detailsContent.querySelectorAll('.remove-tag-btn').forEach(btn => btn.addEventListener('click', handleTagManagement));
        detailsContent.querySelectorAll('.info-btn').forEach(button => {
            button.addEventListener('click', () => {
                const type = button.dataset.type;
                if (type === 'proveedor') renderInfoModal('Proveedor', data.proveedor);
                else if (type === 'ubicacion') renderInfoModal('Ubicación', data.ubicacion);
            });
        });
    }

    function renderInfoModal(title, details) {
        let imageHtml = details.imagen_url ? `<img src="${details.imagen_url}" alt="Imagen de ${details.nombre}" class="info-img">` : '';
        let contentHtml = '';
        if (title === 'Proveedor') {
            contentHtml = `${imageHtml}<p><strong>Nombre:</strong> ${details.nombre}</p><p><strong>Local:</strong> ${details.nombre_local||'N/A'}</p><p><strong>Email:</strong> ${details.correo||'N/A'}</p><p><strong>Teléfono:</strong> ${details.telefono||'N/A'}</p>`;
        } else if (title === 'Ubicación') {
            contentHtml = `${imageHtml}<p><strong>Nombre:</strong> ${details.nombre}</p><p><strong>Barrio:</strong> ${details.barrio||'N/A'}</p><p><strong>Dirección:</strong> ${details.direccion||'N/A'}</p><p><strong>Mapa:</strong> ${details.link ? `<a href="${details.link}" target="_blank">Abrir enlace</a>` : 'N/A'}</p>`;
        }
        infoContent.innerHTML = `<div class="modal-header"><h2>Detalles de ${title}</h2><span class="close-btn" id="info-close-btn">&times;</span></div><hr class="separator"><div class="modal-body">${contentHtml}</div>`;
        infoModal.style.display = 'block';
        infoContent.querySelector('#info-close-btn').addEventListener('click', closeInfoModal);
    }

    async function handleDispatchSubmit(event) {
        event.preventDefault();
        const form = event.target;
        const alimentoId = form.dataset.id;
        const cantidad = form.querySelector('#dispatch-qty').value;
        const csrfToken = document.querySelector('form [name=csrfmiddlewaretoken]').value;
        try {
            const response = await fetch('/alimento/actualizar_cantidad/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                body: JSON.stringify({ alimento_id: alimentoId, cantidad_a_usar: cantidad })
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
            console.error("Error en despacho:", error);
            alert('Ocurrió un error al actualizar la cantidad.');
        }
    }

    async function handleTagManagement(event) {
        event.preventDefault();
        
        // --- THIS BLOCK IS THE FIX ---
        let alimentoId, etiquetaId, accion;
        if (event.type === 'submit') { // 'add' action
            accion = 'add';
            alimentoId = event.currentTarget.dataset.id;
            etiquetaId = document.getElementById('tag-select').value;
        } else { // 'remove' action
            accion = 'remove';
            alimentoId = event.currentTarget.dataset.alimentoId; // Corrected from dataset.id
            etiquetaId = event.currentTarget.dataset.tagId;
        }
        // --- END OF FIX ---

        if (!etiquetaId) return;
        const csrfToken = document.querySelector('form [name=csrfmiddlewaretoken]').value;
        try {
            const response = await fetch('/alimento/gestionar_etiqueta/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                body: JSON.stringify({ alimento_id: alimentoId, etiqueta_id: etiquetaId, accion: accion })
            });
            const result = await response.json();
            if (!response.ok) throw new Error(result.message);
            const data = await (await fetch(`/alimento/detalles/${alimentoId}/`)).json();
            renderDetailsModal(data);
        } catch (error) {
            console.error("Error al gestionar etiqueta:", error);
            alert(`Error: ${error.message}`);
        }
    }
});