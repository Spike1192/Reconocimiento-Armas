const panel = document.getElementById("notificationPanel");
const btn = document.getElementById("btnNotifications");
const notificationBadge = document.getElementById("notificationBadge");
const notificationList = document.getElementById("notificationList");
let ultimaSeccion = null;
let notificaciones = []; // Array para almacenar notificaciones
let notificacionesNoLeidas = 0;

// Conectar a WebSocket para recibir notificaciones en tiempo real
let socket;
function initSocket() {
  // Esperar a que socket.io esté disponible
  if (typeof io === 'undefined') {
    console.log('Esperando a que socket.io se cargue...');
    setTimeout(initSocket, 100);
    return;
  }
  
  try {
    socket = io();
    
    socket.on('connect', () => {
      console.log('Conectado a WebSocket para notificaciones');
    });
    
    socket.on('weapon_detected', (data) => {
      console.log('Nueva detección recibida:', data);
      agregarNotificacion(data);
    });
    
    socket.on('disconnect', () => {
      console.log('Desconectado de WebSocket');
    });
    
    socket.on('connect_error', (error) => {
      console.error('Error de conexión WebSocket:', error);
    });
  } catch (error) {
    console.error('Error inicializando socket:', error);
  }
}

// Función para agregar notificación
function agregarNotificacion(data) {
  const fecha = new Date(data.timestamp);
  const fechaFormateada = fecha.toLocaleDateString('es-ES', { 
    day: '2-digit', 
    month: '2-digit', 
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
  
  const notificacion = {
    id: data.alerta_id || Date.now(),
    tipo: data.tipo_alerta || 'Detección de arma',
    fecha: fechaFormateada,
    timestamp: data.timestamp,
    alerta_id: data.alerta_id,
    camara: data.camara || 'CAMERA 01',
    leida: false
  };
  
  notificaciones.unshift(notificacion); // Agregar al inicio
  notificacionesNoLeidas++;
  
  // Actualizar badge
  actualizarBadge();
  
  // Actualizar lista si el panel está abierto
  if (!panel.classList.contains('translate-x-full')) {
    mostrarNotificaciones();
  }
  
  // Sonido de notificación (opcional)
  try {
    const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjGH0fPRgjMGHm7A7+OZUg4OUqTj8LZjHAY4kdfyzHksBSR3x/DdkEAKFF606euoVRQKRp/g8r5sIQYxh9Hz0YIzBh5uwO/jmVIODlKk4/C2YxwGOJHX8sx5LAUkd8fw3ZBAC');
    audio.volume = 0.3;
    audio.play().catch(() => {}); // Ignorar errores de autoplay
  } catch (e) {}
}

// Función para actualizar el badge de notificaciones
function actualizarBadge() {
  if (notificationBadge) {
    if (notificacionesNoLeidas > 0) {
      notificationBadge.classList.remove('hidden');
      notificationBadge.textContent = notificacionesNoLeidas > 9 ? '9+' : notificacionesNoLeidas;
    } else {
      notificationBadge.classList.add('hidden');
    }
  }
}

// Función para mostrar notificaciones en el panel
function mostrarNotificaciones() {
  if (!notificationList) return;
  
  const noNotifications = document.getElementById("noNotifications");
  
  if (notificaciones.length === 0) {
    notificationList.innerHTML = '<p class="text-white/70 text-center py-4" id="noNotifications">No hay notificaciones</p>';
    return;
  }
  
  if (noNotifications) noNotifications.remove();
  
  notificationList.innerHTML = notificaciones.map(notif => `
    <div class="flex items-center gap-4 bg-[#13244a] p-4 rounded-lg cursor-pointer hover:bg-[#1b3260] transition ${notif.leida ? 'opacity-70' : ''}" 
         data-alerta-id="${notif.alerta_id}" data-notif-id="${notif.id}">
      <div class="w-8 h-8 flex items-center justify-center ${notif.leida ? 'bg-black/40' : 'bg-red-500/80'} rounded-full">
        ${notif.leida ? '▶' : '⚠'}
      </div>
      <div class="flex-1">
        <p class="text-white text-sm font-semibold">${notif.tipo}</p>
        <p class="text-white/70 text-xs">${notif.fecha} - ${notif.camara}</p>
      </div>
    </div>
  `).join('');
  
  // Agregar event listeners a las notificaciones
  notificationList.querySelectorAll('[data-alerta-id]').forEach(item => {
    item.addEventListener('click', async () => {
      const alertaId = item.getAttribute('data-alerta-id');
      const notifId = parseInt(item.getAttribute('data-notif-id'));
      
      // Marcar como leída
      const notif = notificaciones.find(n => n.id === notifId);
      if (notif && !notif.leida) {
        notif.leida = true;
        notificacionesNoLeidas--;
        actualizarBadge();
      }
      
      // Cerrar panel
      panel.classList.add('translate-x-full');
      
      // Ir a eventos y mostrar detalle
      principal.style.display = "none";
      secEventos.style.display = "flex";
      await cargarAlertas();
      
      // Esperar un momento y luego mostrar el detalle
      setTimeout(async () => {
        if (alertaId) {
          await mostrarDetalleAlerta(parseInt(alertaId));
        }
      }, 500);
    });
  });
}

// Cargar notificaciones al iniciar
async function cargarNotificacionesIniciales() {
  try {
    const response = await fetch('/api/alertas');
    if (response.ok) {
      const alertas = await response.json();
      // Convertir alertas a notificaciones (últimas 10)
      notificaciones = alertas.slice(0, 10).map(alerta => {
        const fecha = new Date(alerta.fechaHora);
        return {
          id: alerta.idAlerta,
          tipo: alerta.tipoAlerta,
          fecha: fecha.toLocaleDateString('es-ES', { 
            day: '2-digit', 
            month: '2-digit', 
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
          }),
          timestamp: alerta.fechaHora,
          alerta_id: alerta.idAlerta,
          camara: alerta.camara,
          leida: false
        };
      });
      notificacionesNoLeidas = notificaciones.length;
      actualizarBadge();
    }
  } catch (error) {
    console.error('Error cargando notificaciones:', error);
  }
}

btn.addEventListener("click", () => {
  panel.classList.toggle("translate-x-full");
  if (!panel.classList.contains('translate-x-full')) {
    // Panel abierto, mostrar notificaciones
    mostrarNotificaciones();
    // Marcar todas como leídas al abrir
    notificaciones.forEach(n => n.leida = true);
    notificacionesNoLeidas = 0;
    actualizarBadge();
  }
});


const inicioSesion = document.getElementById("inicioSesion");
const principal = document.getElementById("principal");
const header = document.getElementById("header");
const login = document.getElementById("login");
const cerrarSesion = document.getElementById("cerrarSesion");
const perfil = document.getElementById("perfil");
const btnPerfil = document.getElementById("btnPerfil");
const btnAtras = document.getElementById("btnAtras");
const registro = document.getElementById("registro");
const btnRegistro = document.getElementById("btnRegistro");
const btnAtrasRegistro = document.getElementById("btnAtrasRegistro");
const btnAtrasEventos = document.getElementById("btnAtrasEventos");
const btnAtrasEvento = document.getElementById("btnAtrasEvento")
const btnAtrasVideo = document.getElementById("btnAtrasVideo");
const btnEventos = document.getElementById("btnEventos");
const crearCuenta = document.getElementById("crearCuenta");
const secEventos = document.getElementById("secEventos");

// Función para verificar sesión al cargar la página
async function verificarSesion() {
  try {
    const response = await fetch('/api/check_session');
    const data = await response.json();
    
    if (data.authenticated) {
      // Usuario ya autenticado, mostrar panel principal
      principal.style.display = "block";
      header.style.display = "block";
      login.style.display = "none";
      cargarPerfilUsuario();
      
      // Inicializar WebSocket y cargar notificaciones
      initSocket();
      await cargarNotificacionesIniciales();
    } else {
      // No autenticado, mostrar login
      principal.style.display = "none";
      header.style.display = "none";
      login.style.display = "flex";
    }
  } catch (error) {
    console.error('Error verificando sesión:', error);
    principal.style.display = "none";
    header.style.display = "none";
    login.style.display = "flex";
  }
}

// Función para cargar perfil del usuario
async function cargarPerfilUsuario() {
  try {
    const response = await fetch('/api/user/profile');
    if (response.ok) {
      const usuario = await response.json();
      actualizarPerfilUsuario(usuario);
      return usuario;
    }
  } catch (error) {
    console.error('Error cargando perfil:', error);
  }
}

// Función para actualizar la información del perfil en el HTML
function actualizarPerfilUsuario(usuario) {
  // Actualizar cada campo usando los IDs
  const perfilNombre = document.getElementById('perfilNombre');
  const perfilUsuario = document.getElementById('perfilUsuario');
  const perfilEmail = document.getElementById('perfilEmail');
  const perfilUbicacion = document.getElementById('perfilUbicacion');
  const perfilRol = document.getElementById('perfilRol');
  const perfilTelefono = document.getElementById('perfilTelefono');
  const perfilUltimoAcceso = document.getElementById('perfilUltimoAcceso');
  
  if (perfilNombre) perfilNombre.textContent = usuario.Nombre || 'No disponible';
  if (perfilUsuario) perfilUsuario.textContent = usuario.idUsuario || 'No disponible';
  if (perfilEmail) perfilEmail.textContent = usuario.Email || 'No disponible';
  if (perfilUbicacion) perfilUbicacion.textContent = usuario.UbicacionAsignada || 'No disponible';
  if (perfilRol) perfilRol.textContent = usuario.Rol || 'No disponible';
  if (perfilTelefono) perfilTelefono.textContent = usuario.TelefonoContacto || 'No disponible';
  
  // Actualizar último acceso
  if (perfilUltimoAcceso) {
    if (usuario.UltimoAcceso) {
      const fecha = new Date(usuario.UltimoAcceso);
      const fechaFormateada = fecha.toLocaleDateString('es-ES', { 
        day: '2-digit', 
        month: '2-digit', 
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
      perfilUltimoAcceso.textContent = `Último inicio de sesión: ${fechaFormateada}`;
    } else {
      perfilUltimoAcceso.textContent = 'Último inicio de sesión: No disponible';
    }
  }
}

// Cargar perfil cuando se abre la sección
btnPerfil.addEventListener("click", async () => {
  ultimaSeccion = obtenerSeccionVisible();
  ocultarTodasLasSecciones();
  principal.style.display = "none";
  header.style.display = "none";
  login.style.display = "none";
  video.style.display = "none";
  secEventos.style.display = "none";
  perfil.style.display = "flex";
  
  // Cargar datos del usuario
  await cargarPerfilUsuario();
});

// Función para realizar el login
async function realizarLogin() {
  const form = inicioSesion.closest('form');
  const inputs = form.querySelectorAll('input');
  const usuarioInput = inputs[0]; // Campo usuario
  const claveInput = inputs[1]; // Campo contraseña
  
  const usuario = usuarioInput.value.trim();
  const clave = claveInput.value.trim();
  
  if (!usuario || !clave) {
    alert('Por favor ingrese usuario y contraseña');
    return;
  }
  
  try {
    const response = await fetch('/api/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        usuario: usuario,
        clave: clave
      })
    });
    
    const data = await response.json();
    
    if (response.ok && data.success) {
      // Login exitoso
      principal.style.display = "block";
      header.style.display = "block";
      login.style.display = "none";
      cargarPerfilUsuario();
      
      // Inicializar WebSocket y cargar notificaciones
      initSocket();
      await cargarNotificacionesIniciales();
      
      // Limpiar formulario
      usuarioInput.value = '';
      claveInput.value = '';
    } else {
      // Error en login
      alert(data.error || 'Error al iniciar sesión');
    }
  } catch (error) {
    console.error('Error en login:', error);
    alert('Error de conexión. Por favor intente nuevamente.');
  }
}

// Manejar login con botón
inicioSesion.addEventListener("click", realizarLogin);

// Manejar login con Enter en el formulario
const loginForm = inicioSesion.closest('form');
if (loginForm) {
  loginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    realizarLogin();
  });
  
  // También permitir Enter en los campos de input
  const inputs = loginForm.querySelectorAll('input');
  inputs.forEach(input => {
    input.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        realizarLogin();
      }
    });
  });
}

