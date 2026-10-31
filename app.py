from flask import Flask, render_template_string, request, jsonify
import json, os, math, time
app = Flask(__name__)
ADMIN_PASSWORD = "AGL2026"
viajes, choferes_db, clientes_db, ubicaciones = [], [], [], {}
def cargar():
  global viajes, choferes_db, clientes_db, ubicaciones
  try:
    if os.path.exists("viajes.json"):
      with open("viajes.json") as f: viajes[:] = json.load(f)
    if os.path.exists("choferes_db.json"):
      with open("choferes_db.json") as f: choferes_db[:] = json.load(f)
    if os.path.exists("clientes_db.json"):
      with open("clientes_db.json") as f: clientes_db[:] = json.load(f)
    if os.path.exists("ubicaciones.json"):
      with open("ubicaciones.json") as f: ubicaciones.update(json.load(f))
  except: pass
def guardar():
  try:
    with open("viajes.json","w") as f: json.dump(viajes,f)  
    with open("choferes_db.json","w") as f: json.dump(choferes_db,f)
    with open("clientes_db.json","w") as f: json.dump(clientes_db,f)    
    with open("ubicaciones.json","w") as f: json.dump(ubicaciones,f)
  except Exception as e: print("Error guardar:", e)
cargar()
def haversine(lat1,lon1,lat2,lon2):
    R=6371; dLat=math.radians(lat2-lat1); dLon=math.radians(lon2-lon1)
    a=math.sin(dLat/2)**2+math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dLon/2)**2
    return R*2*math.atan2(math.sqrt(a),math.sqrt(1-a))

