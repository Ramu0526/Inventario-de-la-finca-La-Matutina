document.addEventListener('DOMContentLoaded', () => {
    const detailsModal = document.getElementById('details-modal');
    const infoModal = document.getElementById('info-modal');
    const detailsContent = detailsModal.querySelector('.details-content');
    const infoContent = infoModal.querySelector('.info-content');

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
            const params = new URLSearchParams({
                page,
                nombre: nombreFilter ? nombreFilter.value : '',
                categoria: categoriaFilter ? categoriaFilter.value : '',
                proveedor: proveedorFilter ? proveedorFilter.value : '',
                animal: animalFilter ? animalFilter.value : '',
                items_per_page: window.innerWidth <= 768 ? 6 : 8
            });
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
                const supportedTypes = ['alimentos', 'combustibles', 'control-plagas', 'mantenimientos', 'potreros', 'productos'];
                if (!supportedTypes.includes(itemType)) {
                    alert('La vista de detalles para esta sección aún no está implementada.');
                    return;
                }
                try {
                    const singleItemType = itemType.endsWith('s') ? itemType.slice(0, -1) : itemType;
                    const response = await fetch(`/${singleItemType}/detalles/${itemId}/`);
                    if (!response.ok) throw new Error('Error al cargar datos del item.');
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
                if(noItemsMsg) noItemsMsg.style.display = 'block';
                gridContainer.innerHTML = `<p>No se encontraron ${itemType.replace('-', ' ')}.</p>`;
                return;
            }
            if(noItemsMsg) noItemsMsg.style.display = 'none';
            items.forEach(item => {
                const itemCard = document.createElement('div');
                itemCard.className = 'item-card';
                itemCard.innerHTML = `
                    ${item.imagen_url ? `<img src="${item.imagen_url}" alt="${item.nombre}" class="item-card-img">` : '<div class="item-card-img-placeholder">Sin imagen</div>'}
                    <div class="item-card-body">
                        <h3 class="item-card-title">${item.nombre || item.tipo}</h3>
                        ${item.detalle ? `<p class="item-card-text">${item.detalle}</p>` : ''}
                        <button class="details-btn" data-id="${item.id}">Ver detalles</button>
                    </div>`;
                gridContainer.appendChild(itemCard);
            });
            gridContainer.querySelectorAll('.details-btn').forEach(attachDetailButtonListener);
        };

        const renderPagination = (data) => {
            paginationContainer.innerHTML = '';
            if (data.total_pages > 1) {
                for (let i = 1; i <= data.total_pages; i++) {
                    const button = document.createElement('button');
                    button.className = 'pagination-btn' + (i === data.current_page ? ' active' : '');
                    button.innerText = i;
                    button.addEventListener('click', () => fetchItems(i));
                    paginationContainer.appendChild(button);
                }
            }
        };

        const debounce = (func, delay) => { let t; return (...args) => { clearTimeout(t); t = setTimeout(() => func.apply(this, args), delay); }; };
        if (nombreFilter) nombreFilter.addEventListener('keyup', debounce(() => fetchItems(1), 300));
        if (categoriaFilter) categoriaFilter.addEventListener('change', () => fetchItems(1));
        if (proveedorFilter) proveedorFilter.addEventListener('change', () => fetchItems(1));
        if (animalFilter) animalFilter.addEventListener('change', () => fetchItems(1));
    };

    const closeDetailsModal = () => { detailsModal.style.display = 'none'; detailsContent.innerHTML = ''; };
    const closeInfoModal = () => { infoModal.style.display = 'none'; infoContent.innerHTML = ''; };

    function renderDetailsModal(data, itemType) {
        let content = '';
        if (itemType === 'alimentos') content = renderAlimentoDetails(data);
        else if (itemType === 'combustibles') content = renderCombustibleDetails(data);
        else if (itemType === 'control-plagas') content = renderControlPlagaDetails(data);
        else if (itemType === 'mantenimientos') content = renderMantenimientoDetails(data);
        else if (itemType === 'potreros') content = renderPotreroDetails(data);
        else if (itemType === 'productos') content = renderProductoDetails(data);
        
        detailsContent.innerHTML = content;
        attachCommonListeners(data, itemType);
    }

    // --- RENDERIZADO DE DETALLES ---
    
    function renderAlimentoDetails(d) {
        const renderInfoSection = (d) => `<div class="details-section"><h4>Información</h4><p><strong>Categoría:</strong> ${d.categoria ? d.categoria.nombre : 'N/A'}</p><p><strong>Descripción:</strong> ${d.descripcion || 'N/A'}</p><p><strong>Proveedores:</strong></p><ul class="info-list">${d.proveedores.map((p, index) => `<li class="info-list-item">${p.nombre} <button class="info-btn" data-type="proveedor" data-index="${index}">Ver más</button></li>`).join('') || '<li>N/A</li>'}</ul><p><strong>Ubicaciones:</strong></p><ul class="info-list">${d.ubicaciones.map((u, index) => `<li class="info-list-item">${u.nombre} <button class="info-btn" data-type="ubicacion" data-index="${index}">Ver más</button></li>`).join('') || '<li>N/A</li>'}</ul><p><strong>Fechas:</strong> Compra: ${d.fecha_compra} | Vence: ${d.fecha_vencimiento}</p></div>`;
        const renderInventarioSection = (d) => `<div class="details-section"><h4>Inventario</h4><p><strong>Ingresado:</strong> ${d.cantidad_ingresada} Kg</p><p><strong>Usado:</strong> <span id="qty-usada">${d.cantidad_usada}</span> Kg</p><p><strong>Restante:</strong> <span id="qty-restante">${d.cantidad_restante}</span> Kg</p><p><strong>Precio:</strong> $${d.precio}</p><p><strong>Estado:</strong> <span class="status-${d.estado.toLowerCase()}">${d.estado}</span></p>${d.estado === 'Agotado' ? '<p class="warning-text">¡Inventario agotado!</p>' : ''}</div>`;
        const renderDespachoSection = (d) => `<div class="details-section"><h4>Despacho</h4><div class="management-grid"><form id="dispatch-form" data-id="${d.id}" class="additional-form"><label>Usar Cantidad (Kg):</label><div class="form-row"><input type="number" step="0.01" min="0" id="dispatch-qty" required><button type="submit">Aceptar</button></div></form><form id="add-stock-form" data-id="${d.id}" class="additional-form"><label>Añadir Cantidad (Kg):</label><div class="form-row"><input type="number" step="0.01" min="0" id="add-qty" required><button type="submit">Añadir</button></div></form></div></div>`;
        const renderAdicionalSection = (d) => {
            const mainTags = d.etiquetas.filter(t => t.parent_id === null);
            const subTags = d.etiquetas.filter(t => t.parent_id !== null);
            const mainTagsHtml = mainTags.map(tag => `<li class="tag-item">${tag.nombre} <button class="remove-tag-btn" data-tag-id="${tag.id}" data-alimento-id="${d.id}">&times;</button></li>`).join('');
            const subTagsHtml = subTags.map(tag => `<li class="tag-item">${tag.nombre} <button class="remove-tag-btn" data-tag-id="${tag.id}" data-alimento-id="${d.id}">&times;</button></li>`).join('');
            const availableMainTags = d.todas_las_etiquetas_principales.filter(tag => !mainTags.some(assigned => assigned.id === tag.id)).map(tag => `<option value="${tag.id}">${tag.nombre}</option>`).join('');
            const assignedMainTags = mainTags.map(tag => `<option value="${tag.id}">${tag.nombre}</option>`).join('');
            const availableCategories = d.todas_las_categorias.filter(cat => !d.categoria || d.categoria.id !== cat.id).map(cat => `<option value="${cat.id}">${cat.nombre}</option>`).join('');
            return `<div class="details-section tags-section"><h4>Adicional</h4><p><strong>Etiquetas Principales:</strong></p><ul class="tag-list">${mainTagsHtml || '<li>Ninguna</li>'}</ul><p><strong>Sub-Etiquetas:</strong></p><ul class="tag-list">${subTagsHtml || '<li>Ninguna</li>'}</ul><div class="management-grid"><form id="assign-category-form" data-id="${d.id}" class="additional-form"><label>Asignar Categoría:</label><div class="form-row"><select id="category-select" required><option value="">Seleccione...</option>${availableCategories}</select><button type="submit">Asignar</button></div></form><form id="create-category-form" data-id="${d.id}" class="additional-form"><label>Crear Categoría:</label><div class="form-row"><input type="text" id="new-category-name" placeholder="Nombre..." required><button type="submit">Crear</button></div></form><form id="add-tag-form" data-id="${d.id}" class="additional-form"><label>Añadir Etiqueta:</label><div class="form-row"><select id="tag-select" required><option value="">Seleccione...</option>${availableMainTags}</select><button type="submit">Añadir</button></div></form><form id="create-tag-form" data-id="${d.id}" class="additional-form"><label>Crear Etiqueta Principal:</label><div class="form-row"><input type="text" id="new-tag-name" placeholder="Nombre..." required><button type="submit">Crear</button></div></form><form id="add-subtag-form" data-id="${d.id}" class="additional-form"><label>Añadir Sub-Etiqueta:</label><div class="form-row"><select id="add-subtag-parent-select" required><option value="">Etiqueta Padre...</option>${assignedMainTags}</select><select id="add-subtag-select" required><option value="">Sub-Etiqueta...</option></select><button type="submit">Añadir</button></div></form><form id="create-subtag-form" data-id="${d.id}" class="additional-form"><label>Crear Sub-Etiqueta:</label><div class="form-row"><input type="text" id="new-subtag-name" placeholder="Nombre..." required><select id="parent-tag-select" required><option value="">Asociar a...</option>${assignedMainTags}</select><button type="submit">Crear</button></div></form></div></div>`;
        };
        return `<div class="modal-header"><h2>${d.nombre}</h2><span class="close-btn" id="details-close-btn">&times;</span></div><hr class="separator"><div class="modal-body"><div class="details-grid"><div class="details-left-column">${d.imagen_url ? `<img src="${d.imagen_url}" alt="${d.nombre}" class="details-img">` : '<div class="item-card-img-placeholder">Sin imagen</div>'}</div><div class="details-right-column">${renderInventarioSection(d)}${renderDespachoSection(d)}</div></div><div class="details-bottom-grid">${renderInfoSection(d)}${renderAdicionalSection(d)}</div></div>`;
    }

    function renderCombustibleDetails(d) {
        const renderProviders = () => d.proveedores.map((p, index) => `<li class="info-list-item">${p.nombre} <button class="info-btn" data-type="proveedor" data-index="${index}">Ver más</button></li>`).join('') || '<li>N/A</li>';
        const renderUbicaciones = () => d.ubicaciones.map((u, index) => `<li class="info-list-item">${u.nombre} <button class="info-btn" data-type="ubicacion" data-index="${index}">Ver más</button></li>`).join('') || '<li>N/A</li>';
        return `<div class="modal-header"><h2>${d.tipo}</h2><span class="close-btn" id="details-close-btn">&times;</span></div><hr class="separator"><div class="modal-body"><div class="details-grid"><div class="details-left-column">${d.imagen_url ? `<img src="${d.imagen_url}" alt="${d.tipo}" class="details-img">` : '<div class="item-card-img-placeholder">Sin imagen</div>'}</div><div class="details-right-column"><div class="details-section"><h4>Inventario</h4><p><strong>Galones ingresados:</strong> ${d.cantidad_galones_ingresada}</p><p><strong>Galones usados:</strong> ${d.cantidad_galones_usados}</p><p><strong>Galones restantes:</strong> ${d.cantidad_galones_restantes}</p><p><strong>Precio por galón:</strong> $${d.precio}</p></div><div class="details-section"><h4>Despacho</h4><div class="management-grid"><form id="dispatch-form" data-id="${d.id}" class="additional-form"><label>Usar Cantidad (Gal):</label><div class="form-row"><input type="number" step="0.01" min="0" id="dispatch-qty" required><button type="submit">Aceptar</button></div></form><form id="add-stock-form" data-id="${d.id}" class="additional-form"><label>Añadir Cantidad (Gal):</label><div class="form-row"><input type="number" step="0.01" min="0" id="add-qty" required><button type="submit">Añadir</button></div></form></div></div><div class="details-section"><h4>Información</h4><p><strong>Descripción:</strong> ${d.descripcion || 'N/A'}</p><p><strong>Proveedores:</strong></p><ul class="info-list">${renderProviders()}</ul><p><strong>Ubicaciones:</strong></p><ul class="info-list">${renderUbicaciones()}</ul></div></div></div></div>`;
    }

    function renderControlPlagaDetails(d) {
        const renderProviders = () => d.proveedores.map((p, index) => `<li class="info-list-item">${p.nombre} <button class="info-btn" data-type="proveedor" data-index="${index}">Ver más</button></li>`).join('') || '<li>N/A</li>';
        const renderUbicaciones = () => d.ubicaciones.map((u, index) => `<li class="info-list-item">${u.nombre} <button class="info-btn" data-type="ubicacion" data-index="${index}">Ver más</button></li>`).join('') || '<li>N/A</li>';
        return `<div class="modal-header"><h2>${d.nombre}</h2><span class="close-btn" id="details-close-btn">&times;</span></div><hr class="separator"><div class="modal-body"><div class="details-grid"><div class="details-left-column">${d.imagen_url ? `<img src="${d.imagen_url}" alt="${d.nombre}" class="details-img">` : '<div class="item-card-img-placeholder">Sin imagen</div>'}</div><div class="details-right-column"><div class="details-section"><h4>Inventario</h4><p><strong>Tipo:</strong> ${d.tipo}</p><p><strong>Ingresado:</strong> ${d.cantidad_ingresada} ${d.unidad_medida}</p><p><strong>Usado:</strong> ${d.cantidad_usada} ${d.unidad_medida}</p><p><strong>Restante:</strong> ${d.cantidad_restante} ${d.unidad_medida}</p><p><strong>Precio:</strong> $${d.precio}</p></div><div class="details-section"><h4>Despacho</h4><div class="management-grid"><form id="dispatch-form" data-id="${d.id}" class="additional-form"><label>Usar Cantidad:</label><div class="form-row"><input type="number" step="0.01" min="0" id="dispatch-qty" required><button type="submit">Aceptar</button></div></form><form id="add-stock-form" data-id="${d.id}" class="additional-form"><label>Añadir Cantidad:</label><div class="form-row"><input type="number" step="0.01" min="0" id="add-qty" required><button type="submit">Añadir</button></div></form></div></div><div class="details-section"><h4>Información</h4><p><strong>Descripción:</strong> ${d.descripcion || 'N/A'}</p><p><strong>Proveedores:</strong></p><ul class="info-list">${renderProviders()}</ul><p><strong>Ubicaciones:</strong></p><ul class="info-list">${renderUbicaciones()}</ul><p><strong>Fechas:</strong> Compra: ${d.fecha_compra} | Vence: ${d.fecha_vencimiento}</p></div></div></div></div>`;
    }

    function renderMantenimientoDetails(d) {
        const lugaresHtml = d.lugares_mantenimiento.map(lugar => `<li class="info-list-item">${lugar.nombre} <button class="info-btn" data-type="lugar-mantenimiento" data-id="${lugar.id}">Ver más</button></li>`).join('') || '<li>No asignado</li>';
        return `<div class="modal-header"><h2>${d.equipo}</h2><span class="close-btn" id="details-close-btn">&times;</span></div><hr class="separator"><div class="modal-body"><div class="details-grid"><div class="details-left-column">${d.imagen_url ? `<img src="${d.imagen_url}" alt="${d.equipo}" class="details-img">` : '<div class="item-card-img-placeholder">Sin imagen</div>'}<div class="details-section"><h4>Descripción</h4><p>${d.descripcion || 'No hay descripción.'}</p></div></div><div class="details-right-column"><div class="details-section"><h4>Estado y Fechas</h4><form id="update-mantenimiento-form" data-id="${d.id}"><div class="form-field"><label for="fecha-ultimo">Último Mantenimiento:</label><input type="date" id="fecha-ultimo" value="${d.fecha_ultimo_mantenimiento}"></div><div class="form-field"><label for="fecha-proximo">Próximo Mantenimiento:</label><input type="date" id="fecha-proximo" value="${d.fecha_proximo_mantenimiento}"></div><div class="form-field-checkbox"><input type="checkbox" id="completado" ${d.completado ? 'checked' : ''}><label for="completado">Completado</label></div><button type="submit" class="panel-btn">Guardar Cambios</button></form></div><div class="details-section"><h4>Lugares de Mantenimiento</h4><ul class="info-list">${lugaresHtml}</ul></div></div></div></div>`;
    }

    function renderPotreroDetails(d) {
        const otrosPotrerosOptions = d.otros_potreros.map(p => `<option value="${p.id}" ${p.id === d.intercambio_con_potrero_id ? 'selected' : ''}>${p.nombre}</option>`).join('');
        return `<div class="modal-header"><h2>${d.nombre}</h2><span class="close-btn" id="details-close-btn">&times;</span></div><hr class="separator"><div class="modal-body"><div class="details-grid"><div class="details-left-column">${d.imagen_url ? `<img src="${d.imagen_url}" alt="${d.nombre}" class="details-img">` : '<div class="item-card-img-placeholder">Sin imagen</div>'}<div class="details-section"><h4>Información General</h4><p><strong>Área:</strong> ${d.area_hectareas} hectáreas</p><p><strong>Descripción:</strong> ${d.descripcion || 'No hay descripción.'}</p></div></div><div class="details-right-column"><div class="details-section"><h4>Estado y Acciones</h4><form id="update-potrero-form" data-id="${d.id}"><div class="form-field-checkbox"><input type="checkbox" id="empastado" ${d.empastado ? 'checked' : ''}><label for="empastado">Empastado</label></div><div class="form-field"><label for="fecha-empaste">Próximo Empaste:</label><input type="date" id="fecha-empaste" value="${d.fecha_proximo_empaste}"></div><div class="form-field-checkbox"><input type="checkbox" id="fumigado" ${d.fumigado ? 'checked' : ''}><label for="fumigado">Fumigado</label></div><div class="form-field"><label for="fecha-fumigacion">Próxima Fumigación:</label><input type="date" id="fecha-fumigacion" value="${d.fecha_proxima_fumigacion}"></div><div class="form-field-checkbox"><input type="checkbox" id="rozado" ${d.rozado ? 'checked' : ''}><label for="rozado">Rozado</label></div><div class="form-field"><label for="fecha-rozado">Próximo Rozado:</label><input type="date" id="fecha-rozado" value="${d.fecha_proximo_rozado}"></div><hr class="separator"><h4>Intercambio</h4><div class="form-field"><label for="intercambio-potrero">Intercambiar con:</label><select id="intercambio-potrero"><option value="">Ninguno</option>${otrosPotrerosOptions}</select></div><div class="form-field"><label for="fecha-intercambio">Fecha de Intercambio:</label><input type="date" id="fecha-intercambio" value="${d.fecha_intercambio}"></div><button type="submit" class="panel-btn">Guardar Cambios</button></form></div></div></div></div>`;
    }
    
    function renderProductoDetails(d) {
        const ubicacionesHtml = d.ubicaciones.map((u, index) => `<li class="info-list-item">${u.nombre} <button class="info-btn" data-type="ubicacion" data-index="${index}">Ver más</button></li>`).join('') || '<li>N/A</li>';
        const compradoresOptions = d.todos_los_compradores.map(c => `<option value="${c.id}" ${d.comprador_info && d.comprador_info.id === c.id ? 'selected' : ''}>${c.nombre}</option>`).join('');

        return `
            <div class="modal-header"><h2>${d.nombre}</h2><span class="close-btn" id="details-close-btn">&times;</span></div>
            <hr class="separator">
            <div class="modal-body">
                <div class="details-grid">
                    <div class="details-left-column">
                        ${d.imagen_url ? `<img src="${d.imagen_url}" alt="${d.nombre}" class="details-img">` : '<div class="item-card-img-placeholder">Sin imagen</div>'}
                        <div class="details-section">
                            <h4>Información</h4>
                            <p><strong>Categoría:</strong> ${d.categoria ? d.categoria.nombre : 'N/A'}</p>
                            <p><strong>Descripción:</strong> ${d.descripcion}</p>
                        </div>
                        <div class="details-section">
                            <h4>Ubicaciones del Producto</h4>
                            <ul class="info-list">${ubicacionesHtml}</ul>
                        </div>
                    </div>
                    <div class="details-right-column">
                        <div class="details-section">
                            <h4>Inventario y Venta</h4>
                            <form id="update-producto-form" data-id="${d.id}">
                                <p><strong>Cantidad:</strong> ${d.cantidad} ${d.unidad_medida}</p>
                                <p><strong>Precio Unitario:</strong> $${d.precio}</p>
                                <p><strong>Precio Total:</strong> $${d.precio_total}</p>
                                <p><strong>Fecha Producción:</strong> ${d.fecha_produccion}</p>
                                <div class="form-field"><label for="fecha-venta">Fecha de Venta:</label><input type="date" id="fecha-venta" value="${d.fecha_venta}"></div>
                                <div class="form-field"><label for="estado-producto">Estado:</label><select id="estado-producto">
                                    <option value="DISPONIBLE" ${d.estado === 'DISPONIBLE' ? 'selected' : ''}>Disponible</option>
                                    <option value="APARTADO" ${d.estado === 'APARTADO' ? 'selected' : ''}>Apartado</option>
                                    <option value="VENDIDO" ${d.estado === 'VENDIDO' ? 'selected' : ''}>Vendido</option>
                                </select></div>
                                <hr class="separator">
                                <h4>Comprador</h4>
                                <div class="comprador-info" style="${!d.comprador_info ? 'display: none;' : ''}">
                                    <p><strong>Asignado a:</strong> <span id="comprador-nombre">${d.comprador_info ? d.comprador_info.nombre : ''}</span> <button type="button" class="info-btn" id="ver-comprador-btn">Ver más</button></p>
                                </div>
                                <div class="form-field"><label for="comprador">Asignar a:</label><select id="comprador"><option value="">Ninguno</option>${compradoresOptions}</select></div>
                                <div class="form-field"><label for="valor-abono">Valor de Abono:</label><input type="number" step="0.01" id="valor-abono" value="${d.comprador_info ? d.comprador_info.valor_abono : '0.00'}"></div>
                                <div class="form-field"><label for="valor-compra">Valor de Compra:</label><input type="number" step="0.01" id="valor-compra" value="${d.comprador_info ? d.comprador_info.valor_compra : ''}"></div>
                                <button type="submit" class="panel-btn">Guardar Cambios</button>
                            </form>
                        </div>
                        <div class="details-section">
                            <h4>Crear Nuevo Comprador</h4>
                            <form id="create-comprador-form">
                                <div class="form-field"><label for="nuevo-comprador-nombre">Nombre:</label><input type="text" id="nuevo-comprador-nombre" required></div>
                                <div class="form-field"><label for="nuevo-comprador-telefono">Teléfono:</label><input type="text" id="nuevo-comprador-telefono"></div>
                                <button type="submit" class="panel-btn">Crear Comprador</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>`;
    }

    // --- MANEJO DE EVENTOS ---
    
    function attachCommonListeners(data, itemType) {
        detailsContent.querySelector('#details-close-btn').addEventListener('click', closeDetailsModal);
        const singleItemType = itemType.endsWith('s') ? itemType.slice(0, -1) : itemType;

        if (['alimento', 'combustible', 'control-plaga'].includes(singleItemType)) {
            detailsContent.querySelector('#dispatch-form').addEventListener('submit', (e) => handleDispatchSubmit(e, singleItemType));
            detailsContent.querySelector('#add-stock-form').addEventListener('submit', (e) => handleAddStockSubmit(e, singleItemType));
        }
        if (singleItemType === 'mantenimiento') detailsContent.querySelector('#update-mantenimiento-form').addEventListener('submit', handleUpdateMantenimiento);
        if (singleItemType === 'potrero') detailsContent.querySelector('#update-potrero-form').addEventListener('submit', handleUpdatePotrero);
        if (singleItemType === 'producto') {
            detailsContent.querySelector('#update-producto-form').addEventListener('submit', handleUpdateProducto);
            detailsContent.querySelector('#create-comprador-form').addEventListener('submit', handleCreateComprador);
            const verCompradorBtn = detailsContent.querySelector('#ver-comprador-btn');
            if(verCompradorBtn) {
                verCompradorBtn.addEventListener('click', async () => {
                    if (data.comprador_info && data.comprador_info.id) {
                        try {
                            const response = await fetch(`/comprador/detalles/${data.comprador_info.id}/`);
                            const compradorData = await response.json();
                            renderCompradorInfoModal(compradorData, data.comprador_info.valor_compra);
                        } catch(e) { console.error(e); alert("Error al cargar detalles del comprador."); }
                    }
                });
            }
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
                    if (!parentId) { subtagSelect.innerHTML = '<option value="">Sub-Etiqueta...</option>'; return; }
                    try {
                        const response = await fetch(`/admin/get_sub_etiquetas/?parent_ids=${parentId}`);
                        const subEtiquetas = await response.json();
                        let options = '<option value="">Seleccione...</option>';
                        for (const [id, nombre] of Object.entries(subEtiquetas)) {
                            if (!data.etiquetas.some(t => t.id === parseInt(id))) options += `<option value="${id}">${nombre}</option>`;
                        }
                        subtagSelect.innerHTML = options;
                    } catch (error) {
                        subtagSelect.innerHTML = '<option value="">Error</option>';
                    }
                });
            }
        }
        detailsContent.querySelectorAll('.info-btn').forEach(button => {
            button.addEventListener('click', async () => {
                const type = button.dataset.type;
                const id = button.dataset.id;
                const index = button.dataset.index;
                if (type === 'proveedor') renderInfoModal('Proveedor', data.proveedores[index]);
                if (type === 'ubicacion') renderInfoModal('Ubicación', data.ubicaciones[index]);
                if (type === 'lugar-mantenimiento') {
                    try {
                        const response = await fetch(`/lugar-mantenimiento/detalles/${id}/`);
                        const lugarData = await response.json();
                        renderLugarMantenimientoInfoModal(lugarData);
                    } catch(e) { console.error(e); alert("Error al cargar detalles del lugar."); }
                }
            });
        });
    }

    async function handleApiRequest(url, body, itemId, singleItemType) {
        const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]').value;
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                body: JSON.stringify(body)
            });
            const result = await response.json();
            if (response.ok) {
                alert(result.message);
                if (itemId && singleItemType) {
                    const updatedDetails = await (await fetch(`/${singleItemType}/detalles/${itemId}/`)).json();
                    renderDetailsModal(updatedDetails, singleItemType.endsWith('s') ? singleItemType : singleItemType + 's');
                }
            } else {
                alert(`Error: ${result.message}`);
            }
        } catch (error) {
            console.error(error);
            alert(`Ocurrió un error: ${error.message}`);
        }
    }

    function handleDispatchSubmit(event, singleItemType) {
        event.preventDefault();
        const form = event.target;
        const body = { [`${singleItemType}_id`]: form.dataset.id, cantidad_a_usar: form.querySelector('#dispatch-qty').value };
        handleApiRequest(`/${singleItemType}/actualizar_cantidad/`, body, form.dataset.id, singleItemType);
    }

    function handleAddStockSubmit(event, singleItemType) {
        event.preventDefault();
        const form = event.target;
        const body = { [`${singleItemType}_id`]: form.dataset.id, cantidad_a_anadir: form.querySelector('#add-qty').value };
        handleApiRequest(`/${singleItemType}/anadir_stock/`, body, form.dataset.id, singleItemType);
    }
    
    function handleUpdateMantenimiento(event) {
        event.preventDefault();
        const form = event.target;
        const body = {
            mantenimiento_id: form.dataset.id,
            fecha_ultimo: form.querySelector('#fecha-ultimo').value,
            fecha_proximo: form.querySelector('#fecha-proximo').value,
            completado: form.querySelector('#completado').checked,
        };
        handleApiRequest('/mantenimiento/actualizar/', body, form.dataset.id, 'mantenimiento');
    }

    function handleUpdatePotrero(event) {
        event.preventDefault();
        const form = event.target;
        const body = {
            potrero_id: form.dataset.id,
            empastado: form.querySelector('#empastado').checked,
            fumigado: form.querySelector('#fumigado').checked,
            rozado: form.querySelector('#rozado').checked,
            fecha_proximo_empaste: form.querySelector('#fecha-empaste').value,
            fecha_proxima_fumigacion: form.querySelector('#fecha-fumigacion').value,
            fecha_proximo_rozado: form.querySelector('#fecha-rozado').value,
            intercambio_con_potrero_id: form.querySelector('#intercambio-potrero').value,
            fecha_intercambio: form.querySelector('#fecha-intercambio').value,
        };
        handleApiRequest('/potrero/actualizar/', body, form.dataset.id, 'potrero');
    }

    function handleUpdateProducto(event) {
        event.preventDefault();
        const form = event.target;
        const body = {
            producto_id: form.dataset.id,
            estado: form.querySelector('#estado-producto').value,
            fecha_venta: form.querySelector('#fecha-venta').value,
            comprador_id: form.querySelector('#comprador').value,
            valor_compra: form.querySelector('#valor-compra').value,
            valor_abono: form.querySelector('#valor-abono').value,
        };
        handleApiRequest('/producto/actualizar/', body, form.dataset.id, 'producto');
    }

    async function handleCreateComprador(event) {
        event.preventDefault();
        const form = event.target;
        const nombre = form.querySelector('#nuevo-comprador-nombre').value;
        const telefono = form.querySelector('#nuevo-comprador-telefono').value;
        const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]').value;
        try {
            const response = await fetch('/comprador/crear/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                body: JSON.stringify({ nombre, telefono })
            });
            const result = await response.json();
            if (response.ok) {
                alert(result.message);
                const newOption = new Option(result.nuevo_comprador.nombre, result.nuevo_comprador.id, true, true);
                document.querySelector('#comprador').add(newOption);
                form.reset();
            } else {
                alert(`Error: ${result.message}`);
            }
        } catch (error) {
            console.error(error);
            alert(`Ocurrió un error: ${error.message}`);
        }
    }

    function handleTagManagement(event, singleItemType, action = 'add') {
        event.preventDefault();
        const el = event.currentTarget;
        let itemId, etiquetaId;
        if (action === 'remove') {
            itemId = el.dataset.alimentoId;
            etiquetaId = el.dataset.tagId;
        } else {
            itemId = el.dataset.id;
            etiquetaId = el.id === 'add-subtag-form' ? el.querySelector('#add-subtag-select').value : el.querySelector('select').value;
        }
        if (!etiquetaId) { alert('Por favor, seleccione una etiqueta.'); return; }
        const body = { [`${singleItemType}_id`]: itemId, etiqueta_id: etiquetaId, accion: action };
        handleApiRequest(`/${singleItemType}/gestionar_etiqueta/`, body, itemId, singleItemType);
    }

    function handleCreateTag(event, singleItemType) {
        event.preventDefault();
        const form = event.target;
        const isSubTag = form.id === 'create-subtag-form';
        const body = {
            [`${singleItemType}_id`]: form.dataset.id,
            nombre_etiqueta: form.querySelector(isSubTag ? '#new-subtag-name' : '#new-tag-name').value,
            parent_id: isSubTag ? form.querySelector('#parent-tag-select').value : null,
        };
        if (isSubTag && !body.parent_id) { alert('Por favor, seleccione una etiqueta principal.'); return; }
        handleApiRequest(`/${singleItemType}/crear_etiqueta/`, body, form.dataset.id, singleItemType);
    }

    function handleAssignCategory(event, singleItemType) {
        event.preventDefault();
        const form = event.target;
        const categoriaId = form.querySelector('#category-select').value;
        if (!categoriaId) { alert('Por favor, seleccione una categoría.'); return; }
        const body = { [`${singleItemType}_id`]: form.dataset.id, categoria_id: categoriaId };
        handleApiRequest(`/${singleItemType}/asignar_categoria/`, body, form.dataset.id, singleItemType);
    }

    function handleCreateCategory(event, singleItemType) {
        event.preventDefault();
        const form = event.target;
        const body = { [`${singleItemType}_id`]: form.dataset.id, nombre_categoria: form.querySelector('#new-category-name').value };
        handleApiRequest(`/${singleItemType}/crear_categoria/`, body, form.dataset.id, singleItemType);
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

    function renderLugarMantenimientoInfoModal(d) {
        const proveedoresHtml = d.proveedores.map(p => `<li>${p.nombre}</li>`).join('') || '<li>N/A</li>';
        const ubicacionesHtml = d.ubicaciones.map(u => `<li><a href="${u.link}" target="_blank">Ver en mapa</a></li>`).join('') || '<li>N/A</li>';
        let contentHtml = `<p><strong>Empresa:</strong> ${d.nombre_empresa || 'N/A'}</p><p><strong>Contacto:</strong> ${d.correo || ''} - ${d.numero || ''}</p><p><strong>Descripción:</strong> ${d.descripcion || 'N/A'}</p><p><strong>Proveedores Asociados:</strong></p><ul>${proveedoresHtml}</ul><p><strong>Ubicaciones:</strong></p><ul>${ubicacionesHtml}</ul>`;
        infoContent.innerHTML = `<div class="modal-header"><h2>${d.nombre_lugar}</h2><span class="close-btn" id="info-close-btn">&times;</span></div><hr class="separator"><div class="modal-body">${contentHtml}</div>`;
        infoModal.style.display = 'block';
        infoContent.querySelector('#info-close-btn').addEventListener('click', closeInfoModal);
    }
    
    function renderCompradorInfoModal(d, valorCompra) {
        let contentHtml = `<p><strong>Nombre:</strong> ${d.nombre}</p>
                         <p><strong>Teléfono:</strong> ${d.telefono || 'N/A'}</p>
                         <p><strong>Valor Total Compra:</strong> $${valorCompra}</p>`;
        infoContent.innerHTML = `<div class="modal-header"><h2>Info del Comprador</h2><span class="close-btn" id="info-close-btn">&times;</span></div><hr class="separator"><div class="modal-body">${contentHtml}</div>`;
        infoModal.style.display = 'block';
        infoContent.querySelector('#info-close-btn').addEventListener('click', closeInfoModal);
    }
});