cerrarSesion.addEventListener("click", async () => {
  try {
    const response = await fetch('/api/logout', {
      method: 'POST'
    });
    
    if (response.ok) {
      principal.style.display = "none";
      header.style.display = "none";
      login.style.display = "flex";
    }
  } catch (error) {
    console.error('Error cerrando sesión:', error);
    // Aún así, cerrar la sesión localmente
    principal.style.display = "none";
    header.style.display = "none";
    login.style.display = "flex";
  }
});

// El event listener de btnPerfil se maneja más abajo con la función cargarPerfilUsuario

btnEventos.addEventListener("click", () => {
  principal.style.display = "none"
  secEventos.style.display = "flex"

});

btnAtrasEventos.addEventListener("click", () => {
  principal.style.display = "block"
  secEventos.style.display = "none"

});



btnAtras.addEventListener("click", () => {
  ocultarTodasLasSecciones();

  if (ultimaSeccion) {
    if (ultimaSeccion === principal) {
      principal.style.display = "block";
    } else {
      ultimaSeccion.style.display = "flex";
    }
  }
  header.style.display = "block";
});


// Ocultar funcionalidad de registro - sistema sin registro
btnRegistro.addEventListener("click", () => {
  alert('El registro de nuevos usuarios está deshabilitado. Contacte al administrador.');
  // perfil.style.display = "none"
  // registro.style.display = "flex"
});

