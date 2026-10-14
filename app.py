from flask import Flask, render_template_string, request, jsonify, send_file
import json, io, csv, os, math, time

app = Flask(__name__)
ADMIN_PASSWORD = "AGL2026"
viajes, choferes_db, clientes_db, bloqueados, ubicaciones = [], [], [], [], {}

def cargar():
  global viajes, choferes_db, clientes_db, bloqueados, ubicaciones
  try:
    if os.path.exists("viajes.json"):
      with open("viajes.json") as f: viajes.extend(json.load(f))
    if os.path.exists("choferes_db.json"):
      with open("choferes_db.json") as f: choferes_db.extend(json.load(f))
    if os.path.exists("clientes_db.json"):
      with open("clientes_db.json") as f: clientes_db.extend(json.load(f))
    if os.path.exists("bloqueados.json"):
      with open("bloqueados.json") as f: bloqueados.extend(json.load(f))
    if os.path.exists("ubicaciones.json"):
      with open("ubicaciones.json") as f: ubicaciones.update(json.load(f))
  except: pass
def guardar():
  try:
    with open("viajes.json","w") as f: json.dump(viajes,f)
    with open("choferes_db.json","w") as f: json.dump(choferes_db,f)
    with open("clientes_db.json","w") as f: json.dump(clientes_db,f)
    with open("bloqueados.json","w") as f: json.dump(bloqueados,f)
    with open("ubicaciones.json","w") as f: json.dump(ubicaciones,f)
  except: pass
cargar() 
def haversine(lat1,lon1,lat2,lon2):
    R=6371; dLat=math.radians(lat2-lat1); dLon=math.radians(lon2-lon1)
    a=math.sin(dLat/2)**2+math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dLon/2)**2
    return R*2*math.atan2(math.sqrt(a),math.sqrt(1-a))

