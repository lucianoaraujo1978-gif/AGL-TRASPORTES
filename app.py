from flask import Flask, render_template_string, request, jsonify
import json, os, math
app = Flask(__name__)
ADMIN_PASSWORD = "AGL2026"
viajes, choferes_db, clientes_db = [], [], []
def cargar():
  global viajes, choferes_db, clientes_db
  try:
    if os.path.exists("viajes.json"):
      with open("viajes.json") as f: viajes.extend(json.load(f))
    if os.path.exists("choferes_db.json"):
      with open("choferes_db.json") as f: choferes_db.extend(json.load(f))
    if os.path.exists("clientes_db.json"):
      with open("clientes_db.json") as f: clientes_db.extend(json.load(f))
  except: pass
def guardar():
  try:
    with open("viajes.json","w") as f: json.dump(viajes,f)
    with open("choferes_db.json","w") as f: json.dump(choferes_db,f)
    with open("clientes_db.json","w") as f: json.dump(clientes_db,f)
  except: pass
cargar()
def haversine(lat1,lon1,lat2,lon2):
    R=6371; dLat=math.radians(lat2-lat1); dLon=math.radians(lon2-lon1)
    a=math.sin(dLat/2)**2+math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dLon/2)**2
    return R*2*math.atan2(math.sqrt(a),math.sqrt(1-a))