btnAtrasRegistro.addEventListener("click", () => {
  registro.style.display = "none"
  perfil.style.display = "flex"

});

// Deshabilitar creación de cuenta - sistema sin registro
if (crearCuenta) {
  crearCuenta.addEventListener("click", () => {
    alert('El registro de nuevos usuarios está deshabilitado. Contacte al administrador.');
  });
}

// Verificar sesión al cargar la página
verificarSesion();



btnAtrasVideo.addEventListener("click", () => {
  principal.style.display = "block"
  video.style.display = "none"
  // Limpiar intervalo de actualización de hora
  if (window.horaInterval) {
    clearInterval(window.horaInterval);
    window.horaInterval = null;
  }
});

const infoEvento = document.getElementById("infoEvento")

// Función para cargar alertas desde la API
async function cargarAlertas() {
  try {
    const response = await fetch('/api/alertas');
    if (response.ok) {
      const alertas = await response.json();
      mostrarAlertas(alertas);
      return alertas;
    } else {
      console.error('Error cargando alertas:', response.statusText);
      return [];
    }
  } catch (error) {
    console.error('Error cargando alertas:', error);
    return [];
  }
}

// Función para formatear fecha
function formatearFecha(fechaISO) {
  const fecha = new Date(fechaISO);
  const dia = String(fecha.getDate()).padStart(2, '0');
  const mes = String(fecha.getMonth() + 1).padStart(2, '0');
  const año = fecha.getFullYear();
  const hora = String(fecha.getHours()).padStart(2, '0');
  const minuto = String(fecha.getMinutes()).padStart(2, '0');
  return {
    fecha: `${dia}/${mes}/${año}`,
    hora: `${hora}:${minuto}`
  };
}