HTML = """<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AGL V41.3 CERCANO</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:Arial}body{height:100vh;overflow:hidden;background:#fff}
#map{position:fixed!important;top:0;left:0;width:100%;height:100vh!important;z-index:1}
.top-bar{position:fixed;top:12px;left:12px;right:12px;z-index:10;display:flex;gap:8px;max-width:420px}
.menu-btn{width:46px;height:46px;background:#fff;border:none;border-radius:14px;box-shadow:0 4px 18px rgba(0,0,0,.28);font-size:22px}
.search-card{background:#fff;border-radius:16px;box-shadow:0 8px 28px rgba(0,0,0,.26);padding:6px 10px;flex:1}
.item{display:flex;align-items:center;gap:8px;padding:8px 4px}.item+.item{border-top:1px solid #f0f0f0}
.dot{width:8px;height:8px;border-radius:50%}.o{background:#00c853}.d{background:#ff3b30}
input{flex:1;border:none;outline:none;font-size:14px;font-weight:600;background:transparent}
#menu{position:fixed;top:0;left:-100%;width:84%;max-width:360px;height:100vh;background:#fff;z-index:30;transition:.28s;overflow-y:auto}
#menu.act{left:0}.overlay{position:fixed;inset:0;background:rgba(0,0,0,.35);z-index:20;display:none}.overlay.act{display:block}
.menu-header{padding:20px 16px 12px;border-bottom:1px solid #eee;display:flex;justify-content:space-between}
.menu-body{padding:14px}.menu-linea{padding:14px 4px;font-size:16px;border-bottom:1px solid #f5f5f5;cursor:pointer;display:flex;justify-content:space-between}
.parada-extra{display:none}#cotizacion{position:fixed;bottom:76px;left:12px;right:12px;z-index:11;background:#fff;border-radius:16px;padding:12px 16px;display:none;box-shadow:0 8px 28px rgba(0,0,0,.32);max-width:420px;margin:auto}
.btn-confirm{position:fixed;bottom:12px;left:12px;right:12px;z-index:11;background:#000;color:#fff;font-weight:800;padding:16px;border:none;border-radius:16px;max-width:420px;margin:auto}
#modal-rol{position:fixed;inset:0;z-index:99999;background:rgba(0,0,0,.92);display:flex;align-items:center;justify-content:center;padding:20px}.box-rol{background:#fff;border-radius:20px;padding:24px;width:100%;max-width:360px;text-align:center}
.inp{width:100%;padding:13px;margin:7px 0;border-radius:10px;border:1px solid #ddd;background:#f9f9f9}
#modal-rating{position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,.7);display:none;align-items:center;justify-content:center}
</style></head><body>
<div id="modal-rating"><div style="background:#fff;padding:20px;border-radius:16px;max-width:320px;width:90%"><h3>¿Cómo te fue?</h3><textarea id="comentario-rating" class="inp" placeholder="Comentario"></textarea><button onclick="enviarRating()" style="width:100%;padding:12px;background:#000;color:#fff;border:none;border-radius:10px">ENVIAR</button></div></div>
<div id="modal-rol"><div class="box-rol"><h2>🚕 AGL Transporte</h2><p style="margin:10px 0 16px;color:#666;font-size:12px">V41.3 - CHOFER MÁS CERCANO</p>
<button type="button" onclick="elegirRol('cliente')" style="width:100%;padding:16px;border:none;border-radius:14px;font-weight:800;margin-bottom:10px;background:#000;color:#fff">👤 SOY CLIENTE</button>
<button type="button" onclick="elegirRol('chofer')" style="width:100%;padding:16px;border:none;border-radius:14px;font-weight:800;margin-bottom:10px;background:#00c853;color:#fff">🚗 SOY CHOFER</button>
<button type="button" onclick="elegirRol('admin')" style="width:100%;padding:16px;border:none;border-radius:14px;font-weight:800;background:#0a3552;color:#fff">🔐 SOY ADMIN</button></div></div>
<div id="vista-cliente" style="display:none"><div id="box-login-cliente" style="padding:20px;max-width:400px;margin:70px auto 0;background:#fff;position:relative;z-index:20;border-radius:16px"><h2 style="text-align:center">👤 Cliente</h2><div id="form-login-c"><input id="cli-tel" class="inp" placeholder="Celular"><input id="cli-pass" class="inp" type="password" placeholder="Contraseña"><button onclick="clienteLogin()" style="width:100%;padding:13px;background:#000;color:#fff;border:none;border-radius:10px">ENTRAR</button><p style="text-align:center;margin:10px 0">¿Nuevo?</p><button onclick="mostrarRegistroCli()" style="width:100%;padding:11px;background:#fff;border:1px solid #000;border-radius:10px">REGISTRARME</button><button onclick="volverAlInicio()" style="width:100%;margin-top:10px;padding:11px;background:#eee;border:none;border-radius:10px">⬅ MENU</button><p id="msg-cli" style="color:red;text-align:center;font-size:12px"></p></div><div id="form-registro-c" style="display:none"><input id="cli-reg-nombre" class="inp" placeholder="Nombre"><input id="cli-reg-tel" class="inp" placeholder="Celular"><input id="cli-reg-pass" class="inp" type="password" placeholder="Contraseña"><button onclick="clienteRegistrar()" style="width:100%;padding:13px;background:#00c853;color:#fff;border:none;border-radius:10px">CREAR CUENTA</button><button onclick="mostrarLoginCli()" style="width:100%;padding:10px;background:none;border:none;color:#1976d2">Ya tengo cuenta</button></div></div><div id="box-cliente-viaje" style="display:none"><div id="map"></div><button onclick="miUbicacion()" style="position:fixed;bottom:100px;right:14px;z-index:12;width:50px;height:50px;background:#fff;border:none;border-radius:50%;box-shadow:0 4px 18px rgba(0,0,0,.3)">📍</button><div id="eta-box" style="position:fixed;top:70px;left:14px;z-index:12;background:#000;color:#fff;padding:8px 12px;border-radius:20px;font-size:12px;display:none"></div><div class="top-bar"><button class="menu-btn" onclick="toggleMenu()">☰</button><div class="search-card"><div class="item"><div class="dot o"></div><input id="origen" placeholder="Origen"></div><div class="item parada-extra" id="boxP1"><div class="dot" style="background:#ffcc00"></div><input id="parada1" placeholder="Parada 1"></div><div class="item parada-extra" id="boxP2"><div class="dot" style="background:#ff9500"></div><input id="parada2" placeholder="Parada 2"></div><div class="item parada-extra" id="boxP3"><div class="dot" style="background:#00e5ff"></div><input id="parada3" placeholder="Parada 3"></div><div class="item"><div class="dot d"></div><input id="destino" placeholder="Destino"></div></div></div><div id="menu"><div class="menu-header"><b>🚕 AGL AGS</b><button onclick="toggleMenu()" style="width:34px;height:34px;border-radius:50%;background:#111;color:#fff;border:none">✕</button></div><div class="menu-body"><div class="menu-linea" onclick="agregarParada()"><div><b>agregar parada</b><br><span id="txt-paradas">0 / 3</span></div><span>➕</span></div><div class="menu-linea" onclick="borrarTodo()"><div><b>corregir orden</b></div><span>✏️</span></div><div class="menu-linea" onclick="volverAlInicio()"><div><b>volver a menu inicial</b></div><span>🏠</span></div><div style="padding:12px 4px;border-top:1px solid #eee;margin-top:10px"><b style="font-size:13px">📅 Fecha y hora programada (opcional)</b><br><input type="date" id="fechaViaje" style="width:48%;padding:10px;border:1px solid #ddd;border-radius:8px;margin-top:6px"><input type="time" id="horaViaje" style="width:48%;padding:10px;border:1px solid #ddd;border-radius:8px;margin-top:6px"></div></div><a href="/concentrado" target="_blank" style="display:block;background:#0a3552;color:white;padding:12px;border-radius:12px;text-decoration:none;text-align:center;margin-top:16px">📊 dashboard</a><button onclick="cambiarRol()" style="margin-top:16px;width:100%;background:#ffebee;color:#c62828;border:none;padding:12px;border-radius:12px">Salir</button></div></div><div class="overlay" id="overlay" onclick="toggleMenu()"></div><div id="cotizacion"><div id="dist" style="font-size:11px;color:#666"></div><b id="precio" style="font-size:22px">$0</b></div><button class="btn-confirm" id="btnPedir" onclick="pedir()">Confirmar $0</button></div></div>
<div id="vista-chofer" style="display:none"><div id="box-login-chofer" style="padding:20px;max-width:400px;margin:20px auto;background:#fff;border-radius:16px"><h2 style="text-align:center">🚗 Chofer</h2><div id="form-login"><input id="chofer-tel" class="inp" placeholder="Celular"><input id="chofer-pass" class="inp" type="password" placeholder="Contraseña"><button onclick="choferLogin()" style="width:100%;padding:13px;background:#000;color:#fff;border:none;border-radius:10px">ENTRAR</button><button onclick="mostrarRegistroChofer()" style="width:100%;padding:11px;background:#fff;border:1px solid #000;border-radius:10px;margin-top:10px">REGISTRARME</button><button onclick="volverAlInicio()" style="width:100%;margin-top:10px;padding:11px;background:#eee;border:none;border-radius:10px">⬅ MENU</button></div><div id="form-registro" style="display:none"><input id="reg-nombre" class="inp" placeholder="Nombre"><input id="reg-tel" class="inp" placeholder="Celular"><input id="reg-placas" class="inp" placeholder="Placas"><input id="reg-modelo" class="inp" placeholder="Modelo"><input id="reg-anio" type="number" class="inp" placeholder="Año 2021-2026" min="2021" max="2026"><input id="reg-licencia" class="inp" placeholder="Licencia"><input id="reg-vigencia" type="date" class="inp"><input id="reg-pass" type="password" class="inp" placeholder="Contraseña"><button onclick="choferRegistrar()" style="width:100%;padding:13px;background:#00c853;color:#fff;border:none;border-radius:10px">CREAR CHOFER</button><button onclick="mostrarLoginChofer()" style="width:100%;padding:10px;background:none;border:none;color:#1976d2">Ya tengo cuenta</button></div></div><div id="box-viajes-chofer" style="display:none"><div style="background:#000;color:#fff;padding:12px;display:flex;justify-content:space-between"><span id="nombre-chofer-log">Chofer</span><span id="gps-status" style="font-size:10px;color:#00e676">● GPS activo</span><button onclick="choferLogout()" style="background:#ff5252;color:#fff;border:none;padding:6px 10px;border-radius:6px">Salir</button></div><div style="padding:10px"><div style="background:#e8f5e9;padding:8px;border-radius:8px;font-size:12px;margin-bottom:8px" id="info-cercano">📍 Calculando cercanía...</div><div style="display:flex;gap:6px"><button id="btn-pend" onclick="mostrarViajesChofer('pendientes')" style="flex:1;padding:10px;background:#000;color:#fff;border:none;border-radius:8px">Pendientes</button><button onclick="mostrarViajesChofer('mios')" style="flex:1;padding:10px;background:#fff;border:1px solid #000;border-radius:8px">Mios</button><button onclick="mostrarViajesChofer('completados')" style="flex:1;padding:10px;background:#fff;border:1px solid #000;border-radius:8px">Hechos</button></div><div id="lista-viajes-chofer"></div></div></div></div>
<div id="vista-admin" style="display:none"><div id="admin-login" style="padding:20px;max-width:400px;margin:80px auto;background:#fff;border-radius:16px"><h2 style="text-align:center">🔐 ADMIN</h2><input id="admin-pass-input" type="password" class="inp" placeholder="AGL2026"><button onclick="adminLogin()" style="width:100%;padding:14px;background:#000;color:#fff;border:none;border-radius:10px">ENTRAR</button><button onclick="volverAlInicio()" style="width:100%;margin-top:10px;padding:12px;background:#eee;border:none;border-radius:12px">⬅ VOLVER</button></div><div id="admin-panel" style="display:none;padding:12px;background:#eef2f7;min-height:100vh"><h1 style="color:#0a3552">🔐 ADMIN V41.3 CERCANO</h1><div id="admin-stats" style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px"></div><div style="background:white;padding:12px;border-radius:12px;margin-top:10px"><h3>📦 Viajes con GPS</h3><div id="admin-viajes"></div></div></div></div>
<script>
let map=null,origenMarker=null,destinoMarker=null,parada1Marker=null,parada2Marker=null,parada3Marker=null,routeLine,choferMarker=null,kmActual=0,precioActual=0,tiempoActual=0,numParadasVisibles=0,adminToken=null,miChofer=null,clienteWatch=null,choferWatch=null,ratingId=null,ultimoPendientes=0,intervalChofer=null,miPos={lat:21.8853,lng:-102.2916},origenLatLng=null,destinoLatLng=null;
function toggleMenu(){document.getElementById('menu').classList.toggle('act');document.getElementById('overlay').classList.toggle('act');}
function initMap(){if(map){setTimeout(()=>map.invalidateSize(),200);return;}map=L.map('map',{zoomControl:false}).setView([21.8853,-102.2916],13);L.tileLayer('https://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',{subdomains:['mt0','mt1','mt2','mt3'],maxZoom:20}).addTo(map);map.on('click',e=>{if(!origenMarker){crearOrigen(e.latlng);return;}if(numParadasVisibles>=1&&!parada1Marker){parada1Marker=L.marker(e.latlng,{icon:L.icon({iconUrl:'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-yellow.png',shadowUrl:'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',iconSize:[25,41],iconAnchor:[12,41]})}).addTo(map);fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${e.latlng.lat}&lon=${e.latlng.lng}&zoom=18`).then(r=>r.json()).then(j=>{document.getElementById('parada1').value=j.display_name.split(',').slice(0,3).join(', ');});trazar();return;}if(numParadasVisibles>=2&&!parada2Marker){parada2Marker=L.marker(e.latlng,{icon:L.icon({iconUrl:'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-orange.png',shadowUrl:'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',iconSize:[25,41],iconAnchor:[12,41]})}).addTo(map);fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${e.latlng.lat}&lon=${e.latlng.lng}&zoom=18`).then(r=>r.json()).then(j=>{document.getElementById('parada2').value=j.display_name.split(',').slice(0,3).join(', ');});trazar();return;}if(numParadasVisibles>=3&&!parada3Marker){parada3Marker=L.marker(e.latlng,{icon:L.icon({iconUrl:'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',shadowUrl:'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',iconSize:[25,41],iconAnchor:[12,41]})}).addTo(map);fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${e.latlng.lat}&lon=${e.latlng.lng}&zoom=18`).then(r=>r.json()).then(j=>{document.getElementById('parada3').value=j.display_name.split(',').slice(0,3).join(', ');});trazar();return;}if(!destinoMarker){crearDestino(e.latlng);return;}});}
function elegirRol(r){localStorage.setItem('rol_AGL',r);document.getElementById('modal-rol').style.display='none';if(r==='chofer'){document.getElementById('vista-cliente').style.display='none';document.getElementById('vista-chofer').style.display='block';document.getElementById('vista-admin').style.display='none';verificarSesionChofer();}else if(r==='admin'){document.getElementById('vista-cliente').style.display='none';document.getElementById('vista-chofer').style.display='none';document.getElementById('vista-admin').style.display='block';}else{document.getElementById('vista-chofer').style.display='none';document.getElementById('vista-admin').style.display='none';document.getElementById('vista-cliente').style.display='block';initMap();verificarSesionCliente();}}
function cambiarRol(){localStorage.removeItem('rol_AGL');location.reload();}
function volverAlInicio(){localStorage.removeItem('rol_AGL');location.reload();}
const verdeIcon=new L.Icon({iconUrl:'https://cdn.jsdelivr.net/gh/pointhi/leaflet-color-markers@master/img/marker-icon-2x-green.png',shadowUrl:'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',iconSize:[25,41],iconAnchor:[12,41]});
const rojoIcon=new L.Icon({iconUrl:'https://cdn.jsdelivr.net/gh/pointhi/leaflet-color-markers@master/img/marker-icon-2x-red.png',shadowUrl:'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',iconSize:[25,41],iconAnchor:[12,41]});
function getDir(ll,tipo){fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${ll.lat}&lon=${ll.lng}&zoom=18`).then(r=>r.json()).then(j=>{let nom=j.display_name.split(',').slice(0,3).join(', ');if(tipo==1)document.getElementById('origen').value=nom;else document.getElementById('destino').value=nom;});}
function crearOrigen(ll){origenLatLng=ll;if(!origenMarker){origenMarker=L.marker(ll,{draggable:true,icon:verdeIcon}).addTo(map);origenMarker.on('dragend',function(ev){origenLatLng=ev.target.getLatLng();trazar();});}else origenMarker.setLatLng(ll);getDir(ll,1);trazar();}
function crearDestino(ll){destinoLatLng=ll;if(!destinoMarker){destinoMarker=L.marker(ll,{draggable:true,icon:rojoIcon}).addTo(map);destinoMarker.on('dragend',function(ev){destinoLatLng=ev.target.getLatLng();trazar();});}else destinoMarker.setLatLng(ll);getDir(ll,2);trazar();}
function crearParada1(ll){if(parada1Marker)map.removeLayer(parada1Marker);parada1Marker=L.marker(ll,{draggable:true,icon:L.icon({iconUrl:'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-yellow.png',shadowUrl:'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',iconSize:[25,41],iconAnchor:[12,41]})}).addTo(map);parada1Marker.on('dragend',function(ev){trazar();let nl=ev.target.getLatLng();fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${nl.lat}&lon=${nl.lng}&zoom=18`).then(r=>r.json()).then(j=>{document.getElementById('parada1').value=j.display_name.split(',').slice(0,3).join(', ');});});fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${ll.lat}&lon=${ll.lng}&zoom=18`).then(r=>r.json()).then(j=>{document.getElementById('parada1').value=j.display_name.split(',').slice(0,3).join(', ');});trazar();}
function crearParada2(ll){if(parada2Marker)map.removeLayer(parada2Marker);parada2Marker=L.marker(ll,{draggable:true,icon:L.icon({iconUrl:'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-orange.png',shadowUrl:'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',iconSize:[25,41],iconAnchor:[12,41]})}).addTo(map);parada2Marker.on('dragend',function(ev){trazar();let nl=ev.target.getLatLng();fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${nl.lat}&lon=${nl.lng}&zoom=18`).then(r=>r.json()).then(j=>{document.getElementById('parada2').value=j.display_name.split(',').slice(0,3).join(', ');});});fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${ll.lat}&lon=${ll.lng}&zoom=18`).then(r=>r.json()).then(j=>{document.getElementById('parada2').value=j.display_name.split(',').slice(0,3).join(', ');});trazar();}
function crearParada3(ll){if(parada3Marker)map.removeLayer(parada3Marker);parada3Marker=L.marker(ll,{draggable:true,icon:L.icon({iconUrl:'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',shadowUrl:'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',iconSize:[25,41],iconAnchor:[12,41]})}).addTo(map);parada3Marker.on('dragend',function(ev){trazar();let nl=ev.target.getLatLng();fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${nl.lat}&lon=${nl.lng}&zoom=18`).then(r=>r.json()).then(j=>{document.getElementById('parada3').value=j.display_name.split(',').slice(0,3).join(', ');});});fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${ll.lat}&lon=${ll.lng}&zoom=18`).then(r=>r.json()).then(j=>{document.getElementById('parada3').value=j.display_name.split(',').slice(0,3).join(', ');});trazar();}
function agregarParada(){if(numParadasVisibles>=3){alert('Máximo 3 paradas');return;}numParadasVisibles++;document.getElementById('boxP'+numParadasVisibles).style.display='flex';document.getElementById('txt-paradas').innerText=numParadasVisibles+' / 3';toggleMenu();}
function miUbicacion(){navigator.geolocation.getCurrentPosition(p=>{let ll={lat:p.coords.latitude,lng:p.coords.longitude};miPos=ll;crearOrigen(ll);if(map) map.setView([ll.lat,ll.lng],16);});}

async function trazar(){
    if(!origenMarker) return;
    let pts=[];
    pts.push(origenMarker.getLatLng());
    if(parada1Marker) pts.push(parada1Marker.getLatLng());
    if(parada2Marker) pts.push(parada2Marker.getLatLng());
    if(parada3Marker) pts.push(parada3Marker.getLatLng());
    if(destinoMarker) pts.push(destinoMarker.getLatLng());
    if(pts.length < 2) return;
    let s=pts.map(p=>p.lng+','+p.lat).join(';');
    let r=await fetch(`https://router.project-osrm.org/route/v1/driving/${s}?overview=full&geometries=geojson`);
    let j=await r.json();
    if(!j.routes[0]) return;
    let route=j.routes[0];
    kmActual=Math.round(route.distance/100)/10;
    if(kmActual<0.8)kmActual=0.8;
    tiempoActual=Math.round(route.duration/60);
    if(routeLine)map.removeLayer(routeLine);
    routeLine=L.polyline(route.geometry.coordinates.map(c=>[c[1],c[0]]),{color:'#000',weight:6}).addTo(map);
    precioActual=Math.round(35+(kmActual*6.6)+tiempoActual);
    if(precioActual<65)precioActual=65;
    document.getElementById('cotizacion').style.display='block';
    document.getElementById('dist').innerText=kmActual+' km - '+tiempoActual+' min';
    document.getElementById('precio').innerText='$'+precioActual+' MXN';
    document.getElementById('btnPedir').innerText='Confirmar $'+precioActual;
    document.getElementById('btnPedir').style.display="block";
    map.fitBounds(routeLine.getBounds(),{padding:[60,60]});
}
async function pedir(){if(!precioActual||!origenLatLng) return alert('Toca mapa origen y destino');let ca=JSON.parse(localStorage.getItem('clienteActual')||'null');let id='V'+Date.now();let data={id:id,cliente:ca?ca.nombre:'Cliente',cliente_tel:ca?ca.tel:'',operador:'Por asignar',chofer_tel:'',fecha:new Date().toISOString().split('T')[0],hora:new Date().toLocaleTimeString().slice(0,5),origen:document.getElementById('origen').value,destino:document.getElementById('destino').value,origen_lat:origenLatLng.lat,origen_lng:origenLatLng.lng,destino_lat:destinoLatLng?destinoLatLng.lat:0,destino_lng:destinoLatLng?destinoLatLng.lng:0,kms:kmActual,precio:precioActual,tiempo:tiempoActual,status:'pendiente',timestamp:new Date().toISOString()};await fetch('/api/viaje',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});alert('✅ Viaje solicitado - Buscando chofer más cercano');borrarTodo();}

function borrarTodo(){
    document.getElementById('origen').value="";
    document.getElementById('destino').value="";
    document.getElementById('parada1').value="";
    document.getElementById('parada2').value="";
    document.getElementById('parada3').value="";
    document.getElementById('cotizacion').style.display="none";
    document.getElementById('dist').innerText="";
    document.getElementById('precio').innerText="$0";
    document.getElementById('btnPedir').innerText="Confirmar $0";
    document.getElementById('btnPedir').style.display="none";
    if(origenMarker){map.removeLayer(origenMarker);origenMarker=null;}
    if(destinoMarker){map.removeLayer(destinoMarker);destinoMarker=null;}
    if(parada1Marker){map.removeLayer(parada1Marker);parada1Marker=null;}
    if(parada2Marker){map.removeLayer(parada2Marker);parada2Marker=null;}
    if(parada3Marker){map.removeLayer(parada3Marker);parada3Marker=null;}
    if(routeLine){map.removeLayer(routeLine);routeLine=null;}
    precioActual=0; kmActual=0; origenLatLng=null; destinoLatLng=null;
    numParadasVisibles=0;
    document.getElementById('boxP1').style.display='none';
    document.getElementById('boxP2').style.display='none';
    document.getElementById('boxP3').style.display='none';
    document.getElementById('txt-paradas').innerText='0 / 3';
}
function mostrarRegistroChofer(){document.getElementById('form-login').style.display='none';document.getElementById('form-registro').style.display='block';}
function mostrarLoginChofer(){document.getElementById('form-registro').style.display='none';document.getElementById('form-login').style.display='block';}
async function choferRegistrar(){let n=document.getElementById('reg-nombre').value.trim(),t=document.getElementById('reg-tel').value.trim(),p=document.getElementById('reg-placas').value.trim(),modelo=document.getElementById('reg-modelo').value.trim(),anio=parseInt(document.getElementById('reg-anio').value),lic=document.getElementById('reg-licencia').value.trim(),vig=document.getElementById('reg-vigencia').value,c=document.getElementById('reg-pass').value.trim();if(!n||!t||!p||!modelo||!anio||!lic||!vig||!c){alert('Llena todo');return;}let res=await fetch('/api/chofer/registrar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({nombre:n,tel:t,placas:p,modelo:modelo,anio:anio,licencia:lic,vigencia:vig,pass:c})});let d=await res.json();if(!d.ok){alert(d.error);return;}localStorage.setItem('choferActual',JSON.stringify(d.chofer));verificarSesionChofer();}
async function choferLogin(){let t=document.getElementById('chofer-tel').value.trim(),c=document.getElementById('chofer-pass').value.trim();let res=await fetch('/api/chofer/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({tel:t,pass:c})});let d=await res.json();if(!d.ok){alert(d.error);return;}localStorage.setItem('choferActual',JSON.stringify(d.chofer));verificarSesionChofer();}
function verificarSesionChofer(){let a=JSON.parse(localStorage.getItem('choferActual')||'null');if(a){document.getElementById('box-login-chofer').style.display='none';document.getElementById('box-viajes-chofer').style.display='block';document.getElementById('nombre-chofer-log').innerText=a.nombre;miChofer=a;iniciarGPSChofer();mostrarViajesChofer('pendientes');if(intervalChofer) clearInterval(intervalChofer);intervalChofer=setInterval(()=>mostrarViajesChofer('pendientes'),4000);}else{document.getElementById('box-login-chofer').style.display='block';document.getElementById('box-viajes-chofer').style.display='none';}}
function choferLogout(){if(choferWatch) navigator.geolocation.clearWatch(choferWatch);if(intervalChofer) clearInterval(intervalChofer);localStorage.removeItem('choferActual');verificarSesionChofer();}
function iniciarGPSChofer(){if(!navigator.geolocation) return;choferWatch=navigator.geolocation.watchPosition(pos=>{miPos={lat:pos.coords.latitude,lng:pos.coords.longitude};fetch('/api/chofer/ubicacion',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({tel:miChofer.tel,lat:pos.coords.latitude,lng:pos.coords.longitude})});document.getElementById('gps-status').innerText='● GPS '+pos.coords.latitude.toFixed(4);},{},{enableHighAccuracy:true});}
function mostrarRegistroCli(){document.getElementById('form-login-c').style.display='none';document.getElementById('form-registro-c').style.display='block';}
function mostrarLoginCli(){document.getElementById('form-registro-c').style.display='none';document.getElementById('form-login-c').style.display='block';}
async function clienteRegistrar(){let n=document.getElementById('cli-reg-nombre').value.trim(),t=document.getElementById('cli-reg-tel').value.trim(),c=document.getElementById('cli-reg-pass').value.trim();if(!n||!t||!c){alert('Llena todo');return;}let res=await fetch('/api/cliente/registrar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({nombre:n,tel:t,pass:c})});let d=await res.json();if(!d.ok){alert(d.error);return;}localStorage.setItem('clienteActual',JSON.stringify(d.cliente));alert('✅ Cuenta creada');mostrarLoginCli();}
async function clienteLogin(){let t=document.getElementById('cli-tel').value.trim(),c=document.getElementById('cli-pass').value.trim();let res=await fetch('/api/cliente/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({tel:t,pass:c})});let d=await res.json();if(!d.ok){document.getElementById('msg-cli').innerText=d.error;return;}localStorage.setItem('clienteActual',JSON.stringify(d.cliente));verificarSesionClienteLogged();}
function verificarSesionCliente(){initMap();document.getElementById('box-login-cliente').style.display='block';document.getElementById('box-cliente-viaje').style.display='none';}
function verificarSesionClienteLogged(){initMap();document.getElementById('box-login-cliente').style.display='none';document.getElementById('box-cliente-viaje').style.display='block';setTimeout(()=>{if(map) map.invalidateSize();},400);}

// CALCULO DISTANCIA EN JS
function calcDist(lat1,lon1,lat2,lon2){let R=6371;let dLat=(lat2-lat1)*Math.PI/180;let dLon=(lon2-lon1)*Math.PI/180;let a=Math.sin(dLat/2)**2+Math.cos(lat1*Math.PI/180)*Math.cos(lat2*Math.PI/180)*Math.sin(dLon/2)**2;return R*2*Math.atan2(Math.sqrt(a),Math.sqrt(1-a));}

function mostrarViajesChofer(filtro){
 let ch=JSON.parse(localStorage.getItem('choferActual')||'null'); if(!ch) return;
 fetch('/api/viajes_cercanos?chofer_tel='+ch.tel+'&lat='+miPos.lat+'&lng='+miPos.lng).then(r=>r.json()).then(data=>{
  let lista=document.getElementById('lista-viajes-chofer');
  let fil=data;
  if(filtro==='pendientes') fil=data.filter(x=>x.status==='pendiente');
  if(filtro==='mios') fil=data.filter(x=>x.chofer_tel===ch.tel&&(x.status==='tomado'||x.status==='en_curso'));
  if(filtro==='completados') fil=data.filter(x=>x.chofer_tel===ch.tel&&x.status==='completado');

  if(filtro==='pendientes'){
    document.getElementById('btn-pend').innerText='Pendientes ('+fil.length+')';
    if(fil.length>0){
      document.getElementById('info-cercano').innerText='📍 Más cercano a ti: '+fil[0].dist_km+'km - '+fil[0].origen.substring(0,30);
      if(fil.length>ultimoPendientes){
        if(navigator.vibrate) navigator.vibrate([400,100,400,100,400]);
        try{new Audio('https://actions.google.com/sounds/v1/alarms/beep_short.ogg').play();}catch{}
        if(fil[0].dist_km<2) alert('🔔 ¡ERES EL MÁS CERCANO! Viaje a '+fil[0].dist_km+'km - $'+fil[0].precio);
      }
    }
    ultimoPendientes=fil.length;
  }

  if(fil.length==0){lista.innerHTML='<div style="padding:30px;text-align:center;color:#888">No hay en '+filtro+'</div>';return;}
  lista.innerHTML=fil.slice().reverse().map((x,i)=>{
    let esCercano=i===fil.length-1 && filtro==='pendientes'? '<div style="background:#00c853;color:#fff;font-size:11px;font-weight:800;padding:4px 8px;border-radius:6px;display:inline-block;margin-bottom:4px">📍 MÁS CERCANO A TI - '+x.dist_km+'km</div>' : '<div style="font-size:11px;color:#666">📍 A '+x.dist_km+'km de ti</div>';
    return `<div style="border:${i===fil.length-1 && filtro==='pendientes'?'3px solid #00c853':'2px solid #ddd'};border-radius:12px;padding:10px;margin:8px 0;background:#fff">${esCercano}<b>${x.cliente} $${x.precio}</b> - ${x.kms}km<br>${x.origen.substring(0,50)}<br>→ ${x.destino.substring(0,50)}<br><small>${x.fecha} ${x.hora} | ${x.status}</small><br><div style="margin-top:8px">${x.status==='pendiente'?`<button onclick="tomarViaje('${x.id}')" style="background:${i===fil.length-1?'#00c853':'#000'};color:#fff;border:none;padding:12px 14px;border-radius:8px;font-weight:800;width:100%">${i===fil.length-1?'✅ TOMAR - ERES EL MÁS CERCANO':'TOMAR $'+x.precio}</button>`:''}${x.status==='tomado'?`<button onclick="iniciarViaje('${x.id}')" style="background:#000;color:#fff;border:none;padding:10px 14px;border-radius:8px;width:100%">▶ INICIAR VIAJE</button>`:''}${x.status==='en_curso'?`<button onclick="finalizarViaje('${x.id}')" style="background:#d32f2f;color:#fff;border:none;padding:10px 14px;border-radius:8px;width:100%">⏹ FINALIZAR</button>`:''}</div></div>`;
  }).join('');
 });
}
async function tomarViaje(id){let ch=JSON.parse(localStorage.getItem('choferActual'));let res=await fetch('/api/viaje/tomar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:id,chofer_tel:ch.tel,chofer_nombre:ch.nombre})});let d=await res.json();if(d.ok){if(navigator.vibrate) navigator.vibrate(200); mostrarViajesChofer('mios');}else alert(d.error);}
async function iniciarViaje(id){await fetch('/api/viaje/iniciar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:id})});mostrarViajesChofer('mios');}
async function finalizarViaje(id){await fetch('/api/viaje/finalizar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:id})});ratingId=id;document.getElementById('modal-rating').style.display='flex';mostrarViajesChofer('completados');}
async function adminLogin(){let p=document.getElementById('admin-pass-input').value;let res=await fetch('/api/admin/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:p})});let d=await res.json();if(!d.ok){alert(d.error);return;}adminToken=p;localStorage.setItem('adminToken',p);document.getElementById('admin-login').style.display='none';document.getElementById('admin-panel').style.display='block';cargarAdmin();}
async function cargarAdmin(){let pass=localStorage.getItem('adminToken');let res=await fetch('/api/admin/data',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:pass})});let d=await res.json();document.getElementById('admin-stats').innerHTML=`<div style="background:white;padding:12px;border-radius:12px;text-align:center"><b>${d.choferes.length}</b><br>Choferes</div><div style="background:white;padding:12px;border-radius:12px;text-align:center"><b>${d.viajes.length}</b><br>Viajes</div>`;document.getElementById('admin-viajes').innerHTML=d.viajes.slice().reverse().map(v=>`<div style="border-bottom:1px solid #eee;padding:6px">${v.fecha} ${v.cliente} $${v.precio} - ${v.origen_lat? v.origen_lat.toFixed(3):''} - Chofer: ${v.operador} ${v.status}</div>`).join('');}
function enviarRating(){let c=document.getElementById('comentario-rating').value;fetch('/api/viaje/rating',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:ratingId,rating:5,comentario:c})});document.getElementById('modal-rating').style.display='none';}
(function(){let r=localStorage.getItem('rol_AGL');if(r==='chofer'){document.getElementById('modal-rol').style.display='none';document.getElementById('vista-chofer').style.display='block';verificarSesionChofer();}else if(r==='admin'){document.getElementById('modal-rol').style.display='none';document.getElementById('vista-admin').style.display='block';}else if(r==='cliente'){document.getElementById('modal-rol').style.display='none';document.getElementById('vista-cliente').style.display='block';initMap();verificarSesionCliente();}})();
</script></body></html>
"""