HTML = """<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>AGL V44 - 6 AÑOS + RADAR</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
#alerta-radar{position:fixed;top:0;left:0;right:0;z-index:99999;background:#00c853;color:#fff;padding:16px;text-align:center;font-weight:900;display:none;font-size:15px;animation:parpadeo 1s infinite}
@keyframes parpadeo{0%,100%{background:#00c853}50%{background:#009940}}
*{box-sizing:border-box;margin:0;padding:0;font-family:Arial}body{height:100vh;overflow:hidden;background:#fff}
#map{position:fixed!important;top:0;left:0;width:100%;height:100vh!important;z-index:1}
.top-bar{position:fixed;top:12px;left:12px;right:12px;z-index:10;display:flex;gap:8px;max-width:420px}
.menu-btn{width:46px;height:46px;background:#fff;border:none;border-radius:14px;box-shadow:0 4px 18px rgba(0,0,0,.28);font-size:22px}
.search-card{background:#fff;border-radius:16px;box-shadow:0 8px 28px rgba(0,0,0,.26);padding:6px 10px;flex:1}
.item{display:flex;align-items:center;gap:8px;padding:8px 4px}.item+.item{border-top:1px solid #f0f0f0}
.dot{width:8px;height:8px;border-radius:50%}.o{background:#00c853}.d{background:#ff3b30}
input{flex:1;border:none;outline:none;font-size:13px;font-weight:600;background:transparent}
#menu{position:fixed;top:0;left:-100%;width:86%;max-width:360px;height:100vh;background:#fff;z-index:30;transition:.28s;overflow-y:auto}
#menu.act{left:0}.overlay{position:fixed;inset:0;background:rgba(0,0,0,.35);z-index:20;display:none}.overlay.act{display:block}
.menu-header{padding:20px 16px 12px;border-bottom:1px solid #eee;display:flex;justify-content:space-between;align-items:center}
.menu-body{padding:14px}.menu-linea{padding:14px 4px;font-size:16px;border-bottom:1px solid #f5f5f5;cursor:pointer;display:flex;justify-content:space-between}
.parada-extra{display:none}
#cotizacion{position:fixed;bottom:82px;left:12px;right:12px;z-index:11;background:#fff;border-radius:16px;padding:12px 16px;display:none;box-shadow:0 8px 28px rgba(0,0,0,.32);max-width:420px;margin:auto;text-align:center}
.btn-confirm{position:fixed;bottom:12px;left:12px;right:12px;z-index:11;background:#000;color:#fff;font-weight:800;padding:16px;border:none;border-radius:16px;max-width:420px;margin:auto;display:none;font-size:15px}
#modal-rol{position:fixed;inset:0;z-index:99999;background:rgba(0,0,0,.92);display:flex;align-items:center;justify-content:center;padding:20px}.box-rol{background:#fff;border-radius:20px;padding:24px;width:100%;max-width:360px;text-align:center}
.inp{width:100%;padding:13px;margin:7px 0;border-radius:10px;border:1px solid #ddd;background:#f9f9f9}
</style></head><body>
<div id="alerta-radar">🚨 VIAJE CERCA! <span id="radar-txt"></span></div>
<audio id="beep" src="https://actions.google.com/sounds/v1/alarms/beep_short.ogg"></audio>

<div id="modal-rol"><div class="box-rol"><h2>🚕 AGL Transporte</h2><p style="margin:8px 0 16px;color:#666;font-size:11px">V44 - MIN 6 AÑOS + BANDERAZO $40</p>
<button type="button" onclick="elegirRol('cliente')" style="width:100%;padding:16px;border:none;border-radius:14px;font-weight:800;margin-bottom:10px;background:#000;color:#fff">👤 SOY CLIENTE</button>
<button type="button" onclick="elegirRol('chofer')" style="width:100%;padding:16px;border:none;border-radius:14px;font-weight:800;margin-bottom:10px;background:#00c853;color:#fff">🚗 SOY CHOFER</button>
<button type="button" onclick="elegirRol('admin')" style="width:100%;padding:16px;border:none;border-radius:14px;font-weight:800;background:#0a3552;color:#fff">🔐 SOY ADMIN</button></div></div>

<div id="vista-cliente" style="display:none">
<div id="box-login-cliente" style="padding:20px;max-width:400px;margin:70px auto 0;background:#fff;position:relative;z-index:20;border-radius:16px"><h2 style="text-align:center">👤 Cliente</h2><div id="form-login-c"><input id="cli-tel" class="inp" placeholder="Celular"><input id="cli-pass" class="inp" type="password" placeholder="Contraseña"><button onclick="clienteLogin()" style="width:100%;padding:13px;background:#000;color:#fff;border:none;border-radius:10px">ENTRAR</button><p style="text-align:center;margin:10px 0">¿Nuevo?</p><button onclick="mostrarRegistroCli()" style="width:100%;padding:11px;background:#fff;border:1px solid #000;border-radius:10px">REGISTRARME</button><button onclick="volverAlInicio()" style="width:100%;margin-top:10px;padding:11px;background:#eee;border:none;border-radius:10px">⬅ MENU</button><p id="msg-cli" style="color:red;text-align:center;font-size:12px"></p></div><div id="form-registro-c" style="display:none"><input id="cli-reg-nombre" class="inp" placeholder="Nombre"><input id="cli-reg-tel" class="inp" placeholder="Celular"><input id="cli-reg-pass" class="inp" type="password" placeholder="Contraseña"><button onclick="clienteRegistrar()" style="width:100%;padding:13px;background:#00c853;color:#fff;border:none;border-radius:10px">CREAR CUENTA</button><button onclick="mostrarLoginCli()" style="width:100%;padding:10px;background:none;border:none;color:#1976d2">Ya tengo cuenta</button></div></div>
<div id="box-cliente-viaje" style="display:none"><div id="map"></div><button onclick="miUbicacion()" style="position:fixed;bottom:160px;right:14px;z-index:12;width:50px;height:50px;background:#fff;border:none;border-radius:50%;box-shadow:0 4px 18px rgba(0,0,0,.3)">📍</button>
<div class="top-bar"><button class="menu-btn" onclick="toggleMenu()">☰</button><div class="search-card"><div class="item"><div class="dot o"></div><input id="origen" placeholder="Origen"></div><div class="item parada-extra" id="boxP1"><div class="dot" style="background:#ffcc00"></div><input id="parada1" placeholder="Parada 1"></div><div class="item parada-extra" id="boxP2"><div class="dot" style="background:#ff9500"></div><input id="parada2" placeholder="Parada 2"></div><div class="item parada-extra" id="boxP3"><div class="dot" style="background:#00e5ff"></div><input id="parada3" placeholder="Parada 3"></div><div class="item"><div class="dot d"></div><input id="destino" placeholder="Destino"></div></div></div>
<div id="menu"><div class="menu-header"><b>🚕 AGL AGS</b><button onclick="toggleMenu()" style="width:34px;height:34px;border-radius:50%;background:#111;color:#fff;border:none">✕</button></div>
<div class="menu-body">
  <div style="background:#eef5ff;padding:14px;border-radius:14px;margin-bottom:14px;border:1px solid #b5d0ff">
    <b style="font-size:14px">📅 Programar flete</b><br><span style="font-size:11px;color:#555">Fecha y hora</span>
    <div style="display:flex;gap:8px;margin-top:10px">
      <input type="date" id="fecha" style="flex:1;padding:11px;border-radius:10px;border:1px solid #aaa;background:#fff;font-weight:700">
      <input type="time" id="hora" style="flex:1;padding:11px;border-radius:10px;border:1px solid #aaa;background:#fff;font-weight:700">
    </div>
  </div>
  <div class="menu-linea" onclick="agregarParada()"><div><b>agregar parada</b><br><span id="txt-paradas">0 / 3</span></div><span>➕</span></div>
  <div class="menu-linea" onclick="borrarTodo()"><div><b>corregir orden</b></div><span>✏️</span></div>
  <div class="menu-linea" onclick="volverAlInicio()"><div><b>volver a menu inicial</b></div><span>🏠</span></div>
  <div style="margin-top:20px"><button onclick="cerrarSesionTotal()" style="width:100%;background:#ffebee;color:#c62828;border:none;padding:12px;border-radius:10px;font-weight:700">Cerrar sesión</button></div>
</div></div><div class="overlay" id="overlay" onclick="toggleMenu()"></div>
<div id="cotizacion"><div id="dist" style="font-size:13px;color:#333;font-weight:600"></div><b id="precio" style="font-size:26px;color:#000">$0 MXN</b></div>
<button class="btn-confirm" id="btnPedir" onclick="pedir()">Confirmar Flete $0</button>
</div></div>

<div id="vista-chofer" style="display:none"><div id="box-login-chofer" style="padding:20px;max-width:400px;margin:20px auto;background:#fff;border-radius:16px"><h2 style="text-align:center">🚗 Chofer</h2><div id="form-login"><input id="chofer-tel" class="inp" placeholder="Celular"><input id="chofer-pass" class="inp" type="password" placeholder="Contraseña"><button onclick="choferLogin()" style="width:100%;padding:13px;background:#000;color:#fff;border:none;border-radius:10px">ENTRAR</button><button onclick="mostrarRegistroChofer()" style="width:100%;padding:11px;background:#fff;border:1px solid #000;border-radius:10px;margin-top:10px">REGISTRARME</button><button onclick="volverAlInicio()" style="width:100%;margin-top:10px;padding:11px;background:#eee;border:none;border-radius:10px">⬅ MENU</button><p id="msg-chofer" style="color:red;text-align:center;font-size:12px"></p></div>
<div id="form-registro" style="display:none">
<input id="reg-nombre" class="inp" placeholder="Nombre completo">
<input id="reg-tel" class="inp" placeholder="Celular">
<input id="reg-placas" class="inp" placeholder="Placas - Ej: ABC-123-A" style="text-transform:uppercase">
<input id="reg-modelo" class="inp" placeholder="Modelo con año - Ej: Versa 2022 blanco">
<input id="reg-pass" type="password" class="inp" placeholder="Contraseña">
<button onclick="choferRegistrar()" style="width:100%;padding:13px;background:#00c853;color:#fff;border:none;border-radius:10px">CREAR CHOFER</button>
<button onclick="mostrarLoginChofer()" style="width:100%;padding:10px;background:none;border:none;color:#1976d2">Ya tengo cuenta</button>
</div></div><div id="box-viajes-chofer" style="display:none"><div style="background:#000;color:#fff;padding:12px;display:flex;justify-content:space-between"><span id="nombre-chofer-log">Chofer</span><button onclick="choferLogout()" style="background:#ff5252;color:#fff;border:none;padding:6px 10px;border-radius:6px">Salir</button></div><div style="padding:10px"><div id="lista-viajes-chofer"></div></div></div></div>

<div id="vista-admin" style="display:none"><div id="admin-login" style="padding:20px;max-width:400px;margin:80px auto;background:#fff;border-radius:16px"><h2 style="text-align:center">🔐 ADMIN</h2><input id="admin-pass-input" type="password" class="inp" placeholder="AGL2026"><button onclick="adminLogin()" style="width:100%;padding:14px;background:#000;color:#fff;border:none;border-radius:10px">ENTRAR</button><button onclick="volverAlInicio()" style="width:100%;margin-top:10px;padding:12px;background:#eee;border:none;border-radius:12px">⬅ VOLVER</button></div><div id="admin-panel" style="display:none;padding:12px;background:#eef2f7;min-height:100vh"><h1>🔐 ADMIN V44</h1><div style="display:flex;gap:6px;margin:12px 0"><button onclick="adminTab('viajes')" id="btn-viajes" style="flex:1;padding:12px;background:#000;color:#fff;border:none;border-radius:10px;font-weight:800">Viajes</button><button onclick="adminTab('choferes')" id="btn-choferes" style="flex:1;padding:12px;background:#fff;border:1px solid #000;border-radius:10px;font-weight:800">Choferes</button><button onclick="adminTab('clientes')" id="btn-clientes" style="flex:1;padding:12px;background:#fff;border:1px solid #000;border-radius:10px;font-weight:800">Clientes</button></div><div id="admin-viajes"></div><div id="admin-choferes" style="display:none"></div><div id="admin-clientes" style="display:none"></div><button onclick="volverAlInicio()" style="margin-top:12px;padding:12px;width:100%;background:#000;color:#fff;border:none;border-radius:10px">Volver</button></div></div>

<script>
let map=null,origenMarker=null,destinoMarker=null,parada1Marker=null,parada2Marker=null,parada3Marker=null,routeLine,kmActual=0,precioActual=0,tiempoActual=0,numParadasVisibles=0,miChofer=null,miPos={lat:21.8853,lng:-102.2916},origenLatLng=null,destinoLatLng=null;
function toggleMenu(){document.getElementById('menu').classList.toggle('act');document.getElementById('overlay').classList.toggle('act');}
function initMap(){
  if(map){setTimeout(()=>map.invalidateSize(),200);return;}
  map=L.map('map',{zoomControl:false}).setView([21.8853,-102.2916],13);
  L.tileLayer('https://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',{subdomains:['mt0','mt1','mt2','mt3'],maxZoom:20}).addTo(map);
  map.on('click',e=>{
    if(!origenMarker){crearOrigen(e.latlng);return;}
    if(numParadasVisibles>=1&&!parada1Marker){crearParada1(e.latlng);return;}
    if(numParadasVisibles>=2&&!parada2Marker){crearParada2(e.latlng);return;}
    if(numParadasVisibles>=3&&!parada3Marker){crearParada3(e.latlng);return;}
    if(!destinoMarker){crearDestino(e.latlng);return;}
  });
  let hoy=new Date().toISOString().split('T')[0]; let now=new Date(); now.setMinutes(now.getMinutes()+30); let hora=now.toTimeString().slice(0,5);
  let f=document.getElementById('fecha'); if(f&&!f.value) f.value=hoy; let h=document.getElementById('hora'); if(h&&!h.value) h.value=hora;
}
function elegirRol(r){localStorage.setItem('rol_AGL',r);document.getElementById('modal-rol').style.display='none';if(r==='chofer'){document.getElementById('vista-cliente').style.display='none';document.getElementById('vista-chofer').style.display='block';document.getElementById('vista-admin').style.display='none';verificarSesionChofer();}else if(r==='admin'){document.getElementById('vista-cliente').style.display='none';document.getElementById('vista-chofer').style.display='none';document.getElementById('vista-admin').style.display='block';}else{document.getElementById('vista-chofer').style.display='none';document.getElementById('vista-admin').style.display='none';document.getElementById('vista-cliente').style.display='block';initMap();verificarSesionCliente();}}
function volverAlInicio(){localStorage.removeItem('rol_AGL');document.getElementById('vista-cliente').style.display='none';document.getElementById('vista-chofer').style.display='none';document.getElementById('vista-admin').style.display='none';document.getElementById('modal-rol').style.display='flex';document.getElementById('menu').classList.remove('act');document.getElementById('overlay').classList.remove('act');if(map){map.remove();map=null;}origenMarker=null;destinoMarker=null;parada1Marker=null;parada2Marker=null;parada3Marker=null;routeLine=null;}
function cerrarSesionTotal(){localStorage.clear();location.reload();}
const verdeIcon=new L.Icon({iconUrl:'https://cdn.jsdelivr.net/gh/pointhi/leaflet-color-markers@master/img/marker-icon-2x-green.png',shadowUrl:'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',iconSize:[35,55],iconAnchor:[17,55]});
const rojoIcon=new L.Icon({iconUrl:'https://cdn.jsdelivr.net/gh/pointhi/leaflet-color-markers@master/img/marker-icon-2x-red.png',shadowUrl:'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',iconSize:[35,55],iconAnchor:[17,55]});
const amarilloIcon=new L.Icon({iconUrl:'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-yellow.png',shadowUrl:'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',iconSize:[35,55],iconAnchor:[17,55]});
const naranjaIcon=new L.Icon({iconUrl:'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-orange.png',shadowUrl:'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',iconSize:[35,55],iconAnchor:[17,55]});
const azulIcon=new L.Icon({iconUrl:'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',shadowUrl:'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',iconSize:[35,55],iconAnchor:[17,55]});
function makeDraggable(m, cb){m.on('touchstart mousedown', ()=>{ if(map) map.dragging.disable(); }); m.on('dragend', (ev)=>{ if(map) map.dragging.enable(); cb(ev.target.getLatLng()); }); m.on('touchend', ()=>{ if(map) map.dragging.enable(); });}
async function ponerDireccion(lat,lng,inputId){
  try{
    let r=await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`);
    let j=await r.json();
    if(j && j.display_name){ document.getElementById(inputId).value=j.display_name.split(',').slice(0,4).join(', '); return; }
  }catch(e){}
  document.getElementById(inputId).value=lat.toFixed(5)+', '+lng.toFixed(5);
}
function crearOrigen(ll){origenLatLng=ll; if(!origenMarker){origenMarker=L.marker(ll,{draggable:true,autoPan:true,icon:verdeIcon}).addTo(map); makeDraggable(origenMarker, (nl)=>{origenLatLng=nl; ponerDireccion(nl.lat,nl.lng,'origen'); trazarLocal();});}else origenMarker.setLatLng(ll); ponerDireccion(ll.lat,ll.lng,'origen'); trazarLocal();}
function crearDestino(ll){destinoLatLng=ll; if(!destinoMarker){destinoMarker=L.marker(ll,{draggable:true,autoPan:true,icon:rojoIcon}).addTo(map); makeDraggable(destinoMarker, (nl)=>{destinoLatLng=nl; ponerDireccion(nl.lat,nl.lng,'destino'); trazarLocal();});}else destinoMarker.setLatLng(ll); ponerDireccion(ll.lat,ll.lng,'destino'); trazarLocal();}
function crearParada1(ll){if(!parada1Marker){parada1Marker=L.marker(ll,{draggable:true,autoPan:true,icon:amarilloIcon}).addTo(map); makeDraggable(parada1Marker, (nl)=>{ponerDireccion(nl.lat,nl.lng,'parada1'); trazarLocal();});}else parada1Marker.setLatLng(ll); ponerDireccion(ll.lat,ll.lng,'parada1'); trazarLocal();}
function crearParada2(ll){if(!parada2Marker){parada2Marker=L.marker(ll,{draggable:true,autoPan:true,icon:naranjaIcon}).addTo(map); makeDraggable(parada2Marker, (nl)=>{ponerDireccion(nl.lat,nl.lng,'parada2'); trazarLocal();});}else parada2Marker.setLatLng(ll); ponerDireccion(ll.lat,ll.lng,'parada2'); trazarLocal();}
function crearParada3(ll){if(!parada3Marker){parada3Marker=L.marker(ll,{draggable:true,autoPan:true,icon:azulIcon}).addTo(map); makeDraggable(parada3Marker, (nl)=>{ponerDireccion(nl.lat,nl.lng,'parada3'); trazarLocal();});}else parada3Marker.setLatLng(ll); ponerDireccion(ll.lat,ll.lng,'parada3'); trazarLocal();}
function agregarParada(){if(numParadasVisibles>=3){alert('Máximo 3 paradas');return;}numParadasVisibles++;document.getElementById('boxP'+numParadasVisibles).style.display='flex';document.getElementById('txt-paradas').innerText=numParadasVisibles+' / 3';toggleMenu();}
function miUbicacion(){navigator.geolocation.getCurrentPosition(p=>{let ll={lat:p.coords.latitude,lng:p.coords.longitude};miPos=ll;crearOrigen(ll);if(map) map.setView([ll.lat,ll.lng],16); ponerDireccion(ll.lat,ll.lng,'origen');});}
function calcDist(lat1,lon1,lat2,lon2){let R=6371;let dLat=(lat2-lat1)*Math.PI/180;let dLon=(lon2-lon1)*Math.PI/180;let a=Math.sin(dLat/2)**2+Math.cos(lat1*Math.PI/180)*Math.cos(lat2*Math.PI/180)*Math.sin(dLon/2)**2;return R*2*Math.atan2(Math.sqrt(a),Math.sqrt(1-a));}
function calcularPrecio(km){
    let arranque = 40; let costoKm = 10; let precio;
    if(km <= 1){ precio = arranque; } else { precio = Math.round(arranque + ((km - 1) * costoKm)); }
    if(precio < 80) precio = 80; return precio;
}
function trazarLocal(){
    if(!origenMarker) return; let pts=[]; pts.push(origenMarker.getLatLng());
    if(parada1Marker) pts.push(parada1Marker.getLatLng()); if(parada2Marker) pts.push(parada2Marker.getLatLng()); if(parada3Marker) pts.push(parada3Marker.getLatLng()); if(destinoMarker) pts.push(destinoMarker.getLatLng());
    if(pts.length<2) return;
    let dist=0; for(let i=0;i<pts.length-1;i++){dist+=calcDist(pts[i].lat,pts[i].lng,pts[i+1].lat,pts[i+1].lng);}
    kmActual=Math.round(dist*10)/10; if(kmActual<0.8)kmActual=0.8;
    precioActual=calcularPrecio(kmActual); tiempoActual=Math.round(kmActual*3.2);
    document.getElementById('cotizacion').style.display='block';
    document.getElementById('dist').innerText=kmActual+' km - '+tiempoActual+' min para el cliente';
    document.getElementById('precio').innerText='$'+precioActual+' MXN';
    document.getElementById('btnPedir').innerText='Confirmar Flete $'+precioActual+' - '+kmActual+'km';
    document.getElementById('btnPedir').style.display='block';
    trazarRutaReal(pts);
}
async function trazarRutaReal(pts){
    try{
      let s=pts.map(p=>p.lng+','+p.lat).join(';');
      let r=await fetch(`https://router.project-osrm.org/route/v1/driving/${s}?overview=full&geometries=geojson`);
      let j=await r.json(); if(!j.routes||!j.routes[0]) return;
      let route=j.routes[0];
      kmActual=Math.round(route.distance/100)/10; if(kmActual<0.8)kmActual=0.8;
      tiempoActual=Math.round(route.duration/60);
      precioActual=calcularPrecio(kmActual);
      if(routeLine) map.removeLayer(routeLine);
      routeLine=L.polyline(route.geometry.coordinates.map(c=>[c[1],c[0]]),{color:'#276EF1',weight:6}).addTo(map);
      document.getElementById('dist').innerText=kmActual+' km - '+tiempoActual+' min para el cliente';
      document.getElementById('precio').innerText='$'+precioActual+' MXN';
      document.getElementById('btnPedir').innerText='Confirmar Flete $'+precioActual+' - '+kmActual+'km';
      map.fitBounds(routeLine.getBounds(),{padding:[80,80]});
    }catch(e){
      if(routeLine) map.removeLayer(routeLine);
      routeLine=L.polyline(pts,{color:'#276EF1',weight:6,dashArray:'8,8'}).addTo(map);
    }
}
let intervaloCliente = null;
async function pedir(){
  if(!precioActual||!origenLatLng) return alert('Toca el mapa para origen y destino');
  let ca=JSON.parse(localStorage.getItem('clienteActual')||'null');
  let fecha=document.getElementById('fecha').value; let hora=document.getElementById('hora').value;
  if(!fecha||!hora){alert('Abre el menú ☰ y selecciona fecha y hora'); toggleMenu(); return;}
  let id='V'+Date.now();
  let data={id:id,cliente:ca?ca.nombre:'Cliente',cliente_tel:ca?ca.tel:'',fecha:fecha,hora:hora,origen:document.getElementById('origen').value,destino:document.getElementById('destino').value,origen_lat:origenLatLng.lat,origen_lng:origenLatLng.lng,destino_lat:destinoLatLng?destinoLatLng.lat:0,destino_lng:destinoLatLng?destinoLatLng.lng:0,kms:kmActual,precio:precioActual,status:'pendiente',timestamp:new Date().toISOString()};
  await fetch('/api/viaje',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
  localStorage.setItem('viajeActualId', id);
  alert('✅ Flete CONFIRMADO '+fecha+' '+hora+' $'+precioActual);
  // Ahora muestra seguimiento para cliente
  if(intervaloCliente) clearInterval(intervaloCliente);
  intervaloCliente = setInterval(()=>verEstadoMiViaje(id), 4000);
  verEstadoMiViaje(id);
}
function borrarTodo(){document.getElementById('origen').value="";document.getElementById('destino').value="";document.getElementById('parada1').value="";document.getElementById('parada2').value="";document.getElementById('parada3').value="";document.getElementById('cotizacion').style.display="none";document.getElementById('btnPedir').style.display="none";if(origenMarker){map.removeLayer(origenMarker);origenMarker=null;}if(destinoMarker){map.removeLayer(destinoMarker);destinoMarker=null;}if(parada1Marker){map.removeLayer(parada1Marker);parada1Marker=null;}if(parada2Marker){map.removeLayer(parada2Marker);parada2Marker=null;}if(parada3Marker){map.removeLayer(parada3Marker);parada3Marker=null;}if(routeLine){map.removeLayer(routeLine);routeLine=null;}precioActual=0; kmActual=0; origenLatLng=null; destinoLatLng=null; numParadasVisibles=0;document.getElementById('boxP1').style.display='none';document.getElementById('boxP2').style.display='none';document.getElementById('boxP3').style.display='none';document.getElementById('txt-paradas').innerText='0 / 3';}
function mostrarRegistroChofer(){document.getElementById('form-login').style.display='none';document.getElementById('form-registro').style.display='block';}
function mostrarLoginChofer(){document.getElementById('form-registro').style.display='none';document.getElementById('form-login').style.display='block';}

async function choferRegistrar(){
  let n=document.getElementById('reg-nombre').value.trim(),
      t=document.getElementById('reg-tel').value.trim(),
      pl=document.getElementById('reg-placas').value.trim().toUpperCase(),
      mo=document.getElementById('reg-modelo').value.trim(),
      p=document.getElementById('reg-pass').value.trim();
  if(!n||!t||!pl||!mo||!p){ alert('Llena todo: nombre, cel, placas y modelo con año'); return; }
  let match = mo.match(/(19|20)\\d{2}/);
  if(!match){ alert('En modelo escribe el AÑO. Ej: Versa 2022 blanco'); return; }
  let anio = parseInt(match[0]);
  let anioActual = new Date().getFullYear();
  let anioMinimo = anioActual - 6;
  if(anio < anioMinimo){
    alert('❌ No aceptamos coches con más de 6 años.\\nTu coche es '+anio+' y el mínimo es '+anioMinimo+'.\\nSolo '+anioMinimo+' en adelante.');
    return;
  }
  if(anio > anioActual + 1){ alert('El año no puede ser mayor a '+(anioActual+1)); return; }
  let res=await fetch('/api/chofer/registrar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({nombre:n,tel:t,placas:pl,modelo:mo,anio:anio,pass:p})});
  let d=await res.json();
  if(!d.ok){alert(d.error);return;}
  localStorage.setItem('choferActual',JSON.stringify(d.chofer));
  verificarSesionChofer();
}

async function choferLogin(){let t=document.getElementById('chofer-tel').value.trim(),c=document.getElementById('chofer-pass').value.trim();let res=await fetch('/api/chofer/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({tel:t,pass:c})});let d=await res.json();if(!d.ok){document.getElementById('msg-chofer').innerText=d.error;return;}localStorage.setItem('choferActual',JSON.stringify(d.chofer));verificarSesionChofer();}
let radarInterval=null, ultimoViajeId=null;
function verificarSesionChofer(){
  let a=JSON.parse(localStorage.getItem('choferActual')||'null');
  let va=JSON.parse(localStorage.getItem('viajeActivo')||'null');
  if(a){
    document.getElementById('box-login-chofer').style.display='none';
    document.getElementById('box-viajes-chofer').style.display='block';
    document.getElementById('nombre-chofer-log').innerText=a.nombre;
    miChofer=a;
    if(va){
      viajeActivo=va;
      mostrarViajeActivo(); // si ya tiene viaje, NO inicie radar
    } else {
      iniciarRadarAGL();
    }
  }else{
    document.getElementById('box-login-chofer').style.display='block';
    document.getElementById('box-viajes-chofer').style.display='none';
  }
}
function iniciarRadarAGL(){
  if(navigator.geolocation){
    navigator.geolocation.watchPosition(p=>{
      miPos={lat:p.coords.latitude,lng:p.coords.longitude};
      fetch('/api/chofer/heartbeat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({tel:miChofer.tel,lat:miPos.lat,lng:miPos.lng})});
    },null,{enableHighAccuracy:true});
  }
  if(radarInterval) clearInterval(radarInterval);
  radarInterval=setInterval(()=>{ mostrarViajesChofer(); }, 3000);
  mostrarViajesChofer();
}
function mostrarViajesChofer(){
  let va = localStorage.getItem('viajeActivo');
  if(va){ // si hay viaje activo, no sobreescribas
    return;
  }
  fetch('/api/viajes_cercanos?lat='+miPos.lat+'&lng='+miPos.lng).then(r=>r.json()).then(data=>{
    let lista=document.getElementById('lista-viajes-chofer');
    let fil=data.filter(x=>x.status==='pendiente');
    if(fil.length>0 && fil[0].id!==ultimoViajeId){
      ultimoViajeId=fil[0].id;
      document.getElementById('radar-txt').innerText=fil[0].dist_km+'km - $'+fil[0].precio;
      document.getElementById('alerta-radar').style.display='block';
      try{ document.getElementById('beep').play(); }catch(e){}
      if(navigator.vibrate) navigator.vibrate([300,100,300]);
      setTimeout(()=>{ document.getElementById('alerta-radar').style.display='none'; }, 6000);
    }
    lista.innerHTML=fil.map(x=>`<div style="border:2px solid #00c853;border-radius:12px;padding:12px;margin:8px 0;background:#f0fff4"><b>📍 A ${x.dist_km}km - $${x.precio}</b><br>${x.cliente} | ${x.kms}km<br>📅 ${x.fecha} ${x.hora}<br><span style="font-size:11px">${x.origen}<br>→ ${x.destino}</span><br><button onclick="tomarViaje('${x.id}')" style="background:#000;color:#fff;border:none;padding:12px;width:100%;border-radius:10px;margin-top:8px;font-weight:800">TOMAR $${x.precio}</button></div>`).join('')||'<div style="padding:30px;text-align:center;color:#888">🔍 Radar AGL activo<br>Buscando viajes en 15km...<br><br>Tu pos: '+miPos.lat.toFixed(4)+'</div>';
  });
}
function choferLogout(){ if(radarInterval) clearInterval(radarInterval); localStorage.removeItem('choferActual'); location.reload(); }    
function mostrarRegistroCli(){document.getElementById('form-login-c').style.display='none';document.getElementById('form-registro-c').style.display='block';}
function mostrarLoginCli(){document.getElementById('form-registro-c').style.display='none';document.getElementById('form-login-c').style.display='block';}
async function clienteRegistrar(){let n=document.getElementById('cli-reg-nombre').value.trim(),t=document.getElementById('cli-reg-tel').value.trim(),p=document.getElementById('cli-reg-pass').value.trim();let res=await fetch('/api/cliente/registrar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({nombre:n,tel:t,pass:p})});let d=await res.json();if(!d.ok){alert(d.error);return;}localStorage.setItem('clienteActual',JSON.stringify(d.cliente));verificarSesionClienteLogged();}
async function clienteLogin(){let t=document.getElementById('cli-tel').value.trim(),c=document.getElementById('cli-pass').value.trim();let res=await fetch('/api/cliente/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({tel:t,pass:c})});let d=await res.json();if(!d.ok){document.getElementById('msg-cli').innerText=d.error;return;}localStorage.setItem('clienteActual',JSON.stringify(d.cliente));verificarSesionClienteLogged();}
function verificarSesionCliente(){let ca=JSON.parse(localStorage.getItem('clienteActual')||'null'); initMap(); if(ca){document.getElementById('box-login-cliente').style.display='none';document.getElementById('box-cliente-viaje').style.display='block';setTimeout(()=>{if(map) map.invalidateSize();},400);}else{document.getElementById('box-login-cliente').style.display='block';document.getElementById('box-cliente-viaje').style.display='none';}}
function verificarSesionClienteLogged(){
  initMap();
  document.getElementById('box-login-cliente').style.display='none';
  document.getElementById('box-cliente-viaje').style.display='block';
  setTimeout(()=>{if(map) map.invalidateSize();},400);

  // --- AGREGA ESTO DESDE AQUÍ ---
  let idGuardado = localStorage.getItem('viajeActualId');
  if(idGuardado){
    if(intervaloCliente) clearInterval(intervaloCliente);
    intervaloCliente = setInterval(()=>verEstadoMiViaje(idGuardado), 4000);
    verEstadoMiViaje(idGuardado);
  }
  // --- HASTA AQUÍ ---
}

// Y agrega también esta función nueva ABAJO de verificarSesionClienteLogged:

async function verEstadoMiViaje(id){
  try{
    let r = await fetch('/api/viaje/estado/'+id);
    let v = await r.json();
    if(!v || !v.id) return;

    let cot = document.getElementById('cotizacion');
    cot.style.display='block';

    if(v.status === 'pendiente'){
      cot.innerHTML = `<b>🔍 BUSCANDO CHOFER...</b><br><span style="font-size:12px">${v.origen} → ${v.destino}</span><br>💰 $${v.precio}`;
    } else if(v.status === 'tomado' || v.status === 'en_curso'){
      // TARJETA FIJA 
      cot.innerHTML = `
        <div style="background:#000;color:#fff;padding:12px;border-radius:12px;text-align:left">
          <b style="color:#00e676">✅ CHOFER EN CAMINO </b><br>
          <b>Chofer: ${v.chofer_nombre}</b><br>
          🚗 ${v.chofer_modelo}<br>
          🔖 PLACA: <b style="font-size:20px;letter-spacing:1px">${v.chofer_placas}</b><br>
          <a href="tel:${v.chofer_tel}" style="display:block;background:#fff;color:#000;padding:10px;border-radius:8px;margin-top:8px;text-align:center;text-decoration:none;font-weight:800">📞 LLAMAR CHOFER ${v.chofer_tel}</a>
        </div>`;
    } else if(v.status === 'finalizado'){
      clearInterval(intervaloCliente);
      localStorage.removeItem('viajeActualId');
      cot.innerHTML = `<b>✅ VIAJE FINALIZADO</b>`;
      setTimeout(()=>{ cot.style.display='none'; }, 4000);
    }
  }catch(e){}
}  
let viajeActivo = null;
async function tomarViaje(id){
  let ch=JSON.parse(localStorage.getItem('choferActual'));
  let res=await fetch('/api/viaje/tomar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:id,chofer_tel:ch.tel,chofer_nombre:ch.nombre,chofer_placas:ch.placas||'',chofer_modelo:ch.modelo||''})});
  let d=await res.json();
  if(!d.ok) return alert('Ya lo tomó otro');
  viajeActivo = d.viaje;
  localStorage.setItem('viajeActivo', JSON.stringify(viajeActivo));
  mostrarViajeActivo();
}

function mostrarViajeActivo(){
  let v = viajeActivo || JSON.parse(localStorage.getItem('viajeActivo')||'null');
  if(!v) return;
document.getElementById('lista-viajes-chofer').innerHTML = `
    <div style="background:#000;color:#fff;padding:8px 10px;border-radius:10px;margin-bottom:6px;font-size:12px;line-height:1.2">
      <b>✅ ${v.cliente} - $${v.precio} | ${v.kms}km</b> | ${v.cliente_tel}
    </div>
    <div style="background:#fff;padding:8px;border-radius:10px;border:1px solid #000">
      <div style="font-size:11px;line-height:1.3"><b>O:</b> ${v.origen}<br><b>D:</b> ${v.destino}</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:6px">
        <a href="https://www.google.com/maps/dir/?api=1&destination=${v.origen_lat},${v.origen_lng}" target="_blank" style="display:block;background:#276EF1;color:#fff;text-align:center;padding:8px;border-radius:8px;text-decoration:none;font-weight:800;font-size:11px">📍 ORIGEN</a>
        <a href="https://www.google.com/maps/dir/?api=1&origin=${v.origen_lat},${v.origen_lng}&destination=${v.destino_lat},${v.destino_lng}" target="_blank" style="display:block;background:#000;color:#FFD700;border:1px solid #FFD700;text-align:center;padding:8px;border-radius:8px;text-decoration:none;font-weight:800;font-size:11px">🗺️ RECORRIDO</a>
        <a href="tel:${v.cliente_tel}" style="display:block;background:#fff;border:1px solid #000;color:#000;text-align:center;padding:8px;border-radius:8px;text-decoration:none;font-weight:800;font-size:11px">📞 LLAMAR</a>
        <a href="https://wa.me/52${v.cliente_tel}" target="_blank" style="display:block;background:#25D366;color:#fff;text-align:center;padding:8px;border-radius:8px;text-decoration:none;font-weight:800;font-size:11px">💬 WHATSAPP</a>
      </div>
      <button onclick="finalizarViaje()" style="width:100%;background:#ff3b30;color:#fff;border:none;padding:8px;border-radius:8px;font-weight:800;margin-top:6px;font-size:11px">🏁 FINALIZAR</button>
    </div>
    <div id="map-chofer" style="height:280px;margin-top:6px;border-radius:10px"></div>
  `;
    <div style="background:#fff;padding:12px;border-radius:12px;border:2px solid #000">
      <b>ORIGEN:</b><br>${v.origen}<br><br>
      <b>DESTINO:</b><br>${v.destino}<br><br>
      <a href="https://www.google.com/maps/dir/?api=1&destination=${v.origen_lat},${v.origen_lng}" target="_blank" style="display:block;background:#276EF1;color:#fff;text-align:center;padding:14px;border-radius:10px;text-decoration:none;font-weight:800;margin-bottom:8px">📍 IR A ORIGEN - GOOGLE MAPS</a>
      <a href="https://www.google.com/maps/dir/${encodeURIComponent(v.origen)}/${encodeURIComponent(v.destino)}/" target="_blank" style="display:block;background:#000;color:#FFD700;border:2px solid #FFD700;text-align:center;padding:14px;border-radius:10px;text-decoration:none;font-weight:800;margin-bottom:8px">🗺️ VER RECORRIDO COMPLETO - ${v.kms}km</a>
      <a href="https://waze.com/ul?ll=${v.origen_lat},${v.origen_lng}&navigate=yes" target="_blank" style="display:block;background:#00c853;color:#fff;text-align:center;padding:14px;border-radius:10px;text-decoration:none;font-weight:800;margin-bottom:8px">🚗 ABRIR EN WAZE</a>
      <a href="tel:${v.cliente_tel}" style="display:block;background:#fff;border:2px solid #000;color:#000;text-align:center;padding:14px;border-radius:10px;text-decoration:none;font-weight:800;margin-bottom:8px">📞 LLAMAR CLIENTE</a>
      <a href="https://wa.me/52${v.cliente_tel}" target="_blank" style="display:block;background:#25D366;color:#fff;text-align:center;padding:14px;border-radius:10px;text-decoration:none;font-weight:800;margin-bottom:10px">💬 WHATSAPP CLIENTE</a>
      <button onclick="finalizarViaje()" style="width:100%;background:#ff3b30;color:#fff;border:none;padding:14px;border-radius:10px;font-weight:800">🏁 FINALIZAR VIAJE</button>
    </div>
    <div id="map-chofer" style="height:300px;margin-top:10px;border-radius:14px"></div>
  `;
  setTimeout(()=>{
    let mc = L.map('map-chofer').setView([v.origen_lat, v.origen_lng], 14);
    L.tileLayer('https://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',{subdomains:['mt0','mt1','mt2','mt3']}).addTo(mc);
    L.marker([v.origen_lat, v.origen_lng], {icon: verdeIcon}).addTo(mc).bindPopup("ORIGEN").openPopup();
    if(v.destino_lat) L.marker([v.destino_lat, v.destino_lng], {icon: rojoIcon}).addTo(mc).bindPopup("DESTINO");
  }, 300);
}

function finalizarViaje(){
  if(!confirm('¿Finalizar viaje?')) return;
  let v = JSON.parse(localStorage.getItem('viajeActivo'));
  fetch('/api/viaje/finalizar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:v.id})});
  localStorage.removeItem('viajeActivo');
  viajeActivo=null;
  if(radarInterval) clearInterval(radarInterval);
  alert('✅ Viaje finalizado');
  location.reload();
}
async function adminLogin(){let p=document.getElementById('admin-pass-input').value;let res=await fetch('/api/admin/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:p})});let d=await res.json();if(!d.ok){alert(d.error);return;}localStorage.setItem('adminToken',p);document.getElementById('admin-login').style.display='none';document.getElementById('admin-panel').style.display='block';cargarAdmin();}
function adminTab(tab){
  document.getElementById('admin-viajes').style.display=tab==='viajes'?'block':'none';
  document.getElementById('admin-choferes').style.display=tab==='choferes'?'block':'none';
  document.getElementById('admin-clientes').style.display=tab==='clientes'?'block':'none';
  document.getElementById('btn-viajes').style.background=tab==='viajes'?'#000':'#fff';
  document.getElementById('btn-viajes').style.color=tab==='viajes'?'#fff':'#000';
  document.getElementById('btn-choferes').style.background=tab==='choferes'?'#000':'#fff';
  document.getElementById('btn-choferes').style.color=tab==='choferes'?'#fff':'#000';
  document.getElementById('btn-clientes').style.background=tab==='clientes'?'#000':'#fff';
  document.getElementById('btn-clientes').style.color=tab==='clientes'?'#fff':'#000';
}
async function cargarAdmin(){
  let pass=localStorage.getItem('adminToken');
  let res=await fetch('/api/admin/data',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:pass})});
  let d=await res.json();
  document.getElementById('admin-viajes').innerHTML=d.viajes.slice().reverse().map(v=>`<div style="border-bottom:1px solid #eee;padding:8px;background:#fff;margin:4px 0;border-radius:8px"><b>${v.fecha} ${v.hora}</b> ${v.cliente} $${v.precio} ${v.kms}km<br><span style="font-size:11px">${v.origen} → ${v.destino}</span> <button onclick="borrarAdmin('viaje',null,'${v.id}')" style="background:#ff5252;color:#fff;border:none;padding:4px 8px;border-radius:6px;float:right">Borrar</button></div>`).join('');
  document.getElementById('admin-choferes').innerHTML=(d.choferes||[]).map(c=>`<div style="background:#fff;padding:10px;margin:6px 0;border-radius:10px;border:1px solid #ddd"><b>${c.nombre}</b> - ${c.tel}<br>🚗 ${c.modelo||'Sin modelo'} (${c.anio||''})<br>🔖 Placas: <b>${c.placas||'Sin placas'}</b> <button onclick="borrarAdmin('chofer','${c.tel}')" style="background:#ff5252;color:#fff;border:none;padding:4px 8px;border-radius:6px;float:right">Borrar</button></div>`).join('')||'Sin choferes';
  document.getElementById('admin-clientes').innerHTML=(d.clientes||[]).map(c=>`<div style="background:#fff;padding:8px;margin:4px 0;border-radius:8px">${c.nombre} - ${c.tel} <button onclick="borrarAdmin('cliente','${c.tel}')" style="background:#ff5252;color:#fff;border:none;padding:4px 8px;border-radius:6px;float:right">Borrar</button></div>`).join('')||'Sin clientes';
}
async function borrarAdmin(tipo,tel,id){
  let pass=localStorage.getItem('adminToken');
  if(!confirm('¿Borrar?')) return;
  await fetch('/api/admin/borrar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:pass,tipo:tipo,tel:tel,id:id})});
  cargarAdmin();
}
(function(){
  let r=localStorage.getItem('rol_AGL'); let ca=JSON.parse(localStorage.getItem('clienteActual')||'null'); let ch=JSON.parse(localStorage.getItem('choferActual')||'null'); let at=localStorage.getItem('adminToken');
  if(ch && (r==='chofer' || !r)){document.getElementById('modal-rol').style.display='none';document.getElementById('vista-chofer').style.display='block';verificarSesionChofer();}
  else if(at && r==='admin'){document.getElementById('modal-rol').style.display='none';document.getElementById('vista-admin').style.display='block';document.getElementById('admin-login').style.display='none';document.getElementById('admin-panel').style.display='block';cargarAdmin();}
  else if(ca){localStorage.setItem('rol_AGL','cliente');document.getElementById('modal-rol').style.display='none';document.getElementById('vista-cliente').style.display='block';verificarSesionCliente();}
  else if(r==='cliente'){document.getElementById('modal-rol').style.display='none';document.getElementById('vista-cliente').style.display='block';verificarSesionCliente();}
})();
</script></body></html>
"""
@app.route("/")
def index(): return render_template_string(HTML)
@app.route("/api/viaje", methods=["POST"])
def api_viaje():
    data=request.json; viajes.append(data); guardar(); return jsonify({"ok":True})
