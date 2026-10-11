from flask import Flask, render_template_string, request, jsonify, send_file
import os, json, io, csv
from datetime import datetime
app = Flask(__name__)
viajes = []

MAPA_HTML = """
<!DOCTYPE html>
<html><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<title>AGL TRANSPORTES</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
*{box-sizing:border-box} body{margin:0;font-family:Arial;background:#000}
#map{height:100vh;width:100%}
.panel{position:fixed;bottom:0;left:0;right:0;background:white;z-index:9999;border-radius:24px 24px 0 0;padding:18px;max-height:85vh;overflow-y:auto;box-shadow:0 -5px 20px rgba(0,0,0,0.3)}
.handle{width:40px;height:5px;background:#ddd;border-radius:10px;margin:0 auto 12px}
.row{display:flex;gap:8px;margin-bottom:10px}
.input{flex:1;background:#f1f3f5;border:none;padding:14px;border-radius:12px;font-size:15px;outline:none;display:flex;align-items:center;gap:6px}
.input input, .input select{border:none;background:transparent;flex:1;font-size:15px;outline:none}
.btn{flex:1;padding:16px;border-radius:14px;border:none;font-weight:bold;font-size:16px;cursor:pointer}
.btn-dark{background:#0a3552;color:white}.btn-light{background:#e9ecef;color:#000}
.info{background:#0a3552;color:white;padding:12px;border-radius:12px;text-align:center;font-size:15px;margin-top:10px}
.topbar{position:fixed;top:10px;left:10px;right:10px;z-index:1000;display:flex;justify-content:space-between}
.chip{background:white;padding:10px 14px;border-radius:20px;font-weight:bold;box-shadow:0 2px 8px rgba(0,0,0,0.2);text-decoration:none;color:#0a3552;font-size:13px}
</style>
</head>
<body>
<div id="map"></div>
<div class="topbar">
  <a href="/concentrado" target="_blank" class="chip">📊 Concentrado</a>
  <button onclick="miUbicacion()" class="chip" style="border:none">📍 Mi ubicación</button>
</div>

<div class="panel">
<div class="handle"></div>
<div style="font-weight:bold;font-size:18px;margin-bottom:10px;color:#0a3552">🚕 Nuevo Viaje AGL</div>

<div class="row"><div class="input">🏢 <input id="solicita" placeholder="¿Quién solicita? Ej: RH Bimbo"></div></div>
<div class="row"><div class="input">👤 <input id="cliente" placeholder="Nombre del pasajero"></div></div>
<div class="row"><div class="input">🚗 <select id="operador"><option value="">-- Asignar Chofer --</option><option>Luciano</option><option>Operador 1</option><option>Operador 2</option><option>Operador 3</option></select></div><div class="input">👥 <select id="pax"><option>1</option><option>2</option><option>3</option><option>4</option></select></div></div>
<div class="row"><div class="input">📅 <input type="date" id="fecha"></div><div class="input">⏰ <input type="time" id="hora"></div></div>

<div class="row"><div class="input" id="boxO">🔴 <input id="origenTxt" placeholder="Toca mapa para ORIGEN" readonly></div></div>
<div class="row"><div class="input" id="boxD">🔵 <input id="destinoTxt" placeholder="Toca mapa para DESTINO" readonly></div></div>

<div id="info" class="info" style="display:none"></div>

<div class="row" style="margin-top:14px">
  <button class="btn btn-light" onclick="borrar()">Borrar</button>
  <button class="btn btn-dark" onclick="confirmar()">✓ Confirmar y avisar chofer</button>
</div>
<div style="font-size:11px;color:gray;text-align:center;margin-top:8px">Toca 2 veces el mapa: 1 para origen, 2 para destino. La ruta azul y kms salen solos.</div>
</div>

<script>
var map=L.map('map',{zoomControl:false}).setView([20.6597,-103.3496],14);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
var pts=[], marks=[], line=null, kms=0, mins=0;
var ico=L.divIcon({html:'<div style="font-size:28px">📍</div>',iconSize:[30,30],iconAnchor:[15,30],className:''});

function miUbicacion(){navigator.geolocation.getCurrentPosition(p=>{map.setView([p.coords.latitude,p.coords.longitude],16); L.marker([p.coords.latitude,p.coords.longitude]).addTo(map).bindPopup("Estás aquí").openPopup();});}

map.on('click', function(e){
  if(pts.length>=2){ pts=[]; marks.forEach(m=>map.removeLayer(m)); marks=[]; if(line) map.removeLayer(line); document.getElementById('info').style.display='none'; }
  pts.push(e.latlng);
  var m=L.marker(e.latlng,{icon:ico}).addTo(map); marks.push(m);
  var idx=pts.length-1;
  fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${e.latlng.lat}&lon=${e.latlng.lng}`).then(r=>r.json()).then(d=>{
    var dir=d.display_name?d.display_name.split(',').slice(0,3).join(','):e.latlng.lat.toFixed(5)+','+e.latlng.lng.toFixed(5);
    if(idx==0) document.getElementById('origenTxt').value=dir;
    else document.getElementById('destinoTxt').value=dir;
  });
  if(pts.length==2) trazar();
});

function trazar(){
  var c=pts.map(p=>p.lng+','+p.lat).join(';');
  fetch(`https://router.project-osrm.org/route/v1/driving/${c}?overview=full&geometries=geojson`).then(r=>r.json()).then(data=>{
    if(!data.routes[0]) return;
    var r=data.routes[0]; kms=(r.distance/1000); mins=Math.round(r.duration/60);
    if(line) map.removeLayer(line);
    line=L.geoJSON(r.geometry,{style:{color:'#0a3552',weight:6}}).addTo(map);
    map.fitBounds(line.getBounds(),{padding:[80,80]});
    var el=document.getElementById('info');
    el.style.display='block';
    el.innerHTML=`🚗 Ruta lista: <b>${kms.toFixed(1)} km</b> • ⏱️ <b>${mins} min</b> • El chofer recibirá recordatorio`;
  });
}

function borrar(){ pts=[]; marks.forEach(m=>map.removeLayer(m)); marks=[]; if(line) map.removeLayer(line); document.getElementById('origenTxt').value=''; document.getElementById('destinoTxt').value=''; document.getElementById('info').style.display='none'; }

function confirmar(){
  if(pts.length<2){ alert('Toca el mapa 2 veces para poner origen y destino'); return; }
  var op=document.getElementById('operador').value; if(!op){ alert('Selecciona el chofer'); return; }
  var data={
    solicita: document.getElementById('solicita').value||'No registrado',
    cliente: document.getElementById('cliente').value||'Sin nombre',
    operador: op,
    pasajeros: document.getElementById('pax').value,
    fecha: document.getElementById('fecha').value || new Date().toISOString().split('T')[0],
    hora: document.getElementById('hora').value || new Date().toLocaleTimeString(),
    origen: document.getElementById('origenTxt').value,
    destino: document.getElementById('destinoTxt').value,
    paradas: document.getElementById('origenTxt').value+' -> '+document.getElementById('destinoTxt').value,
    kms: kms.toFixed(1), mins: mins,
    latO: pts[0].lat, lngO: pts[0].lng, latD: pts[1].lat, lngD: pts[1].lng,
    timestamp: new Date().toISOString()
  };
  fetch('/api/viaje',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)}).then(r=>r.json()).then(()=>{
    // Aviso tipo Uber para chofer
    var msg=`🚕 *NUEVO VIAJE AGL*%0A👤 Cliente: ${data.cliente}%0A🏢 Solicita: ${data.solicita}%0A🚗 Chofer: ${data.operador}%0A📅 ${data.fecha} ${data.hora}%0A🔴 Origen: ${data.origen}%0A🔵 Destino: ${data.destino}%0A📏 ${data.kms} km - ${data.mins} min%0A%0A🗺️ Ver ruta: https://www.google.com/maps/dir/${data.latO},${data.lngO}/${data.latD},${data.lngD}/`;
    var url=`https://wa.me/?text=${msg}`;
    if(confirm('✅ Viaje guardado!\\n¿Quieres avisar al chofer por WhatsApp ahora?')){ window.open(url,'_blank'); }
    alert('Quedó programado como recordatorio para '+data.operador+' en el concentrado');
    borrar();
  });
}
</script>
</body>
</html>
"""

