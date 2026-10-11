from flask import Flask, render_template_string, request, jsonify, send_file
import os, json, io, csv
from datetime import datetime

app = Flask(__name__)
viajes = []

# Cargar viajes si existen
try:
    if os.path.exists("/tmp/viajes.json"):
        with open("/tmp/viajes.json") as f:
            viajes.extend(json.load(f))
except:
    pass

MAPA = '''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AGL V35 AGS BONITO 4 PARADAS</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:Arial}
body{height:100vh;overflow:hidden}
#map{position:fixed!important;top:0;left:0;width:100%;height:100vh!important;z-index:1}
.top{position:fixed;top:12px;left:12px;right:12px;z-index:10;display:flex;gap:10px;max-width:420px}
.menu-btn{width:46px;height:46px;background:#fff;border:none;border-radius:14px;box-shadow:0 4px 18px rgba(0,0,0,.28);font-size:20px}
.search-card{background:#fff;border-radius:16px;box-shadow:0 8px 28px rgba(0,0,0,.26);padding:8px 10px;flex:1}
.item{display:flex;align-items:center;gap:8px;padding:8px 4px}
.item+.item{border-top:1px solid #eee}
.dot{width:8px;height:8px;border-radius:50%}.dot.o{background:#00c853}.dot.d{background:#ff3b30}
input{flex:1;border:none;outline:none;font-size:14px;font-weight:600;background:transparent}
#menu{position:fixed;top:0;left:-100%;width:82%;max-width:320px;height:100vh;background:#fff;z-index:30;transition:.28s;padding:18px 14px;overflow-y:auto}
#menu.act{left:0}
.overlay{position:fixed;inset:0;background:rgba(0,0,0,.35);z-index:20;display:none}
.overlay.act{display:block}
#menu button{width:100%;text-align:left;background:#f6f6f6;border:none;padding:13px 12px;border-radius:12px;margin-bottom:8px;font-weight:700}
.parada-extra{display:none}
#cotizacion{position:fixed;bottom:72px;left:12px;right:12px;z-index:11;background:#fff;border-radius:16px;padding:12px 14px;display:none;box-shadow:0 8px 28px rgba(0,0,0,.32);max-width:420px;margin:auto}
.btn{position:fixed;bottom:10px;left:12px;right:12px;z-index:11;background:#000;color:#fff;font-weight:800;padding:16px;border:none;border-radius:16px;max-width:420px;margin:auto}
</style>
</head>
<body>
<div id="map"></div>
<button onclick="miUbicacion()" style="position:fixed;bottom:90px;right:14px;z-index:12;width:50px;height:50px;background:#fff;border:none;border-radius:50%;box-shadow:0 4px 18px rgba(0,0,0,.3);font-size:22px">📍</button>
<div class="top"><button class="menu-btn" onclick="toggleMenu()">☰</button><div class="search-card"><div class="item"><div class="dot o"></div><input id="origen" placeholder="Origen - AGS"></div><div class="item parada-extra" id="boxP1"><div class="dot" style="background:#ffcc00"></div><input id="parada1" placeholder="Parada 1"></div><div class="item parada-extra" id="boxP2"><div class="dot" style="background:#ff9500"></div><input id="parada2" placeholder="Parada 2"></div><div class="item parada-extra" id="boxP3"><div class="dot" style="background:#00e5ff"></div><input id="parada3" placeholder="Parada 3"></div><div class="item"><div class="dot d"></div><input id="destino" placeholder="¿A dónde va?"></div></div></div>
<div id="menu"><div style="display:flex;justify-content:space-between;margin-bottom:16px"><b>🚕 AGL AGS</b><button onclick="toggleMenu()" style="width:36px;height:36px;border-radius:50%;background:#111;color:#fff">✕</button></div><button onclick="agregarParada();toggleMenu()">➕ Agregar parada (hasta 3)</button><button onclick="setTipo('mapa');toggleMenu()">🗺️ Mapa</button><button onclick="setTipo('satelite');toggleMenu()">🛰️ Satélite</button><a href="/concentrado" style="display:block;background:#0a3552;color:white;padding:13px 12px;border-radius:12px;text-decoration:none;font-weight:700;margin-bottom:8px;text-align:center">📊 CONCENTRADO</a><div style="margin-top:12px"><input id="nombre" placeholder="👤 Cliente" style="width:100%;background:#f5f5f5;border:none;padding:11px;border-radius:10px;margin-bottom:6px;font-weight:600"><div style="display:flex;gap:6px"><select id="pasajeros" style="background:#e8f5e9;border:none;padding:8px;border-radius:10px;font-weight:800"><option value="4" selected>👥 4</option><option>1</option><option>2</option><option>3</option><option>5</option><option>6</option></select><input type="date" id="fechaViaje"><input type="time" id="horaViaje"></div></div><div style="display:flex;gap:8px;margin-top:16px"><button onclick="borrarTodo()" style="flex:1;background:#fff;border:1.5px solid #8bc34a;padding:12px;border-radius:12px;font-weight:800">BORRAR</button><button onclick="toggleMenu()" style="flex:1;background:#000;color:#fff;padding:12px;border-radius:12px;font-weight:800">CERRAR</button></div></div>
<div class="overlay" id="overlay" onclick="toggleMenu()"></div>
<div id="cotizacion"><div id="dist" style="font-size:11px;color:#666"></div><b id="precio" style="font-size:22px">$0 MXN</b></div>
<button class="btn" id="btnPedir" onclick="pedir()">Confirmar $0</button>
<script>
const NUMERO="524491909860";
let map,origenMarker=null,destinoMarker=null,parada1Marker=null,parada2Marker=null,parada3Marker=null,routeLine,kmActual=0,precioActual=0,numParadasVisibles=0,capaMapa,capaSate;
function toggleMenu(){document.getElementById('menu').classList.toggle('act');document.getElementById('overlay').classList.toggle('act');}
const verdeIcon=new L.Icon({iconUrl:'https://cdn.jsdelivr.net/gh/pointhi/leaflet-color-markers@master/img/marker-icon-2x-green.png',shadowUrl:'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',iconSize:[25,41],iconAnchor:[12,41]});
const rojoIcon=new L.Icon({iconUrl:'https://cdn.jsdelivr.net/gh/pointhi/leaflet-color-markers@master/img/marker-icon-2x-red.png',shadowUrl:'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',iconSize:[25,41],iconAnchor:[12,41]});
const amarilloIcon=new L.Icon({iconUrl:'https://cdn.jsdelivr.net/gh/pointhi/leaflet-color-markers@master/img/marker-icon-2x-yellow.png',shadowUrl:'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',iconSize:[25,41],iconAnchor:[12,41]});
const naranjaIcon=new L.Icon({iconUrl:'https://cdn.jsdelivr.net/gh/pointhi/leaflet-color-markers@master/img/marker-icon-2x-orange.png',shadowUrl:'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',iconSize:[25,41],iconAnchor:[12,41]});
const celesteIcon=new L.Icon({iconUrl:'https://cdn.jsdelivr.net/gh/pointhi/leaflet-color-markers@master/img/marker-icon-2x-blue.png',shadowUrl:'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',iconSize:[25,41],iconAnchor:[12,41]});
map=L.map('map',{zoomControl:false}).setView([21.8853,-102.2916],13);
capaMapa=L.tileLayer('https://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',{subdomains:['mt0','mt1','mt2','mt3'],maxZoom:20}).addTo(map);
capaSate=L.tileLayer('https://{s}.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}',{subdomains:['mt0','mt1','mt2','mt3'],maxZoom:20});
function setTipo(t){if(t=='mapa'){if(map.hasLayer(capaSate))map.removeLayer(capaSate);capaMapa.addTo(map);}else{if(map.hasLayer(capaMapa))map.removeLayer(capaMapa);capaSate.addTo(map);}}
async function getDir(ll,tipo){try{const r=await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${ll.lat}&lon=${ll.lng}&zoom=18`);const j=await r.json();let nom=j.display_name.split(',').slice(0,3).join(', ');if(tipo==1) document.getElementById('origen').value=nom;else if(tipo==2) document.getElementById('destino').value=nom;else if(tipo==3) document.getElementById('parada1').value=nom;else if(tipo==4) document.getElementById('parada2').value=nom;else if(tipo==5) document.getElementById('parada3').value=nom;}catch{}}
function crearOrigen(ll){if(!origenMarker){origenMarker=L.marker(ll,{draggable:true,icon:verdeIcon}).addTo(map);origenMarker.on('dragend',()=>{getDir(origenMarker.getLatLng(),1);trazar();});}else origenMarker.setLatLng(ll); getDir(ll,1); trazar();}
function crearDestino(ll){if(!destinoMarker){destinoMarker=L.marker(ll,{draggable:true,icon:rojoIcon}).addTo(map);destinoMarker.on('dragend',()=>{getDir(destinoMarker.getLatLng(),2);trazar();});}else destinoMarker.setLatLng(ll); getDir(ll,2); trazar();}
function crearParada(ll,t){if(t==1){if(!parada1Marker){parada1Marker=L.marker(ll,{draggable:true,icon:amarilloIcon}).addTo(map);parada1Marker.on('dragend',()=>{getDir(parada1Marker.getLatLng(),3);trazar();});}else parada1Marker.setLatLng(ll); getDir(ll,3);}else if(t==2){if(!parada2Marker){parada2Marker=L.marker(ll,{draggable:true,icon:naranjaIcon}).addTo(map);parada2Marker.on('dragend',()=>{getDir(parada2Marker.getLatLng(),4);trazar();});}else parada2Marker.setLatLng(ll); getDir(ll,4);}else if(t==3){if(!parada3Marker){parada3Marker=L.marker(ll,{draggable:true,icon:celesteIcon}).addTo(map);parada3Marker.on('dragend',()=>{getDir(parada3Marker.getLatLng(),5);trazar();});}else parada3Marker.setLatLng(ll); getDir(ll,5);}trazar();}
function agregarParada(){if(numParadasVisibles==0){document.getElementById('boxP1').style.display='flex';numParadasVisibles=1;}else if(numParadasVisibles==1){document.getElementById('boxP2').style.display='flex';numParadasVisibles=2;}else if(numParadasVisibles==2){document.getElementById('boxP3').style.display='flex';numParadasVisibles=3;}else alert('Máximo 3 paradas extra');}
function miUbicacion(){navigator.geolocation.getCurrentPosition(pos=>{const p={lat:pos.coords.latitude,lng:pos.coords.longitude};crearOrigen(p);map.setView([p.lat,p.lng],16);});}
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
    kmActual=Math.round(route.distance/100)/10; if(kmActual<0.8)kmActual=0.8;
    if(routeLine)map.removeLayer(routeLine);
    routeLine=L.polyline(route.geometry.coordinates.map(c=>[c[1],c[0]]),{color:'#000',weight:6}).addTo(map);
    let cnt=(parada1Marker?1:0)+(parada2Marker?1:0)+(parada3Marker?1:0);
    let precio=65+cnt*10; if(kmActual>6){precio=35+(kmActual*6.6)+(route.duration/60)+cnt*10; if(precio<65)precio=65;}
    precioActual=Math.round(precio);
    document.getElementById('cotizacion').style.display='block';
    document.getElementById('dist').innerText=kmActual+' km - '+pts.length+' puntos';
    document.getElementById('precio').innerText='$'+precioActual+' MXN';
    document.getElementById('btnPedir').innerText='Confirmar $'+precioActual;
    map.fitBounds(routeLine.getBounds(),{padding:[60,60]});
  }catch{}
}
async function pedir(){
  if(!precioActual) return alert('Toca el mapa primero');
  let nombre=document.getElementById('nombre').value||'Cliente AGS';
  let fecha=document.getElementById('fechaViaje').value||new Date().toISOString().split('T')[0];
  let hora=document.getElementById('horaViaje').value||new Date().toLocaleTimeString();
  let pax=document.getElementById('pasajeros').value;
  let origen=document.getElementById('origen').value;
  let destino=document.getElementById('destino').value;
  let p1=document.getElementById('parada1').value;
  let p2=document.getElementById('parada2').value;
  let p3=document.getElementById('parada3').value;
  let paradasTxt=[origen,p1,p2,p3,destino].filter(x=>x).join(' → ');
  let data={solicita:'App V35',cliente:nombre,operador:'Por asignar',pasajeros:pax,fecha:fecha,hora:hora,origen:origen,parada1:p1,parada2:p2,parada3:p3,destino:destino,paradas:paradasTxt,kms:kmActual,precio:precioActual,latO:origenMarker?origenMarker.getLatLng().lat:21.8853,lngO:origenMarker?origenMarker.getLatLng().lng:-102.2916,latD:destinoMarker?destinoMarker.getLatLng().lat:21.8853,lngD:destinoMarker?destinoMarker.getLatLng().lng:-102.2916,timestamp:new Date().toISOString()};
  fetch('/api/viaje',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
  let linkMapa=`https://www.google.com/maps/dir/${origen}/${destino}`;
  let msg=`🚕 *VIAJE AGL AGS*%0A👤 ${nombre}%0A🔴 ${origen}%0A${p1?'🟡 '+p1+'%0A':''}${p2?'🟠 '+p2+'%0A':''}${p3?'🔵 '+p3+'%0A':''}🔵 ${destino}%0A📏 ${kmActual} km • $${precioActual}%0A🗺️ ${linkMapa}`;
  window.open(`https://wa.me/${NUMERO}?text=${msg}`,'_blank');
}
function borrarTodo(){
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
</script>
</body>
</html>
'''

