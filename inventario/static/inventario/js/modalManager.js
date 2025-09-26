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
                const supportedTypes = ['alimentos', 'combustibles', 'control-plagas', 'mantenimientos', 'potreros', 'productos', 'medicamentos', 'ganado'];
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

    window.setupCreateVacunaModal = async () => {
        const modal = document.getElementById('crear-vacuna-modal');
        const form = modal.querySelector('#create-vacuna-form');
        const closeBtn = modal.querySelector('.close-btn');

        try {
            const response = await fetch('/get_vacuna_form_data/');
            const data = await response.json();
            
            const allProveedoresOptions = data.proveedores.map(p => `<option value="${p.id}">${p.nombre}</option>`).join('');
            const allUbicacionesOptions = data.ubicaciones.map(u => `<option value="${u.id}">${u.nombre}</option>`).join('');
            const allEtiquetasOptions = data.etiquetas.map(e => `<option value="${e.id}">${e.nombre}</option>`).join('');

            form.innerHTML = `
                <div class="form-grid-columns">
                    <div class="form-column">
                        <div class="form-field"><label for="vacuna-nombre">Nombre:</label><input type="text" id="vacuna-nombre" required></div>
                        <div class="form-field"><label for="vacuna-tipo">Tipo:</label><input type="text" id="vacuna-tipo"></div>
                        <div class="form-field"><label for="vacuna-precio">Precio:</label><input type="number" step="0.01" id="vacuna-precio" value="0.00" required></div>
                        <div class="form-field"><label for="vacuna-cantidad">Cantidad:</label><input type="number" step="0.01" id="vacuna-cantidad" required></div>
                        <div class="form-field"><label for="vacuna-unidad">Unidad Medida:</label><select id="vacuna-unidad"><option value="U">Unidad</option><option value="ml">Mililitros (ml)</option><option value="g">Gramos (g)</option></select></div>
                        <div class="form-field"><label for="vacuna-fecha-compra">Fecha Compra:</label><input type="date" id="vacuna-fecha-compra" required></div>
                        <div class="form-field"><label for="vacuna-fecha-vencimiento">Fecha Vencimiento:</label><input type="date" id="vacuna-fecha-vencimiento" required></div>
                        <div class="form-field-checkbox"><input type="checkbox" id="vacuna-disponible" checked><label for="vacuna-disponible">Disponible</label></div>
                    </div>
                    <div class="form-column">
                        <div class="form-field"><label for="vacuna-dosis-crecimiento">Dosis Crecimiento:</label><input type="text" id="vacuna-dosis-crecimiento"></div>
                        <div class="form-field"><label for="vacuna-dosis-edad">Dosis Edad:</label><input type="text" id="vacuna-dosis-edad"></div>
                        <div class="form-field"><label for="vacuna-dosis-peso">Dosis Peso:</label><input type="text" id="vacuna-dosis-peso"></div>
                        <div class="form-field-full"><label for="vacuna-proveedores">Proveedores:</label><select id="vacuna-proveedores" multiple>${allProveedoresOptions}</select></div>
                        <div class="form-field-full"><label for="vacuna-ubicaciones">Ubicaciones:</label><select id="vacuna-ubicaciones" multiple>${allUbicacionesOptions}</select></div>
                        <div class="form-field-full"><label for="vacuna-etiquetas">Etiquetas:</label><select id="vacuna-etiquetas" multiple>${allEtiquetasOptions}</select></div>
                    </div>
                </div>
                <div class="form-field-full"><label for="vacuna-descripcion">Descripción:</label><textarea id="vacuna-descripcion"></textarea></div>
                <button type="submit" class="panel-btn" style="margin-top: 1rem;">Crear Vacuna</button>
            `;
            modal.style.display = 'block';
        } catch (error) {
            console.error("Error fetching form data for vacuna:", error);
            alert("No se pudo abrir el formulario para crear vacunas.");
        }

        closeBtn.addEventListener('click', () => { modal.style.display = 'none'; });
        form.addEventListener('submit', handleCreateVacuna);
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
        else if (itemType === 'medicamentos') content = renderMedicamentoDetails(data);
        else if (itemType === 'ganado') content = renderGanadoDetails(data);
        
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
        return `<div class="modal-header"><h2>${d.nombre}</h2><span class="close-btn" id="details-close-btn">&times;</span></div><hr class="separator"><div class="modal-body"><div class="details-grid"><div class="details-left-column">${d.imagen_url ? `<img src="${d.imagen_url}" alt="${d.nombre}" class="details-img">` : '<div class="item-card-img-placeholder">Sin imagen</div>'}<div class="details-section"><h4>Información</h4><p><strong>Categoría:</strong> ${d.categoria ? d.categoria.nombre : 'N/A'}</p><p><strong>Descripción:</strong> ${d.descripcion}</p></div><div class="details-section"><h4>Ubicaciones del Producto</h4><ul class="info-list">${ubicacionesHtml}</ul></div></div><div class="details-right-column"><div class="details-section"><h4>Inventario y Venta</h4><form id="update-producto-form" data-id="${d.id}"><p><strong>Cantidad:</strong> ${d.cantidad} ${d.unidad_medida}</p><p><strong>Precio Unitario:</strong> $${d.precio}</p><p><strong>Precio Total:</strong> $${d.precio_total}</p><p><strong>Fecha Producción:</strong> ${d.fecha_produccion}</p><div class="form-field"><label for="fecha-venta">Fecha de Venta:</label><input type="date" id="fecha-venta" value="${d.fecha_venta}"></div><div class="form-field"><label for="estado-producto">Estado:</label><select id="estado-producto"><option value="DISPONIBLE" ${d.estado === 'DISPONIBLE' ? 'selected' : ''}>Disponible</option><option value="APARTADO" ${d.estado === 'APARTADO' ? 'selected' : ''}>Apartado</option><option value="VENDIDO" ${d.estado === 'VENDIDO' ? 'selected' : ''}>Vendido</option></select></div><hr class="separator"><h4>Comprador</h4><div class="comprador-info" style="${!d.comprador_info ? 'display: none;' : ''}"><p><strong>Asignado a:</strong> <span id="comprador-nombre">${d.comprador_info ? d.comprador_info.nombre : ''}</span> <button type="button" class="info-btn" id="ver-comprador-btn">Ver más</button></p></div><div class="form-field"><label for="comprador">Asignar a:</label><select id="comprador"><option value="">Ninguno</option>${compradoresOptions}</select></div><div class="form-field"><label for="valor-abono">Valor de Abono:</label><input type="number" step="0.01" id="valor-abono" value="${d.comprador_info ? d.comprador_info.valor_abono : '0.00'}"></div><div class="form-field"><label for="valor-compra">Valor de Compra:</label><input type="number" step="0.01" id="valor-compra" value="${d.comprador_info ? d.comprador_info.valor_compra : ''}"></div><button type="submit" class="panel-btn">Guardar Cambios</button></form></div><div class="details-section"><h4>Crear Nuevo Comprador</h4><form id="create-comprador-form"><div class="form-field"><label for="nuevo-comprador-nombre">Nombre:</label><input type="text" id="nuevo-comprador-nombre" required></div><div class="form-field"><label for="nuevo-comprador-telefono">Teléfono:</label><input type="text" id="nuevo-comprador-telefono"></div><button type="submit" class="panel-btn">Crear Comprador</button></form></div></div></div></div>`;
    }

    function renderMedicamentoDetails(d) {
        const proveedoresHtml = d.proveedores.map(p => `<li class="info-list-item">${p.nombre}</li>`).join('') || '<li>N/A</li>';
        const ubicacionesHtml = d.ubicaciones.map(u => `<li class="info-list-item">${u.nombre}</li>`).join('') || '<li>N/A</li>';
    
        return `
            <div class="modal-header">
                <h2>${d.nombre}</h2>
                <span class="close-btn" id="details-close-btn">&times;</span>
            </div>
            <hr class="separator">
            <div class="modal-body">
                <div class="details-grid">
                    <div class="details-left-column">
                        ${d.imagen_url ? `<img src="${d.imagen_url}" alt="${d.nombre}" class="details-img">` : '<div class="item-card-img-placeholder">Sin imagen</div>'}
                        <div class="details-section">
                            <h4>Inventario</h4>
                            <p><strong>Cantidad:</strong> ${d.cantidad_ingresada} ${d.unidad_medida}</p>
                            <p><strong>Usado:</strong> ${d.cantidad_usada} ${d.unidad_medida}</p>
                            <p><strong>Restante:</strong> ${d.cantidad_restante} ${d.unidad_medida}</p>
                            <p><strong>Precio:</strong> $${d.precio}</p>
                        </div>
                        <div class="details-section">
                            <h4>Despacho</h4>
                            <div class="management-grid">
                                <form id="dispatch-form" data-id="${d.id}" class="additional-form">
                                    <label>Usar Cantidad:</label>
                                    <div class="form-row">
                                        <input type="number" step="0.01" min="0" id="dispatch-qty" required>
                                        <button type="submit">Aceptar</button>
                                    </div>
                                </form>
                                <form id="add-stock-form" data-id="${d.id}" class="additional-form">
                                    <label>Añadir Cantidad:</label>
                                    <div class="form-row">
                                        <input type="number" step="0.01" min="0" id="add-qty" required>
                                        <button type="submit">Añadir</button>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>
                    <div class="details-right-column">
                        <div class="details-section">
                            <h4>Información</h4>
                            <p><strong>Categoría:</strong> ${d.categoria ? d.categoria.nombre : 'N/A'}</p>
                            <p><strong>Descripción:</strong> ${d.descripcion}</p>
                            <p><strong>Proveedores:</strong></p>
                            <ul class="info-list">${proveedoresHtml}</ul>
                            <p><strong>Ubicaciones:</strong></p>
                            <ul class="info-list">${ubicacionesHtml}</ul>
                            <p><strong>Fechas:</strong> Compra: ${d.fecha_compra} | Ingreso: ${d.fecha_ingreso} | Vence: ${d.fecha_vencimiento}</p>
                        </div>
                    </div>
                </div>
                <div class="details-bottom-grid">
                    <div class="details-section">
                        <h4>Gestión de Vacunas</h4>
                        <button id="crear-vacuna-btn" class="panel-btn">Crear Vacuna Asociada</button>
                    </div>
                </div>
            </div>`;
    }
    
    function renderGanadoDetails(d) {
        const historialVacunacionHtml = d.historial_vacunacion.length > 0 ?
            d.historial_vacunacion.map(v => `
                <li class="info-list-item">
                    <span>${v.fecha_aplicacion}: ${v.vacuna_nombre} (Próx: ${v.fecha_proxima_dosis})</span>
                    <div class="historial-acciones">
                        <button class="panel-btn-sm view-vacuna-btn" data-id="${v.vacuna_id}">Ver Vacuna</button>
                        <button class="panel-btn-sm view-note-btn" data-notas="${v.notas}">Ver Nota</button>
                        <button class="panel-btn-sm edit-vacunacion-btn" data-id="${v.id}">Editar</button>
                        <button class="panel-btn-sm delete-vacunacion-btn" data-id="${v.id}">Eliminar</button>
                    </div>
                </li>`).join('') : '<li>Sin registros.</li>';

        const historialMedicamentosHtml = d.historial_medicamentos.length > 0 ?
            d.historial_medicamentos.map(m => `
                <li class="info-list-item">
                    <span>${m.fecha_aplicacion}: ${m.medicamento_nombre}</span>
                    <div class="historial-acciones">
                        <button class="panel-btn-sm view-medicamento-btn" data-id="${m.medicamento_id}">Ver Medicamento</button>
                        <button class="panel-btn-sm view-note-btn" data-notas="${m.notas}">Ver Nota</button>
                        <button class="panel-btn-sm edit-medicamento-btn" data-id="${m.id}">Editar</button>
                        <button class="panel-btn-sm delete-medicamento-btn" data-id="${m.id}">Eliminar</button>
                    </div>
                </li>`).join('') : '<li>Sin registros.</li>';

        const vacunasOptions = d.todas_las_vacunas.map(v => `<option value="${v.id}">${v.nombre}</option>`).join('');
        const medicamentosOptions = d.todos_los_medicamentos.map(m => `<option value="${m.id}">${m.nombre}</option>`).join('');
        const estadosSaludOptions = d.todos_los_estados_salud.map(e => `<option value="${e.value}" ${d.estado_salud === e.value ? 'selected' : ''}>${e.label}</option>`).join('');
        const tiposPeñeOptions = d.todos_los_tipos_peñe.map(p => `<option value="${p.value}" ${d.peñe === p.value ? 'selected' : ''}>${p.label}</option>`).join('');
        const estadosAnimalOptions = d.todos_los_estados.map(e => `<option value="${e.value}" ${d.estado === e.value ? 'selected' : ''}>${e.label}</option>`).join('');
        const crecimientoOptions = d.todos_los_crecimientos.map(c => `<option value="${c.value}" ${d.crecimiento === c.value ? 'selected' : ''}>${c.label}</option>`).join('');

        return `
            <div class="modal-header"><h2>${d.identificador} - ${d.animal}</h2><span class="close-btn" id="details-close-btn">&times;</span></div>
            <hr class="separator">
            <div class="modal-body">
                <div class="details-grid-ganado">
                    <div class="details-left-column">
                        ${d.imagen_url ? `<img src="${d.imagen_url}" alt="${d.identificador}" class="details-img">` : '<div class="item-card-img-placeholder">Sin imagen</div>'}
                        <div class="details-section">
                            <h4>Información Principal</h4>
                            <form id="update-ganado-form" data-id="${d.id}">
                                <p><strong>Raza:</strong> ${d.raza || 'N/A'}</p>
                                <p><strong>Género:</strong> ${d.genero}</p>
                                <div class="form-field"><label for="ganado-peso">Peso (Kg):</label><input type="number" step="0.01" id="ganado-peso" value="${d.peso_kg}"></div>
                                <p><strong>Edad:</strong> ${d.edad}</p>
                                <p><strong>Fecha de Nacimiento:</strong> ${d.fecha_nacimiento}</p>
                                
                                <div class="form-field"><label for="ganado-crecimiento">Crecimiento:</label><select id="ganado-crecimiento">${crecimientoOptions}</select></div>
                                <div class="form-field"><label for="ganado-estado">Estado:</label><select id="ganado-estado">${estadosAnimalOptions}</select></div>
                                
                                <div id="fallecido-fields" style="display: none;">
                                    <div class="form-field"><label for="ganado-fecha-fallecimiento">Fecha Fallecimiento:</label><input type="date" id="ganado-fecha-fallecimiento" value="${d.fecha_fallecimiento}"></div>
                                </div>
                                <div id="vendido-fields" style="display: none;">
                                     <div class="form-field"><label for="ganado-fecha-venta">Fecha Venta:</label><input type="date" id="ganado-fecha-venta" value="${d.fecha_venta}"></div>
                                     <div class="form-field"><label for="ganado-valor-venta">Valor Venta:</label><input type="number" step="0.01" id="ganado-valor-venta" value="${d.valor_venta}"></div>
                                     <div class="form-field"><label for="ganado-comprador">Comprador:</label><input type="text" id="ganado-comprador" value="${d.comprador}"></div>
                                     <div class="form-field"><label for="ganado-comprador-telefono">Teléfono Comprador:</label><input type="text" id="ganado-comprador-telefono" value="${d.comprador_telefono}"></div>
                                </div>

                                <div class="form-field"><label for="ganado-estado-salud">Estado de Salud:</label><select id="ganado-estado-salud">${estadosSaludOptions}</select></div>
                                <div class="form-field"><label for="ganado-peñe">Tipo de Peñe:</label><select id="ganado-peñe">${tiposPeñeOptions}</select></div>
                                
                                <div id="peñe-fields" style="display: none;">
                                     <div class="form-field"><label for="ganado-fecha-peñe">Fecha de Peñe:</label><input type="date" id="ganado-fecha-peñe" value="${d.fecha_peñe}"></div>
                                     <div class="form-field"><label for="ganado-descripcion-peñe">Descripción del Peñe:</label><textarea id="ganado-descripcion-peñe">${d.descripcion_peñe}</textarea></div>
                                </div>

                                <div class="form-field"><label for="ganado-descripcion">Notas / Descripción:</label><textarea id="ganado-descripcion">${d.descripcion}</textarea></div>
                                <button type="submit" class="panel-btn">Guardar Cambios</button>
                            </form>
                        </div>
                    </div>
                    <div class="details-right-column">
                        <div class="details-section">
                            <h4>Historial de Vacunación</h4>
                            <ul class="info-list">${historialVacunacionHtml}</ul>
                        </div>
                        <div class="details-section">
                            <h4>Registrar Nueva Vacunación</h4>
                            <form id="registrar-vacunacion-form" data-id="${d.id}">
                                <div class="form-field"><label for="vacuna-select">Vacuna:</label><select id="vacuna-select" required><option value="">Seleccione...</option>${vacunasOptions}</select></div>
                                <div id="vacuna-details-preview" class="details-preview"></div>
                                <div class="form-field"><label for="fecha-aplicacion-vacuna">Fecha Aplicación:</label><input type="date" id="fecha-aplicacion-vacuna" required></div>
                                <div class="form-field"><label for="fecha-proxima-vacuna">Próxima Dosis:</label><input type="date" id="fecha-proxima-vacuna"></div>
                                <div class="form-field"><label for="vacunacion-notas">Notas:</label><textarea id="vacunacion-notas"></textarea></div>
                                <button type="submit" class="panel-btn">Registrar Vacuna</button>
                            </form>
                        </div>
                    </div>
                    <div class="details-bottom-column">
                        <div class="details-section">
                            <h4>Historial de Medicamentos</h4>
                            <ul class="info-list">${historialMedicamentosHtml}</ul>
                        </div>
                        <div class="details-section">
                            <h4>Registrar Nuevo Medicamento</h4>
                            <form id="registrar-medicamento-form" data-id="${d.id}">
                                <div class="form-field"><label for="medicamento-select">Medicamento:</label><select id="medicamento-select" required><option value="">Seleccione...</option>${medicamentosOptions}</select></div>
                                <div class="form-field"><label for="fecha-aplicacion-medicamento">Fecha Aplicación:</label><input type="date" id="fecha-aplicacion-medicamento" required></div>
                                <div class="form-field"><label for="medicamento-notas">Notas:</label><textarea id="medicamento-notas"></textarea></div>
                                <button type="submit" class="panel-btn">Registrar Medicamento</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>`;
    }
    
    // --- MANEJO DE EVENTOS ---
    
    function attachCommonListeners(data, itemType) {
        const closeBtn = detailsContent.querySelector('#details-close-btn');
        if (closeBtn) closeBtn.addEventListener('click', closeDetailsModal);

        const singleItemType = itemType.endsWith('s') && itemType !== 'ganado' ? itemType.slice(0, -1) : itemType;

        const dispatchForm = detailsContent.querySelector('#dispatch-form');
        if (dispatchForm) dispatchForm.addEventListener('submit', (e) => handleDispatchSubmit(e, singleItemType));

        const addStockForm = detailsContent.querySelector('#add-stock-form');
        if (addStockForm) addStockForm.addEventListener('submit', (e) => handleAddStockSubmit(e, singleItemType));

        const updateMantenimientoForm = detailsContent.querySelector('#update-mantenimiento-form');
        if (updateMantenimientoForm) updateMantenimientoForm.addEventListener('submit', handleUpdateMantenimiento);

        const updatePotreroForm = detailsContent.querySelector('#update-potrero-form');
        if (updatePotreroForm) updatePotreroForm.addEventListener('submit', handleUpdatePotrero);
        
        const updateProductoForm = detailsContent.querySelector('#update-producto-form');
        if (updateProductoForm) updateProductoForm.addEventListener('submit', handleUpdateProducto);

        const createCompradorForm = detailsContent.querySelector('#create-comprador-form');
        if (createCompradorForm) createCompradorForm.addEventListener('submit', handleCreateComprador);

        const verCompradorBtn = detailsContent.querySelector('#ver-comprador-btn');
        if (verCompradorBtn) {
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
        
        const crearVacunaBtn = detailsContent.querySelector('#crear-vacuna-btn');
        if (crearVacunaBtn) {
            crearVacunaBtn.addEventListener('click', () => {
                const crearVacunaModal = document.getElementById('crear-vacuna-modal');
                if (crearVacunaModal) {
                    setupCreateVacunaModal();
                    crearVacunaModal.style.display = 'block';
                }
            });
        }

        const addTagForm = detailsContent.querySelector('#add-tag-form');
        if (addTagForm) addTagForm.addEventListener('submit', (e) => handleTagManagement(e, singleItemType));
        detailsContent.querySelectorAll('.remove-tag-btn').forEach(btn => btn.addEventListener('click', (e) => handleTagManagement(e, singleItemType, 'remove')));
        const createTagForm = detailsContent.querySelector('#create-tag-form');
        if(createTagForm) createTagForm.addEventListener('submit', (e) => handleCreateTag(e, singleItemType));
        const createSubtagForm = detailsContent.querySelector('#create-subtag-form');
        if(createSubtagForm) createSubtagForm.addEventListener('submit', (e) => handleCreateTag(e, singleItemType));
        const assignCategoryForm = detailsContent.querySelector('#assign-category-form');
        if(assignCategoryForm) assignCategoryForm.addEventListener('submit', (e) => handleAssignCategory(e, singleItemType));
        const createCategoryForm = detailsContent.querySelector('#create-category-form');
        if(createCategoryForm) createCategoryForm.addEventListener('submit', (e) => handleCreateCategory(e, singleItemType));
        const addSubtagForm = detailsContent.querySelector('#add-subtag-form');
        if(addSubtagForm) addSubtagForm.addEventListener('submit', (e) => handleTagManagement(e, singleItemType));

        const addSubtagParentSelect = detailsContent.querySelector('#add-subtag-parent-select');
        if (addSubtagParentSelect) {
            addSubtagParentSelect.addEventListener('change', async (e) => {
                const parentId = e.target.value;
                const subtagSelect = detailsContent.querySelector('#add-subtag-select');
                if (!subtagSelect) return;
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

        // Ganado-specific listeners
        const updateGanadoForm = detailsContent.querySelector('#update-ganado-form');
        if (updateGanadoForm) {
            updateGanadoForm.addEventListener('submit', handleUpdateGanado);
            
            const estadoSelect = detailsContent.querySelector('#ganado-estado');
            const peñeSelect = detailsContent.querySelector('#ganado-peñe');

            const toggleGanadoFields = () => {
                const estadoValue = estadoSelect.value;
                const peñeValue = peñeSelect.value;

                const fallecidoFields = detailsContent.querySelector('#fallecido-fields');
                const vendidoFields = detailsContent.querySelector('#vendido-fields');
                const peñeFields = detailsContent.querySelector('#peñe-fields');

                if (fallecidoFields) fallecidoFields.style.display = estadoValue === 'FALLECIDO' ? 'block' : 'none';
                if (vendidoFields) vendidoFields.style.display = estadoValue === 'VENDIDO' ? 'block' : 'none';
                if (peñeFields) peñeFields.style.display = ['NATURAL', 'INSEMINACION', 'ARTIFICIAL'].includes(peñeValue) ? 'block' : 'none';
            };

            if (estadoSelect) estadoSelect.addEventListener('change', toggleGanadoFields);
            if (peñeSelect) peñeSelect.addEventListener('change', toggleGanadoFields);

            // Initial call to set state
            toggleGanadoFields();
        }

        detailsContent.querySelectorAll('.view-note-btn').forEach(btn => btn.addEventListener('click', handleViewNote));
        
        const registrarVacunacionForm = detailsContent.querySelector('#registrar-vacunacion-form');
        if(registrarVacunacionForm) registrarVacunacionForm.addEventListener('submit', handleRegistrarVacunacion);
        
        detailsContent.querySelectorAll('.view-vacuna-btn').forEach(btn => btn.addEventListener('click', handleViewVacuna));
        detailsContent.querySelectorAll('.edit-vacunacion-btn').forEach(btn => btn.addEventListener('click', (event) => handleEditVacunacion(event, data)));
        detailsContent.querySelectorAll('.delete-vacunacion-btn').forEach(btn => btn.addEventListener('click', (event) => handleDeleteVacunacion(event, data)));
        
        const vacunaSelect = detailsContent.querySelector('#vacuna-select');
        if (vacunaSelect) {
            vacunaSelect.addEventListener('change', handleVacunaSelectChange);
        }

        const registrarMedicamentoForm = detailsContent.querySelector('#registrar-medicamento-form');
        if(registrarMedicamentoForm) registrarMedicamentoForm.addEventListener('submit', (event) => handleRegistrarMedicamento(event, data));
        
        detailsContent.querySelectorAll('.view-medicamento-btn').forEach(btn => btn.addEventListener('click', (event) => handleViewMedicamento(event)));
        detailsContent.querySelectorAll('.edit-medicamento-btn').forEach(btn => btn.addEventListener('click', (event) => handleEditMedicamento(event, data)));
        detailsContent.querySelectorAll('.delete-medicamento-btn').forEach(btn => btn.addEventListener('click', (event) => handleDeleteMedicamento(event, data)));
        
        detailsContent.querySelectorAll('.info-btn').forEach(button => {
            button.addEventListener('click', async () => {
                const type = button.dataset.type;
                const id = button.dataset.id;
                const index = button.dataset.index;
                if (type === 'proveedor' && data.proveedores) renderInfoModal('Proveedor', data.proveedores[index]);
                if (type === 'ubicacion' && data.ubicaciones) renderInfoModal('Ubicación', data.ubicaciones[index]);
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
        const csrfTokenElement = document.querySelector('input[name=csrfmiddlewaretoken]');
        if (!csrfTokenElement) {
            console.error('CSRF token not found!');
            alert('Error de seguridad. Recargue la página.');
            return;
        }
        const csrfToken = csrfTokenElement.value;

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
                    const detailsResponse = await fetch(`/${singleItemType}/detalles/${itemId}/`);
                    if (!detailsResponse.ok) throw new Error('Error al recargar los datos del item.');
                    const updatedDetails = await detailsResponse.json();
                    const pluralItemType = singleItemType === 'ganado' ? 'ganado' : singleItemType + 's';
                    renderDetailsModal(updatedDetails, pluralItemType);
                } else {
                    closeDetailsModal();
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

    async function handleCreateVacuna(event) {
        event.preventDefault();
        const form = event.target;
        const getMultiSelectValues = (id) => Array.from(form.querySelector(id).selectedOptions).map(option => option.value);

        const body = {
            nombre: form.querySelector('#vacuna-nombre').value,
            tipo: form.querySelector('#vacuna-tipo').value,
            cantidad: form.querySelector('#vacuna-cantidad').value,
            unidad_medida: form.querySelector('#vacuna-unidad').value,
            fecha_compra: form.querySelector('#vacuna-fecha-compra').value,
            fecha_vencimiento: form.querySelector('#vacuna-fecha-vencimiento').value,
            proveedores: getMultiSelectValues('#vacuna-proveedores'),
            ubicaciones: getMultiSelectValues('#vacuna-ubicaciones'),
            etiquetas: getMultiSelectValues('#vacuna-etiquetas'),
            descripcion: form.querySelector('#vacuna-descripcion').value,
            dosis_crecimiento: form.querySelector('#vacuna-dosis-crecimiento').value,
            dosis_edad: form.querySelector('#vacuna-dosis-edad').value,
            dosis_peso: form.querySelector('#vacuna-dosis-peso').value,
            disponible: form.querySelector('#vacuna-disponible').checked
        };
        
        await handleApiRequest('/vacuna/crear/', body);
        form.reset();
    }
    
    async function handleRegistrarVacunacion(event) {
        event.preventDefault();
        const form = event.target;
        const body = {
            ganado_id: form.dataset.id,
            vacuna_id: form.querySelector('#vacuna-select').value,
            fecha_aplicacion: form.querySelector('#fecha-aplicacion-vacuna').value,
            fecha_proxima_dosis: form.querySelector('#fecha-proxima-vacuna').value,
            notas: form.querySelector('#vacunacion-notas').value,
        };
        handleApiRequest('/ganado/registrar_vacunacion/', body, form.dataset.id, 'ganado');
    }

    function handleViewNote(event) {
        const notas = event.target.dataset.notas;
        infoContent.innerHTML = `<div class="modal-header"><h2>Nota</h2><span class="close-btn" id="info-close-btn">&times;</span></div><hr class="separator"><div class="modal-body"><p>${notas}</p></div>`;
        infoModal.style.display = 'block';
        infoContent.querySelector('#info-close-btn').addEventListener('click', closeInfoModal);
    }

    function handleEditVacunacion(event, ganadoData) {
        const registroId = event.target.dataset.id;
        const registro = ganadoData.historial_vacunacion.find(r => r.id == registroId);
        if (!registro) return alert('No se encontró el registro de vacunación.');

        const fechaAplicacionISO = registro.fecha_aplicacion.split('/').reverse().join('-');
        let fechaProximaDosisISO = '';
        if (registro.fecha_proxima_dosis && registro.fecha_proxima_dosis !== 'N/A') {
            fechaProximaDosisISO = registro.fecha_proxima_dosis.split('/').reverse().join('-');
        }

        const nuevaFechaAplicacion = prompt("Editar Fecha de Aplicación (YYYY-MM-DD):", fechaAplicacionISO);
        if (nuevaFechaAplicacion === null) return;
        const nuevaFechaProxima = prompt("Editar Próxima Dosis (YYYY-MM-DD, opcional):", fechaProximaDosisISO);
        if (nuevaFechaProxima === null) return;
        const nuevasNotas = prompt("Editar Notas:", registro.notas === 'No hay notas.' ? '' : registro.notas);
        if (nuevasNotas === null) return;
        
        const body = {
            registro_id: registroId,
            fecha_aplicacion: nuevaFechaAplicacion,
            fecha_proxima_dosis: nuevaFechaProxima || null,
            notas: nuevasNotas,
        };
        handleApiRequest('/ganado/editar_vacunacion/', body, ganadoData.id, 'ganado');
    }

    async function handleViewVacuna(event) {
        const vacunaId = event.target.dataset.id;
        try {
            const response = await fetch(`/vacuna/detalles/${vacunaId}/`);
            if (!response.ok) throw new Error('No se pudo cargar la información de la vacuna.');
            const data = await response.json();
            const formatList = (items) => items.length > 0 ? `<ul class="info-list">${items.map(item => `<li class="info-list-item">${item.nombre}</li>`).join('')}</ul>` : '<p>N/A</p>';
            let contentHtml = `
                <div class="details-grid">
                    <div class="details-left-column">
                        ${data.imagen_url ? `<img src="${data.imagen_url}" alt="${data.nombre}" class="details-img">` : '<div class="item-card-img-placeholder">Sin imagen</div>'}
                        <div class="details-section"><h4>Información Principal</h4><p><strong>Nombre:</strong> ${data.nombre}</p><p><strong>Tipo:</strong> ${data.tipo || 'N/A'}</p><p><strong>Cantidad Restante:</strong> ${data.cantidad} ${data.unidad_medida}</p><p><strong>Precio:</strong> $${parseFloat(data.precio).toLocaleString('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p><p><strong>Disponible:</strong> <span class="status-${data.disponible ? 'disponible' : 'agotado'}">${data.disponible ? 'Sí' : 'No'}</span></p></div>
                        <div class="details-section"><h4>Dosis Recomendadas</h4><p><strong>Crecimiento:</strong> ${data.dosis_crecimiento || 'N/A'}</p><p><strong>Edad:</strong> ${data.dosis_edad || 'N/A'}</p><p><strong>Peso:</strong> ${data.dosis_peso || 'N/A'}</p></div>
                    </div>
                    <div class="details-right-column">
                        <div class="details-section"><h4>Información Adicional</h4><p><strong>Fechas:</strong> Compra: ${data.fecha_compra || 'N/A'} | Vence: ${data.fecha_vencimiento || 'N/A'}</p><p><strong>Descripción:</strong></p><p>${data.descripcion || 'No hay descripción.'}</p></div>
                        <div class="details-section"><h4>Proveedores</h4>${formatList(data.proveedores)}</div>
                        <div class="details-section"><h4>Ubicaciones</h4>${formatList(data.ubicaciones)}</div>
                        <div class="details-section"><h4>Etiquetas</h4>${formatList(data.etiquetas)}</div>
                    </div>
                </div>`;
            infoContent.innerHTML = `<div class="modal-header"><h2>Detalles de la Vacuna</h2><span class="close-btn" id="info-close-btn">&times;</span></div><hr class="separator"><div class="modal-body">${contentHtml}</div>`;
            infoModal.style.display = 'block';
            infoContent.querySelector('#info-close-btn').addEventListener('click', closeInfoModal);
        } catch (error) {
            alert(error.message);
        }
    }
    
    async function handleViewMedicamento(event) {
        const medicamentoId = event.target.dataset.id;
        try {
            const response = await fetch(`/medicamento/detalles/${medicamentoId}/`);
            if (!response.ok) throw new Error('No se pudo cargar la información del medicamento.');
            const data = await response.json();
            let contentHtml = `
                <div class="details-grid">
                    <div class="details-left-column">
                        ${data.imagen_url ? `<img src="${data.imagen_url}" alt="${data.nombre}" class="details-img">` : '<div class="item-card-img-placeholder">Sin imagen</div>'}
                        <div class="details-section"><h4>Información</h4><p><strong>Categoría:</strong> ${data.categoria ? data.categoria.nombre : 'N/A'}</p><p><strong>Descripción:</strong> ${data.descripcion}</p><p><strong>Fechas:</strong> Compra: ${data.fecha_compra} | Vence: ${data.fecha_vencimiento}</p></div>
                    </div>
                    <div class="details-right-column">
                        <div class="details-section"><h4>Inventario</h4><p><strong>Restante:</strong> ${data.cantidad_restante} ${data.unidad_medida}</p><p><strong>Precio:</strong> $${data.precio}</p></div>
                    </div>
                </div>`;
            infoContent.innerHTML = `<div class="modal-header"><h2>Detalles del Medicamento</h2><span class="close-btn" id="info-close-btn">&times;</span></div><hr class="separator"><div class="modal-body">${contentHtml}</div>`;
            infoModal.style.display = 'block';
            infoContent.querySelector('#info-close-btn').addEventListener('click', closeInfoModal);
        } catch (error) {
            alert(error.message);
        }
    }

    function handleUpdateGanado(event) {
        event.preventDefault();
        const form = event.target;
        const body = {
            ganado_id: form.dataset.id,
            peso_kg: form.querySelector('#ganado-peso').value,
            estado: form.querySelector('#ganado-estado').value,
            estado_salud: form.querySelector('#ganado-estado-salud').value,
            peñe: form.querySelector('#ganado-peñe').value,
            descripcion: form.querySelector('#ganado-descripcion').value,
            crecimiento: form.querySelector('#ganado-crecimiento').value,
            fecha_fallecimiento: form.querySelector('#ganado-fecha-fallecimiento').value,
            fecha_venta: form.querySelector('#ganado-fecha-venta').value,
            valor_venta: form.querySelector('#ganado-valor-venta').value,
            comprador: form.querySelector('#ganado-comprador').value,
            comprador_telefono: form.querySelector('#ganado-comprador-telefono').value,
            fecha_peñe: form.querySelector('#ganado-fecha-peñe').value,
            descripcion_peñe: form.querySelector('#ganado-descripcion-peñe').value,
        };
        handleApiRequest('/ganado/actualizar/', body, form.dataset.id, 'ganado');
    }

    function handleDeleteVacunacion(event, ganadoData) {
        const registroId = event.target.dataset.id;
        if (confirm('¿Está seguro de que desea eliminar este registro de vacunación?')) {
            const body = { registro_id: registroId };
            handleApiRequest('/ganado/eliminar_vacunacion/', body, ganadoData.id, 'ganado');
        }
    }

    async function handleRegistrarMedicamento(event, ganadoData) {
        event.preventDefault();
        const form = event.target;
        const body = {
            ganado_id: form.dataset.id,
            medicamento_id: form.querySelector('#medicamento-select').value,
            fecha_aplicacion: form.querySelector('#fecha-aplicacion-medicamento').value,
            notas: form.querySelector('#medicamento-notas').value,
        };
        handleApiRequest('/ganado/registrar_medicamento/', body, form.dataset.id, 'ganado');
    }

    function handleEditMedicamento(event, ganadoData) {
        const registroId = event.target.dataset.id;
        const registro = ganadoData.historial_medicamentos.find(r => r.id == registroId);
        if (!registro) return alert('No se encontró el registro del medicamento.');

        const fechaAplicacionISO = registro.fecha_aplicacion.split('/').reverse().join('-');
        const nuevaFechaAplicacion = prompt("Editar Fecha de Aplicación (YYYY-MM-DD):", fechaAplicacionISO);
        if (nuevaFechaAplicacion === null) return;
        const nuevasNotas = prompt("Editar Notas:", registro.notas === 'No hay notas.' ? '' : registro.notas);
        if (nuevasNotas === null) return;
        
        const body = {
            registro_id: registroId,
            fecha_aplicacion: nuevaFechaAplicacion,
            notas: nuevasNotas,
        };
        handleApiRequest('/ganado/editar_medicamento/', body, ganadoData.id, 'ganado');
    }

    function handleDeleteMedicamento(event, ganadoData) {
        const registroId = event.target.dataset.id;
        if (confirm('¿Está seguro de que desea eliminar este registro de medicamento?')) {
            const body = { registro_id: registroId };
            handleApiRequest('/ganado/eliminar_medicamento/', body, ganadoData.id, 'ganado');
        }
    }

    async function handleVacunaSelectChange(event) {
        const vacunaId = event.target.value;
        const previewContainer = document.getElementById('vacuna-details-preview');
        if (!vacunaId) {
            previewContainer.innerHTML = '';
            previewContainer.style.display = 'none';
            return;
        }
        try {
            const response = await fetch(`/vacuna/detalles/${vacunaId}/`);
            if (!response.ok) throw new Error('No se pudo cargar la información de la vacuna.');
            const data = await response.json();
            previewContainer.innerHTML = `
                <p><strong>Tipo:</strong> ${data.tipo || 'N/A'}</p>
                <p><strong>Cantidad Restante:</strong> ${data.cantidad} ${data.unidad_medida}</p>
                <p><strong>Dosis (Crecimiento):</strong> ${data.dosis_crecimiento || 'N/A'}</p>
                <p><strong>Dosis (Edad):</strong> ${data.dosis_edad || 'N/A'}</p>
                <p><strong>Dosis (Peso):</strong> ${data.dosis_peso || 'N/A'}</p>
                <p><strong>Descripción:</strong> ${data.descripcion || 'N/A'}</p>
            `;
            previewContainer.style.display = 'block';
        } catch (error) {
            previewContainer.innerHTML = `<p class="error-text">${error.message}</p>`;
            previewContainer.style.display = 'block';
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