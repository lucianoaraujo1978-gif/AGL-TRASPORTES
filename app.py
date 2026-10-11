from flask import Flask, render_template_string, request, jsonify, send_file
import json, io, csv, os

app = Flask(__name__)
ADMIN_PASSWORD = "AGL2026"

viajes, choferes_db, clientes_db, bloqueados, ubicaciones = [], [], [], [], {}

def cargar():
    global viajes, choferes_db, clientes_db, bloqueados, ubicaciones
    try:
        if os.path.exists("/tmp/viajes.json"):
            with open("/tmp/viajes.json") as f: viajes.extend(json.load(f))
        if os.path.exists("/tmp/choferes_db.json"):
            with open("/tmp/choferes_db.json") as f: choferes_db.extend(json.load(f))
        if os.path.exists("/tmp/clientes_db.json"):
            with open("/tmp/clientes_db.json") as f: clientes_db.extend(json.load(f))
        if os.path.exists("/tmp/bloqueados.json"):
            with open("/tmp/bloqueados.json") as f: bloqueados.extend(json.load(f))
        if os.path.exists("/tmp/ubicaciones.json"):
            with open("/tmp/ubicaciones.json") as f: ubicaciones.update(json.load(f))
    except: pass

def guardar():
    try:
        with open("/tmp/viajes.json","w") as f: json.dump(viajes,f)
        with open("/tmp/choferes_db.json","w") as f: json.dump(choferes_db,f)
        with open("/tmp/clientes_db.json","w") as f: json.dump(clientes_db,f)
        with open("/tmp/bloqueados.json","w") as f: json.dump(bloqueados,f)
        with open("/tmp/ubicaciones.json","w") as f: json.dump(ubicaciones,f)
    except: pass

cargar()

