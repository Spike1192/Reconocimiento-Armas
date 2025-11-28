const panel = document.getElementById("notificationPanel");
const btn = document.getElementById("btnNotifications");
let ultimaSeccion = null;


btn.addEventListener("click", () => {
  panel.classList.toggle("translate-x-full");
  console.log("hola")
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


inicioSesion.addEventListener("click", () => {
  principal.style.display = "block"
  header.style.display = "block"
  login.style.display = "none"

});

cerrarSesion.addEventListener("click", () => {
  principal.style.display = "none"
  header.style.display = "none"
  login.style.display = "flex"

});

btnPerfil.addEventListener("click", () => {
  ultimaSeccion = obtenerSeccionVisible();
  ocultarTodasLasSecciones();
  principal.style.display = "none"
  header.style.display = "none"
  login.style.display = "none"
  video.style.display = "none"
  secEventos.style.display = "none"
  perfil.style.display = "flex"

});

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


btnRegistro.addEventListener("click", () => {
  perfil.style.display = "none"
  registro.style.display = "flex"
});

btnAtrasRegistro.addEventListener("click", () => {
  registro.style.display = "none"
  perfil.style.display = "flex"

});

inicioSesion.addEventListener("click", () => {
  principal.style.display = "block"
  header.style.display = "block"
  login.style.display = "none"

});

crearCuenta.addEventListener("click", () => {
  login.style.display = "flex"
  registro.style.display = "none"
});



btnAtrasVideo.addEventListener("click", () => {
  principal.style.display = "block"
  video.style.display = "none"
});

const infoEvento = document.getElementById("infoEvento")

const eventos = [
  {
    camara: {
      fecha: "03:15:20",
      camara: "CAMERA 01"
    },
    contenido: {
      titulo: "Sujeto detectado",
      texto: "00/00/00",
      minuto: "01:30"
    },
    aspectos:{
      motivo: "motivo camara 01",
      solucion: "soolucion camara 01"
    }
  },
  {
    camara: {
      fecha: "04:22:11",
      camara: "CAMERA 02"
    },
    contenido: {
      titulo: "Movimiento sospechoso",
      texto: "12/10/24",
      minuto: "02:30"
    },
    aspectos:{
      motivo: "motivo camara 02",
      solucion: "soolucion camara 02"
    }
  },
  {
    camara: {
      fecha: "07:50:02",
      camara: "CAMERA 03"
    },
    contenido: {
      titulo: "Auto detectado",
      texto: "05/07/25",
      minuto: "04:35"
    },
    aspectos:{
      motivo: "motivo camara 02",
      solucion: "soolucion camara 02"
    }
  }
];

const listaCamaras = [
  { hora: "03:15:20", camara: "CAMERA 01" },
  { hora: "03:15:20", camara: "CAMERA 02" },
  { hora: "03:15:20", camara: "CAMERA 03" },
  { hora: "03:15:20", camara: "CAMERA 04" },
  { hora: "03:15:20", camara: "CAMERA 05" },
  { hora: "03:15:20", camara: "CAMERA 06" }
];


const camPrincipal = document.getElementById("camPrincipal");

listaCamaras.forEach(item => {
  const camhtml = `
    <div class=" videos cursor-pointer relative bg-[#1a2332] border border-[#2d3e50] rounded-lg shadow-xl overflow-hidden">

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
    `
    camPrincipal.innerHTML += camhtml
});

const videos = document.querySelectorAll(".videos")
const video = document.getElementById("video");

videos.forEach(vide => {
  vide.addEventListener("click", () => {

    const spans = vide.querySelectorAll("span");
    const spansVideo = video.querySelectorAll("span");

    const primerValor = spans[0].textContent;
    const segundoValor = spans[1].textContent;

    spansVideo[0].textContent = primerValor
    spansVideo[1].textContent = segundoValor

    video.style.display = "flex"
    principal.style.display = "none"
    infoEvento.style.display = "none"
  });
});


const listaEventos = document.getElementById("listaEventos");

eventos.forEach((e, i) => {
  const html = `
    <div class="evento cursor-pointer w-full h-[200px] rounded-lg flex items-center mb-4 bg-[#0A1330']" data-index="${i}">

      <div class="flex justify-center w-[35%] h-[80%]">
        <div class="videos w-[90%] h-full relative bg-[#1a2332]  rounded-lg overflow-hidden">
          
          <span class="absolute top-2 left-2 bg-black/70 text-green-400 text-[11px] px-2 py-1 rounded font-mono">
            ${e.camara.fecha}
          </span>

          <span class="absolute bottom-2 right-2 bg-black/70 text-white text-[10px] px-2 py-1 rounded font-mono font-semibold">
            ${e.camara.camara}
          </span>

          <div class="w-full h-full flex items-center justify-center bg-gradient-to-br from-[#1a3a2e] to-[#0f2419]">
            <svg class="w-16 h-16 opacity-20" fill="none" stroke="#00ff00" viewBox="0 0 24 24" stroke-width="1.5">
              <path d="M23 7l-7 5 7 5V7z"></path>
              <rect x="1" y="5" width="15" height="14" rx="2"></rect>
            </svg>
          </div>
        </div>
      </div>

      <div class="pl-12">
        <h1 class="text-[25px] font-semibold mb-4 tracking-tight">
          ${e.contenido.titulo}
        </h1>
        <p class="text-white/80 text-[13px] font-light mb-5">
          ${e.contenido.texto} -- ${e.contenido.minuto}
        </p>
      </div>

    </div>
  `;

  listaEventos.innerHTML += html;
});



setTimeout(() => {
  document.querySelectorAll(".evento").forEach(evento => {
    evento.addEventListener("click", () => {
      const index = evento.getAttribute("data-index");
      const data = eventos[index];

      // Rellenar títulos e info
      document.getElementById("tituloEvento").innerText = data.contenido.titulo;
      document.getElementById("fechaYMinuto").innerText = `${data.contenido.texto} -- ${data.contenido.minuto}`;
      
      // Motivo y solución
      document.getElementById("motivoTexto").innerText = data.aspectos.motivo;
      document.getElementById("solucionTexto").innerText = data.aspectos.solucion;

      // Mostrar la sección si fuera necesario
      infoEvento.style.display = "flex"
      secEventos.style.display = "none"
    });
  });
}, 100);

btnAtrasEvento.addEventListener("click", () => {
  secEventos.style.display = "flex"
  infoEvento.style.display = "none"

});


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