// Función para mostrar alertas en la lista
function mostrarAlertas(alertas) {
  const listaEventos = document.getElementById("listaEventos");
  if (!listaEventos) return;
  
  listaEventos.innerHTML = ''; // Limpiar lista anterior
  
  if (alertas.length === 0) {
    listaEventos.innerHTML = '<p class="text-white/70 text-center py-8">No hay eventos registrados</p>';
    return;
  }
  
  alertas.forEach((alerta, index) => {
    const fechaFormateada = formatearFecha(alerta.fechaHora);
    const imagenUrl = alerta.image_path ? `/captures/${alerta.image_path.split('/').pop()}` : '';
    
    const html = `
      <div class="evento cursor-pointer w-full h-[200px] rounded-lg flex items-center mb-4 bg-[#0A1330]" data-index="${index}" data-alerta-id="${alerta.idAlerta}">

        <div class="flex justify-center w-[35%] h-[80%]">
          <div class="videos w-[90%] h-full relative bg-[#1a2332] rounded-lg overflow-hidden">
            ${imagenUrl ? 
              `<img src="${imagenUrl}" alt="Alerta ${alerta.idAlerta}" class="w-full h-full object-cover">` :
              `<div class="w-full h-full flex items-center justify-center bg-gradient-to-br from-[#1a3a2e] to-[#0f2419]">
                <svg class="w-16 h-16 opacity-20" fill="none" stroke="#00ff00" viewBox="0 0 24 24" stroke-width="1.5">
                  <path d="M23 7l-7 5 7 5V7z"></path>
                  <rect x="1" y="5" width="15" height="14" rx="2"></rect>
                </svg>
              </div>`
            }
            
            <span class="absolute top-2 left-2 bg-black/70 text-green-400 text-[11px] px-2 py-1 rounded font-mono">
              ${fechaFormateada.hora}
            </span>

            <span class="absolute bottom-2 right-2 bg-black/70 text-white text-[10px] px-2 py-1 rounded font-mono font-semibold">
              ${alerta.camara}
            </span>
          </div>
        </div>

        <div class="pl-12">
          <h1 class="text-[25px] font-semibold mb-4 tracking-tight">
            ${alerta.tipoAlerta}
          </h1>
          <p class="text-white/80 text-[13px] font-light mb-5">
            ${fechaFormateada.fecha} -- ${fechaFormateada.hora}
          </p>
        </div>

      </div>
    `;

    listaEventos.innerHTML += html;
  });
  
  // Agregar event listeners a los eventos
  setTimeout(() => {
    document.querySelectorAll(".evento").forEach(evento => {
      evento.addEventListener("click", async () => {
        const alertaId = evento.getAttribute("data-alerta-id");
        await mostrarDetalleAlerta(alertaId);
      });
    });
  }, 100);
}