CONCENTRADO_HTML = '''
<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Concentrado AGL</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>body{font-family:Arial;margin:0;background:#eef2f7;padding:12px}h1{color:#0a3552}.card{background:white;padding:14px;border-radius:14px;margin-bottom:10px}table{width:100%;border-collapse:collapse;font-size:11px}th,td{border:1px solid #ddd;padding:6px}th{background:#0a3552;color:white}.btn{background:#0a3552;color:white;padding:10px 14px;border-radius:10px;text-decoration:none;display:inline-block;margin-right:6px}.grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px}</style>
</head><body>
<h1>📊 Concentrado AGL - Aguascalientes V35</h1>
<a href="/" class="btn">← Mapa Bonito</a><a href="/excel" class="btn" style="background:#16a34a">⬇️ Excel</a><button onclick="location.reload()" class="btn" style="background:black">🔄 Actualizar</button>
<div class="grid"><div class="card">Total<br><b style="font-size:22px">{{total}}</b> viajes</div><div class="card">KMs<br><b style="font-size:22px">{{total_kms}} km</b></div><div class="card">Ingresos<br><b style="font-size:22px">${{total_precio}}</b></div></div>
<div class="card"><canvas id="c1"></canvas></div>
<div class="card" style="overflow:auto"><table><tr><th>#</th><th>Fecha</th><th>Cliente</th><th>Origen</th><th>Paradas</th><th>Destino</th><th>KMs</th><th>$</th><th>Maps</th></tr>
{% for v in viajes %}<tr><td>{{loop.index}}</td><td>{{v.fecha}} {{v.hora}}</td><td>{{v.cliente}}</td><td>{{v.origen[:40]}}</td><td>{{v.paradas[:60]}}</td><td>{{v.destino[:40]}}</td><td>{{v.kms}}</td><td>${{v.precio}}</td><td><a href="https://www.google.com/maps/dir/{{v.latO}},{{v.lngO}}/{{v.latD}},{{v.lngD}}/" target="_blank">🧭</a></td></tr>{% endfor %}
</table></div>
<script>var viajes={{viajes_json|safe}};new Chart(document.getElementById('c1'),{type:'bar',data:{labels:viajes.map((v,[STRIPPED] por Viaje'}}}});</script>
</body></html>
'''