HTML = """<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AGL V41.1 ADMIN PASS</title>
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
</style></head><body>
<div id="modal-rol"><div class="box-rol"><h2>🚕 AGL Transporte</h2><p style="margin:10px 0 16px;color:#666;font-size:12px">V41.1 - Admin ve pass</p>
<button type="button" onclick="elegirRol('cliente')" style="width:100%;padding:16px;border:none;border-radius:14px;font-weight:800;margin-bottom:10px;background:#000;color:#fff">👤 SOY CLIENTE</button>
<button type="button" onclick="elegirRol('chofer')" style="width:100%;padding:16px;border:none;border-radius:14px;font-weight:800;margin-bottom:10px;background:#00c853;color:#fff">🚗 SOY CHOFER</button>
<button type="button" onclick="elegirRol('admin')" style="width:100%;padding:16px;border:none;border-radius:14px;font-weight:800;background:#0a3552;color:#fff">🔐 SOY ADMIN</button></div></div>
<div id="vista-cliente" style="display:none"><div id="box-login-cliente" style="padding:20px;max-width:400px;margin:70px auto 0;background:#fff;position:relative;z-index:20;border-radius:16px"><h2 style="text-align:center">👤 Cliente</h2><div id="form-login-c"><input id="cli-tel" class="inp" placeholder="Celular"><input id="cli-pass" class="inp" type="password" placeholder="Contrasena"><button onclick="clienteLogin()" style="width:100%;padding:13px;background:#000;color:#fff;border:none;border-radius:10px">ENTRAR</button><p style="text-align:center;margin:10px 0">¿Nuevo?</p><button onclick="mostrarRegistroCli()" style="width:100%;padding:11px;background:#fff;border:1px solid #000;border-radius:10px">REGISTRARME</button><button onclick="volverAlInicio()" style="width:100%;margin-top:10px;padding:11px;background:#eee;border:none;border-radius:10px">⬅ MENU</button><p id="msg-cli" style="color:red;text-align:center;font-size:12px"></p></div><div id="form-registro-c" style="display:none"><input id="cli-reg-nombre" class="inp" placeholder="Nombre"><input id="cli-reg-tel" class="inp" placeholder="Celular"><input id="cli-reg-pass" class="inp" type="password" placeholder="Contrasena"><button onclick="clienteRegistrar()" style="width:100%;padding:13px;background:#00c853;color:#fff;border:none;border-radius:10px">CREAR CUENTA</button><button onclick="mostrarLoginCli()" style="width:100%;padding:10px;background:none;border:none;color:#1976d2">Ya tengo cuenta</button></div></div><div id="box-cliente-viaje" style="display:none"><div id="map"></div><button onclick="miUbicacion()" style="position:fixed;bottom:100px;right:14px;z-index:12;width:50px;height:50px;background:#fff;border:none;border-radius:50%;box-shadow:0 4px 18px rgba(0,0,0,.3)">📍</button><div id="eta-box" style="position:fixed;top:70px;left:14px;z-index:12;background:#000;color:#fff;padding:8px 12px;border-radius:20px;font-size:12px;display:none"></div><div class="top-bar"><button class="menu-btn" onclick="toggleMenu()">☰</button><div class="search-card"><div class="item"><div class="dot o"></div><input id="origen" placeholder="Origen"></div><div class="item parada-extra" id="boxP1"><div class="dot" style="background:#ffcc00"></div><input id="parada1" placeholder="Parada 1"></div><div class="item parada-extra" id="boxP2"><div class="dot" style="background:#ff9500"></div><input id="parada2" placeholder="Parada 2"></div><div class="item parada-extra" id="boxP3"><div class="dot" style="background:#00e5ff"></div><input id="parada3" placeholder="Parada 3"></div><div class="item"><div class="dot d"></div><input id="destino" placeholder="Destino"></div></div></div><div id="menu"><div class="menu-header"><b>🚕 AGL AGS</b><button onclick="toggleMenu()" style="width:34px;height:34px;border-radius:50%;background:#111;color:#fff;border:none">✕</button></div><div class="menu-body"><div class="menu-linea" onclick="document.getElementById('horaViaje').showPicker()"><div><b>hora de servicio</b><br><span id="txt-hora">--:--</span></div><span>🕒</span></div><div class="menu-linea" onclick="document.getElementById('fechaViaje').showPicker()"><div><b>fecha</b><br><span id="txt-fecha">hoy</span></div><span>📅</span></div><div class="menu-linea" onclick="agregarParada()"><div><b>agregar parada</b><br><span id="txt-paradas">0 / 3</span></div><span>➕</span></div><div class="menu-linea" onclick="borrarTodo()"><div><b>corregir orden</b></div><span>✏️</span></div><div class="menu-linea" onclick="volverAlInicio()"><div><b>volver a menu inicial</b></div><span>🏠</span></div><div class="menu-linea" onclick="verChoferAsignado()"><div><b>chofer por asignar</b><br><span id="txt-chofer" style="font-size:11px">conductor</span></div><span>🚗</span></div><div style="display:none"><input type="date" id="fechaViaje" onchange="document.getElementById('txt-fecha').innerText=this.value"><input type="time" id="horaViaje" onchange="document.getElementById('txt-hora').innerText=this.value"></div><a href="/concentrado" target="_blank" style="display:block;background:#0a3552;color:white;padding:12px;border-radius:12px;text-decoration:none;text-align:center;margin-top:16px">📊 dashboard</a><button onclick="cambiarRol()" style="margin-top:16px;width:100%;background:#ffebee;color:#c62828;border:none;padding:12px;border-radius:12px">Salir</button></div></div><div class="overlay" id="overlay" onclick="toggleMenu()"></div><div id="cotizacion"><div id="dist" style="font-size:11px;color:#666"></div><b id="precio" style="font-size:22px">$0</b><div id="txt-foraneo" style="font-size:11px;color:#ff6d00;font-weight:800;display:none">FORANEO +5km</div></div><button class="btn-confirm" id="btnPedir" onclick="pedir()">Confirmar $0</button></div></div>
<div id="vista-chofer" style="display:none"><div id="box-login-chofer" style="padding:20px;max-width:400px;margin:20px auto;background:#fff;border-radius:16px"><h2 style="text-align:center">🚗 Chofer</h2><div id="form-login"><input id="chofer-tel" class="inp" placeholder="Celular"><input id="chofer-pass" class="inp" type="password" placeholder="Contrasena"><button onclick="choferLogin()" style="width:100%;padding:13px;background:#000;color:#fff;border:none;border-radius:10px">ENTRAR</button><button onclick="mostrarRegistroChofer()" style="width:100%;padding:11px;background:#fff;border:1px solid #000;border-radius:10px;margin-top:10px">REGISTRARME</button><button onclick="volverAlInicio()" style="width:100%;margin-top:10px;padding:11px;background:#eee;border:none;border-radius:10px">⬅ MENU</button></div><div id="form-registro" style="display:none"><input id="reg-nombre" class="inp" placeholder="Nombre"><input id="reg-tel" class="inp" placeholder="Celular"><input id="reg-placas" class="inp" placeholder="Placas"><input id="reg-modelo" class="inp" placeholder="Modelo"><input id="reg-anio" type="number" class="inp" placeholder="Año 2021-2026" min="2021" max="2026"><input id="reg-licencia" class="inp" placeholder="Licencia"><input id="reg-vigencia" type="date" class="inp"><input id="reg-pass" type="password" class="inp" placeholder="Contrasena"><button onclick="choferRegistrar()" style="width:100%;padding:13px;background:#00c853;color:#fff;border:none;border-radius:10px">CREAR CHOFER</button><button onclick="mostrarLoginChofer()" style="width:100%;padding:10px;background:none;border:none;color:#1976d2">Ya tengo cuenta</button></div></div><div id="box-viajes-chofer" style="display:none"><div style="background:#000;color:#fff;padding:12px;display:flex;justify-content:space-between"><span id="nombre-chofer-log">Chofer</span><span id="gps-status" style="font-size:10px;color:#00e676">● GPS activo</span><button onclick="choferLogout()" style="background:#ff5252;color:#fff;border:none;padding:6px 10px;border-radius:6px">Salir</button></div><div style="padding:10px"><div style="display:flex;gap:6px"><button onclick="mostrarViajesChofer('pendientes')" style="flex:1;padding:10px;background:#000;color:#fff;border:none;border-radius:8px">Pendientes</button><button onclick="mostrarViajesChofer('mios')" style="flex:1;padding:10px;background:#fff;border:1px solid #000;border-radius:8px">Mios</button><button onclick="mostrarViajesChofer('completados')" style="flex:1;padding:10px;background:#fff;border:1px solid #000;border-radius:8px">Hechos</button></div><div id="lista-viajes-chofer"></div></div></div></div>
<div id="vista-admin" style="display:none"><div id="admin-login" style="padding:20px;max-width:400px;margin:80px auto;background:#fff;border-radius:16px"><h2 style="text-align:center">🔐 ADMIN</h2><input id="admin-pass-input" type="password" class="inp" placeholder="Clave unica AGL2026"><button onclick="adminLogin()" style="width:100%;padding:14px;background:#000;color:#fff;border:none;border-radius:10px">ENTRAR</button><button onclick="volverAlInicio()" style="width:100%;margin-top:10px;padding:12px;background:#eee;border:none;border-radius:12px">⬅ VOLVER</button></div><div id="admin-panel" style="display:none;padding:12px;background:#eef2f7;min-height:100vh"><h1 style="color:#0a3552">🔐 ADMIN V41.1</h1><div style="display:flex;gap:6px;flex-wrap:wrap;margin:10px 0"><a href="/" style="background:#0a3552;color:white;padding:8px 12px;border-radius:8px;text-decoration:none">Mapa</a><a href="/concentrado" style="background:#16a34a;color:white;padding:8px 12px;border-radius:8px;text-decoration:none">Concentrado</a><a href="/excel" style="background:#ff9500;color:white;padding:8px 12px;border-radius:8px;text-decoration:none">Excel</a><button onclick="adminLogout()" style="background:#ff5252;color:white;padding:8px 12px;border:none;border-radius:8px">Salir</button></div><div id="admin-stats" style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px"></div><div style="background:white;padding:12px;border-radius:12px;margin-top:10px"><h3>🚗 Choferes - Ver pass</h3><div id="admin-choferes"></div></div><div style="background:white;padding:12px;border-radius:12px;margin-top:10px"><h3>👤 Clientes - Ver pass + Reset</h3><div id="admin-clientes"></div></div><div style="background:white;padding:12px;border-radius:12px;margin-top:10px"><h3>📦 Viajes</h3><div id="admin-viajes" style="max-height:300px;overflow:auto;font-size:11px"></div></div></div></div>
<script>
if(window.location.href.includes('reset=1')){localStorage.clear();}
let map=null,origenMarker=null,destinoMarker=null,parada1Marker=null,parada2Marker=null,parada3Marker=null,routeLine,choferMarker=null,kmActual=0,precioActual=0,tiempoActual=0,numParadasVisibles=0,capaMapa,capaSate,adminToken=null,miChofer=null,clienteWatch=null,ratingId=null;
function toggleMenu(){document.getElementById('menu').classList.toggle('act');document.getElementById('overlay').classList.toggle('act');}
function initMap(){if(map){map.invalidateSize();return;}try{map=L.map('map',{zoomControl:false}).setView([21.8853,-102.2916],13);capaMapa=L.tileLayer('https://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',{subdomains:['mt0','mt1','mt2','mt3'],maxZoom:20}).addTo(map);capaSate=L.tileLayer('https://{s}.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}',{subdomains:['mt0','mt1','mt2','mt3'],maxZoom:20});map.on('click',e=>{if(!origenMarker){crearOrigen(e.latlng);return;}if(numParadasVisibles>=1&&!parada1Marker){crearParada(e.latlng,1);return;}if(numParadasVisibles>=2&&!parada2Marker){crearParada(e.latlng,2);return;}if(numParadasVisibles>=3&&!parada3Marker){crearParada(e.latlng,3);return;}if(!destinoMarker){crearDestino(e.latlng);return;}});}catch(err){}}
function elegirRol(r){localStorage.setItem('rol_AGL',r);document.getElementById('modal-rol').style.display='none';if(r==='chofer'){document.getElementById('vista-cliente').style.display='none';document.getElementById('vista-chofer').style.display='block';document.getElementById('vista-admin').style.display='none';verificarSesionChofer();}else if(r==='admin'){document.getElementById('vista-cliente').style.display='none';document.getElementById('vista-chofer').style.display='none';document.getElementById('vista-admin').style.display='block';}else{document.getElementById('vista-chofer').style.display='none';document.getElementById('vista-admin').style.display='none';document.getElementById('vista-cliente').style.display='block';initMap();setTimeout(()=>{if(map) map.invalidateSize();},400);verificarSesionCliente();}}
function cambiarRol(){if(clienteWatch) navigator.geolocation.clearWatch(clienteWatch);localStorage.removeItem('rol_AGL');location.reload();}
function volverAlInicio(){localStorage.removeItem('rol_AGL');document.getElementById('vista-cliente').style.display='none';document.getElementById('vista-chofer').style.display='none';document.getElementById('vista-admin').style.display='none';document.getElementById('modal-rol').style.display='flex';}
(function(){if(window.location.href.includes('reset=1')) return;let r=(localStorage.getItem('rol_AGL')||'').toLowerCase();if(!r) return;if(r==='chofer'){document.getElementById('modal-rol').style.display='none';document.getElementById('vista-cliente').style.display='none';document.getElementById('vista-chofer').style.display='block';verificarSesionChofer();}else if(r==='admin'){document.getElementById('modal-rol').style.display='none';document.getElementById('vista-cliente').style.display='none';document.getElementById('vista-chofer').style.display='none';document.getElementById('vista-admin').style.display='block';}})();
const verdeIcon=new L.Icon({iconUrl:'https://cdn.jsdelivr.net/gh/pointhi/leaflet-color-markers@master/img/marker-icon-2x-green.png',shadowUrl:'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',iconSize:[25,41],iconAnchor:[12,41]});
const rojoIcon=new L.Icon({iconUrl:'https://cdn.jsdelivr.net/gh/pointhi/leaflet-color-markers@master/img/marker-icon-2x-red.png',shadowUrl:'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',iconSize:[25,41],iconAnchor:[12,41]});
const amarilloIcon=new L.Icon({iconUrl:'https://cdn.jsdelivr.net/gh/pointhi/leaflet-color-markers@master/img/marker-icon-2x-yellow.png',shadowUrl:'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',iconSize:[25,41],iconAnchor:[12,41]});
const naranjaIcon=new L.Icon({iconUrl:'https://cdn.jsdelivr.net/gh/pointhi/leaflet-color-markers@master/img/marker-icon-2x-orange.png',shadowUrl:'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',iconSize:[25,41],iconAnchor:[12,41]});
const celesteIcon=new L.Icon({iconUrl:'https://cdn.jsdelivr.net/gh/pointhi/leaflet-color-markers@master/img/marker-icon-2x-blue.png',shadowUrl:'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',iconSize:[25,41],iconAnchor:[12,41]});
const flechaIcon=L.divIcon({html:'<div style="background:#000;color:#fff;width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center">➤</div>',iconSize:[28,28]});
async function getDir(ll,tipo){try{const r=await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${ll.lat}&lon=${ll.lng}&zoom=18`);const j=await r.json();let nom=j.display_name.split(',').slice(0,3).join(', ');if(tipo==1)document.getElementById('origen').value=nom;else if(tipo==2)document.getElementById('destino').value=nom;else if(tipo==3)document.getElementById('parada1').value=nom;else if(tipo==4)document.getElementById('parada2').value=nom;else if(tipo==5)document.getElementById('parada3').value=nom;}catch{}}
function crearOrigen(ll){if(!origenMarker){origenMarker=L.marker(ll,{draggable:true,icon:verdeIcon}).addTo(map);origenMarker.on('dragend',()=>{getDir(origenMarker.getLatLng(),1);trazar();});}else origenMarker.setLatLng(ll);getDir(ll,1);trazar();}
function crearDestino(ll){if(!destinoMarker){destinoMarker=L.marker(ll,{draggable:true,icon:rojoIcon}).addTo(map);destinoMarker.on('dragend',()=>{getDir(destinoMarker.getLatLng(),2);trazar();});}else destinoMarker.setLatLng(ll);getDir(ll,2);trazar();}
function crearParada(ll,t){if(t==1){if(!parada1Marker){parada1Marker=L.marker(ll,{draggable:true,icon:amarilloIcon}).addTo(map);parada1Marker.on('dragend',()=>{getDir(parada1Marker.getLatLng(),3);trazar();});}else parada1Marker.setLatLng(ll);getDir(ll,3);}else if(t==2){if(!parada2Marker){parada2Marker=L.marker(ll,{draggable:true,icon:naranjaIcon}).addTo(map);parada2Marker.on('dragend',()=>{getDir(parada2Marker.getLatLng(),4);trazar();});}else parada2Marker.setLatLng(ll);getDir(ll,4);}else if(t==3){if(!parada3Marker){parada3Marker=L.marker(ll,{draggable:true,icon:celesteIcon}).addTo(map);parada3Marker.on('dragend',()=>{getDir(parada3Marker.getLatLng(),5);trazar();});}else parada3Marker.setLatLng(ll);getDir(ll,5);}trazar();}
function agregarParada(){if(numParadasVisibles==0){document.getElementById('boxP1').style.display='flex';numParadasVisibles=1;}else if(numParadasVisibles==1){document.getElementById('boxP2').style.display='flex';numParadasVisibles=2;}else if(numParadasVisibles==2){document.getElementById('boxP3').style.display='flex';numParadasVisibles=3;}document.getElementById('txt-paradas').innerText=numParadasVisibles+' / 3';}
function miUbicacion(){navigator.geolocation.getCurrentPosition(p=>{let ll={lat:p.coords.latitude,lng:p.coords.longitude};crearOrigen(ll);if(map) map.setView([ll.lat,ll.lng],16);});}
function esForaneo(ll){let R=6371, dLat=(ll.lat-21.8853)*Math.PI/180, dLng=(ll.lng+102.2916)*Math.PI/180, a=Math.sin(dLat/2)**2+Math.cos(21.8853*Math.PI/180)*Math.cos(ll.lat*Math.PI/180)*Math.sin(dLng/2)**2;return R*2*Math.atan2(Math.sqrt(a),Math.sqrt(1-a))>(12+5);}
async function trazar(){if(!origenMarker) return;let pts=[origenMarker.getLatLng()];if(parada1Marker)pts.push(parada1Marker.getLatLng());if(parada2Marker)pts.push(parada2Marker.getLatLng());if(parada3Marker)pts.push(parada3Marker.getLatLng());if(destinoMarker)pts.push(destinoMarker.getLatLng());if(pts.length<2)return;try{let s=pts.map(p=>p.lng+','+p.lat).join(';');let r=await fetch(`https://router.project-osrm.org/route/v1/driving/${s}?overview=full&geometries=geojson`);let j=await r.json();if(!j.routes[0])return;let route=j.routes[0];kmActual=Math.round(route.distance/100)/10;if(kmActual<0.8)kmActual=0.8;tiempoActual=Math.round(route.duration/60);if(routeLine&&map)map.removeLayer(routeLine);routeLine=L.polyline(route.geometry.coordinates.map(c=>[c[1],c[0]]),{color:'#000',weight:6}).addTo(map);let cnt=(parada1Marker?1:0)+(parada2Marker?1:0)+(parada3Marker?1:0);let foraneo=pts.some(p=>esForaneo(p));let precio=65+cnt*10;if(kmActual>6){precio=35+(kmActual*6.6)+tiempoActual+cnt*10;if(foraneo)precio+=kmActual*2;if(precio<65)precio=65;}precioActual=Math.round(precio);document.getElementById('cotizacion').style.display='block';document.getElementById('dist').innerText=kmActual+' km - '+tiempoActual+' min';document.getElementById('precio').innerText='$'+precioActual+' MXN';document.getElementById('btnPedir').innerText='Confirmar $'+precioActual;document.getElementById('txt-foraneo').style.display=foraneo?'block':'none';if(map) map.fitBounds(routeLine.getBounds(),{padding:[60,60]});}catch{}}
async function pedir(){if(!precioActual) return alert('Toca mapa');let ca=JSON.parse(localStorage.getItem('clienteActual')||'null');let nombre=ca?ca.nombre:'Cliente';let fecha=document.getElementById('fechaViaje').value||new Date().toISOString().split('T')[0];let hora=document.getElementById('horaViaje').value||new Date().toLocaleTimeString().slice(0,5);let origen=document.getElementById('origen').value;let destino=document.getElementById('destino').value;let id='V'+Date.now();let data={id:id,cliente:nombre,cliente_tel:ca?ca.tel:'',operador:'Por asignar',chofer_tel:'',fecha:fecha,hora:hora,origen:origen,destino:destino,kms:kmActual,precio:precioActual,tiempo:tiempoActual,status:'pendiente',timestamp:new Date().toISOString(),rating:0};fetch('/api/viaje',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});alert('✅ Viaje solicitado');}
function borrarTodo(){document.getElementById('origen').value="";document.getElementById('destino').value="";document.getElementById('parada1').value="";document.getElementById('parada2').value="";document.getElementById('parada3').value="";document.getElementById('boxP1').style.display='none';document.getElementById('boxP2').style.display='none';document.getElementById('boxP3').style.display='none';numParadasVisibles=0;document.getElementById('cotizacion').style.display="none";if(origenMarker&&map){map.removeLayer(origenMarker);origenMarker=null;}if(destinoMarker&&map){map.removeLayer(destinoMarker);destinoMarker=null;}if(parada1Marker&&map){map.removeLayer(parada1Marker);parada1Marker=null;}if(parada2Marker&&map){map.removeLayer(parada2Marker);parada2Marker=null;}if(parada3Marker&&map){map.removeLayer(parada3Marker);parada3Marker=null;}if(routeLine&&map){map.removeLayer(routeLine);routeLine=null;}precioActual=0;}
function mostrarRegistroChofer(){document.getElementById('form-login').style.display='none';document.getElementById('form-registro').style.display='block';}
function mostrarLoginChofer(){document.getElementById('form-registro').style.display='none';document.getElementById('form-login').style.display='block';}
async function choferRegistrar(){let n=document.getElementById('reg-nombre').value.trim(),t=document.getElementById('reg-tel').value.trim(),p=document.getElementById('reg-placas').value.trim(),modelo=document.getElementById('reg-modelo').value.trim(),anio=parseInt(document.getElementById('reg-anio').value),lic=document.getElementById('reg-licencia').value.trim(),vig=document.getElementById('reg-vigencia').value,c=document.getElementById('reg-pass').value.trim();if(!n||!t||!p||!modelo||!anio||!lic||!vig||!c){alert('Llena todo');return;}let res=await fetch('/api/chofer/registrar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({nombre:n,tel:t,placas:p,modelo:modelo,anio:anio,licencia:lic,vigencia:vig,pass:c})});let d=await res.json();if(!d.ok){alert(d.error);return;}localStorage.setItem('choferActual',JSON.stringify(d.chofer));verificarSesionChofer();}
async function choferLogin(){let t=document.getElementById('chofer-tel').value.trim(),c=document.getElementById('chofer-pass').value.trim();let res=await fetch('/api/chofer/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({tel:t,pass:c})});let d=await res.json();if(!d.ok){alert(d.error);return;}localStorage.setItem('choferActual',JSON.stringify(d.chofer));verificarSesionChofer();}
function verificarSesionChofer(){let a=JSON.parse(localStorage.getItem('choferActual')||'null');if(a){document.getElementById('box-login-chofer').style.display='none';document.getElementById('box-viajes-chofer').style.display='block';document.getElementById('nombre-chofer-log').innerText=a.nombre;miChofer=a;iniciarGPSChofer();mostrarViajesChofer('pendientes');}else{document.getElementById('box-login-chofer').style.display='block';document.getElementById('box-viajes-chofer').style.display='none';}}
function choferLogout(){if(clienteWatch) navigator.geolocation.clearWatch(clienteWatch);localStorage.removeItem('choferActual');verificarSesionChofer();}
function mostrarRegistroCli(){document.getElementById('form-login-c').style.display='none';document.getElementById('form-registro-c').style.display='block';}
function mostrarLoginCli(){document.getElementById('form-registro-c').style.display='none';document.getElementById('form-login-c').style.display='block';}
async function clienteRegistrar(){let n=document.getElementById('cli-reg-nombre').value.trim(),t=document.getElementById('cli-reg-tel').value.trim(),c=document.getElementById('cli-reg-pass').value.trim();if(!n||!t||!c){alert('Llena todo');return;}let res=await fetch('/api/cliente/registrar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({nombre:n,tel:t,pass:c})});let d=await res.json();if(!d.ok){alert(d.error);return;}localStorage.setItem('clienteActual',JSON.stringify(d.cliente));document.getElementById('msg-cli').innerText='✅ Creado! Ahora dale Ya tengo cuenta';mostrarLoginCli();}
async function clienteLogin(){let t=document.getElementById('cli-tel').value.trim(),c=document.getElementById('cli-pass').value.trim();let res=await fetch('/api/cliente/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({tel:t,pass:c})});let d=await res.json();if(!d.ok){document.getElementById('msg-cli').innerText=d.error;alert(d.error);return;}localStorage.setItem('clienteActual',JSON.stringify(d.cliente));verificarSesionClienteLogged();}
function verificarSesionCliente(){initMap();document.getElementById('box-login-cliente').style.display='block';document.getElementById('box-cliente-viaje').style.display='none';document.getElementById('form-login-c').style.display='block';document.getElementById('form-registro-c').style.display='none';let a=JSON.parse(localStorage.getItem('clienteActual')||'null');if(a&&a.tel){document.getElementById('cli-tel').value=a.tel;}}
function verificarSesionClienteLogged(){initMap();document.getElementById('box-login-cliente').style.display='none';document.getElementById('box-cliente-viaje').style.display='block';setTimeout(()=>{if(map) map.invalidateSize();},400);iniciarSeguimientoCliente();}
function iniciarGPSChofer(){if(!navigator.geolocation) return;clienteWatch=navigator.geolocation.watchPosition(pos=>{fetch('/api/chofer/ubicacion',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({tel:miChofer.tel,lat:pos.coords.latitude,lng:pos.coords.longitude})});document.getElementById('gps-status').innerText='● GPS '+pos.coords.latitude.toFixed(3);},{},{enableHighAccuracy:true});}
function iniciarSeguimientoCliente(){setInterval(async()=>{let ca=JSON.parse(localStorage.getItem('clienteActual')||'null');if(!ca) return;let res=await fetch('/api/viajes/cliente/'+ca.tel);let vs=await res.json();let activo=vs.find(v=>v.status==='tomado'||v.status==='en_curso');if(activo&&activo.chofer_tel){let r2=await fetch('/api/chofer/ubicacion/'+activo.chofer_tel);let ub=await r2.json();if(ub.ok){if(!choferMarker)choferMarker=L.marker([ub.lat,ub.lng],{icon:flechaIcon}).addTo(map);else choferMarker.setLatLng([ub.lat,ub.lng]);document.getElementById('eta-box').style.display='block';document.getElementById('eta-box').innerText='🚗 '+activo.operador+' en camino';}}},5000);}
function mostrarViajesChofer(filtro){let ch=JSON.parse(localStorage.getItem('choferActual')||'null');fetch('/api/viajes').then(r=>r.json()).then(v=>{let lista=document.getElementById('lista-viajes-chofer');let fil=v;if(filtro==='pendientes')fil=v.filter(x=>x.status==='pendiente');if(filtro==='mios')fil=v.filter(x=>x.chofer_tel===ch.tel&&(x.status==='tomado'||x.status==='en_curso'));if(filtro==='completados')fil=v.filter(x=>x.chofer_tel===ch.tel&&x.status==='completado');if(fil.length==0){lista.innerHTML='<div style="padding:30px;text-align:center;color:#888">No hay en '+filtro+'</div>';return;}lista.innerHTML=fil.slice().reverse().map(x=>`<div style="border:2px solid #00c853;border-radius:12px;padding:10px;margin:8px 0"><b>${x.cliente} $${x.precio}</b><br>${x.origen.substring(0,40)}<br>→ ${x.destino.substring(0,40)}<br><small>${x.fecha} ${x.status}</small><br>${x.status==='pendiente'?`<button onclick="tomarViaje('${x.id}')" style="background:#00c853;color:#fff;border:none;padding:8px 12px;border-radius:8px">✅ TOMAR</button>`:''}${x.status==='tomado'?`<button onclick="iniciarViaje('${x.id}')" style="background:#000;color:#fff;border:none;padding:8px 12px;border-radius:8px">▶ INICIAR</button>`:''}${x.status==='en_curso'?`<button onclick="finalizarViaje('${x.id}')" style="background:#d32f2f;color:#fff;border:none;padding:8px 12px;border-radius:8px">⏹ FINALIZAR</button>`:''}</div>`).join('');});}
async function tomarViaje(id){let ch=JSON.parse(localStorage.getItem('choferActual'));let res=await fetch('/api/viaje/tomar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:id,chofer_tel:ch.tel,chofer_nombre:ch.nombre})});let d=await res.json();if(d.ok) mostrarViajesChofer('mios');}
async function iniciarViaje(id){await fetch('/api/viaje/iniciar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:id})});mostrarViajesChofer('mios');}
async function finalizarViaje(id){await fetch('/api/viaje/finalizar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:id})});ratingId=id;document.getElementById('modal-rating').style.display='flex';mostrarViajesChofer('completados');}
function verChoferAsignado(){let ca=JSON.parse(localStorage.getItem('clienteActual')||'null');if(!ca) return;fetch('/api/viajes/cliente/'+ca.tel).then(r=>r.json()).then(v=>{let a=v.find(x=>x.status!=='completado');if(!a||!a.chofer_tel){alert('Sin chofer aún');return;}fetch('/api/chofer/info/'+a.chofer_tel).then(r=>r.json()).then(c=>{alert('Conductor: '+a.operador);});});}
async function adminLogin(){let p=document.getElementById('admin-pass-input').value;let res=await fetch('/api/admin/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:p})});let d=await res.json();if(!d.ok){alert(d.error);return;}adminToken=p;localStorage.setItem('adminToken',p);document.getElementById('admin-login').style.display='none';document.getElementById('admin-panel').style.display='block';cargarAdmin();}
function adminLogout(){localStorage.removeItem('adminToken');adminToken=null;document.getElementById('admin-panel').style.display='none';document.getElementById('admin-login').style.display='block';}
async function cargarAdmin(){let pass=adminToken||localStorage.getItem('adminToken');let res=await fetch('/api/admin/data',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:pass})});let d=await res.json();if(!d.ok){alert(d.error);return;}document.getElementById('admin-stats').innerHTML=`<div style="background:white;padding:12px;border-radius:12px;text-align:center"><b>${d.choferes.length}</b><br>Choferes</div><div style="background:white;padding:12px;border-radius:12px;text-align:center"><b>${d.clientes.length}</b><br>Clientes</div><div style="background:white;padding:12px;border-radius:12px;text-align:center"><b>${d.viajes.length}</b><br>Viajes</div>`;document.getElementById('admin-choferes').innerHTML=d.choferes.map(c=>`<div style="border:1px solid #ddd;padding:10px;border-radius:10px;margin-bottom:6px"><b>${c.nombre}</b> ${c.tel}<br><small>${c.placas} - Pass: <b style="color:blue">${c.pass||'--'}</b></small><br>${d.bloqueados.includes(c.tel)?'🚫':'✅'}<br><div style="margin-top:6px"><button onclick="resetPass('${c.tel}','chofer')" style="background:#1976d2;color:white;border:none;padding:6px 10px;border-radius:6px">Reset a 123456</button><button onclick="bloquearChofer('${c.tel}')" style="background:#ff9500;color:white;border:none;padding:6px 10px;border-radius:6px;margin-left:4px">Bloq</button><button onclick="eliminarChofer('${c.tel}')" style="background:#ff3b30;color:white;border:none;padding:6px 10px;border-radius:6px;margin-left:4px">X</button></div></div>`).join('');document.getElementById('admin-clientes').innerHTML=d.clientes.map(c=>`<div style="border:1px solid #ddd;padding:10px;border-radius:10px;margin-bottom:6px"><b>${c.nombre}</b> ${c.tel}<br><small>Pass: <b style="color:blue;font-size:14px">${c.pass||'--'}</b></small> ${d.bloqueados.includes(c.tel)?'🚫':'✅'}<br><div style="margin-top:6px"><button onclick="resetPass('${c.tel}','cliente')" style="background:#1976d2;color:white;border:none;padding:6px 10px;border-radius:6px">Reset a 123456</button><button onclick="eliminarCliente('${c.tel}')" style="background:#ff3b30;color:white;border:none;padding:6px 10px;border-radius:6px;margin-left:4px">Borrar</button></div></div>`).join('');document.getElementById('admin-viajes').innerHTML=d.viajes.slice().reverse().slice(0,100).map(v=>`<div style="border-bottom:1px solid #eee;padding:4px">${v.fecha} ${v.cliente} → ${v.operador} $${v.precio} ${v.status}</div>`).join('');}
async function resetPass(tel,tipo){if(!confirm('Resetear pass de '+tel+' a 123456?'))return;await fetch('/api/admin/reset_pass',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:adminToken||localStorage.getItem('adminToken'),tel:tel,tipo:tipo,new_pass:'123456'})});alert('✅ Ahora la clave es 123456');cargarAdmin();}
async function eliminarChofer(tel){if(!confirm('Eliminar '+tel))return;await fetch('/api/admin/delete_chofer',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:adminToken||localStorage.getItem('adminToken'),tel:tel})});cargarAdmin();}
async function eliminarCliente(tel){if(!confirm('Eliminar cliente '+tel))return;await fetch('/api/admin/delete_cliente',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:adminToken||localStorage.getItem('adminToken'),tel:tel})});cargarAdmin();}
async function bloquearChofer(tel){await fetch('/api/admin/block',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:adminToken||localStorage.getItem('adminToken'),tel:tel})});cargarAdmin();}
async function bloquearCliente(tel){await fetch('/api/admin/block',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:adminToken||localStorage.getItem('adminToken'),tel:tel})});cargarAdmin();}
function enviarRating(){let c=document.getElementById('comentario-rating').value;fetch('/api/viaje/rating',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:ratingId,rating:5,comentario:c})});document.getElementById('modal-rating').style.display='none';}
</script></body></html>
"""