// Función para mostrar detalle de alerta
let alertaActualId = null;

async function mostrarDetalleAlerta(alertaId) {
  alertaActualId = alertaId;
  try {
    const response = await fetch(`/api/alerta/${alertaId}`);
    if (response.ok) {
      const alerta = await response.json();
      const fechaFormateada = formatearFecha(alerta.fechaHora);
      
      // Rellenar información
      document.getElementById("tituloEvento").innerText = alerta.tipoAlerta;
      document.getElementById("fechaYMinuto").innerText = `${fechaFormateada.fecha} -- ${fechaFormateada.hora}`;
      
      const motivoTexto = document.getElementById("motivoTexto");
      const solucionTexto = document.getElementById("solucionTexto");
      motivoTexto.textContent = alerta.motivo || 'No especificado';
      solucionTexto.textContent = alerta.solucion || 'Pendiente de revisión';
      
      // Hacer los campos editables
      motivoTexto.contentEditable = true;
      solucionTexto.contentEditable = true;
      motivoTexto.style.border = "1px solid rgba(255,255,255,0.3)";
      motivoTexto.style.padding = "8px";
      motivoTexto.style.borderRadius = "4px";
      motivoTexto.style.minHeight = "60px";
      solucionTexto.style.border = "1px solid rgba(255,255,255,0.3)";
      solucionTexto.style.padding = "8px";
      solucionTexto.style.borderRadius = "4px";
      solucionTexto.style.minHeight = "60px";
      
      // Mostrar imagen si existe
      const videoContainer = document.querySelector("#infoEvento .videos");
      if (videoContainer && alerta.image_path) {
        const imagenUrl = `/captures/${alerta.image_path.split('/').pop()}`;
        videoContainer.innerHTML = `
          <img src="${imagenUrl}" alt="Alerta ${alerta.idAlerta}" class="w-full h-full object-cover">
          <span class="absolute top-2 left-2 bg-black/70 text-green-400 text-[11px] px-2 py-1 rounded font-mono">
            ${fechaFormateada.hora}
          </span>
          <span class="absolute bottom-2 right-2 bg-black/70 text-white text-[10px] px-2 py-1 rounded font-mono font-semibold">
            ${alerta.camara}
          </span>
        `;
      }
      
      // Mostrar sección
      infoEvento.style.display = "flex";
      secEventos.style.display = "none";
    }
  } catch (error) {
    console.error('Error cargando detalle de alerta:', error);
  }
}