@app.route("/api/chofer/heartbeat", methods=["POST"])
def heartbeat():
    d=request.json
    ubicaciones[d['tel']]={'lat':d['lat'],'lng':d['lng'],'ts':time.time()}
    guardar()
    return jsonify({"ok":True})
@app.route("/api/viajes_cercanos")
def viajes_cercanos():
    lat=float(request.args.get('lat',21.8853)); lng=float(request.args.get('lng',-102.2916))
    result=[]
    for v in viajes:
        if v.get('status')!='pendiente': continue
        if not v.get('origen_lat'): continue
        d=haversine(lat,lng,v.get('origen_lat'),v.get('origen_lng'))
        if d <= 15.0:
            vc=dict(v); vc['dist_km']=round(d,1); result.append(vc)
    return jsonify(sorted(result, key=lambda x: x['dist_km']))
@app.route("/api/chofer/registrar", methods=["POST"])
def chofer_reg():
    d=request.json
    if any(c['tel']==d['tel'] for c in choferes_db): return jsonify({"ok":False,"error":"Ya registrado"})
    choferes_db.append(d); guardar(); return jsonify({"ok":True,"chofer":d})
@app.route("/api/chofer/login", methods=["POST"])
def chofer_login():
    d=request.json; f=next((c for c in choferes_db if c['tel']==d['tel'] and c['pass']==d['pass']),None)
    return jsonify({"ok":True,"chofer":f}) if f else jsonify({"ok":False,"error":"Pass mal"})