@app.route("/")
def index(): return render_template_string(HTML)

@app.route("/api/viaje", methods=["POST"])
def api_viaje():
    data=request.json
    # V41.4 - BUSCA CHOFER MAS CERCANO Y RESERVA 20s
    nearest_tel=None
    nearest_dist=9999
    lat_o=data.get('origen_lat')
    lng_o=data.get('origen_lng')
    if lat_o and lng_o:
        for tel, pos in ubicaciones.items():
            try:
                d=haversine(lat_o, lng_o, pos['lat'], pos['lng'])
                if d<nearest_dist:
                    nearest_dist=d
                    nearest_tel=tel
            except: pass
    data['chofer_cercano']=nearest_tel
    data['reserva_hasta']=time.time()+20 if nearest_tel else 0
    data['dist_cercano']=nearest_dist if nearest_tel else 0
    viajes.append(data); guardar(); return jsonify({"ok":True, "chofer_cercano":nearest_tel})

@app.route("/api/viajes_cercanos")
def viajes_cercanos():
    lat=float(request.args.get('lat',21.8853)); lng=float(request.args.get('lng',-102.2916)); chofer_tel=request.args.get('chofer_tel','')
    # Calcula distancia a cada viaje pendiente
    result=[]
    for v in viajes:
        if v.get('origen_lat') and v.get('origen_lng'):
            d=haversine(lat,lng,v['origen_lat'],v['origen_lng'])
        else:
            d=99.0
        vc=dict(v); vc['dist_km']=round(d,1)
        result.append(vc)
    # Ordena por distancia si es pendiente
    result_sorted=sorted([x for x in result if x['status']=='pendiente'], key=lambda x: x['dist_km']) + [x for x in result if x['status']!='pendiente']
    # Pero para que el chofer vea todos, devolvemos ordenado por distancia los pendientes primero
    pendientes_orden=sorted([x for x in result if x['status']=='pendiente'], key=lambda x: x['dist_km'])
    otros=[x for x in result if x['status']!='pendiente']
    return jsonify(pendientes_orden + otros)