// Cargar alertas cuando se muestra la sección de eventos
btnEventos.addEventListener("click", async () => {
  principal.style.display = "none";
  secEventos.style.display = "flex";
  await cargarAlertas();
});

const listaCamaras = [
  { hora: "03:15:20", camara: "CAMERA 01", activa: true },
  { hora: "03:15:20", camara: "CAMERA 02", activa: false },
  { hora: "03:15:20", camara: "CAMERA 03", activa: false },
  { hora: "03:15:20", camara: "CAMERA 04", activa: false },
  { hora: "03:15:20", camara: "CAMERA 05", activa: false },
  { hora: "03:15:20", camara: "CAMERA 06", activa: false }
];


const camPrincipal = document.getElementById("camPrincipal");

listaCamaras.forEach((item, index) => {
  let camhtml = '';
  
  if (item.activa && item.camara === "CAMERA 01") {
    // Cámara 01 con video feed activo
    const horaActual = new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    camhtml = `
      <div class="videos cursor-pointer relative bg-[#1a2332] border border-[#2d3e50] rounded-lg shadow-xl overflow-hidden" data-camera="CAMERA 01">

        <span class="absolute top-2 left-2 bg-black/70 text-green-400 text-[11px] px-2 py-1 rounded font-mono z-10" id="horaCam01">
          ${horaActual}
        </span>

        <span class="absolute bottom-2 right-2 bg-black/70 text-white text-[10px] px-2 py-1 rounded font-mono font-semibold z-10">
          ${item.camara}
        </span>

        <img src="/video_feed" alt="Video Feed" class="w-full h-full object-cover" id="videoFeed01">
      </div>
    `;
    
    // Actualizar hora cada segundo
    setInterval(() => {
      const horaElement = document.getElementById("horaCam01");
      if (horaElement) {
        const horaActual = new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        horaElement.textContent = horaActual;
      }
    }, 1000);
  } else {
    // Cámaras estáticas
    camhtml = `
      <div class="videos cursor-pointer relative bg-[#1a2332] border border-[#2d3e50] rounded-lg shadow-xl overflow-hidden" data-camera="${item.camara}">

        <span class="absolute top-2 left-2 bg-black/70 text-green-400 text-[11px] px-2 py-1 rounded font-mono">
          ${item.hora}
        </span>

        <span class="absolute bottom-2 right-2 bg-black/70 text-white text-[10px] px-2 py-1 rounded font-mono font-semibold">
          ${item.camara}
        </span>

        <div class="w-full h-full flex items-center justify-center bg-gradient-to-br from-[#1a3a2e] to-[#0f2419]">
          <svg class="w-16 h-16 opacity-20" viewBox="0 0 24 24" fill="none" stroke="#00ff00" stroke-width="1.5">
            <path d="M23 7l-7 5 7 5V7z"></path>
            <rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect>
          </svg>
        </div>

      </div>
    `;
  }
  
  camPrincipal.innerHTML += camhtml;
});

const videos = document.querySelectorAll(".videos")
const video = document.getElementById("video");