CONCENTRADO_HTML = """
<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Concentrado</title><script src="https://cdn.jsdelivr.net/npm/chart.js"></script><style>body{font-family:Arial;margin:0;background:#eef2f7;padding:12px}h1{color:#0a3552;font-size:20px}.card{background:white;padding:14px;border-radius:14px;margin-bottom:10px;box-shadow:0 2px 8px rgba(0,0,0,0.06)}table{width:100%;border-collapse:collapse;font-size:12px}th,td{border:1px solid #ddd;padding:7px}th{background:#0a3552;color:white}.btn{background:#0a3552;color:white;padding:10px 14px;border:none;border-radius:10px;text-decoration:none;margin-right:6px;display:inline-block}.grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px}@media(max-width:700px){.grid{grid-template-columns:1fr}}</style></head><body>
<h1>📊 Concentrado AGL</h1><a href="/" class="btn">← Mapa</a><a href="/excel" class="btn" style="background:#16a34a">⬇️ Excel</a>
<div class="grid"><div class="card">Total<br><b style="font-size:24px;color:#0a3552">{{total}}</b> viajes</div><div class="card">KMs<br><b style="font-size:24px;color:#0a3552">{{total_kms}} km</b></div><div class="card">Promedio<br><b style="font-size:24px;color:#0a3552">{{prom}} km</b></div></div>
<div class="card"><canvas id="c1"></canvas></div><div class="card"><canvas id="c2"></canvas></div>
<div class="card" style="overflow:auto"><table><tr><th>#</th><th>Fecha/Hora</th><th>Solicita</th><th>Operador</th><th>Cliente</th><th>Ruta</th><th>KMs</th><th>Acción</th></tr>{% for v in viajes %}<tr><td>{{loop.index}}</td><td>{{v.fecha}} {{v.hora}}</td><td>{{v.solicita}}</td><td><b>{{v.operador}}</b></td><td>{{v.cliente}}</td><td>{{v.origen[:30]}} → {{v.destino[:30]}}</td><td>{{v.kms}}</td><td><a href="https://www.google.com/maps/dir/{{v.latO}},{{v.lngO}}/{{v.latD}},{{v.lngD}}/" target="_blank">🧭 Ir</a></td></tr>{% endfor %}</table></div>
<script>var viajes={{viajes_json|safe}};new Chart(document.getElementById('c1'),{type:'bar',data:{labels:viajes.map((v,i)=>'#'+(i+1)),datasets:[{label:'KMs',data:viajes.map(v=>parseFloat(v.kms)||0),backgroundColor:'#0a3552'}]},options:{plugins:{title:{display:true,text:'KMs por viaje'}}}});var porOp={};viajes.forEach(v=>porOp[v.operador]=(porOp[v.operador]||0)+1);new Chart(document.getElementById('c2'),{type:'doughnut',data:{labels:Object.keys(porOp),datasets:[{data:Object.values(porOp),backgroundColor:['#0a3552','#16a34a','#f59e0b','#ef4444']}]},options:{plugins:{title:{display:true,text:'Viajes por operador'}}}});</script></body></html>
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
    return send_file(mem, as_attachment=True, download_name=f"AGL_{datetime.now().strftime('%Y-%m-%d')}.csv", mimetype="text/csv")
try:
    if os.path.exists("/tmp/viajes.json"):
        with open("/tmp/viajes.json") as f: viajes.extend(json.load(f))
except: pass
if __name__=="__main__": app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