@app.route("/api/viajes")
def api_viajes(): return jsonify(viajes)

@app.route("/api/viajes/cliente/<tel>")
def api_viajes_cliente(tel): return jsonify([v for v in viajes if v.get('cliente_tel')==tel][-20:])

@app.route("/api/chofer/registrar", methods=["POST"])
def chofer_reg():
    d=request.json
    if any(c['tel']==d['tel'] for c in choferes_db): return jsonify({"ok":False,"error":"Ya registrado"})
    choferes_db.append(d); guardar(); return jsonify({"ok":True,"chofer":d})

@app.route("/api/chofer/login", methods=["POST"])
def chofer_login():
    d=request.json
    f=next((c for c in choferes_db if c['tel']==d['tel'] and c['pass']==d['pass']),None)
    return jsonify({"ok":True,"chofer":f}) if f else jsonify({"ok":False,"error":"Pass mal"})

@app.route("/api/chofer/ubicacion", methods=["POST"])
def chofer_ubic():
    d=request.json; ubicaciones[d['tel']]={"lat":d['lat'],"lng":d['lng']}; guardar(); return jsonify({"ok":True})

@app.route("/api/cliente/registrar", methods=["POST"])
def cli_reg():
    d=request.json
    if any(c['tel']==d['tel'] for c in clientes_db): return jsonify({"ok":False,"error":"Ya registrado"})
    clientes_db.append(d); guardar(); return jsonify({"ok":True,"cliente":d})