@app.route("/")
def index(): return render_template_string(HTML)

@app.route("/api/viaje", methods=["POST"])
def api_viaje():
    data=request.json; viajes.append(data); guardar(); return jsonify({"ok":True})

@app.route("/api/viajes")
def api_viajes(): return jsonify(viajes)

@app.route("/api/viajes/cliente/<tel>")
def api_viajes_cliente(tel): return jsonify([v for v in viajes if v.get('cliente_tel')==tel][-20:])

@app.route("/api/chofer/registrar", methods=["POST"])
def chofer_reg():
    d=request.json
    if d['tel'] in bloqueados: return jsonify({"ok":False,"error":"BLOQUEADO"})
    if any(c['tel']==d['tel'] for c in choferes_db): return jsonify({"ok":False,"error":"Ya registrado"})
    if int(d.get('anio',0))<2021: return jsonify({"ok":False,"error":"Solo 2021+"})
    choferes_db.append(d); guardar(); return jsonify({"ok":True,"chofer":d})

@app.route("/api/chofer/login", methods=["POST"])
def chofer_login():
    d=request.json
    if d['tel'] in bloqueados: return jsonify({"ok":False,"error":"BLOQUEADO"})
    f=next((c for c in choferes_db if c['tel']==d['tel'] and c['pass']==d['pass']),None)
    return jsonify({"ok":True,"chofer":f}) if f else jsonify({"ok":False,"error":"Pass incorrecto - revisa en Admin"})