videos.forEach(vide => {
  vide.addEventListener("click", () => {
    // Obtener información de la cámara
    const spans = vide.querySelectorAll("span");
    const cameraName = vide.getAttribute("data-camera") || spans[1]?.textContent || "CAMERA 01";
    const hora = spans[0]?.textContent || new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    
    // Actualizar textos en la vista ampliada
    const horaVideoAmpliado = document.getElementById("horaVideoAmpliado");
    const nombreCamaraAmpliado = document.getElementById("nombreCamaraAmpliado");
    const videoFeedAmpliado = document.getElementById("videoFeedAmpliado");
    const videoPlaceholder = document.getElementById("videoPlaceholder");
    
    if (horaVideoAmpliado) horaVideoAmpliado.textContent = hora;
    if (nombreCamaraAmpliado) nombreCamaraAmpliado.textContent = cameraName;
    
    // Si es CAMERA 01, mostrar el video feed
    if (cameraName === "CAMERA 01") {
      if (videoFeedAmpliado) {
        videoFeedAmpliado.style.display = "block";
        // Forzar recarga del video feed
        const imgVideo = document.getElementById("imgVideoFeedAmpliado");
        if (imgVideo) {
          // Limpiar src anterior y establecer nuevo
          imgVideo.src = '';
          // Pequeño delay para asegurar que se limpia
          setTimeout(() => {
            // Agregar timestamp para evitar caché y forzar recarga
            const timestamp = new Date().getTime();
            imgVideo.src = `/video_feed?t=${timestamp}`;
            imgVideo.onerror = function() {
              console.error('Error cargando video feed');
              // Si falla, intentar recargar
              setTimeout(() => {
                const newTimestamp = new Date().getTime();
                imgVideo.src = `/video_feed?t=${newTimestamp}`;
              }, 1000);
            };
          }, 100);
        }
      }
      if (videoPlaceholder) {
        videoPlaceholder.style.display = "none";
      }
      
      // Actualizar hora cada segundo
      if (window.horaInterval) clearInterval(window.horaInterval);
      window.horaInterval = setInterval(() => {
        if (horaVideoAmpliado) {
          const horaActual = new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
          horaVideoAmpliado.textContent = horaActual;
        }
      }, 1000);
    } else {
      // Para otras cámaras, mostrar placeholder
      if (videoFeedAmpliado) {
        videoFeedAmpliado.style.display = "none";
        const imgVideo = document.getElementById("imgVideoFeedAmpliado");
        if (imgVideo) {
          imgVideo.src = '';
        }
      }
      if (videoPlaceholder) {
        videoPlaceholder.style.display = "flex";
      }
      if (window.horaInterval) clearInterval(window.horaInterval);
    }
    
    // Mostrar sección de video
    video.style.display = "flex"
    principal.style.display = "none"
    infoEvento.style.display = "none"
  });
});


// El código de eventos ahora se maneja en la función mostrarAlertas()

btnAtrasEvento.addEventListener("click", () => {
  secEventos.style.display = "flex"
  infoEvento.style.display = "none"
});

// Guardar cambios en la alerta
const btnGuardar = document.getElementById("Guardar");

if (btnGuardar) {
  btnGuardar.addEventListener("click", async () => {
    if (!alertaActualId) return;
    
    const motivoTexto = document.getElementById("motivoTexto");
    const solucionTexto = document.getElementById("solucionTexto");
    
    try {
      const response = await fetch(`/api/alerta/${alertaActualId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          motivo: motivoTexto.textContent.trim(),
          solucion: solucionTexto.textContent.trim()
        })
      });
      
      if (response.ok) {
        alert('Cambios guardados correctamente');
        // Recargar alertas
        await cargarAlertas();
      } else {
        alert('Error al guardar los cambios');
      }
    } catch (error) {
      console.error('Error guardando alerta:', error);
      alert('Error de conexión al guardar');
    }
  });
}


function obtenerSeccionVisible() {
  const secciones = [principal, login, video, secEventos, infoEvento, registro];
  return secciones.find(sec => sec.style.display !== "none" && sec.style.display !== "");
}

function ocultarTodasLasSecciones() {
  principal.style.display = "none";
  login.style.display = "none";
  perfil.style.display = "none";
  video.style.display = "none";
  secEventos.style.display = "none";
  infoEvento.style.display = "none";
  registro.style.display = "none";
}