@app.route("/api/cliente/login", methods=["POST"])
def cli_login():
    d=request.json
    f=next((c for c in clientes_db if c['tel']==d['tel'] and c['pass']==d['pass']),None)
    return jsonify({"ok":True,"cliente":f}) if f else jsonify({"ok":False,"error":"Cel o pass mal"})

@app.route("/api/viaje/tomar", methods=["POST"])
def tomar():
    d=request.json
    now=time.time()
    for v in viajes:
        if v['id']==d['id'] and v['status']=='pendiente':
            reserva_hasta=v.get('reserva_hasta',0)
            chofer_cercano=v.get('chofer_cercano')
            if reserva_hasta>now and chofer_cercano and d['chofer_tel']!=chofer_cercano:
                restante=int(reserva_hasta-now)
                return jsonify({"ok":False,"error":f"⏳ Reservado para chofer más cercano {chofer_cercano} - te quedan {restante}s. Distancia: {v.get('dist_cercano',0):.2f}km"})
            v['status']='tomado'; v['operador']=d['chofer_nombre']; v['chofer_tel']=d['chofer_tel']; guardar(); return jsonify({"ok":True})
    return jsonify({"ok":False,"error":"Ya tomado por otro chofer"})

@app.route("/api/viaje/iniciar", methods=["POST"])
def iniciar():
    for v in viajes:
        if v['id']==request.json['id']: v['status']='en_curso'; guardar(); return jsonify({"ok":True})
    return jsonify({"ok":False})