@app.route("/api/chofer/info/<tel>")
def chofer_info(tel):
    f=next((c for c in choferes_db if c['tel']==tel),None)
    if not f: return jsonify({"ok":False})
    return jsonify({"ok":True,"chofer":f,"servicios":len([v for v in viajes if v.get('chofer_tel')==tel]),"rating":4.8})

@app.route("/api/chofer/ubicacion", methods=["POST"])
def chofer_ubic():
    d=request.json; ubicaciones[d['tel']]={"lat":d['lat'],"lng":d['lng']}; guardar(); return jsonify({"ok":True})

@app.route("/api/chofer/ubicacion/<tel>")
def get_ubic(tel):
    u=ubicaciones.get(tel); return jsonify({"ok":True,"lat":u['lat'],"lng":u['lng']}) if u else jsonify({"ok":False})

@app.route("/api/cliente/registrar", methods=["POST"])
def cli_reg():
    d=request.json
    if any(c['tel']==d['tel'] for c in clientes_db): return jsonify({"ok":False,"error":"Ya registrado - dale Ya tengo cuenta"})
    clientes_db.append(d); guardar(); return jsonify({"ok":True,"cliente":d})

@app.route("/api/cliente/login", methods=["POST"])
def cli_login():
    d=request.json
    f=next((c for c in clientes_db if c['tel']==d['tel'] and c['pass']==d['pass']),None)
    return jsonify({"ok":True,"cliente":f}) if f else jsonify({"ok":False,"error":"Cel o pass mal - Ve a Admin AGL2026 y resetea a 123456"})

