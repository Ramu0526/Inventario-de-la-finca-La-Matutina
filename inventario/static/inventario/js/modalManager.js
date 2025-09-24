document.addEventListener('DOMContentLoaded', () => {
    const detailsModal = document.getElementById('details-modal');
    const infoModal = document.getElementById('info-modal');
    const detailsContent = detailsModal.querySelector('.details-content');
    const infoContent = infoModal.querySelector('.info-content');

    // Hacemos la función global para que el HTML pueda llamarla
    window.setupModal = (itemType) => {
        const openBtn = document.getElementById(`${itemType}-btn`);
        const mainModal = document.getElementById(`${itemType}-modal`);
        if (!openBtn || !mainModal) return;

        const mainCloseBtn = mainModal.querySelector('.close-btn');
        const gridContainer = mainModal.querySelector('.modal-grid');
        const paginationContainer = mainModal.querySelector('.pagination-controls');
        
        const nombreFilter = mainModal.querySelector('.filtro-nombre');
        const categoriaFilter = mainModal.querySelector('.filtro-categoria');
        const proveedorFilter = mainModal.querySelector('.filtro-proveedor');
        const animalFilter = mainModal.querySelector('.filtro-animal');

        openBtn.addEventListener('click', () => {
            mainModal.style.display = 'block';
            fetchItems(1);
        });

        mainCloseBtn.addEventListener('click', () => { mainModal.style.display = 'none'; });

        window.addEventListener('click', (event) => {
            if (event.target === mainModal) mainModal.style.display = 'none';
            if (event.target === detailsModal) closeDetailsModal();
            if (event.target === infoModal) closeInfoModal();
        });

        const fetchItems = async (page = 1) => {
            const nombre = nombreFilter ? nombreFilter.value : '';
            const categoria = categoriaFilter ? categoriaFilter.value : '';
            const proveedor = proveedorFilter ? proveedorFilter.value : '';
            const animal = animalFilter ? animalFilter.value : '';
            const itemsPerPage = window.innerWidth <= 768 ? 6 : 8;
            
            const params = new URLSearchParams({ page, nombre, categoria, proveedor, animal, items_per_page: itemsPerPage });
            const url = `/${itemType}/?${params.toString()}`;

            try {
                const response = await fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
                if (!response.ok) throw new Error(`Network response was not ok for ${itemType}`);
                const data = await response.json();
                renderGrid(data.items);
                renderPagination(data);
            } catch (error) {
                console.error(`Error fetching ${itemType}:`, error);
                gridContainer.innerHTML = `<p>Error al cargar los ${itemType.replace('-', ' ')}.</p>`;
            }
        };

        const attachDetailButtonListener = (button) => {
            button.addEventListener('click', async () => {
                const itemId = button.dataset.id;
                
                if (itemType !== 'alimentos' && itemType !== 'combustibles') {
                    alert('La vista de detalles para esta sección aún no está implementada.');
                    return;
                }

                try {
                    const singleItemType = itemType.slice(0, -1);
                    const response = await fetch(`/${singleItemType}/detalles/${itemId}/`);
                    if (!response.ok) throw new Error(`Error al cargar datos del item.`);
                    const data = await response.json();
                    renderDetailsModal(data, itemType);
                    detailsModal.style.display = 'block';
                } catch (error) {
                    console.error("Error fetching details:", error);
                    alert(error.message);
                }
            });
        };

        const renderGrid = (items) => {
            const noItemsMsg = mainModal.querySelector('.no-items-msg');
            gridContainer.innerHTML = '';

            if (!items || items.length === 0) {
                if (noItemsMsg) noItemsMsg.style.display = 'block';
                gridContainer.innerHTML = `<p>No se encontraron ${itemType.replace('-', ' ')}.</p>`;
                return;
            }

            if (noItemsMsg) noItemsMsg.style.display = 'none';
            
            items.forEach(item => {
                const itemCard = document.createElement('div');
                itemCard.className = 'item-card';
                const detalleHTML = item.detalle ? `<p class="item-card-text">${item.detalle}</p>` : '';

                itemCard.innerHTML = `
                    ${item.imagen_url ? 
                        `<img src="${item.imagen_url}" alt="Imagen de ${item.nombre}" class="item-card-img">` : 
                        '<div class="item-card-img-placeholder">Sin imagen</div>'
                    }
                    <div class="item-card-body">
                        <h3 class="item-card-title">${item.nombre || item.tipo}</h3>
                        ${detalleHTML}
                        <button class="details-btn" data-id="${item.id}">Ver detalles</button>
                    </div>
                `;
                gridContainer.appendChild(itemCard);
            });
            gridContainer.querySelectorAll('.details-btn').forEach(attachDetailButtonListener);
        };
        
        const renderPagination = (data) => {
            paginationContainer.innerHTML = '';
            if (data.total_pages > 1) {
                for (let i = 1; i <= data.total_pages; i++) {
                    const button = document.createElement('button');
                    button.className = 'pagination-btn';
                    if (i === data.current_page) button.classList.add('active');
                    button.innerText = i;
                    button.addEventListener('click', () => fetchItems(i));
                    paginationContainer.appendChild(button);
                }
            }
        };

        const debounce = (func, delay) => {
            let timeout;
            return (...args) => {
                clearTimeout(timeout);
                timeout = setTimeout(() => func.apply(this, args), delay);
            };
        };
        
        if (nombreFilter) nombreFilter.addEventListener('keyup', debounce(() => fetchItems(1), 300));
        if (categoriaFilter) categoriaFilter.addEventListener('change', () => fetchItems(1));
        if (proveedorFilter) proveedorFilter.addEventListener('change', () => fetchItems(1));
        if (animalFilter) animalFilter.addEventListener('change', () => fetchItems(1));
    };

    const closeDetailsModal = () => { detailsModal.style.display = 'none'; detailsContent.innerHTML = ''; };
    const closeInfoModal = () => { infoModal.style.display = 'none'; infoContent.innerHTML = ''; };
    
    // --- SECCIÓN DE DETALLES RESTAURADA ---

    function renderDetailsModal(data, itemType) {
        let content = '';
        if (itemType === 'alimentos') {
            content = renderAlimentoDetails(data);
        } else if (itemType === 'combustibles') {
            content = renderCombustibleDetails(data);
        }
        detailsContent.innerHTML = content;
        attachCommonListeners(data, itemType);
    }

    function renderAlimentoDetails(d) {
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
                <div class="management-grid">
                    <form id="dispatch-form" data-id="${d.id}" class="additional-form">
                        <label>Usar Cantidad (Kg):</label>
                        <div class="form-row"><input type="number" step="0.01" min="0" id="dispatch-qty" required><button type="submit">Aceptar</button></div>
                    </form>
                    <form id="add-stock-form" data-id="${d.id}" class="additional-form">
                        <label>Añadir Cantidad (Kg):</label>
                        <div class="form-row"><input type="number" step="0.01" min="0" id="add-qty" required><button type="submit">Añadir</button></div>
                    </form>
                </div>
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
            const mainTags = d.etiquetas.filter(t => t.parent_id === null);
            const subTags = d.etiquetas.filter(t => t.parent_id !== null);
            const mainTagsHtml = mainTags.map(tag => `<li class="info-list-item">${tag.nombre} <button class="remove-tag-btn" data-tag-id="${tag.id}" data-alimento-id="${d.id}">&times;</button></li>`).join('') || '<li>Ninguna</li>';
            const subTagsHtml = subTags.map(tag => `<li class="info-list-item">${tag.nombre} <button class="remove-tag-btn" data-tag-id="${tag.id}" data-alimento-id="${d.id}">&times;</button></li>`).join('') || '<li>Ninguna</li>';
            const renderAvailableMainTags = () => d.todas_las_etiquetas_principales.filter(tag => !mainTags.some(assigned => assigned.id === tag.id)).map(tag => `<option value="${tag.id}">${tag.nombre}</option>`).join('');
            const renderAssignedMainTags = () => mainTags.map(tag => `<option value="${tag.id}">${tag.nombre}</option>`).join('');
            const renderAvailableCategories = () => d.todas_las_categorias.filter(cat => !d.categoria || d.categoria.id !== cat.id).map(cat => `<option value="${cat.id}">${cat.nombre}</option>`).join('');

            return `
                <div class="details-section tags-section">
                    <h4>Adicional</h4>
                    <p><strong>Etiquetas:</strong></p>
                    <ul class="tag-list">${mainTagsHtml}</ul>
                    <p><strong>Sub-Etiquetas:</strong></p>
                    <ul class="tag-list">${subTagsHtml}</ul>
                    <div class="management-grid">
                        <form id="assign-category-form" data-id="${d.id}" class="additional-form"><label>Añadir Categoría:</label><div class="form-row"><select id="category-select" required><option value="">Seleccione...</option>${renderAvailableCategories()}</select><button type="submit">Añadir</button></div></form>
                        <form id="create-category-form" data-id="${d.id}" class="additional-form"><label>Crear Categoría:</label><div class="form-row"><input type="text" id="new-category-name" placeholder="Nombre..." required><button type="submit">Crear</button></div></form>
                        <form id="add-tag-form" data-id="${d.id}" class="additional-form"><label>Añadir Etiqueta:</label><div class="form-row"><select id="tag-select"><option value="">Seleccione...</option>${renderAvailableMainTags()}</select><button type="submit">Añadir</button></div></form>
                        <form id="create-tag-form" data-id="${d.id}" class="additional-form"><label>Crear Etiqueta:</label><div class="form-row"><input type="text" id="new-tag-name" placeholder="Nombre..." required><button type="submit">Crear</button></div></form>
                        <form id="add-subtag-form" data-id="${d.id}" class="additional-form"><label>Añadir Sub-Etiqueta:</label><div class="form-row"><select id="add-subtag-parent-select" required><option value="">Etiqueta Padre...</option>${renderAssignedMainTags()}</select><select id="add-subtag-select" required><option value="">Sub-Etiqueta...</option></select><button type="submit">Añadir</button></div></form>
                        <form id="create-subtag-form" data-id="${d.id}" class="additional-form"><label>Crear Sub-Etiqueta:</label><div class="form-row"><input type="text" id="new-subtag-name" placeholder="Nombre..." required><select id="parent-tag-select" required><option value="">Asociar a...</option>${renderAssignedMainTags()}</select><button type="submit">Crear</button></div></form>
                    </div>
                </div>`;
        };

        return `<div class="modal-header"><h2>${d.nombre}</h2><span class="close-btn" id="details-close-btn">&times;</span></div>
            <hr class="separator"><div class="modal-body"><div class="details-grid"><div class="details-left-column">
            ${d.imagen_url ? `<img src="${d.imagen_url}" alt="Vista previa de ${d.nombre}" class="details-img">` : '<div class="item-card-img-placeholder">Sin imagen</div>'}
            </div><div class="details-right-column">${renderInventarioSection(d)}${renderDespachoSection(d)}</div></div>
            <div class="details-bottom-grid">${renderInfoSection(d)}${renderAdicionalSection(d)}</div></div>`;
    }

    function renderCombustibleDetails(d) {
        const renderProviders = () => d.proveedores.map((p, index) => `<li class="info-list-item">${p.nombre} <button class="info-btn" data-type="proveedor" data-index="${index}">Ver más</button></li>`).join('') || '<li>N/A</li>';
        const renderUbicaciones = () => d.ubicaciones.map((u, index) => `<li class="info-list-item">${u.nombre} <button class="info-btn" data-type="ubicacion" data-index="${index}">Ver más</button></li>`).join('') || '<li>N/A</li>';
        return `<div class="modal-header"><h2>${d.tipo}</h2><span class="close-btn" id="details-close-btn">&times;</span></div>
            <hr class="separator"><div class="modal-body"><div class="details-grid"><div class="details-left-column">
            ${d.imagen_url ? `<img src="${d.imagen_url}" alt="Vista previa de ${d.tipo}" class="details-img">` : '<div class="item-card-img-placeholder">Sin imagen</div>'}
            </div><div class="details-right-column"><div class="details-section"><h4>Inventario</h4>
            <p><strong>Galones ingresados:</strong> ${d.cantidad_galones_ingresada}</p>
            <p><strong>Galones usados:</strong> ${d.cantidad_galones_usados}</p>
            <p><strong>Galones restantes:</strong> ${d.cantidad_galones_restantes}</p>
            <p><strong>Precio por galón:</strong> $${d.precio}</p></div><div class="details-section"><h4>Despacho</h4>
            <div class="management-grid"><form id="dispatch-form" data-id="${d.id}" class="additional-form">
            <label>Usar Cantidad (Gal):</label><div class="form-row"><input type="number" step="0.01" min="0" id="dispatch-qty" required><button type="submit">Aceptar</button></div></form>
            <form id="add-stock-form" data-id="${d.id}" class="additional-form"><label>Añadir Cantidad (Gal):</label>
            <div class="form-row"><input type="number" step="0.01" min="0" id="add-qty" required><button type="submit">Añadir</button></div></form></div></div>
            <div class="details-section"><h4>Información</h4><p><strong>Proveedores:</strong></p><ul class="info-list">${renderProviders()}</ul>
            <p><strong>Ubicaciones:</strong></p><ul class="info-list">${renderUbicaciones()}</ul></div></div></div></div>`;
    }

    function attachCommonListeners(data, itemType) {
        detailsContent.querySelector('#details-close-btn').addEventListener('click', closeDetailsModal);
        const singleItemType = itemType.slice(0, -1);

        if (singleItemType === 'alimento' || singleItemType === 'combustible') {
            detailsContent.querySelector('#dispatch-form').addEventListener('submit', (e) => handleDispatchSubmit(e, singleItemType));
            detailsContent.querySelector('#add-stock-form').addEventListener('submit', (e) => handleAddStockSubmit(e, singleItemType));
        }
        
        if (singleItemType === 'alimento') {
            detailsContent.querySelector('#add-tag-form').addEventListener('submit', (e) => handleTagManagement(e, singleItemType));
            detailsContent.querySelectorAll('.remove-tag-btn').forEach(btn => btn.addEventListener('click', (e) => handleTagManagement(e, singleItemType, 'remove')));
            detailsContent.querySelector('#create-tag-form').addEventListener('submit', (e) => handleCreateTag(e, singleItemType));
            detailsContent.querySelector('#create-subtag-form').addEventListener('submit', (e) => handleCreateTag(e, singleItemType));
            detailsContent.querySelector('#assign-category-form').addEventListener('submit', (e) => handleAssignCategory(e, singleItemType));
            detailsContent.querySelector('#create-category-form').addEventListener('submit', (e) => handleCreateCategory(e, singleItemType));
            detailsContent.querySelector('#add-subtag-form').addEventListener('submit', (e) => handleTagManagement(e, singleItemType));
            
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
                        const response = await fetch(`/admin/get_sub_etiquetas/?parent_ids=${parentId}`);
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
        }

        detailsContent.querySelectorAll('.info-btn').forEach(button => {
            button.addEventListener('click', () => {
                const type = button.dataset.type;
                const index = parseInt(button.dataset.index, 10);
                if (type === 'proveedor') renderInfoModal('Proveedor', data.proveedores[index]);
                if (type === 'ubicacion') renderInfoModal('Ubicación', data.ubicaciones[index]);
            });
        });
    }

    async function handleDispatchSubmit(event, singleItemType) {
        event.preventDefault();
        const form = event.target;
        const itemId = form.dataset.id;
        const cantidad = form.querySelector('#dispatch-qty').value;
        const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]').value;
        try {
            const response = await fetch(`/${singleItemType}/actualizar_cantidad/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                body: JSON.stringify({ [`${singleItemType}_id`]: itemId, cantidad_a_usar: cantidad })
            });
            const result = await response.json();
            if (response.ok) {
                alert(result.message);
                const updatedDetails = await (await fetch(`/${singleItemType}/detalles/${itemId}/`)).json();
                renderDetailsModal(updatedDetails, singleItemType + 's');
            } else {
                alert(`Error: ${result.message}`);
            }
        } catch (error) {
            alert('Ocurrió un error al actualizar la cantidad.');
        }
    }

    async function handleAddStockSubmit(event, singleItemType) {
        event.preventDefault();
        const form = event.target;
        const itemId = form.dataset.id;
        const cantidad = form.querySelector('#add-qty').value;
        const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]').value;
        try {
            const response = await fetch(`/${singleItemType}/anadir_stock/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                body: JSON.stringify({ [`${singleItemType}_id`]: itemId, cantidad_a_anadir: cantidad })
            });
            const result = await response.json();
            if (response.ok) {
                alert(result.message);
                const updatedDetails = await (await fetch(`/${singleItemType}/detalles/${itemId}/`)).json();
                renderDetailsModal(updatedDetails, singleItemType + 's');
            } else {
                alert(`Error: ${result.message}`);
            }
        } catch (error) {
            alert('Ocurrió un error al añadir stock.');
        }
    }
    
    async function handleTagManagement(event, singleItemType, action = 'add') {
        event.preventDefault();
        const form = event.currentTarget;
        const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]').value;
        let itemId, etiquetaId;

        if (action === 'remove') {
            itemId = form.dataset.alimentoId;
            etiquetaId = form.dataset.tagId;
        } else if (form.id === 'add-tag-form') {
            itemId = form.dataset.id;
            etiquetaId = form.querySelector('#tag-select').value;
        } else if (form.id === 'add-subtag-form') {
            itemId = form.dataset.id;
            etiquetaId = form.querySelector('#add-subtag-select').value;
        }

        if (!etiquetaId) {
             alert('Por favor, seleccione una etiqueta.');
             return;
        }

        try {
            const response = await fetch(`/${singleItemType}/gestionar_etiqueta/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                body: JSON.stringify({ [`${singleItemType}_id`]: itemId, etiqueta_id: etiquetaId, accion: action })
            });
            const result = await response.json();
            if (!response.ok) throw new Error(result.message);
            const data = await (await fetch(`/${singleItemType}/detalles/${itemId}/`)).json();
            renderDetailsModal(data, singleItemType + 's');
        } catch (error) {
            alert(`Error: ${error.message}`);
        }
    }

    async function handleCreateTag(event, singleItemType) {
        event.preventDefault();
        const form = event.target;
        const itemId = form.dataset.id;
        const isSubTag = form.id === 'create-subtag-form';
        const nombreEtiqueta = form.querySelector(isSubTag ? '#new-subtag-name' : '#new-tag-name').value;
        const parentId = isSubTag ? form.querySelector('#parent-tag-select').value : null;
        if (isSubTag && !parentId) {
            alert('Por favor, seleccione una etiqueta principal para la sub-etiqueta.');
            return;
        }
        const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]').value;
        try {
            const response = await fetch(`/${singleItemType}/crear_etiqueta/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                body: JSON.stringify({ [`${singleItemType}_id`]: itemId, nombre_etiqueta: nombreEtiqueta, parent_id: parentId })
            });
            const result = await response.json();
            if (response.ok) {
                alert(result.message);
                const updatedDetails = await (await fetch(`/${singleItemType}/detalles/${itemId}/`)).json();
                renderDetailsModal(updatedDetails, singleItemType + 's');
            } else {
                alert(`Error: ${result.message}`);
            }
        } catch (error) {
            alert('Ocurrió un error al crear la etiqueta.');
        }
    }

    async function handleAssignCategory(event, singleItemType) {
        event.preventDefault();
        const form = event.target;
        const itemId = form.dataset.id;
        const categoriaId = form.querySelector('#category-select').value;
        if (!categoriaId) {
            alert('Por favor, seleccione una categoría.');
            return;
        }
        const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]').value;
        try {
            const response = await fetch(`/${singleItemType}/asignar_categoria/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                body: JSON.stringify({ [`${singleItemType}_id`]: itemId, categoria_id: categoriaId })
            });
            const result = await response.json();
            if (response.ok) {
                alert(result.message);
                const updatedDetails = await (await fetch(`/${singleItemType}/detalles/${itemId}/`)).json();
                renderDetailsModal(updatedDetails, singleItemType + 's');
            } else {
                alert(`Error: ${result.message}`);
            }
        } catch (error) {
            alert('Ocurrió un error al asignar la categoría.');
        }
    }

    async function handleCreateCategory(event, singleItemType) {
        event.preventDefault();
        const form = event.target;
        const itemId = form.dataset.id;
        const nombreCategoria = form.querySelector('#new-category-name').value;
        const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]').value;
        try {
            const response = await fetch(`/${singleItemType}/crear_categoria/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                body: JSON.stringify({ [`${singleItemType}_id`]: itemId, nombre_categoria: nombreCategoria })
            });
            const result = await response.json();
            if (response.ok) {
                alert(result.message);
                const updatedDetails = await (await fetch(`/${singleItemType}/detalles/${itemId}/`)).json();
                renderDetailsModal(updatedDetails, singleItemType + 's');
            } else {
                alert(`Error: ${result.message}`);
            }
        } catch (error) {
            alert('Ocurrió un error al crear la categoría.');
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
});