// Apuntando al backend local de Python (Flask)
const API_URL = 'http://localhost:5000/api';
let charts = {}; 

function mostrarSeccion(id) {
    document.querySelectorAll('.seccion-app').forEach(sec => sec.classList.add('hidden'));
    document.getElementById(`sec-${id}`).classList.remove('hidden');
    if(id === 'turnos') cargarTurnos();
    if(id === 'caja') cargarCaja();
    if(id === 'estadisticas') cargarEstadisticas();
    if(id === 'catalogo') cargarCatalogo();
}

async function guardarDato(endpoint, data) {
    try {
        const res = await fetch(`${API_URL}/${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error('Error al guardar');
        return await res.json();
    } catch (error) {
        console.error("Error en guardarDato:", error);
    }
}

async function borrarDato(endpoint, id, recargarCallback) {
    await fetch(`${API_URL}/${endpoint}/${id}`, { method: 'DELETE' });
    recargarCallback();
}

async function borrarTodos(endpoint) {
    if(confirm(`¿Estás seguro de borrar todos los registros de ${endpoint}?`)) {
        await fetch(`${API_URL}/${endpoint}`, { method: 'DELETE' });
        if(endpoint === 'turnos') cargarTurnos();
        if(endpoint === 'caja') cargarCaja();
        if(endpoint === 'estadisticas') cargarEstadisticas();
        if(endpoint === 'cortes') cargarCatalogo();
    }
}

async function editarTurno(id, clienteActual) {
    const nuevoCliente = prompt("Editar nombre del cliente:", clienteActual);
    if (nuevoCliente && nuevoCliente !== clienteActual) {
        await fetch(`${API_URL}/turnos/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ cliente: nuevoCliente })
        });
        cargarTurnos();
    }
}

// TURNOS
// Busca esta parte en tu app.js y déjala así:
document.getElementById('form-turno').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const nuevoTurno = {
        cliente: document.getElementById('t-cliente').value,
        fecha: document.getElementById('t-fecha').value,
        hora: document.getElementById('t-hora').value,
        servicio: document.getElementById('t-servicio').value
    };

    // 1. Enviamos el dato
    await guardarDato('turnos', nuevoTurno);
    
    // 2. Limpiamos el formulario
    e.target.reset();
    
    // 3. ¡IMPORTANTE! Forzamos la recarga de la tabla
    setTimeout(() => {
        cargarTurnos();
    }, 100); // Damos 100ms de margen al servidor
});

async function cargarTurnos() {
    try {
        const res = await fetch('http://localhost:5000/api/turnos');
        const turnos = await res.json();
        
        console.log("Datos cargados desde el servidor:", turnos); // Mira esto en F12

        const lista = document.getElementById('lista-turnos');
        lista.innerHTML = ''; 

        if (turnos.length === 0) {
            lista.innerHTML = '<tr><td colspan="5" class="py-4 text-gray-500">No hay turnos registrados</td></tr>';
            return;
        }

        turnos.forEach(t => {
            // Usamos t.id porque es lo que devuelve SQLite
            lista.innerHTML += `
                <tr class="border-b hover:bg-gray-50">
                    <td class="py-2 px-4">${t.cliente}</td>
                    <td class="py-2 px-4">${t.fecha}</td>
                    <td class="py-2 px-4">${t.hora}</td>
                    <td class="py-2 px-4">${t.servicio}</td>
                    <td class="py-2 px-4">
                        <button onclick="borrarDato('turnos', ${t.id}, cargarTurnos)" class="text-red-500 hover:text-red-700 font-bold">Eliminar</button>
                    </td>
                </tr>`;
        });
    } catch (error) {
        console.error("Error al conectar con la API:", error);
    }
}

// CAJA
document.getElementById('form-caja').addEventListener('submit', async (e) => {
    e.preventDefault();
    await guardarDato('caja', {
        tipo: document.getElementById('c-tipo').value,
        monto: parseFloat(document.getElementById('c-monto').value),
        descripcion: document.getElementById('c-desc').value
    });
    e.target.reset();
    cargarCaja();
});

