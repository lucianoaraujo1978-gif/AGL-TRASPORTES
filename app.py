from flask import Flask, render_template_string, request, redirect, session
import sqlite3, datetime, os

app = Flask(__name__)
app.secret_key = 'agl2024'

# Base de datos
def init_db():
    conn = sqlite3.connect('agl.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios
                 (id INTEGER PRIMARY KEY, nombre TEXT, telefono TEXT, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS viajes
                 (id INTEGER PRIMARY KEY, fecha TEXT, supervisor TEXT, camion TEXT, caja TEXT,
                  operador TEXT, origen TEXT, destino TEXT, kms REAL,
                  lat_origen REAL, lon_origen REAL, lat_destino REAL, lon_destino REAL,
                  usuario_id INTEGER)''')
    conn.commit()
    conn.close()

init_db()

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AGL TRASPORTES</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
body{font-family:Arial;background:#f0f2f5;margin:0;padding:10px}
.card{background:white;padding:15px;border-radius:12px;box-shadow:0 2px 8px #0002;margin-bottom:15px}
input,button{width:100%;padding:12px;margin:5px 0;border-radius:8px;border:1px solid #ccc;box-sizing:border-box}
button{background:#0a3d62;color:white;font-weight:bold;border:none}
#map{height:350px;border-radius:12px;margin:10px 0}
.header{background:#0a3d62;color:white;padding:15px;border-radius:12px;text-align:center;margin-bottom:15px}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{border:1px solid #ddd;padding:6px;text-align:left}
th{background:#0a3d62;color:white}
</style>
</head>
<body>
<div class="header"><h2>🚛 AGL TRASPORTES</h2></div>

{% if not session.get('user') %}
<div class="card">
<h3>Login / Registro</h3>
<form method="post" action="/login">
<input name="telefono" placeholder="Telefono" required>
<input name="password" type="password" placeholder="Password" required>
<button type="submit">Entrar</button>
</form>
<hr>
<form method="post" action="/registro">
<input name="nombre" placeholder="Nombre completo" required>
<input name="telefono" placeholder="Telefono" required>
<input name="password" type="password" placeholder="Password" required>
<button type="submit" style="background:#27ae60">Registrarse</button>
</form>
</div>

{% else %}
<div class="card">
<p>Bienvenido: <b>{{session['nombre']}}</b> <a href="/logout">[Salir]</a></p>
<h3>Nuevo Viaje</h3>
<form method="post" action="/add">
<input name="fecha" type="date" value="{{hoy}}" required>
<input name="supervisor" placeholder="Supervisor" required>
<input name="camion" placeholder="No. Camion" required>
<input name="caja" placeholder="No. Caja" required>
<input name="operador" placeholder="Operador" required>
<input name="origen" id="origen" placeholder="Origen (ej: Aguascalientes)" required>
<input name="destino" id="destino" placeholder="Destino (ej: Guadalajara)" required>
<input type="hidden" id="lat_origen" name="lat_origen">
<input type="hidden" id="lon_origen" name="lon_origen">
<input type="hidden" id="lat_destino" name="lat_destino">
<input type="hidden" id="lon_destino" name="lon_destino">
<button type="button" onclick="calcularRuta()">📍 Calcular Ruta y KM en Mapa</button>
<input name="kms" id="kms" placeholder="KMs (se calcula solo)" required>
<button type="submit" style="background:#e67e22">Guardar Viaje</button>
</form>
<div id="map"></div>
<p id="info"></p>
</div>

<div class="card">
<h3>Historial de Viajes</h3>
<table>
<tr><th>Fecha</th><th>Ruta</th><th>KM</th><th>Camion</th></tr>
{% for v in viajes %}
<tr><td>{{v[1]}}</td><td>{{v[6]}} -> {{v[7]}}</td><td>{{v[8]}}</td><td>{{v[3]}}</td></tr>
{% endfor %}
</table>
</div>

<script>
var map = L.map('map').setView([22.0, -102.0], 5);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
var control = null;

async function geocode(q){
  let r = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${q}`);
  let d = await r.json();
  return d[0];
}

async function calcularRuta(){
  let o = document.getElementById('origen').value;
  let d = document.getElementById('destino').value;
  if(!o ||!d){alert('Pon origen y destino');return;}
  let go = await geocode(o);
  let gd = await geocode(d);
  if(!go ||!gd){alert('No encontré la direccion');return;}

  document.getElementById('lat_origen').value = go.lat;
  document.getElementById('lon_origen').value = go.lon;
  document.getElementById('lat_destino').value = gd.lat;
  document.getElementById('lon_destino').value = gd.lon;

  // calcular distancia haversine
  let R=6371;
  let dLat=(gd.lat-go.lat)*Math.PI/180;
  let dLon=(gd.lon-go.lon)*Math.PI/180;
  let a=Math.sin(dLat/2)**2+Math.cos(go.lat*Math.PI/180)*Math.cos(gd.lat*Math.PI/180)*Math.sin(dLon/2)**2;
  let c=2*Math.atan2(Math.sqrt(a),Math.sqrt(1-a));
  let dist=R*c;
  document.getElementById('kms').value = dist.toFixed(1);
  document.getElementById('info').innerHTML = `Distancia aprox: <b>${dist.toFixed(1)} km</b>`;

  if(control){map.removeLayer(control);}
  control = L.layerGroup().addTo(map);
  L.marker([go.lat, go.lon]).addTo(control).bindPopup('Origen: '+o);
  L.marker([gd.lat, gd.lon]).addTo(control).bindPopup('Destino: '+d);
  L.polyline([[go.lat, go.lon],[gd.lat, gd.lon]], {color:'blue'}).addTo(control);
  map.fitBounds([[go.lat, go.lon],[gd.lat, gd.lon]]);
}
</script>

{% endif %}
</body>
</html>
"""

@app.route('/')
def index():
    hoy = datetime.date.today().isoformat()
    viajes=[]
    if session.get('user'):
        conn = sqlite3.connect('agl.db')
        c = conn.cursor()
        c.execute('SELECT * FROM viajes WHERE usuario_id=? ORDER BY id DESC', (session['user'],))
        viajes = c.fetchall()
        conn.close()
    return render_template_string(HTML, viajes=viajes, hoy=hoy)

@app.route('/registro', methods=['POST'])
def registro():
    conn = sqlite3.connect('agl.db')
    c = conn.cursor()
    c.execute('INSERT INTO usuarios (nombre,telefono,password) VALUES (?,?,?)',
              (request.form['nombre'], request.form['telefono'], request.form['password']))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    conn = sqlite3.connect('agl.db')
    c = conn.cursor()
    c.execute('SELECT * FROM usuarios WHERE telefono=? AND password=?',
              (request.form['telefono'], request.form['password']))
    u = c.fetchone()
    conn.close()
    if u:
        session['user']=u[0]
        session['nombre']=u[1]
    return redirect('/')

@app.route('/add', methods=['POST'])
def add():
    if not session.get('user'): return redirect('/')
    conn = sqlite3.connect('agl.db')
    c = conn.cursor()
    c.execute('INSERT INTO viajes (fecha,supervisor,camion,caja,operador,origen,destino,kms,lat_origen,lon_origen,lat_destino,lon_destino,usuario_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',
              (request.form['fecha'], request.form['supervisor'], request.form['camion'], request.form['caja'],
               request.form['operador'], request.form['origen'], request.form['destino'], float(request.form['kms']),
               request.form['lat_origen'], request.form['lon_origen'], request.form['lat_destino'], request.form['lon_destino'],
               session['user']))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT',5000)))