@app.route("/api/viaje/tomar", methods=["POST"])
def tomar():
    d=request.json
    for v in viajes:
        if v['id']==d['id']: v['status']='tomado'; v['operador']=d['chofer_nombre']; v['chofer_tel']=d['chofer_tel']; guardar(); return jsonify({"ok":True,"viaje":v})
    return jsonify({"ok":False})

@app.route("/api/viaje/iniciar", methods=["POST"])
def iniciar():
    d=request.json
    for v in viajes:
        if v['id']==d['id']: v['status']='en_curso'; guardar(); return jsonify({"ok":True})
    return jsonify({"ok":False})

@app.route("/api/viaje/finalizar", methods=["POST"])
def finalizar():
    d=request.json
    for v in viajes:
        if v['id']==d['id']: v['status']='completado'; guardar(); return jsonify({"ok":True})
    return jsonify({"ok":False})

@app.route("/api/viaje/rating", methods=["POST"])
def rating():
    d=request.json
    for v in viajes:
        if v['id']==d['id']: v['rating']=d['rating']; guardar(); return jsonify({"ok":True})
    return jsonify({"ok":False})

@app.route("/api/admin/login", methods=["POST"])
def admin_login():
    return jsonify({"ok":True}) if request.json.get('password')==ADMIN_PASSWORD else jsonify({"ok":False,"error":"Clave mal - es AGL2026"})

