document.addEventListener('DOMContentLoaded', () => {
    const mainModal = document.getElementById('alimentos-modal');
    if (!mainModal) return;

    const openBtn = document.getElementById('alimentos-btn');
    const mainCloseBtn = mainModal.querySelector('.close-btn');
    const detailsModal = document.getElementById('details-modal');
    const detailsContent = detailsModal.querySelector('.details-content');
    const infoModal = document.getElementById('info-modal');
    const infoContent = infoModal.querySelector('.info-content');
    
    // Filter elements
    const nombreFilter = document.getElementById('filtro-nombre');
    const categoriaFilter = document.getElementById('filtro-categoria');
    const proveedorFilter = document.getElementById('filtro-proveedor');
    const gridContainer = mainModal.querySelector('.modal-grid');
    const paginationContainer = mainModal.querySelector('.pagination-controls');

    openBtn.addEventListener('click', () => {
        mainModal.style.display = 'block';
        // Initial fetch/render when modal opens
        fetchAlimentos(1);
    });
    mainCloseBtn.addEventListener('click', () => { mainModal.style.display = 'none'; });
    window.addEventListener('click', (event) => {
        if (event.target == mainModal) mainModal.style.display = 'none';
        if (event.target == detailsModal) closeDetailsModal();
        if (event.target == infoModal) closeInfoModal();
    });

    const fetchAlimentos = async (page = 1) => {
        const nombre = nombreFilter.value;
        const categoria = categoriaFilter.value;
        const proveedor = proveedorFilter.value;
        const itemsPerPage = window.innerWidth <= 768 ? 6 : 8;

        const url = `/lista_productos/?page=${page}&nombre=${nombre}&categoria=${categoria}&proveedor=${proveedor}&items_per_page=${itemsPerPage}`;
        
        try {
            const response = await fetch(url, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            const data = await response.json();
            renderAlimentosGrid(data.alimentos);
            renderPagination(data);
        } catch (error) {
            console.error('Error fetching alimentos:', error);
            gridContainer.innerHTML = '<p>Error al cargar los alimentos. Por favor, intente de nuevo.</p>';
        }
    };
    
    const renderAlimentosGrid = (alimentos) => {
        const noAlimentosMsg = document.getElementById('no-alimentos-msg');
        gridContainer.innerHTML = '';
        
        if (alimentos.length === 0) {
            if(noAlimentosMsg) noAlimentosMsg.style.display = 'block';
            gridContainer.innerHTML = '<p>No se encontraron alimentos con los filtros seleccionados.</p>';
            return;
        }

        if(noAlimentosMsg) noAlimentosMsg.style.display = 'none';
        alimentos.forEach(alimento => {
            const itemCard = document.createElement('div');
            itemCard.className = 'item-card';
            itemCard.innerHTML = `
                ${alimento.imagen_url ? 
                    `<img src="${alimento.imagen_url}" alt="Imagen de ${alimento.nombre}" class="item-card-img">` : 
                    '<div class="item-card-img-placeholder">Sin imagen</div>'
                }
                <div class="item-card-body">
                    <h3 class="item-card-title">${alimento.nombre}</h3>
                    <p class="item-card-text">Cantidad: ${alimento.cantidad_kg_ingresada} Kg</p>
                    <button class="details-btn" data-id="${alimento.id}">Ver detalles</button>
                </div>
            `;
            gridContainer.appendChild(itemCard);
        });
        // Re-attach event listeners for the new detail buttons
        gridContainer.querySelectorAll('.details-btn').forEach(attachDetailButtonListener);
    };

    const renderPagination = (data) => {
        paginationContainer.innerHTML = '';
        if (data.total_pages > 1) {
            for (let i = 1; i <= data.total_pages; i++) {
                const button = document.createElement('button');
                button.className = 'pagination-btn';
                if (i === data.current_page) {
                    button.classList.add('active');
                }
                button.innerText = i;
                button.dataset.page = i;
                button.addEventListener('click', (e) => {
                    e.preventDefault();
                    fetchAlimentos(i);
                });
                paginationContainer.appendChild(button);
            }
        }
    };

    // Debounce function to limit the rate of API calls
    const debounce = (func, delay) => {
        let timeout;
        return (...args) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), delay);
        };
    };

    nombreFilter.addEventListener('keyup', debounce(() => fetchAlimentos(1), 300));
    categoriaFilter.addEventListener('change', () => fetchAlimentos(1));
    proveedorFilter.addEventListener('change', () => fetchAlimentos(1));
    window.addEventListener('resize', debounce(() => fetchAlimentos(1), 200));

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
        // --- Helper functions for rendering sections ---
        const renderInventarioSection = (d) => `
            <div class="details-section">
                <h4>Inventario</h4>
                <p><strong>Ingresado:</strong> ${d.cantidad_ingresada} Kg</p>
                <p><strong>Usado:</strong> <span id="qty-usada">${d.cantidad_usada}</span> Kg</p>
                <p><strong>Restante:</strong> <span id="qty-restante">${d.cantidad_restante}</span> Kg</p>
                <p><strong>Precio:</strong> $${d.precio}</p>
                <p><strong>Estado:</strong> <span class="status-${d.estado.toLowerCase()}">${d.estado}</span></p>
                ${d.estado === 'Agotado' ? '<p class="warning-text">¡Inventario agotado! Considere añadir más cantidad.</p>' : ''}
            </div>`;

        const renderDespachoSection = (d) => `
            <div class="details-section">
                <h4>Despacho</h4>
                <form id="dispatch-form" data-id="${d.id}" class="dispatch-form-group">
                    <label>Usar Cantidad (Kg):</label>
                    <div class="form-row"><input type="number" step="0.01" min="0" id="dispatch-qty" required><button type="submit">Aceptar</button></div>
                </form>
                <form id="add-stock-form" data-id="${d.id}" class="dispatch-form-group">
                    <label>Añadir Cantidad (Kg):</label>
                    <div class="form-row"><input type="number" step="0.01" min="0" id="add-qty" required><button type="submit">Añadir</button></div>
                </form>
            </div>`;

        const renderInfoSection = (d) => {
            const renderProviders = () => d.proveedores.map((p, index) => `<li class="info-list-item">${p.nombre} <button class="info-btn" data-type="proveedor" data-index="${index}">Ver más</button></li>`).join('');
            const renderUbicaciones = () => {
                if (!d.ubicaciones || d.ubicaciones.length === 0) return '<li>N/A</li>';
                return d.ubicaciones.map((u, index) => `<li class="info-list-item">${u.nombre} <button class="info-btn" data-type="ubicacion" data-index="${index}">Ver más</button></li>`).join('');
            };
            return `
                <div class="details-section">
                    <h4>Información</h4>
                    <p><strong>Categoría:</strong> ${d.categoria ? d.categoria.nombre : 'N/A'}</p>
                    <p><strong>Proveedores:</strong></p><ul class="info-list">${renderProviders()}</ul>
                    <p><strong>Ubicaciones:</strong></p><ul class="info-list">${renderUbicaciones()}</ul>
                    <p><strong>Fechas:</strong> Compra: ${d.fecha_compra} | Vencimiento: ${d.fecha_vencimiento}</p>
                </div>`;
        };

        const renderAdicionalSection = (d) => {
            const renderTags = () => {
                const mainTags = d.etiquetas.filter(t => t.parent_id === null);
                const subTags = d.etiquetas.filter(t => t.parent_id !== null);
                return mainTags.map(tag => {
                    const childrenHtml = subTags.filter(st => st.parent_id === tag.id).map(st => `<li class="info-list-item sub-item">${st.nombre} <button class="remove-tag-btn" data-tag-id="${st.id}" data-alimento-id="${d.id}">&times;</button></li>`).join('');
                    return `<li class="info-list-item main-item">${tag.nombre} <button class="remove-tag-btn" data-tag-id="${tag.id}" data-alimento-id="${d.id}">&times;</button></li>${childrenHtml ? `<ul>${childrenHtml}</ul>` : ''}`;
                }).join('');
            };
            const renderTagOptions = () => d.todas_las_etiquetas_principales.filter(tag => !d.etiquetas.some(assigned => assigned.id === tag.id && assigned.parent_id === null)).map(tag => `<option value="${tag.id}">${tag.nombre}</option>`).join('');
            const renderMainTagOptions = (assignedTags) => assignedTags.filter(tag => tag.parent_id === null).map(tag => `<option value="${tag.id}">${tag.nombre}</option>`).join('');

            return `
                <div class="details-section tags-section">
                    <h4>Adicional</h4>
                    <p><strong>Etiquetas y Sub-Etiquetas:</strong></p>
                    <ul class="tag-list" id="tag-list-container">${renderTags()}</ul>
                    <form id="add-tag-form" data-id="${d.id}" class="additional-form"><label>Añadir Etiqueta Principal:</label><div class="form-row"><select id="tag-select"><option value="">Seleccione...</option>${renderTagOptions()}</select><button type="submit">Añadir</button></div></form>
                    <hr class="thin-separator">
                    <form id="create-tag-form" data-id="${d.id}" class="additional-form"><label>Crear Etiqueta Principal:</label><div class="form-row"><input type="text" id="new-tag-name" placeholder="Nombre nueva etiqueta" required><button type="submit">Crear</button></div></form>
                    <hr class="thin-separator">
                    <form id="create-subtag-form" data-id="${d.id}" class="additional-form"><label>Crear Sub-Etiqueta:</label><div class="form-row"><input type="text" id="new-subtag-name" placeholder="Nombre sub-etiqueta" required><select id="parent-tag-select" required><option value="">Asociar a...</option>${renderMainTagOptions(d.etiquetas)}</select><button type="submit">Crear</button></div></form>
                    <hr class="thin-separator">
                    <form id="add-subtag-form" data-id="${d.id}" class="additional-form">
                        <label>Añadir Sub-Etiqueta Existente:</label>
                        <div class="form-row">
                            <select id="add-subtag-parent-select" required><option value="">Seleccione Etiqueta Principal</option>${renderMainTagOptions(d.etiquetas)}</select>
                            <select id="add-subtag-select" required><option value="">Seleccione Sub-Etiqueta</option></select>
                            <button type="submit">Añadir</button>
                        </div>
                    </form>
                    <hr class="thin-separator">
                    <form id="create-category-form" data-id="${d.id}" class="additional-form"><label>Crear y Asignar Categoría:</label><div class="form-row"><input type="text" id="new-category-name" placeholder="Nombre nueva categoría" required><button type="submit">Crear</button></div></form>
                </div>`;
        };

        // --- Main HTML structure ---
        detailsContent.innerHTML = `
            <div class="modal-header"><h2>${data.nombre}</h2><span class="close-btn" id="details-close-btn">&times;</span></div>
            <hr class="separator">
            <div class="modal-body">
                <div class="details-main-grid">
                    <div class="details-left-column">
                        ${data.imagen_url ? `<img src="${data.imagen_url}" alt="Vista previa de ${data.nombre}" class="details-img">` : '<div class="item-card-img-placeholder">Sin imagen</div>'}
                    </div>
                    <div class="details-right-column">
                        ${renderInventarioSection(data)}
                        ${renderDespachoSection(data)}
                    </div>
                </div>
                <div class="details-bottom-grid">
                    ${renderInfoSection(data)}
                    ${renderAdicionalSection(data)}
                </div>
            </div>`;

        // --- Attach event listeners ---
        detailsContent.querySelector('#details-close-btn').addEventListener('click', closeDetailsModal);
        detailsContent.querySelector('#dispatch-form').addEventListener('submit', handleDispatchSubmit);
        detailsContent.querySelector('#add-stock-form').addEventListener('submit', handleAddStockSubmit);
        detailsContent.querySelector('#add-tag-form').addEventListener('submit', handleTagManagement);
        detailsContent.querySelectorAll('.remove-tag-btn').forEach(btn => btn.addEventListener('click', handleTagManagement));
        detailsContent.querySelector('#create-tag-form').addEventListener('submit', handleCreateTag);
        detailsContent.querySelector('#create-subtag-form').addEventListener('submit', handleCreateTag);
        detailsContent.querySelector('#create-category-form').addEventListener('submit', handleCreateCategory);
        
        const addSubtagParentSelect = detailsContent.querySelector('#add-subtag-parent-select');
        if (addSubtagParentSelect) {
            addSubtagParentSelect.addEventListener('change', async (e) => {
                const parentId = e.target.value;
                const subtagSelect = detailsContent.querySelector('#add-subtag-select');
                subtagSelect.innerHTML = '<option value="">Cargando...</option>';
                if (!parentId) {
                    subtagSelect.innerHTML = '<option value="">Seleccione Sub-Etiqueta</option>';
                    return;
                }
                try {
                    const response = await fetch(`/get_sub_etiquetas/?parent_ids=${parentId}`);
                    const subEtiquetasExistentes = await response.json();
                    
                    let options = '<option value="">Seleccione Sub-Etiqueta</option>';
                    for (const [id, nombre] of Object.entries(subEtiquetasExistentes)) {
                        if (!data.etiquetas.some(assigned => assigned.id === parseInt(id))) {
                            options += `<option value="${id}">${nombre}</option>`;
                        }
                    }
                    subtagSelect.innerHTML = options;
                } catch (error) {
                    console.error('Error fetching sub-etiquetas:', error);
                    subtagSelect.innerHTML = '<option value="">Error al cargar</option>';
                }
            });
        }
        detailsContent.querySelector('#add-subtag-form').addEventListener('submit', handleTagManagement);

        detailsContent.querySelectorAll('.info-btn').forEach(button => {
            button.addEventListener('click', () => {
                const type = button.dataset.type;
                if (type === 'proveedor') {
                    const index = parseInt(button.dataset.index, 10);
                    renderInfoModal('Proveedor', data.proveedores[index]);
                } else if (type === 'ubicacion') {
                    const index = parseInt(button.dataset.index, 10);
                    renderInfoModal('Ubicación', data.ubicaciones[index]);
                }
            });
        });
    }

    async function handleCreateTag(event) {
        event.preventDefault();
        const form = event.target;
        const alimentoId = form.dataset.id;
        const isSubTag = form.id === 'create-subtag-form';
        const nombreEtiqueta = form.querySelector(isSubTag ? '#new-subtag-name' : '#new-tag-name').value;
        const parentId = isSubTag ? form.querySelector('#parent-tag-select').value : null;

        if (isSubTag && !parentId) {
            alert('Por favor, seleccione una etiqueta principal para la sub-etiqueta.');
            return;
        }

        const csrfToken = document.querySelector('form [name=csrfmiddlewaretoken]').value;
        try {
            const response = await fetch('/alimento/crear_etiqueta/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                body: JSON.stringify({ 
                    alimento_id: alimentoId, 
                    nombre_etiqueta: nombreEtiqueta,
                    parent_id: parentId
                })
            });
            const result = await response.json();
            if (response.ok) {
                alert(result.message);
                const updatedDetails = await (await fetch(`/alimento/detalles/${alimentoId}/`)).json();
                renderDetailsModal(updatedDetails);
            } else {
                alert(`Error: ${result.message}`);
            }
        } catch (error) {
            console.error("Error al crear etiqueta:", error);
            alert('Ocurrió un error al crear la etiqueta.');
        }
    }

    async function handleCreateCategory(event) {
        event.preventDefault();
        const form = event.target;
        const alimentoId = form.dataset.id;
        const nombreCategoria = form.querySelector('#new-category-name').value;
        const csrfToken = document.querySelector('form [name=csrfmiddlewaretoken]').value;

        try {
            const response = await fetch('/alimento/crear_categoria/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                body: JSON.stringify({ 
                    alimento_id: alimentoId, 
                    nombre_categoria: nombreCategoria 
                })
            });
            const result = await response.json();
            if (response.ok) {
                alert(result.message);
                const updatedDetails = await (await fetch(`/alimento/detalles/${alimentoId}/`)).json();
                renderDetailsModal(updatedDetails);
            } else {
                alert(`Error: ${result.message}`);
            }
        } catch (error) {
            console.error("Error al crear categoría:", error);
            alert('Ocurrió un error al crear la categoría.');
        }
    }

    async function handleAddStockSubmit(event) {
        event.preventDefault();
        const form = event.target;
        const alimentoId = form.dataset.id;
        const cantidad = form.querySelector('#add-qty').value;
        const csrfToken = document.querySelector('form [name=csrfmiddlewaretoken]').value;

        try {
            const response = await fetch('/alimento/anadir_stock/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                body: JSON.stringify({ alimento_id: alimentoId, cantidad_a_anadir: cantidad })
            });
            const result = await response.json();
            if (response.ok) {
                alert(result.message);
                // Re-fetch details and re-render the modal to show updated state
                const updatedDetails = await (await fetch(`/alimento/detalles/${alimentoId}/`)).json();
                renderDetailsModal(updatedDetails);
            } else {
                alert(`Error: ${result.message}`);
            }
        } catch (error) {
            console.error("Error al añadir stock:", error);
            alert('Ocurrió un error al actualizar la cantidad.');
        }
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
                // Re-fetch details and re-render the modal to show updated state
                const updatedDetails = await (await fetch(`/alimento/detalles/${alimentoId}/`)).json();
                renderDetailsModal(updatedDetails);
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
        
        let alimentoId, etiquetaId, accion;
        accion = 'add';
        alimentoId = event.currentTarget.dataset.id;

        if (event.currentTarget.id === 'add-tag-form') {
            etiquetaId = document.getElementById('tag-select').value;
        } else if (event.currentTarget.id === 'add-subtag-form') {
            etiquetaId = document.getElementById('add-subtag-select').value;
        } else { // 'remove' action
            accion = 'remove';
            alimentoId = event.currentTarget.dataset.alimentoId;
            etiquetaId = event.currentTarget.dataset.tagId;
        }

        if (!etiquetaId) {
             alert('Por favor, seleccione una etiqueta.');
             return;
        }
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