@app.route("/api/viaje/finalizar", methods=["POST"])
def finalizar():
    for v in viajes:
        if v['id']==request.json['id']: v['status']='completado'; guardar(); return jsonify({"ok":True})
    return jsonify({"ok":False})

@app.route("/api/viaje/rating", methods=["POST"])
def rating():
    for v in viajes:
        if v['id']==request.json['id']: v['rating']=request.json['rating']; guardar(); return jsonify({"ok":True})
    return jsonify({"ok":False})

@app.route("/api/admin/login", methods=["POST"])
def admin_login(): return jsonify({"ok":True}) if request.json.get('password')==ADMIN_PASSWORD else jsonify({"ok":False})

@app.route("/api/admin/data", methods=["POST"])
def admin_data():
    if request.json.get('password')!=ADMIN_PASSWORD: return jsonify({"ok":False})
    return jsonify({"ok":True,"choferes":choferes_db,"viajes":viajes})

@app.route("/concentrado")
def conc():
    html=f"<h1>Concentrado {len(viajes)}</h1><table border=1>"
    for v in viajes: html+=f"<tr><td>{v.get('cliente')}</td><td>{v.get('origen')}</td><td>{v.get('dist_km','-')}</td><td>{v.get('operador')}</td></tr>"
    return html+"</table>"

if __name__=="__main__": app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
