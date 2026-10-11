from flask import Flask, render_template_string, request, jsonify, send_file
import os, json, io, csv
from datetime import datetime

app = Flask(__name__)
viajes = []

MAPA_HTML = """... (pega el código anterior que ya tienes con estos 2 campos nuevos)..."""
# ABAJO TE DEJO EL ARCHIVO COMPLETO BONITO - COPIA ESTO:

from flask import Flask, render_template_string, request, jsonify, send_file
import os, json, io, csv
from datetime import datetime
app = Flask(__name__)
viajes = []

MAPA_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>AGL TRANSPORTES</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
*{box-sizing:border-box} body{margin:0;font-family:Arial;background:#fff;overflow:hidden}
#map{height:100vh;width:100%;position:absolute;top:0;left:0;z-index:1}
.menu{position:absolute;top:0;left:0;width:360px;height:100vh;background:white;z-index:1000;padding:15px;box-shadow:2px 0 15px rgba(0,0,0,0.3);overflow-y:auto}
.menu-top{display:flex;justify-content:space-between;align-items:center;font-weight:bold;font-size:22px;margin-bottom:15px;color:#0a3552}
.btn-x{background:black;color:white;border:none;width:34px;height:34px;border-radius:50%;cursor:pointer;font-size:20px}
.item{background:#f5f5f7;border:none;width:100%;padding:12px;border-radius:12px;text-align:left;margin-bottom:10px;font-size:14px;display:flex;align-items:center;gap:8px}
.input-icon{display:flex;align-items:center;background:#f5f5f7;border-radius:12px;padding:10px;flex:1}
.input-icon input,.input-icon select{border:none;background:transparent;outline:none;flex:1;font-size:14px}
.row{display:flex;gap:8px;margin-bottom:12px}
.parada{background:#f5f5f7;border-radius:12px;padding:10px;margin-bottom:8px;display:flex;align-items:center;gap:8px}
.parada input{border:none;background:transparent;outline:none;flex:1;font-size:14px}
.del{color:red;font-weight:bold;cursor:pointer;font-size:18px;padding:0 5px}
.btns{display:flex;gap:10px;margin-top:15px}
.btn{flex:1;padding:13px;border-radius:12px;border:2px solid #000;font-weight:bold;cursor:pointer;font-size:14px}
.btn-borrar{background:white;color:black}.btn-cerrar{background:#0a3552;color:white;border-color:#0a3552}
.info{margin-top:12px;background:#0a3552;color:white;padding:12px;border-radius:10px;font-size:13px;display:none;line-height:1.6}
.btn-edit{background:white;color:#0a3552;border:none;padding:10px;border-radius:8px;font-weight:bold;width:100%;margin-top:10px;cursor:pointer}
.link-conc{position:absolute;top:15px;right:15px;z-index:1100;background:#0a3552;color:white;padding:12px 16px;border-radius:12px;text-decoration:none;font-weight:bold;box-shadow:0 2px 10px rgba(0,0,0,0.4)}
</style>
</head>
<body>
<div id="map"></div>
<a href="/concentrado" class="link-conc" target="_blank">📊 Concentrado</a>
<div class="menu" id="menu">
  <div class="menu-top"><span>🚗 AGL TRANSPORTES</span><button class="btn-x" onclick="toggleMenu()">×</button></div>

  <div class="item">🏢 <input id="solicita" placeholder="¿Quién pide el viaje? (Ej: RH Bimbo)"></div>
  <div class="item">👤 <input id="cliente" placeholder="Cliente / Pasajero principal"></div>
  <div class="item">🚕 <input id="operador" placeholder="Operador / Chofer"></div>

  <div class="row">
    <div class="input-icon">👥 <select id="pasajeros"><option>4</option><option>1</option><option>2</option><option>3</option><option>5</option><option>6</option></select></div>
    <div class="input-icon">📅 <input type="date" id="fecha"></div>
    <div class="input-icon">⏰ <input type="time" id="hora"></div>
  </div>
  <button class="item" onclick="agregarParada()">➕ Agregar parada (máx 4)</button>
  <div id="listaParadas"></div>
  <div id="info" class="info"></div>
  <div class="btns">
    <button class="btn btn-borrar" onclick="borrarTodo()">BORRAR</button>
    <button class="btn btn-cerrar" onclick="cerrarViaje()">CERRAR Y GUARDAR</button>
  </div>
</div>
<button id="btnAbrir" onclick="toggleMenu()" style="position:absolute;top:15px;left:15px;z-index:1100;background:white;border:none;padding:12px 16px;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.3);display:none">☰ AGL</button>
<script>
var map = L.map('map', {zoomControl:false}).setView([20.6597, -103.3496], 13);
var baseMap = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
L.control.zoom({position:'bottomright'}).addTo(map);
var puntos=[null,null], markers=[], routeLine=null, maxParadas=4;
var iconCoche = L.divIcon({html:'🚗', iconSize:[32,32], iconAnchor:[16,16], className:''});
var ultimoKms=0, ultimoMin=0;
function toggleMenu(){var m=document.getElementById('menu'),b=document.getElementById('btnAbrir'); if(m.style.display==='none'){m.style.display='block';b.style.display='none'} else {m.style.display='none';b.style.display='block'; setTimeout(()=>map.invalidateSize(),200);}}
function renderParadas(){var cont=document.getElementById('listaParadas'); cont.innerHTML=''; puntos.forEach((p,idx)=>{var div=document.createElement('div');div.className='parada';var ph=idx===0?'Origen - click mapa':idx===puntos.length-1?'Destino - click':'Parada '+(idx+1);var ic=idx===0?'<span style="color:red">●</span>':'<span>●</span>';div.innerHTML=`${ic} <input id="p${idx}" placeholder="${ph}"> <span class="del" onclick="borrarParada(${idx})">×</span>`;cont.appendChild(div);});}
function agregarParada(){if(puntos.length>=maxParadas){alert('Máximo 4');return;} puntos.push(null); renderParadas();}
function borrarParada(i){if(puntos.length<=2){alert('Mínimo 2');return;} puntos.splice(i,1); renderParadas(); refrescarMarkers();}
function refrescarMarkers(){markers.forEach(m=>map.removeLayer(m)); markers=[]; puntos.forEach(p=>{if(p){var m=L.marker(p,{icon:iconCoche}).addTo(map); markers.push(m);}});}
map.on('click', function(e){var ll=e.latlng; var vacio=puntos.findIndex(p=>p===null); if(vacio===-1){if(puntos.length<maxParadas){puntos.push(ll); renderParadas();} else {puntos[puntos.length-1]=ll;} vacio=puntos.length-1;} else {puntos[vacio]=ll;} refrescarMarkers(); reverse(ll,vacio); if(puntos.filter(p=>p).length>=2) trazarRuta();});
function reverse(latlng,idx){fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${latlng.lat}&lon=${latlng.lng}`).then(r=>r.json()).then(d=>{var dir=d.display_name?d.display_name.split(',').slice(0,4).join(','):latlng.lat.toFixed(5)+','+latlng.lng.toFixed(5); var inp=document.getElementById('p'+idx); if(inp) inp.value=dir;});}
function trazarRuta(){var valid=puntos.filter(p=>p!==null); if(valid.length<2) return; var coords=valid.map(p=>`${p.lng},${p.lat}`).join(';'); fetch(`https://router.project-osrm.org/route/v1/driving/${coords}?overview=full&geometries=geojson`).then(r=>r.json()).then(data=>{if(!data.routes||!data.routes[0]) return; var r=data.routes[0]; ultimoKms=(r.distance/1000); ultimoMin=Math.round(r.duration/60); var info=document.getElementById('info'); info.style.display='block'; info.innerHTML=`🚗 ${ultimoKms.toFixed(1)} km • ⏱️ ${ultimoMin} min<br><button class="btn-edit" onclick="editarViaje()">✏️ EDITAR SI SE EQUIVOCARON</button>`; if(routeLine) map.removeLayer(routeLine); routeLine=L.geoJSON(r.geometry,{style:{color:'#0a3552',weight:5}}).addTo(map); map.fitBounds(routeLine.getBounds(),{padding:[50,50]});});}
function borrarTodo(){puntos=[null,null]; markers.forEach(m=>map.removeLayer(m)); markers=[]; if(routeLine) map.removeLayer(routeLine); renderParadas(); document.getElementById('info').style.display='none';}
function cerrarViaje(){
  var dirs=[]; puntos.forEach((p,i)=>{var inp=document.getElementById('p'+i); if(inp) dirs.push(inp.value);});
  var data={
    solicita: document.getElementById('solicita').value||'No registrado',
    cliente: document.getElementById('cliente').value||'Sin cliente',
    operador: document.getElementById('operador').value||'Sin operador',
    pasajeros: document.getElementById('pasajeros').value,
    fecha: document.getElementById('fecha').value || new Date().toISOString().split('T')[0],
    hora: document.getElementById('hora').value || new Date().toLocaleTimeString(),
    origen: dirs[0]||'', destino: dirs[dirs.length-1]||'', paradas: dirs.join(' -> '),
    kms: ultimoKms.toFixed(1), mins: ultimoMin, timestamp: new Date().toISOString()
  };
  fetch('/api/viaje',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)})
.then(r=>r.json()).then(resp=>{
    alert('✅ Guardado!\\nOperador: '+data.operador+'\\nSolicita: '+data.solicita+'\\nKms: '+data.kms);
    document.getElementById('info').innerHTML += `<br><a href="/concentrado" target="_blank" style="color:white;text-decoration:underline">📊 Ver en concentrado</a>`;
  });
}
function editarViaje(){alert('Corrige y vuelve a dar CERRAR Y GUARDAR, se guarda sin costo.');}
renderParadas();
</script>
</body>
</html>
"""

CONCENTRADO_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Concentrado AGL</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
body{font-family:Arial;margin:0;background:#eef2f7;padding:15px}
h1{color:#0a3552}
.card{background:white;padding:18px;border-radius:16px;box-shadow:0 4px 15px rgba(0,0,0,0.08);margin-bottom:15px}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{border:1px solid #e5e7eb;padding:10px;text-align:left}
th{background:#0a3552;color:white;position:sticky;top:0}
.btn{background:#0a3552;color:white;padding:11px 18px;border:none;border-radius:10px;cursor:pointer;text-decoration:none;display:inline-block;margin-right:8px;font-weight:bold}
.grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:15px}
.kpi{font-size:28px;font-weight:bold;color:#0a3552}
@media(max-width:900px){.grid{grid-template-columns:1fr} table{font-size:11px}}
</style>
</head>
<body>
<h1>📊 Concentrado AGL TRANSPORTES</h1>
<a href="/" class="btn">← Mapa</a>
<a href="/excel" class="btn" style="background:#16a34a">⬇️ Descargar Excel</a>
<button onclick="location.reload()" class="btn" style="background:black">🔄 Actualizar</button>

<div class="grid">
  <div class="card"><div>Total Viajes</div><div class="kpi">{{total}}</div><div>viajes registrados</div></div>
  <div class="card"><div>Total Kilómetros</div><div class="kpi">{{total_kms}} km</div><div>recorridos</div></div>
  <div class="card"><div>Promedio</div><div class="kpi">{{prom}} km</div><div>por viaje</div></div>
</div>

<div class="grid" style="grid-template-columns:1fr 1fr">
  <div class="card"><canvas id="chartKms"></canvas></div>
  <div class="card"><canvas id="chartOperador"></canvas></div>
</div>

<div class="card"><canvas id="chartDias"></canvas></div>

<div class="card" style="overflow-x:auto">
<table>
<tr><th>#</th><th>Fecha</th><th>Hora</th><th>¿Quién pide?</th><th>Operador</th><th>Cliente</th><th>Pax</th><th>Origen</th><th>Destino</th><th>KMs</th><th>Min</th></tr>
{% for v in viajes %}
<tr><td>{{loop.index}}</td><td>{{v.fecha}}</td><td>{{v.hora}}</td><td><b>{{v.solicita}}</b></td><td style="color:#0a3552;font-weight:bold">{{v.operador}}</td><td>{{v.cliente}}</td><td>{{v.pasajeros}}</td><td>{{v.origen[:50]}}</td><td>{{v.destino[:50]}}</td><td><b>{{v.kms}}</b></td><td>{{v.mins}}</td></tr>
{% endfor %}
</table>
{% if not viajes %}<p style="text-align:center;padding:20px">Aún no hay viajes. Cierra un viaje en el mapa y aparecerá aquí automáticamente.</p>{% endif %}
</div>

<script>
var viajes = {{viajes_json|safe}};
var labels = viajes.map((v,i)=>'#'+(i+1)+' '+v.cliente.substring(0,10));
var kmsData = viajes.map(v=>parseFloat(v.kms)||0);
new Chart(document.getElementById('chartKms'), {
  type: 'bar',
  data: {labels: labels, datasets: [{label:'KMs', data: kmsData, backgroundColor:'#0a3552', borderRadius:8}]},
  options: {responsive:true, plugins:{title:{display:true,text:'Kilómetros por Viaje'}}}
});
var porOp={}; viajes.forEach(v=>{ porOp[v.operador]=(porOp[v.operador]||0)+1; });
new Chart(document.getElementById('chartOperador'), {
  type: 'doughnut',
  data: {labels: Object.keys(porOp), datasets: [{data: Object.values(porOp), backgroundColor:['#0a3552','#16a34a','#f59e0b','#ef4444','#8b5cf6']}]},
  options: {responsive:true, plugins:{title:{display:true,text:'Viajes por Operador'}}}
});
var porDia={}; viajes.forEach(v=>{ porDia[v.fecha]=(porDia[v.fecha]||0)+1; });
new Chart(document.getElementById('chartDias'), {
  type: 'line',
  data: {labels: Object.keys(porDia), datasets: [{label:'Viajes', data: Object.values(porDia), borderColor:'#0a3552', backgroundColor:'rgba(10,53,82,0.1)', fill:true, tension:0.4}]},
  options: {responsive:true, plugins:{title:{display:true,text:'Contabilidad - Viajes por Día'}}}
});
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(MAPA_HTML)

@app.route("/api/viaje", methods=["POST"])
def api_viaje():
    data = request.json
    viajes.append(data)
    try:
        with open("/tmp/viajes.json","w") as f: json.dump(viajes,f)
    except: pass
    return jsonify({"ok":True})

@app.route("/concentrado")
def concentrado():
    total=len(viajes); total_kms=sum(float(v.get('kms',0) or 0) for v in viajes); prom=round(total_kms/total,1) if total else 0
    return render_template_string(CONCENTRADO_HTML, viajes=viajes, viajes_json=json.dumps(viajes), total=total, total_kms=round(total_kms,1), prom=prom)

@app.route("/excel")
def excel():
    output=io.StringIO(); writer=csv.writer(output)
    writer.writerow(['#','Fecha','Hora','Quien Pide','Operador','Cliente','Pasajeros','Origen','Destino','Ruta Completa','KMs','Mins','Timestamp'])
    for i,v in enumerate(viajes,1):
        writer.writerow([i, v.get('fecha'), v.get('hora'), v.get('solicita'), v.get('operador'), v.get('cliente'), v.get('pasajeros'), v.get('origen'), v.get('destino'), v.get('paradas'), v.get('kms'), v.get('mins'), v.get('timestamp')])
    mem=io.BytesIO(); mem.write(output.getvalue().encode('utf-8-sig')); mem.seek(0)
    return send_file(mem, as_attachment=True, download_name=f"concentrado_AGL_{datetime.now().strftime('%Y-%m-%d')}.csv", mimetype="text/csv")

try:
    if os.path.exists("/tmp/viajes.json"):
        with open("/tmp/viajes.json") as f: viajes.extend(json.load(f))
except: pass

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