HTML = """<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>AGL V41.9 DISTANCIA FIX</title>
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
<div id="modal-rol"><div class="box-rol"><h2>🚕 AGL Transporte</h2><p style="margin:8px 0 16px;color:#666;font-size:11px">V41.9 - DISTANCIA Y COSTO FIJO</p>
<button type="button" onclick="elegirRol('cliente')" style="width:100%;padding:16px;border:none;border-radius:14px;font-weight:800;margin-bottom:10px;background:#000;color:#fff">👤 SOY CLIENTE</button>
<button type="button" onclick="elegirRol('chofer')" style="width:100%;padding:16px;border:none;border-radius:14px;font-weight:800;margin-bottom:10px;background:#00c853;color:#fff">🚗 SOY CHOFER</button>
<button type="button" onclick="elegirRol('admin')" style="width:100%;padding:16px;border:none;border-radius:14px;font-weight:800;background:#0a3552;color:#fff">🔐 SOY ADMIN</button></div></div>

<div id="vista-cliente" style="display:none">
<div id="box-login-cliente" style="padding:20px;max-width:400px;margin:70px auto 0;background:#fff;position:relative;z-index:20;border-radius:16px"><h2 style="text-align:center">👤 Cliente</h2><div id="form-login-c"><input id="cli-tel" class="inp" placeholder="Celular"><input id="cli-pass" class="inp" type="password" placeholder="Contraseña"><button onclick="clienteLogin()" style="width:100%;padding:13px;background:#000;color:#fff;border:none;border-radius:10px">ENTRAR</button><button onclick="volverAlInicio()" style="width:100%;margin-top:10px;padding:11px;background:#eee;border:none;border-radius:10px">⬅ MENU</button></div></div>

<div id="box-cliente-viaje" style="display:none"><div id="map"></div><button onclick="miUbicacion()" style="position:fixed;bottom:160px;right:14px;z-index:12;width:50px;height:50px;background:#fff;border:none;border-radius:50%;box-shadow:0 4px 18px rgba(0,0,0,.3)">📍</button>
<div class="top-bar"><button class="menu-btn" onclick="toggleMenu()">☰</button><div class="search-card"><div class="item"><div class="dot o"></div><input id="origen" placeholder="Origen"></div><div class="item parada-extra" id="boxP1"><div class="dot" style="background:#ffcc00"></div><input id="parada1" placeholder="Parada 1"></div><div class="item parada-extra" id="boxP2"><div class="dot" style="background:#ff9500"></div><input id="parada2" placeholder="Parada 2"></div><div class="item parada-extra" id="boxP3"><div class="dot" style="background:#00e5ff"></div><input id="parada3" placeholder="Parada 3"></div><div class="item"><div class="dot d"></div><input id="destino" placeholder="Destino"></div></div></div>

<div id="menu"><div class="menu-header"><b>🚕 AGL AGS</b><button onclick="toggleMenu()" style="width:34px;height:34px;border-radius:50%;background:#111;color:#fff;border:none">✕</button></div>
<div class="menu-body">
  <div style="background:#eef5ff;padding:14px;border-radius:14px;margin-bottom:14px;border:1px solid #b5d0ff">
    <b style="font-size:14px">📅 Programar flete</b><br><span style="font-size:11px;color:#555">Fecha y hora para el cliente</span>
    <div style="display:flex;gap:8px;margin-top:10px">
      <input type="date" id="fecha" style="flex:1;padding:11px;border-radius:10px;border:1px solid #aaa;background:#fff;font-weight:700">
      <input type="time" id="hora" style="flex:1;padding:11px;border-radius:10px;border:1px solid #aaa;background:#fff;font-weight:700">
    </div>
  </div>
  <div class="menu-linea" onclick="agregarParada()"><div><b>agregar parada</b><br><span id="txt-paradas">0 / 3</span></div><span>➕</span></div>
  <div class="menu-linea" onclick="borrarTodo()"><div><b>corregir orden</b></div><span>✏️</span></div>
  <div class="menu-linea" onclick="volverAlInicio()"><div><b>volver a menu inicial</b></div><span>🏠</span></div>
</div></div><div class="overlay" id="overlay" onclick="toggleMenu()"></div>

<div id="cotizacion"><div id="dist" style="font-size:13px;color:#333;font-weight:600"></div><b id="precio" style="font-size:26px;color:#000">$0 MXN</b></div>
<button class="btn-confirm" id="btnPedir" onclick="pedir()">Confirmar Flete $0</button>
</div></div>

<div id="vista-chofer" style="display:none"><div id="box-login-chofer" style="padding:20px;max-width:400px;margin:20px auto;background:#fff;border-radius:16px"><h2 style="text-align:center">🚗 Chofer</h2><div id="form-login"><input id="chofer-tel" class="inp" placeholder="Celular"><input id="chofer-pass" class="inp" type="password" placeholder="Contraseña"><button onclick="choferLogin()" style="width:100%;padding:13px;background:#000;color:#fff;border:none;border-radius:10px">ENTRAR</button><button onclick="volverAlInicio()" style="width:100%;margin-top:10px;padding:11px;background:#eee;border:none;border-radius:10px">⬅ MENU</button></div></div><div id="box-viajes-chofer" style="display:none"><div style="background:#000;color:#fff;padding:12px;display:flex;justify-content:space-between"><span id="nombre-chofer-log">Chofer</span><button onclick="choferLogout()" style="background:#ff5252;color:#fff;border:none;padding:6px 10px;border-radius:6px">Salir</button></div><div style="padding:10px"><div id="lista-viajes-chofer"></div></div></div></div>

<div id="vista-admin" style="display:none"><div id="admin-login" style="padding:20px;max-width:400px;margin:80px auto;background:#fff;border-radius:16px"><h2 style="text-align:center">🔐 ADMIN</h2><input id="admin-pass-input" type="password" class="inp" placeholder="AGL2026"><button onclick="adminLogin()" style="width:100%;padding:14px;background:#000;color:#fff;border:none;border-radius:10px">ENTRAR</button><button onclick="volverAlInicio()" style="width:100%;margin-top:10px;padding:12px;background:#eee;border:none;border-radius:12px">⬅ VOLVER</button></div><div id="admin-panel" style="display:none;padding:12px;background:#eef2f7;min-height:100vh"><h1>ADMIN</h1><div id="admin-viajes"></div><button onclick="volverAlInicio()" style="margin-top:12px;padding:12px;width:100%;background:#000;color:#fff;border:none;border-radius:10px">Volver</button></div></div>

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
const verdeIcon=new L.Icon({iconUrl:'https://cdn.jsdelivr.net/gh/pointhi/leaflet-color-markers@master/img/marker-icon-2x-green.png',shadowUrl:'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',iconSize:[35,55],iconAnchor:[17,55]});
const rojoIcon=new L.Icon({iconUrl:'https://cdn.jsdelivr.net/gh/pointhi/leaflet-color-markers@master/img/marker-icon-2x-red.png',shadowUrl:'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',iconSize:[35,55],iconAnchor:[17,55]});
function makeDraggable(m, cb){m.on('touchstart mousedown', ()=> map.dragging.disable()); m.on('dragend', (ev)=>{ map.dragging.enable(); cb(ev.target.getLatLng()); }); m.on('touchend', ()=> map.dragging.enable());}
function crearOrigen(ll){origenLatLng=ll; if(!origenMarker){origenMarker=L.marker(ll,{draggable:true,autoPan:true,icon:verdeIcon}).addTo(map); makeDraggable(origenMarker, (nl)=>{origenLatLng=nl; trazarLocal();});}else origenMarker.setLatLng(ll); trazarLocal();}
function crearDestino(ll){destinoLatLng=ll; if(!destinoMarker){destinoMarker=L.marker(ll,{draggable:true,autoPan:true,icon:rojoIcon}).addTo(map); makeDraggable(destinoMarker, (nl)=>{destinoLatLng=nl; trazarLocal();});}else destinoMarker.setLatLng(ll); trazarLocal();}
function crearParada1(ll){if(!parada1Marker){parada1Marker=L.marker(ll,{draggable:true,autoPan:true,icon:L.icon({iconUrl:'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-yellow.png',shadowUrl:'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',iconSize:[35,55],iconAnchor:[17,55]})}).addTo(map); makeDraggable(parada1Marker, ()=>trazarLocal());}else parada1Marker.setLatLng(ll); trazarLocal();}
function crearParada2(ll){if(!parada2Marker){parada2Marker=L.marker(ll,{draggable:true,autoPan:true,icon:L.icon({iconUrl:'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-orange.png',shadowUrl:'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',iconSize:[35,55],iconAnchor:[17,55]})}).addTo(map); makeDraggable(parada2Marker, ()=>trazarLocal());}else parada2Marker.setLatLng(ll); trazarLocal();}
function crearParada3(ll){if(!parada3Marker){parada3Marker=L.marker(ll,{draggable:true,autoPan:true,icon:L.icon({iconUrl:'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',shadowUrl:'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',iconSize:[35,55],iconAnchor:[17,55]})}).addTo(map); makeDraggable(parada3Marker, ()=>trazarLocal());}else parada3Marker.setLatLng(ll); trazarLocal();}
function agregarParada(){if(numParadasVisibles>=3){alert('Máximo 3');return;}numParadasVisibles++;document.getElementById('boxP'+numParadasVisibles).style.display='flex';document.getElementById('txt-paradas').innerText=numParadasVisibles+' / 3';toggleMenu();}
function miUbicacion(){navigator.geolocation.getCurrentPosition(p=>{let ll={lat:p.coords.latitude,lng:p.coords.longitude};miPos=ll;crearOrigen(ll);if(map) map.setView([ll.lat,ll.lng],16);});}
function calcDist(lat1,lon1,lat2,lon2){let R=6371;let dLat=(lat2-lat1)*Math.PI/180;let dLon=(lon2-lon1)*Math.PI/180;let a=Math.sin(dLat/2)**2+Math.cos(lat1*Math.PI/180)*Math.cos(lat2*Math.PI/180)*Math.sin(dLon/2)**2;return R*2*Math.atan2(Math.sqrt(a),Math.sqrt(1-a));}
function trazarLocal(){
    if(!origenMarker) return; let pts=[]; pts.push(origenMarker.getLatLng());
    if(parada1Marker) pts.push(parada1Marker.getLatLng()); if(parada2Marker) pts.push(parada2Marker.getLatLng()); if(parada3Marker) pts.push(parada3Marker.getLatLng()); if(destinoMarker) pts.push(destinoMarker.getLatLng());
    if(pts.length<2) return;
    let dist=0; for(let i=0;i<pts.length-1;i++){dist+=calcDist(pts[i].lat,pts[i].lng,pts[i+1].lat,pts[i+1].lng);}
    kmActual=Math.round(dist*10)/10; if(kmActual<0.8)kmActual=0.8;
    precioActual=Math.round(20+(kmActual*6)); if(precioActual<80)precioActual=80;
    tiempoActual=Math.round(kmActual*3.2);
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
      precioActual=Math.round(20+(kmActual*6)); if(precioActual<80)precioActual=80;
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
async function pedir(){
  if(!precioActual) return alert('Toca mapa');
  let ca=JSON.parse(localStorage.getItem('clienteActual')||'null');
  let fecha=document.getElementById('fecha').value; let hora=document.getElementById('hora').value;
  if(!fecha||!hora){alert('Abre menú ☰ y pon fecha y hora');toggleMenu();return;}
  let id='V'+Date.now();
  let data={id:id,cliente:ca?ca.nombre:'Cliente',fecha:fecha,hora:hora,origen:'Origen',destino:'Destino',origen_lat:origenLatLng.lat,origen_lng:origenLatLng.lng,destino_lat:destinoLatLng.lat,destino_lng:destinoLatLng.lng,kms:kmActual,precio:precioActual,status:'pendiente'};
  await fetch('/api/viaje',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
  alert('✅ Confirmado $'+precioActual+' '+kmActual+'km - '+fecha+' '+hora);
  borrarTodo();
}
function borrarTodo(){document.getElementById('origen').value="";document.getElementById('destino').value="";document.getElementById('cotizacion').style.display="none";document.getElementById('btnPedir').style.display="none";if(origenMarker){map.removeLayer(origenMarker);origenMarker=null;}if(destinoMarker){map.removeLayer(destinoMarker);destinoMarker=null;}if(parada1Marker){map.removeLayer(parada1Marker);parada1Marker=null;}if(parada2Marker){map.removeLayer(parada2Marker);parada2Marker=null;}if(parada3Marker){map.removeLayer(parada3Marker);parada3Marker=null;}if(routeLine){map.removeLayer(routeLine);routeLine=null;}precioActual=0; kmActual=0; origenLatLng=null; destinoLatLng=null; numParadasVisibles=0;document.getElementById('boxP1').style.display='none';document.getElementById('boxP2').style.display='none';document.getElementById('boxP3').style.display='none';document.getElementById('txt-paradas').innerText='0 / 3';}
function mostrarRegistroChofer(){}
function verificarSesionChofer(){}
function choferLogin(){}
function choferLogout(){localStorage.removeItem('choferActual');}
function mostrarRegistroCli(){}
function verificarSesionCliente(){initMap();document.getElementById('box-login-cliente').style.display='none';document.getElementById('box-cliente-viaje').style.display='block';setTimeout(()=>{if(map) map.invalidateSize();},400);}
function clienteLogin(){verificarSesionCliente();}
function adminLogin(){let p=document.getElementById('admin-pass-input').value;if(p==='AGL2026'){localStorage.setItem('adminToken',p);document.getElementById('admin-login').style.display='none';document.getElementById('admin-panel').style.display='block';}}
(function(){let r=localStorage.getItem('rol_AGL');if(r==='cliente'){document.getElementById('modal-rol').style.display='none';document.getElementById('vista-cliente').style.display='block';verificarSesionCliente();}else if(r==='chofer'){document.getElementById('modal-rol').style.display='none';document.getElementById('vista-chofer').style.display='block';}else if(r==='admin'){document.getElementById('modal-rol').style.display='none';document.getElementById('vista-admin').style.display='block';}})();
</script></body></html>
"""
@app.route("/")
def index(): return render_template_string(HTML)
@app.route("/api/viaje", methods=["POST"])
def api_viaje():
    viajes.append(request.json); guardar(); return jsonify({"ok":True})
@app.route("/api/viajes_cercanos")
def viajes_cercanos(): return jsonify(viajes)
if __name__=="__main__": app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