@app.route("/api/admin/data", methods=["POST"])
def admin_data():
    if request.json.get('password')!=ADMIN_PASSWORD: return jsonify({"ok":False})
    return jsonify({"ok":True,"choferes":choferes_db,"clientes":clientes_db,"viajes":viajes,"bloqueados":bloqueados,"ubicaciones":ubicaciones})

@app.route("/api/admin/delete_chofer", methods=["POST"])
def del_ch():
    if request.json.get('password')!=ADMIN_PASSWORD: return jsonify({"ok":False})
    global choferes_db; choferes_db=[c for c in choferes_db if c['tel']!=request.json['tel']]; guardar(); return jsonify({"ok":True})

@app.route("/api/admin/delete_cliente", methods=["POST"])
def del_cl():
    if request.json.get('password')!=ADMIN_PASSWORD: return jsonify({"ok":False})
    global clientes_db; clientes_db=[c for c in clientes_db if c['tel']!=request.json['tel']]; guardar(); return jsonify({"ok":True})

@app.route("/api/admin/reset_pass", methods=["POST"])
def reset_pass():
    if request.json.get('password')!=ADMIN_PASSWORD: return jsonify({"ok":False})
    tel=request.json['tel']; tipo=request.json['tipo']; newp=request.json.get('new_pass','123456')
    if tipo=='cliente':
        for c in clientes_db:
            if c['tel']==tel: c['pass']=newp; guardar(); return jsonify({"ok":True})
    else:
        for c in choferes_db:
            if c['tel']==tel: c['pass']=newp; guardar(); return jsonify({"ok":True})
    return jsonify({"ok":False})