@app.route("/api/cliente/registrar", methods=["POST"])
def cli_reg():
    d=request.json
    if any(c['tel']==d['tel'] for c in clientes_db): return jsonify({"ok":False,"error":"Ya registrado"})
    clientes_db.append(d); guardar(); return jsonify({"ok":True,"cliente":d})
@app.route("/api/cliente/login", methods=["POST"])
def cli_login():
    d=request.json; f=next((c for c in clientes_db if c['tel']==d['tel'] and c['pass']==d['pass']),None)
    return jsonify({"ok":True,"cliente":f}) if f else jsonify({"ok":False,"error":"Cel o pass mal"})

@app.route("/api/viaje/tomar", methods=["POST"])
def tomar():
    data = request.json
    for v in viajes:
        if v['id']==data['id']: 
            v['status']='tomado'
            v['chofer_tel']=data.get('chofer_tel')
            v['chofer_nombre']=data.get('chofer_nombre')
            v['chofer_placas']=data.get('chofer_placas')
            v['chofer_modelo']=data.get('chofer_modelo')
            v['tomado_en']=time.strftime("%Y-%m-%d %H:%M:%S")
            guardar()
            try:
                import requests
                SHEET_URL = os.environ.get("SHEET_URL", "") 
                if SHEET_URL:
                    requests.post(SHEET_URL, json=v, timeout=3)
            except: pass
            return jsonify({"ok":True, "viaje":v})
    return jsonify({"ok":False})

