from flask import Flask, render_template_string, request, jsonify, send_file
import os, json, io, csv
from datetime import datetime
app = Flask(__name__)
viajes = []

# ESTE ES EL CODIGO QUE ME PASASTE - COPIADO TAL CUAL - V35 BONITO
MAPA_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AGL V35 - Aguascalientes 4 Paradas</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,Roboto,Arial}
body{height:100vh;overflow:hidden}
#map{position:fixed!important;top:0;left:0;width:100%;height:100vh!important;z-index:1}
.top{position:fixed;top:12px;left:12px;right:12px;z-index:10;display:flex;gap:10px;max-width:420px}
.menu-btn{width:46px;height:46px;background:#fff;border:none;border-radius:14px;box-shadow:0 4px 18px rgba(0,0,0,.28);font-size:20px}
.search-card{background:#fff;border-radius:16px;box-shadow:0 8px 28px rgba(0,0,0,.26);padding:8px 10px;flex:1}
.item{display:flex;align-items:center;gap:8px;padding:8px 4px}
.item+.item{border-top:1px solid #eee}
.dot{width:8px;height:8px;border-radius:50%}.dot.o{background:#ff3b30}.dot.d{background:#000}
input{flex:1;border:none;outline:none;font-size:14px;font-weight:600;background:transparent}
#menu{position:fixed;top:0;left:-100%;width:82%;max-width:320px;height:100vh;background:#fff;z-index:30;transition:.28s;padding:18px 14px;overflow-y:auto}
#menu.act{left:0}
.overlay{position:fixed;inset:0;background:rgba(0,0,0,.35);z-index:20;display:none}
.overlay.act{display:block}
#menu button{width:100%;text-align:left;background:#f6f6f6;border:none;padding:13px 12px;border-radius:12px;margin-bottom:8px;font-weight:700}
.parada-extra{display:none}
#cotizacion{position:fixed;bottom:72px;left:12px;right:12px;z-index:11;background:#fff;border-radius:16px;padding:12px 14px;display:none;box-shadow:0 8px 28px rgba(0,0,0,.32);max-width:420px;margin:auto}
.btn{position:fixed;bottom:10px;left:12px;right:12px;z-index:11;background:#000;color:#fff;font-weight:800;padding:16px;border:none;border-radius:16px;max-width:420px;margin:auto}
#modal-rol{position:fixed;inset:0;z-index:99999;background:rgba(0,0,0,.85);display:flex;align-items:center;justify-content:center;padding:20px}
.box-rol{background:#fff;border-radius:20px;padding:24px;width:100%;max-width:340px;text-align:center}
</style>
</head>
<body>

<div id="modal-rol"><div class="box-rol"><h2>🚕 AGL Transporte</h2><p style="margin:10px 0 18px;color:#666;font-size:13px">¿Cómo vas a usar la app?</p><button onclick="elegirRol('cliente')" style="width:100%;padding:16px;border:none;border-radius:14px;font-weight:800;margin-bottom:10px;background:#000;color:#fff">👤 SOY CLIENTE</button><button onclick="elegirRol('chofer')" style="width:100%;padding:16px;border:none;border-radius:14px;font-weight:800;background:#00c853;color:#fff">🚗 SOY CHOFER</button><br><br><a href="/concentrado" target="_blank" style="font-size:12px;color:#0a3552">📊 Ver Concentrado AGL</a></div></div>

<div id="vista-cliente" style="display:none">
<div id="box-login-cliente" style="padding:20px;max-width:400px;margin:100px auto 0;background:#fff;position:relative;z-index:20;border-radius:16px">
  <h2 style="text-align:center">👤 ACCESO CLIENTE</h2>
  <div id="form-login-c">
    <input id="cli-tel" placeholder="Celular" style="width:100%;padding:12px;margin:6px 0;border-radius:8px;border:1px solid #ccc">
    <input id="cli-pass" type="password" placeholder="Contraseña" style="width:100%;padding:12px;margin:6px 0;border-radius:8px;border:1px solid #ccc">
    <button onclick="clienteLogin()" style="width:100%;padding:12px;background:#000;color:#fff;border:none;border-radius:8px;font-weight:800">ENTRAR</button>
    <button onclick="volverAlInicio()" style="width:100%;margin-top:10px;padding:12px;background:#eee;color:#000;border:none;border-radius:12px;font-weight:800">MENU INICIO</button>
<p style="text-align:center;margin:10px 0">¿No tienes cuenta?</p>
    <button onclick="mostrarRegistroCli()" style="width:100%;padding:10px;background:#fff;border:1px solid #000;border-radius:8px">REGISTRARME</button>
  </div>
  <div id="form-registro-c" style="display:none">
    <input id="cli-reg-nombre" placeholder="Tu nombre" style="width:100%;padding:12px;margin:6px 0;border-radius:8px;border:1px solid #ccc">
    <input id="cli-reg-tel" placeholder="Celular" style="width:100%;padding:12px;margin:6px 0;border-radius:8px;border:1px solid #ccc">
    <input id="cli-reg-pass" type="password" placeholder="Crea contraseña" style="width:100%;padding:12px;margin:6px 0;border-radius:8px;border:1px solid #ccc">
    <button onclick="clienteRegistrar()" style="width:100%;padding:12px;background:#00c853;color:#fff;border:none;border-radius:8px;font-weight:800">CREAR CUENTA</button>
    <button onclick="mostrarLoginCli()" style="width:100%;padding:10px;background:none;border:none;color:#1976d2">Ya tengo cuenta</button>
    <p id="msg-error-c" style="color:red;font-size:12px;text-align:center"></p>
  </div>
</div>
<div id="box-cliente-viaje" style="display:none">
<div id="map"></div>
<button onclick="miUbicacion()" style="position:fixed;bottom:90px;right:14px;z-index:12;width:50px;height:50px;background:#fff;border:none;border-radius:50%;box-shadow:0 4px 18px rgba(0,0,0,.3);font-size:22px">📍</button>
<div class="top"><button class="menu-btn" onclick="toggleMenu()">☰</button><div class="search-card"><div class="item"><div class="dot o"></div><input id="origen" placeholder="Origen - Aguascalientes"></div><div class="item parada-extra" id="boxP1"><div class="dot" style="background:#ffcc00"></div><input id="parada1" placeholder="Parada 1"></div><div class="item parada-extra" id="boxP2"><div class="dot" style="background:#ff9500"></div><input id="parada2" placeholder="Parada 2"></div><div class="item parada-extra" id="boxP3"><div class="dot" style="background:#00e5ff"></div><input id="parada3" placeholder="Parada 3"></div><div class="item"><div class="dot d"></div><input id="destino" placeholder="¿A dónde va?"></div></div></div>
<div id="menu"><div style="display:flex;justify-content:space-between;margin-bottom:16px"><b>🚕 AGL AGS</b><button onclick="toggleMenu()" style="width:36px;height:36px;border-radius:50%;background:#111;color:#fff">✕</button></div><button onclick="agregarParada();toggleMenu()">➕ Agregar parada (hasta 3)</button><button onclick="setTipo('mapa');toggleMenu()">🗺️ Mapa</button><button onclick="setTipo('satelite');toggleMenu()">🛰️ Satélite</button><div style="margin-top:12px"><input id="nombre" placeholder="👤 Cliente" style="width:100%;background:#f5f5f5;border:none;padding:11px;border-radius:10px;margin-bottom:6px;font-weight:600"><div style="display:flex;gap:6px"><select id="pasajeros" style="background:#e8f5e9;border:none;padding:8px;border-radius:10px;font-weight:800"><option value="4" selected>👥 4</option><option>1</option><option>2</option><option>3</option><option>5</option><option>6</option></select><input type="date" id="fechaViaje"><input type="time" id="horaViaje"></div></div><div style="display:flex;gap:8px;margin-top:16px"><button onclick="borrarTodo()" style="flex:1;background:#fff;border:1.5px solid #8bc34a;padding:12px;border-radius:12px;font-weight:800">BORRAR</button><button onclick="toggleMenu()" style="flex:1;background:#000;color:#fff;padding:12px;border-radius:12px;font-weight:800">CERRAR</button></div><button onclick="cambiarRol()" style="margin-top:12px;background:#e3f2fd!important;color:#1976d2!important">🔄 Cambiar a Chofer</button><a href="/concentrado" target="_blank" style="display:block;text-align:center;margin-top:12px;background:#0a3552;color:white;padding:12px;border-radius:12px;text-decoration:none;font-weight:800">📊 Ver Concentrado</a><div id="miniInfo" style="margin-top:10px;font-size:11px;color:#888;text-align:center">Base: Aguascalientes<br>21.8853, -102.2916</div></div>
<div class="overlay" id="overlay" onclick="toggleMenu()"></div>
<div id="cotizacion"><div id="dist" style="font-size:11px;color:#666"></div><b id="precio" style="font-size:22px">$0 MXN</b><div id="avisoFecha" style="font-size:10px;font-weight:800;text-align:center;margin-top:6px;padding:6px;border-radius:8px;background:#000;color:#fff">Ruta calculada</div></div>
<button class="btn" id="btnPedir" onclick="pedir()">Confirmar $0</button>
</div>
</div>
<div id="vista-chofer" style="display:none">
  <div id="box-login-chofer" style="padding:20px;max-width:400px;margin:0 auto">
    <h2 style="text-align:center">🚗 ACCESO CHOFER</h2>
    <div id="form-login">
      <input id="chofer-tel" placeholder="Celular" style="width:100%;padding:12px;margin:6px 0;border-radius:8px;border:1px solid #ccc">
      <input id="chofer-pass" type="password" placeholder="Contraseña" style="width:100%;padding:12px;margin:6px 0;border-radius:8px;border:1px solid #ccc">
      <button onclick="choferLogin()" style="width:100%;padding:12px;background:#000;color:#fff;border:none;border-radius:8px;font-weight:800">ENTRAR</button>
      <button onclick="volverAlInicio()" style="width:100%;margin-top:10px;padding:12px;background:#eee;color:#000;border:none;border-radius:12px;font-weight:800">MENU INICIO</button>
      <p style="text-align:center">¿No tienes cuenta?</p>
      <button onclick="mostrarRegistroChofer()" style="width:100%;padding:10px;background:#fff;border:1px solid #000;border-radius:8px">REGISTRARME</button>
    </div>
    <div id="form-registro" style="display:none">
      <input id="reg-nombre" placeholder="Nombre completo" style="width:100%;padding:12px;margin:6px 0;border-radius:8px;border:1px solid #ccc">
      <input id="reg-tel" placeholder="Celular" style="width:100%;padding:12px;margin:6px 0;border-radius:8px;border:1px solid #ccc">
      <input id="reg-placas" placeholder="Placas" style="width:100%;padding:12px;margin:6px 0;border-radius:8px;border:1px solid #ccc">
      <input id="reg-modelo" placeholder="Modelo EJ: Versa 2022" style="width:100%;padding:12px;margin:6px 0;border-radius:8px;border:1px solid #ccc">
      <input id="reg-anio" type="number" placeholder="Año (2021-2026)" min="2021" max="2026" style="width:100%;padding:12px;margin:6px 0;border-radius:8px;border:1px solid #ccc">
      <input id="reg-licencia" placeholder="No. Licencia" style="width:100%;padding:12px;margin:6px 0;border-radius:8px;border:1px solid #ccc">
      <input id="reg-vigencia" type="date" style="width:100%;padding:12px;margin:6px 0;border-radius:8px;border:1px solid #ccc">
      <input id="reg-pass" type="password" placeholder="Contraseña" style="width:100%;padding:12px;margin:6px 0;border-radius:8px;border:1px solid #ccc">
      <button onclick="choferRegistrar()" style="width:100%;padding:12px;background:#00c853;color:#fff;border:none;border-radius:8px;font-weight:800;margin-top:8px">CREAR CUENTA</button>
      <button onclick="mostrarLoginChofer()" style="width:100%;padding:10px;background:none;border:none;color:#1976d2">Ya tengo cuenta</button>
      <p id="msg-error" style="color:red;font-size:12px"></p>
    </div>
  </div>
  <div id="box-viajes-chofer" style="display:none">
    <div style="background:#000;color:#fff;padding:10px;display:flex;justify-content:space-between"><span id="nombre-chofer-log">Chofer</span><button onclick="choferLogout()" style="background:#ff5252;color:#fff;border:none;padding:6px 10px;border-radius:6px">Salir</button></div>
    <div id="lista-viajes-chofer"></div>
    <div style="padding:12px"><a href="/" style="background:#0a3552;color:white;padding:10px 14px;border-radius:10px;text-decoration:none">← Volver al Mapa</a> <a href="/concentrado" style="background:#16a34a;color:white;padding:10px 14px;border-radius:10px;text-decoration:none">📊 Concentrado</a></div>
  </div>
</div>
<script>
const NUMERO="524491909860";
let map,origenMarker=null,destinoMarker=null,parada1Marker=null,parada2Marker=null,parada3Marker=null,routeLine,kmActual=0,precioActual=0,numParadasVisibles=0,capaMapa,capaSate;let viajeEnCurso = null;
function toggleMenu(){document.getElementById('menu').classList.toggle('act');document.getElementById('overlay').classList.toggle('act');}
function elegirRol(r){
  localStorage.setItem('rol_AGL',r);
  document.getElementById('modal-rol').style.display='none';
  if(r==='chofer'){
    document.getElementById('vista-cliente').style.display='none';
    document.getElementById('vista-chofer').style.display='block';
    verificarSesionChofer();
  }else{
    document.getElementById('vista-chofer').style.display='none';
    document.getElementById('vista-cliente').style.display='block';
    verificarSesionCliente();
    setTimeout(()=>{ if(map) map.invalidateSize(); },500);
  }
}
function cambiarRol(){if(confirm('¿Cambiar rol?')){localStorage.removeItem('rol_AGL');location.reload();}}
(function(){let r=(localStorage.getItem('rol_AGL')||'').toLowerCase();if(r==='cliente'||r==='chofer'){document.getElementById('modal-rol').style.display='none';if(r==='chofer'){document.getElementById('vista-cliente').style.display='none';document.getElementById('vista-chofer').style.display='block';verificarSesionChofer();}else{document.getElementById('vista-chofer').style.display='none';document.getElementById('vista-cliente').style.display='block';verificarSesionCliente();}}})();

const verdeIcon=new L.Icon({iconUrl:'https://cdn.jsdelivr.net/gh/pointhi/leaflet-color-markers@master/img/marker-icon-2x-green.png',shadowUrl:'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',iconSize:[25,41],iconAnchor:[12,41]});
const rojoIcon=new L.Icon({iconUrl:'https://cdn.jsdelivr.net/gh/pointhi/leaflet-color-markers@master/img/marker-icon-2x-red.png',shadowUrl:'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',iconSize:[25,41],iconAnchor:[12,41]});
const amarilloIcon=new L.Icon({iconUrl:'https://cdn.jsdelivr.net/gh/pointhi/leaflet-color-markers@master/img/marker-icon-2x-yellow.png',shadowUrl:'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',iconSize:[25,41],iconAnchor:[12,41]});
const naranjaIcon=new L.Icon({iconUrl:'https://cdn.jsdelivr.net/gh/pointhi/leaflet-color-markers@master/img/marker-icon-2x-orange.png',shadowUrl:'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',iconSize:[25,41],iconAnchor:[12,41]});
const celesteIcon=new L.Icon({iconUrl:'https://cdn.jsdelivr.net/gh/pointhi/leaflet-color-markers@master/img/marker-icon-2x-blue.png',shadowUrl:'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',iconSize:[25,41],iconAnchor:[12,41]});

map=L.map('map',{zoomControl:false}).setView([21.8853,-102.2916],13);
capaMapa=L.tileLayer('https://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',{subdomains:['mt0','mt1','mt2','mt3'],maxZoom:20}).addTo(map);
capaSate=L.tileLayer('https://{s}.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}',{subdomains:['mt0','mt1','mt2','mt3'],maxZoom:20});
function setTipo(t){if(t=='mapa'){if(map.hasLayer(capaSate))map.removeLayer(capaSate);capaMapa.addTo(map);}else{if(map.hasLayer(capaMapa))map.removeLayer(capaMapa);capaSate.addTo(map);}}

async function getDir(ll,tipo){
  try{
    const r=await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${ll.lat}&lon=${ll.lng}&zoom=18`);
    const j=await r.json();
    let nom=j.display_name.split(',').slice(0,3).join(', ');
    if(tipo==1) document.getElementById('origen').value=nom;
    else if(tipo==2) document.getElementById('destino').value=nom;
    else if(tipo==3) document.getElementById('parada1').value=nom;
    else if(tipo==4) document.getElementById('parada2').value=nom;
    else if(tipo==5) document.getElementById('parada3').value=nom;
  }catch{}
}
function crearOrigen(ll){if(!origenMarker){origenMarker=L.marker(ll,{draggable:true,icon:verdeIcon}).addTo(map);origenMarker.on('dragend',()=>{getDir(origenMarker.getLatLng(),1);trazar();});}else origenMarker.setLatLng(ll); getDir(ll,1); trazar();}
function crearDestino(ll){if(!destinoMarker){destinoMarker=L.marker(ll,{draggable:true,icon:rojoIcon}).addTo(map);destinoMarker.on('dragend',()=>{getDir(destinoMarker.getLatLng(),2);trazar();});}else destinoMarker.setLatLng(ll); getDir(ll,2); trazar();}
function crearParada(ll,t){if(t==1){if(!parada1Marker){parada1Marker=L.marker(ll,{draggable:true,icon:amarilloIcon}).addTo(map);parada1Marker.on('dragend',()=>{getDir(parada1Marker.getLatLng(),3);trazar();});}else parada1Marker.setLatLng(ll); getDir(ll,3);}else if(t==2){if(!parada2Marker){parada2Marker=L.marker(ll,{draggable:true,icon:naranjaIcon}).addTo(map);parada2Marker.on('dragend',()=>{getDir(parada2Marker.getLatLng(),4);trazar();});}else parada2Marker.setLatLng(ll); getDir(ll,4);}else if(t==3){if(!parada3Marker){parada3Marker=L.marker(ll,{draggable:true,icon:celesteIcon}).addTo(map);parada3Marker.on('dragend',()=>{getDir(parada3Marker.getLatLng(),5);trazar();});}else parada3Marker.setLatLng(ll); getDir(ll,5);}trazar();}
function agregarParada(){if(numParadasVisibles==0){document.getElementById('boxP1').style.display='flex';numParadasVisibles=1;}else if(numParadasVisibles==1){document.getElementById('boxP2').style.display='flex';numParadasVisibles=2;}else if(numParadasVisibles==2){document.getElementById('boxP3').style.display='flex';numParadasVisibles=3;}}
function miUbicacion(){navigator.geolocation.getCurrentPosition(pos=>{const p={lat:pos.coords.latitude,lng:pos.coords.longitude};crearOrigen(p);map.setView([p.lat,p.lng],16);});}
setTimeout(miUbicacion,1000);
map.on('click',e=>{if(!origenMarker){crearOrigen(e.latlng);return;}if(numParadasVisibles>=1&&!parada1Marker){crearParada(e.latlng,1);return;}if(numParadasVisibles>=2&&!parada2Marker){crearParada(e.latlng,2);return;}if(numParadasVisibles>=3&&!parada3Marker){crearParada(e.latlng,3);return;}if(!destinoMarker){crearDestino(e.latlng);return;}});

async function trazar(){
  if(!origenMarker) return;
  let pts=[];pts.push(origenMarker.getLatLng());
  if(parada1Marker)pts.push(parada1Marker.getLatLng());
  if(parada2Marker)pts.push(parada2Marker.getLatLng());
  if(parada3Marker)pts.push(parada3Marker.getLatLng());
  if(destinoMarker)pts.push(destinoMarker.getLatLng());
  if(pts.length<2)return;
  try{
    const s=pts.map(p=>p.lng+','+p.lat).join(';');
    const r=await fetch(`https://router.project-osrm.org/route/v1/driving/${s}?overview=full&geometries=geojson`);
    const j=await r.json(); if(!j.routes[0])return;
    const route=j.routes[0];
    kmActual=Math.round(route.distance/100)/10;
    if(kmActual<0.8)kmActual=0.8;
    if(routeLine)map.removeLayer(routeLine);
    routeLine=L.polyline(route.geometry.coordinates.map(c=>[c[1],c[0]]),{color:'#000',weight:6}).addTo(map);
    let cnt=(parada1Marker?1:0)+(parada2Marker?1:0)+(parada3Marker?1:0);
    let precio=65+cnt*10;
    if(kmActual>6){precio=35+(kmActual*6.6)+(route.duration/60)+cnt*10; if(precio<65)precio=65;}
    precioActual=Math.round(precio);
    document.getElementById('cotizacion').style.display='block';
    document.getElementById('dist').innerText=kmActual+' km • '+(pts.length-1)+' tramos';
    document.getElementById('precio').innerText='$'+precioActual+' MXN';
    document.getElementById('btnPedir').innerText='Confirmar $'+precioActual;
    map.fitBounds(routeLine.getBounds(),{padding:[60,60]});
  }catch{}
}
async function pedir(){
  if(!precioActual) return alert('Primero toca el mapa para calcular ruta');
  let nombre = document.getElementById('nombre').value || document.getElementById('cli-reg-nombre')?.value || 'Cliente AGS';
  let fecha = document.getElementById('fechaViaje').value || new Date().toISOString().split('T')[0];
  let hora = document.getElementById('horaViaje').value || new Date().toLocaleTimeString();
  let pax = document.getElementById('pasajeros').value;

  let origenTxt = document.getElementById('origen').value;
  let destinoTxt = document.getElementById('destino').value;
  let p1 = document.getElementById('parada1').value;
  let p2 = document.getElementById('parada2').value;
  let p3 = document.getElementById('parada3').value;

  let todosPuntos = [origenTxt];
  if(p1) todosPuntos.push(p1);
  if(p2) todosPuntos.push(p2);
  if(p3) todosPuntos.push(p3);
  if(destinoTxt) todosPuntos.push(destinoTxt);

  let dataParaBackend = {
    solicita: 'App V35',
    cliente: nombre,
    operador: 'Por asignar',
    pasajeros: pax,
    fecha: fecha,
    hora: hora,
    origen: origenTxt,
    parada1: p1,
    parada2: p2,
    parada3: p3,
    destino: destinoTxt,
    paradas: todosPuntos.join(' → '),
    kms: kmActual,
    mins: 0,
    precio: precioActual,
    latO: origenMarker?origenMarker.getLatLng().lat:21.8853,
    lngO: origenMarker?origenMarker.getLatLng().lng:-102.2916,
    latD: destinoMarker?destinoMarker.getLatLng().lat:21.8853,
    lngD: destinoMarker?destinoMarker.getLatLng().lng:-102.2916,
    timestamp: new Date().toISOString()
  };

  // Guardar en backend para concentrado
  fetch('/api/viaje',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(dataParaBackend)});

  // Guardar local para chofer
  let viajesLocal = JSON.parse(localStorage.getItem('viajes')||'[]');
  viajesLocal.push({
    cliente: nombre,
    origen: origenTxt,
    destino: destinoTxt,
    km: kmActual,
    precio: precioActual,
    link: `https://www.google.com/maps/dir/${origenTxt}/${destinoTxt}`
  });
  localStorage.setItem('viajes', JSON.stringify(viajesLocal));

  let linkMapa = `https://www.google.com/maps/dir/${origenTxt}/${destinoTxt}`;
  let msg = `🚕 *VIAJE AGL AGS V35*%0A👤 Cliente: ${nombre}%0A📅 ${fecha} ${hora} • 👥 ${pax}%0A🔴 Origen: ${origenTxt}%0A${p1?'🟡 Parada1: '+p1+'%0A':''}${p2?'🟠 Parada2: '+p2+'%0A':''}${p3?'🔵 Parada3: '+p3+'%0A':''}🔵 Destino: ${destinoTxt}%0A📏 ${kmActual} km • $${precioActual}%0A🗺️ ${linkMapa}`;
  window.open(`https://wa.me/${NUMERO}?text=${msg}`,'_blank');
}
function borrarTodo(){
  if(!confirm('¿Borrar?')) return;
  document.getElementById('origen').value="";document.getElementById('destino').value="";
  document.getElementById('parada1').value="";document.getElementById('parada2').value="";document.getElementById('parada3').value="";
  document.getElementById('boxP1').style.display='none';document.getElementById('boxP2').style.display='none';document.getElementById('boxP3').style.display='none';
  numParadasVisibles=0;document.getElementById('cotizacion').style.display="none";
  if(origenMarker){map.removeLayer(origenMarker);origenMarker=null;}
  if(destinoMarker){map.removeLayer(destinoMarker);destinoMarker=null;}
  if(parada1Marker){map.removeLayer(parada1Marker);parada1Marker=null;}
  if(parada2Marker){map.removeLayer(parada2Marker);parada2Marker=null;}
  if(parada3Marker){map.removeLayer(parada3Marker);parada3Marker=null;}
  if(routeLine){map.removeLayer(routeLine);routeLine=null;}
  precioActual=0;document.getElementById('btnPedir').innerText='Confirmar $0';
}
function mostrarViajesChofer(){
  const c=document.getElementById('lista-viajes-chofer');
  const v=JSON.parse(localStorage.getItem('viajes')||'[]');
  if(v.length==0){c.innerHTML='<div style="padding:40px;color:#888">No hay viajes<br><small>Esperando cliente en Aguascalientes</small></div>';return;}
  c.innerHTML=v.slice().reverse().map((x,i)=>{
    let idx=v.length-1-i;
    return `<div style="border:2px solid #00c853;margin:10px;padding:12px;border-radius:12px;background:#fff;text-align:left;color:#000"><b>👤 ${x.cliente} - $${x.precio} - ${x.km}km</b><br>De: ${x.origen}<br>A: ${x.destino}<br><button onclick="tomarViajeReal(${idx})" style="width:100%;margin-top:8px;padding:12px;background:#00c853;color:#fff;border:none;border-radius:8px;font-weight:800">✅ TOMAR VIAJE</button></div>`;
  }).join('');
}
function tomarViajeReal(idx){
  let viajes=JSON.parse(localStorage.getItem('viajes')||'[]');
  let vv=viajes[idx];
  if(!confirm('¿Tomar viaje de '+vv.cliente+'?')) return;
  alert('Viaje tomado: '+vv.cliente+' - Abriendo ruta...');
  window.open(vv.link,'_blank');
}
function mostrarRegistroChofer(){document.getElementById('form-login').style.display='none';document.getElementById('form-registro').style.display='block';}
function mostrarLoginChofer(){document.getElementById('form-registro').style.display='none';document.getElementById('form-login').style.display='block';}
function choferRegistrar(){
  let n=document.getElementById('reg-nombre').value.trim();
  let t=document.getElementById('reg-tel').value.trim();
  let p=document.getElementById('reg-placas').value.trim();
  let modelo=document.getElementById('reg-modelo').value.trim();
  let anio=parseInt(document.getElementById('reg-anio').value);
  let lic=document.getElementById('reg-licencia').value.trim();
  let vig=document.getElementById('reg-vigencia').value;
  let c=document.getElementById('reg-pass').value.trim();
  let msg=document.getElementById('msg-error');
  if(!n||!t||!p||!modelo||!anio||!lic||!vig||!c){msg.innerText='Llena todo';return;}
  if(anio < 2021){msg.innerText='❌ Solo 2021 en adelante';return;}
  let choferes=JSON.parse(localStorage.getItem('choferes')||'[]');
  if(choferes.find(x=>x.tel==t)){msg.innerText='Ya registrado';return;}
  let nuevo={nombre:n,tel:t,placas:p,modelo:modelo,anio:anio,licencia:lic,vigencia:vig,pass:c};
  choferes.push(nuevo); localStorage.setItem('choferes',JSON.stringify(choferes));
  localStorage.setItem('choferActual',JSON.stringify(nuevo));
  alert('✅ Registrado '+n); verificarSesionChofer();
}
function choferLogin(){
  let t=document.getElementById('chofer-tel').value.trim();
  let c=document.getElementById('chofer-pass').value.trim();
  let choferes=JSON.parse(localStorage.getItem('choferes')||'[]');
  let f=choferes.find(x=>x.tel==t && x.pass==c);
  if(!f){alert('Datos mal');return;}
  localStorage.setItem('choferActual',JSON.stringify(f)); verificarSesionChofer();
}
function verificarSesionChofer(){
  let a=JSON.parse(localStorage.getItem('choferActual')||'null');
  if(a){
    document.getElementById('box-login-chofer').style.display='none';
    document.getElementById('box-viajes-chofer').style.display='block';
    document.getElementById('nombre-chofer-log').innerText='👤 '+a.nombre+' | '+a.placas+' '+a.anio;
    mostrarViajesChofer();
  }else{
    document.getElementById('box-login-chofer').style.display='block';
    document.getElementById('box-viajes-chofer').style.display='none';
  }
}
function choferLogout(){localStorage.removeItem('choferActual');verificarSesionChofer();}
function mostrarRegistroCli(){document.getElementById('form-login-c').style.display='none';document.getElementById('form-registro-c').style.display='block';}
function mostrarLoginCli(){document.getElementById('form-registro-c').style.display='none';document.getElementById('form-login-c').style.display='block';}
function clienteRegistrar(){
 let n=document.getElementById('cli-reg-nombre').value.trim();
 let t=document.getElementById('cli-reg-tel').value.trim();
 let c=document.getElementById('cli-reg-pass').value.trim();
 if(!n||!t||!c){document.getElementById('msg-error-c').innerText='Llena todo';return;}
 let clientes=JSON.parse(localStorage.getItem('clientes')||'[]');
 if(clientes.find(x=>x.tel==t)){document.getElementById('msg-error-c').innerText='Ya registrado';return;}
 let nuevo={nombre:n,tel:t,pass:c};
 clientes.push(nuevo); localStorage.setItem('clientes',JSON.stringify(clientes));
 localStorage.setItem('clienteActual',JSON.stringify(nuevo));
 alert('✅ Bienvenido '+n); verificarSesionCliente();
}
function clienteLogin(){
 let t=document.getElementById('cli-tel').value.trim();
 let c=document.getElementById('cli-pass').value.trim();
 let clientes=JSON.parse(localStorage.getItem('clientes')||'[]');
 let f=clientes.find(x=>x.tel==t && x.pass==c);
 if(!f){alert('Celular o contraseña mal');return;}
 localStorage.setItem('clienteActual',JSON.stringify(f)); verificarSesionCliente();
}
function verificarSesionCliente(){
 let a=JSON.parse(localStorage.getItem('clienteActual')||'null');
 if(a){
   document.getElementById('box-login-cliente').style.display='none';
   document.getElementById('box-cliente-viaje').style.display='block';
   setTimeout(()=>{ map.invalidateSize(); },400);
 }else{
   document.getElementById('box-login-cliente').style.display='block';
   document.getElementById('box-cliente-viaje').style.display='none';
 }
}
function volverAlInicio(){
  localStorage.removeItem('clienteActual');
  localStorage.removeItem('choferActual');
  document.getElementById('vista-cliente').style.display='none';
  document.getElementById('vista-chofer').style.display='none';
  document.getElementById('modal-rol').style.display='flex';
}
</script>
</body>
</html>
"""

CONCENTRADO_HTML = """
<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Concentrado AGL AGS</title><script src="https://cdn.jsdelivr.net/npm/chart.js"></script><style>body{font-family:Arial;margin:0;background:#eef2f7;padding:12px}h1{color:#0a3552}.card{background:white;padding:14px;border-radius:14px;margin-bottom:10px;box-shadow:0 2px 6px rgba(0,0,0,0.1)}.grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px}table{width:100%;border-collapse:collapse;font-size:11px}th,td{border:1px solid #ddd;padding:6px}th{background:#0a3552;color:white}.btn{background:#0a3552;color:white;padding:10px 14px;border-radius:10px;text-decoration:none;display:inline-block;margin-right:6px}@media(max-width:700px){.grid{grid-template-columns:1fr}}</style></head><body>
<h1>📊 Concentrado AGL - Aguascalientes V35</h1><a href="/" class="btn">← Mapa Bonito</a><a href="/excel" class="btn" style="background:#16a34a">⬇️ Excel 4 Paradas</a><button onclick="location.reload()" class="btn" style="background:black">🔄 Actualizar</button>
<div class="grid"><div class="card">Total<br><b style="font-size:22px">{{total}}</b> viajes</div><div class="card">KMs<br><b style="font-size:22px">{{total_kms}} km</b></div><div class="card">Ingresos<br><b style="font-size:22px">${{total_precio}}</b></div></div>
<div class="card"><canvas id="c1"></canvas></div><div class="card" style="overflow:auto"><table><tr><th>#</th><th>Fecha</th><th>Cliente</th><th>Origen → Destino</th><th>Paradas</th><th>KMs</th><th>$</th><th>Maps</th></tr>{% for v in viajes %}<tr><td>{{loop.index}}</td><td>{{v.fecha}} {{v.hora}}</td><td>{{v.cliente}}</td><td style="max-width:200px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{{v.origen}} → {{v.destino}}</td><td style="max-width:200px">{{v.paradas}}</td><td>{{v.kms}}</td><td>${{v.precio or v.kms}}</td><td><a href="https://www.google.com/maps/dir/{{v.latO}},{{v.lngO}}/{{v.latD}},{{v.lngD}}/" target="_blank">🧭</a></td></tr>{% endfor %}</table></div>
<script>var viajes={{viajes_json|safe}};new Chart(document.getElementById('c1'),{type:'bar',data:{labels:viajes.map((v,[STRIPPED] por viaje'}}}});</script></body></html>
"""

@app.route("/")
def index(): return render_template_string(MAPA_HTML)
@app.route("/api/viaje", methods=["POST"])
def api_viaje():
    data=request.json; viajes.append(data)
    try:
        with open("/tmp/viajes.json","w") as f: json.dump(viajes,f)
    except: pass
    return jsonify({"ok":True})
@app.route("/concentrado")
def concentrado():
    total=len(viajes); tk=sum(float(v.get('kms',0) or 0) for v in viajes); tp=sum(float(v.get('precio',0) or 0) for v in viajes);
    return render_template_string(CONCENTRADO_HTML, viajes=viajes, viajes_json=json.dumps(viajes), total=total, total_kms=round(tk,1), total_precio=round(tp,2))
@app.route("/excel")
def excel():
    output=io.StringIO(); w=csv.writer(output); w.writerow(['#','Fecha','Hora','Cliente','Origen','Parada1','Parada2','Parada3','Destino','KMs','Precio','Paradas Completas'])
    for i,v in enumerate(viajes,1): w.writerow([i,v.get('fecha'),v.get('hora'),v.get('cliente'),v.get('origen'),v.get('parada1'),v.get('parada2'),v.get('parada3'),v.get('destino'),v.get('kms'),v.get('precio'),v.get('paradas')])
    mem=io.BytesIO(); mem.write(output.getvalue().encode('utf-8-sig')); mem.seek(0)
    return send_file(mem, as_attachment=True, download_name=f"AGL_AGS_V35_{datetime.now().strftime('%Y-%m-%d')}.csv", mimetype="text/csv")
try:
    if os.path.exists("/tmp/viajes.json"):
        with open("/tmp/viajes.json") as f: viajes.extend(json.load(f))
except: pass
if __name__=="__main__": app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