@app.route("/")
def index():
    return render_template_string(MAPA)

@app.route("/api/viaje", methods=["POST"])
def api_viaje():
    data = request.json
    viajes.append(data)
    try:
        with open("/tmp/viajes.json","w") as f:
            json.dump(viajes,f)
    except:
        pass
    return jsonify({"ok":True})

@app.route("/concentrado")
def concentrado():
    total=len(viajes)
    tk=sum(float(v.get('kms',0) or 0) for v in viajes)
    tp=sum(float(v.get('precio',0) or 0) for v in viajes)
    return render_template_string(CONCENTRADO_HTML, viajes=viajes, viajes_json=json.dumps(viajes), total=total, total_kms=round(tk,1), total_precio=round(tp,2))

@app.route("/excel")
def excel():
    output=io.StringIO()
    w=csv.writer(output)
    w.writerow(['#','Fecha','Hora','Cliente','Origen','Parada1','Parada2','Parada3','Destino','KMs','Precio','Paradas'])
    for i,v in enumerate(viajes,1):
        w.writerow([i,v.get('fecha'),v.get('hora'),v.get('cliente'),v.get('origen'),v.get('parada1'),v.get('parada2'),v.get('parada3'),v.get('destino'),v.get('kms'),v.get('precio'),v.get('paradas')])
    mem=io.BytesIO()
    mem.write(output.getvalue().encode('utf-8-sig'))
    mem.seek(0)
    return send_file(mem, as_attachment=True, download_name=f"AGL_AGS_{datetime.now().strftime('%Y-%m-%d')}.csv", mimetype="text/csv")

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