@app.route("/api/viaje/finalizar", methods=["POST"])
def finalizar():
    for v in viajes:
        if v['id']==request.json['id']: 
            v['status']='finalizado'
            guardar()
            return jsonify({"ok":True})
    return jsonify({"ok":False})
@app.route("/api/viaje/estado/<id_viaje>")
def estado_viaje(id_viaje):
    for v in viajes:
        if v['id']==id_viaje:
            return jsonify(v)
    return jsonify({"ok":False})

@app.route("/api/viajes_cliente")
def viajes_cliente():
    tel = request.args.get('tel')
    result = [v for v in viajes if v.get('cliente_tel')==tel and v.get('status') in ['pendiente','tomado','en_curso']]
    return jsonify(result)
@app.route("/api/admin/login", methods=["POST"])
def admin_login(): return jsonify({"ok":True}) if request.json.get('password')==ADMIN_PASSWORD else jsonify({"ok":False,"error":"Pass mal"})
@app.route("/api/admin/data", methods=["POST"])
def admin_data():
    if request.json.get('password')!=ADMIN_PASSWORD: return jsonify({"ok":False})
    return jsonify({"ok":True,"choferes":choferes_db,"viajes":viajes, "clientes":clientes_db})
@app.route("/api/admin/borrar", methods=["POST"])
def admin_borrar():
    data = request.json
    if data.get('password')!=ADMIN_PASSWORD: return jsonify({"ok":False})
    tipo = data.get('tipo'); tel = data.get('tel'); id_viaje = data.get('id')
    if tipo == 'chofer': choferes_db[:] = [c for c in choferes_db if c['tel'] != tel]
    elif tipo == 'cliente': clientes_db[:] = [c for c in clientes_db if c['tel'] != tel]
    elif tipo == 'viaje': viajes[:] = [v for v in viajes if v['id'] != id_viaje]
    guardar(); return jsonify({"ok":True})
if __name__=="__main__": app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