@app.route("/api/admin/block", methods=["POST"])
def block():
    if request.json.get('password')!=ADMIN_PASSWORD: return jsonify({"ok":False})
    tel=request.json['tel']
    if tel in bloqueados: bloqueados.remove(tel)
    else: bloqueados.append(tel)
    guardar(); return jsonify({"ok":True})

@app.route("/concentrado")
def conc():
    total=len(viajes); 
    html=f"<h1>Concentrado {total} viajes</h1><a href='/excel'>Excel</a> <a href='/'>Mapa</a><table border=1><tr><th>Fecha</th><th>Cliente</th><th>Chofer</th></tr>"
    for v in viajes: html+=f"<tr><td>{v.get('fecha')}</td><td>{v.get('cliente')}</td><td>{v.get('operador')}</td></tr>"
    html+="</table>"; return html

@app.route("/excel")
def excel():
    out=io.StringIO(); w=csv.writer(out); w.writerow(['Fecha','Cliente','Chofer','KMs','Precio'])
    for v in viajes: w.writerow([v.get('fecha'),v.get('cliente'),v.get('operador'),v.get('kms'),v.get('precio')])
    mem=io.BytesIO(); mem.write(out.getvalue().encode('utf-8-sig')); mem.seek(0)
    return send_file(mem, as_attachment=True, download_name="AGL.csv", mimetype="text/csv")

if __name__=="__main__": app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