async function cargarCaja() {
    const res = await fetch(`${API_URL}/caja`);
    const registros = await res.json();
    const lista = document.getElementById('lista-caja');
    lista.innerHTML = '';
    let balance = 0;

    registros.forEach(r => {
        const isIngreso = r.tipo === 'Ingreso';
        balance += isIngreso ? r.monto : -r.monto;
        lista.innerHTML += `
            <li class="flex justify-between items-center bg-white p-3 shadow rounded border-l-4 ${isIngreso ? 'border-green-500' : 'border-red-500'}">
                <div>
                    <span class="font-bold">${r.descripcion}</span>
                    <span class="text-sm text-gray-500 ml-2">(${r.tipo})</span>
                </div>
                <div class="flex items-center gap-4">
                    <span class="font-bold ${isIngreso ? 'text-green-600' : 'text-red-600'}">$${r.monto}</span>
                    <button onclick="borrarDato('caja', '${r._id}', cargarCaja)" class="text-red-500 hover:text-red-700">✖</button>
                </div>
            </li>`;
    });
    document.getElementById('balance-total').innerText = `Balance Total: $${balance}`;
}

// ESTADÍSTICAS
document.getElementById('form-est').addEventListener('submit', async (e) => {
    e.preventDefault();
    await guardarDato('estadisticas', {
        categoria: document.getElementById('e-cat').value,
        nombre: document.getElementById('e-nombre').value,
        valor: parseInt(document.getElementById('e-valor').value)
    });
    e.target.reset();
    cargarEstadisticas();
});

async function cargarEstadisticas() {
    const res = await fetch(`${API_URL}/estadisticas`);
    const datos = await res.json();
    const lista = document.getElementById('lista-estadisticas');
    lista.innerHTML = '';
    
    const categorias = { 'Servicios': { labels: [], data: [] }, 'Clientes': { labels: [], data: [] }, 'Horarios': { labels: [], data: [] } };

    datos.forEach(d => {
        if(categorias[d.categoria]){
            categorias[d.categoria].labels.push(d.nombre);
            categorias[d.categoria].data.push(d.valor);
        }
        lista.innerHTML += `
            <li class="bg-gray-50 p-2 border rounded flex justify-between">
                <span>${d.nombre} (${d.categoria}): <b class="text-purple-600">${d.valor}</b></span>
                <button onclick="borrarDato('estadisticas', '${d._id}', cargarEstadisticas)" class="text-red-500">✖</button>
            </li>`;
    });

    dibujarGrafico('chart-servicios', 'Servicios más Solicitados', categorias['Servicios']);
    dibujarGrafico('chart-clientes', 'Clientes Frecuentes', categorias['Clientes']);
    dibujarGrafico('chart-horarios', 'Horarios Pico', categorias['Horarios']);
}

function dibujarGrafico(canvasId, titulo, datosCat) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    if(charts[canvasId]) charts[canvasId].destroy(); 
    
    charts[canvasId] = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: datosCat.labels,
            datasets: [{
                data: datosCat.data,
                backgroundColor: ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899']
            }]
        },
        options: { plugins: { title: { display: true, text: titulo } } }
    });
}

// CATÁLOGO
document.getElementById('form-corte').addEventListener('submit', async (e) => {
    e.preventDefault();
    await guardarDato('cortes', {
        nombre: document.getElementById('cat-nombre').value,
        url_imagen: document.getElementById('cat-url').value
    });
    e.target.reset();
    cargarCatalogo();
});

async function cargarCatalogo() {
    const res = await fetch(`${API_URL}/cortes`);
    const cortes = await res.json();
    const grid = document.getElementById('grid-catalogo');
    grid.innerHTML = '';

    cortes.forEach(c => {
        grid.innerHTML += `
            <div class="bg-white rounded shadow overflow-hidden flex flex-col hover:shadow-lg transition">
                <img src="${c.url_imagen}" alt="${c.nombre}" class="w-full h-48 object-cover" onerror="this.src='https://via.placeholder.com/300x200?text=Error+de+Imagen'">
                <div class="p-4 flex justify-between items-center bg-gray-50">
                    <h4 class="font-bold capitalize">${c.nombre}</h4>
                    <button onclick="borrarDato('cortes', '${c._id}', cargarCatalogo)" class="text-red-500 hover:text-red-700">Borrar</button>
                </div>
            </div>`;
    });
}

// Init
mostrarSeccion('turnos');

// Al final del archivo app.js
window.onload = () => {
    mostrarSeccion('turnos'); // Esto ya llama a cargarTurnos() internamente
};