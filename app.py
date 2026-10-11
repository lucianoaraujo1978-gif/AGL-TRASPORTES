from flask import Flask, render_template_string, request, jsonify, send_file
import os, json, io, csv
from datetime import datetime
app = Flask(__name__)
viajes = []

MAPA_HTML = """
<!DOCTYPE html>
<html><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>AGL - Aguascalientes</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
*{box-sizing:border-box} body{margin:0;font-family:Arial;background:#fff}
#map{height:100vh;width:100%;position:absolute;top:0;left:0;z-index:1}
.topbar{position:fixed;top:0;left:0;right:0;height:60px;background:#0a3552;z-index:1000;display:flex;align-items:center;justify-content:space-between;padding:0 16px;color:white}
.chip{background:white;color:#0a3552;padding:8px 14px;border-radius:20px;font-weight:700;text-decoration:none;font-size:12px;margin-left:6px;border:none;cursor:pointer}
.side{position:fixed;top:76px;left:16px;width:400px;background:white;z-index:1000;border-radius:18px;padding:18px;box-shadow:0 10px 30px rgba(0,0,0,0.25);max-height:calc(100vh - 90px);overflow-y:auto}
.field{background:#f2f4f7;border-radius:12px;padding:12px 14px;display:flex;align-items:center;gap:10px;margin-bottom:10px}
.field input,.field select{border:none;background:transparent;outline:none;flex:1;font-size:14px;font-weight:600}
.row{display:flex;gap:10px}
.btn{flex:1;padding:14px;border-radius:12px;border:none;font-weight:800;font-size:14px;cursor:pointer}
.btn-dark{background:#0a3552;color:white}.btn-light{background:#eef2f7}
.kpi{background:#0a3552;color:white;border-radius:14px;padding:12px;text-align:center;display:none;margin-top:10px}
@media(max-width:900px){.side{top:auto;bottom:0;left:0;right:0;width:100%;border-radius:20px 20px 0 0;max-height:70vh}}
</style>
</head>
<body>
<div id="map"></div>
<div class="topbar"><b>🚕 AGL TRANSPORTES - AGS</b><div><a href="/concentrado" target="_blank" class="chip">📊 Concentrado</a><button onclick="miUbicacion()" class="chip">📍 Mi ubicación</button></div></div>
<div class="side">
<h2 style="margin:0 0 10px;color:#0a3552">✨ Nuevo Viaje - Aguascalientes</h2>
<div class="field">🏢 <input id="solicita" placeholder="¿Quién solicita? Ej: RH Bimbo"></div>
<div class="field">👤 <input id="cliente" placeholder="Pasajero / Cliente"></div>
<div class="row"><div class="field" style="flex:1">🚗 <select id="operador"><option value="">-- Chofer --</option><option>Luciano</option><option>Operador 1</option><option>Operador 2</option><option>Operador 3</option></select></div><div class="field" style="flex:0.5">👥 <select id="pax"><option>1</option><option>2</option><option>3</option><option>4</option></select></div></div>
<div class="row"><div class="field" style="flex:1">📅 <input type="date" id="fecha"></div><div class="field" style="flex:1">⏰ <input type="time" id="hora"></div></div>
<div class="field">🔴 <input id="origenTxt" placeholder="Origen - toca el mapa" readonly></div>
<div class="field">🔵 <input id="destinoTxt" placeholder="Destino - toca el mapa" readonly></div>
<div id="info" class="kpi"></div>
<div class="row" style="margin-top:12px"><button class="btn btn-light" onclick="borrar()">Borrar</button><button class="btn btn-dark" onclick="confirmar()">✓ Confirmar</button></div>
</div>
<script>
var map=L.map('map',{zoomControl:false}).setView([21.8853, -102.2916], 13);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19}).addTo(map);
L.control.zoom({position:'bottomright'}).addTo(map);

// ICONOS COMO GOOGLE MAPS
var iconRojo = L.icon({
    iconUrl: 'https://maps.google.com/mapfiles/ms/icons/red-dot.png',
    iconSize: [32, 32],
    iconAnchor: [16, 32]
});
var iconAzul = L.icon({
    iconUrl: 'https://maps.google.com/mapfiles/ms/icons/blue-dot.png',
    iconSize: [32, 32],
    iconAnchor: [16, 32]
});

var pts=[], marks=[], line=null, kms=0, mins=0;
function miUbicacion(){navigator.geolocation.getCurrentPosition(p=>{map.setView([p.coords.latitude,p.coords.longitude],16); L.marker([p.coords.latitude,p.coords.longitude]).addTo(map).bindPopup("Estás aquí").openPopup();});}
map.on('click', function(e){
  if(pts.length>=2){ pts=[]; marks.forEach(m=>map.removeLayer(m)); marks=[]; if(line) map.removeLayer(line); document.getElementById('info').style.display='none'; }
  pts.push(e.latlng);
  var icono = pts.length==1 ? iconRojo : iconAzul;
  var m=L.marker(e.latlng,{icon:icono}).addTo(map); marks.push(m);
  var idx=pts.length-1;
  fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${e.latlng.lat}&lon=${e.latlng.lng}`).then(r=>r.json()).then(d=>{
    var dir=d.display_name?d.display_name.split(',').slice(0,4).join(','):e.latlng.lat.toFixed(5)+','+e.latlng.lng.toFixed(5);
    if(idx==0) document.getElementById('origenTxt').value=dir; else document.getElementById('destinoTxt').value=dir;
  });
  if(pts.length==2) trazar();
});
function trazar(){
  var c=pts.map(p=>p.lng+','+p.lat).join(';');
  fetch(`https://router.project-osrm.org/route/v1/driving/${c}?overview=full&geometries=geojson`).then(r=>r.json()).then(data=>{
    if(!data.routes||!data.routes[0]) return;
    var r=data.routes[0]; kms=(r.distance/1000); mins=Math.round(r.duration/60);
    if(line) map.removeLayer(line);
    line=L.geoJSON(r.geometry,{style:{color:'#0a3552',weight:6}}).addTo(map);
    map.fitBounds(line.getBounds(),{padding:[100,100]});
    var el=document.getElementById('info'); el.style.display='block';
    el.innerHTML=`<b>${kms.toFixed(1)} km • ${mins} min</b><br><small>Ruta en Aguascalientes lista</small>`;
  });
}
function borrar(){ pts=[]; marks.forEach(m=>map.removeLayer(m)); marks=[]; if(line) map.removeLayer(line); document.getElementById('origenTxt').value=''; document.getElementById('destinoTxt').value=''; document.getElementById('info').style.display='none'; }
function confirmar(){
  if(pts.length<2){ alert('Toca 2 puntos en Aguascalientes'); return; }
  var op=document.getElementById('operador').value; if(!op){ alert('Elige chofer'); return; }
  var data={ solicita: document.getElementById('solicita').value||'No registrado', cliente: document.getElementById('cliente').value||'Sin nombre', operador: op, pasajeros: document.getElementById('pax').value, fecha: document.getElementById('fecha').value || new Date().toISOString().split('T')[0], hora: document.getElementById('hora').value || new Date().toLocaleTimeString(), origen: document.getElementById('origenTxt').value, destino: document.getElementById('destinoTxt').value, paradas: document.getElementById('origenTxt').value+' -> '+document.getElementById('destinoTxt').value, kms: kms.toFixed(1), mins: mins, latO: pts[0].lat, lngO: pts[0].lng, latD: pts[1].lat, lngD: pts[1].lng, timestamp: new Date().toISOString() };
  fetch('/api/viaje',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)}).then(r=>r.json()).then(()=>{
    var msg=`🚕 *VIAJE AGL AGS*%0A👤 ${data.cliente}%0A🏢 ${data.solicita}%0A🚗 ${data.operador}%0A📏 ${data.kms} km%0A🗺️ https://www.google.com/maps/dir/${data.latO},${data.lngO}/${data.latD},${data.lngD}/`;
    if(confirm('✅ Guardado en AGS! ¿Avisar chofer?')) window.open(`https://wa.me/?text=${msg}`,'_blank');
    borrar();
  });
}
</script>
</body>
</html>
"""
CONCENTRADO_HTML = """
<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Concentrado AGS</title><script src="https://cdn.jsdelivr.net/npm/chart.js"></script><style>body{font-family:Arial;margin:0;background:#eef2f7;padding:12px}h1{color:#0a3552}.card{background:white;padding:14px;border-radius:14px;margin-bottom:10px}.grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px}table{width:100%;border-collapse:collapse;font-size:12px}th,td{border:1px solid #ddd;padding:7px}th{background:#0a3552;color:white}.btn{background:#0a3552;color:white;padding:10px 14px;border-radius:10px;text-decoration:none;display:inline-block;margin-right:6px}@media(max-width:700px){.grid{grid-template-columns:1fr}}</style></head><body>
<h1>📊 Concentrado AGL - Aguascalientes</h1><a href="/" class="btn">← Mapa AGS</a><a href="/excel" class="btn" style="background:#16a34a">⬇️ Excel</a>
<div class="grid"><div class="card">Total<br><b style="font-size:22px">{{total}}</b> viajes</div><div class="card">KMs<br><b style="font-size:22px">{{total_kms}} km</b></div><div class="card">Prom<br><b style="font-size:22px">{{prom}} km</b></div></div>
<div class="card"><canvas id="c1"></canvas></div><div class="card"><canvas id="c2"></canvas></div>
<div class="card" style="overflow:auto"><table><tr><th>#</th><th>Fecha</th><th>Solicita</th><th>Operador</th><th>Cliente</th><th>KMs</th><th>Maps</th></tr>{% for v in viajes %}<tr><td>{{loop.index}}</td><td>{{v.fecha}} {{v.hora}}</td><td>{{v.solicita}}</td><td><b>{{v.operador}}</b></td><td>{{v.cliente}}</td><td>{{v.kms}}</td><td><a href="https://www.google.com/maps/dir/{{v.latO}},{{v.lngO}}/{{v.latD}},{{v.lngD}}/" target="_blank">🧭</a></td></tr>{% endfor %}</table></div>
<script>var viajes={{viajes_json|safe}};new Chart(document.getElementById('c1'),{type:'bar',data:{labels:viajes.map((v,i)=>v.cliente.substring(0,8)),datasets:[{label:'KMs',data:viajes.map(v=>parseFloat(v.kms)||0),backgroundColor:'#0a3552'}]},options:{plugins:{title:{display:true,text:'KMs por viaje'}}}}});var porOp={};viajes.forEach(v=>{porOp[v.operador]=(porOp[v.operador]||0)+1;});new Chart(document.getElementById('c2'),{type:'doughnut',data:{labels:Object.keys(porOp),datasets:[{data:Object.values(porOp),backgroundColor:['#0a3552','#16a34a','#f59e0b','#ef4444']}]},options:{plugins:{title:{display:true,text:'Viajes por Operador'}}}});</script></body></html>
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
    total=len(viajes); tk=sum(float(v.get('kms',0) or 0) for v in viajes); prom=round(tk/total,1) if total else 0
    return render_template_string(CONCENTRADO_HTML, viajes=viajes, viajes_json=json.dumps(viajes), total=total, total_kms=round(tk,1), prom=prom)
@app.route("/excel")
def excel():
    output=io.StringIO(); w=csv.writer(output); w.writerow(['#','Fecha','Hora','Solicita','Operador','Cliente','Origen','Destino','KMs','Mins'])
    for i,v in enumerate(viajes,1): w.writerow([i,v.get('fecha'),v.get('hora'),v.get('solicita'),v.get('operador'),v.get('cliente'),v.get('origen'),v.get('destino'),v.get('kms'),v.get('mins')])
    mem=io.BytesIO(); mem.write(output.getvalue().encode('utf-8-sig')); mem.seek(0)
    return send_file(mem, as_attachment=True, download_name=f"AGL_AGS_{datetime.now().strftime('%Y-%m-%d')}.csv", mimetype="text/csv")
if __name__=="__main__": app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
