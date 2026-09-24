const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs');

const app = express();
const port = process.env.PORT || 3000;

// Data is saved to a JSON file so a restart does not wipe the tracks.
// On Render, point DATA_FILE at a persistent disk (e.g. /var/data/locations.json),
// otherwise the file is lost on every deploy.
const DATA_FILE = process.env.DATA_FILE || path.join(__dirname, 'data', 'locations.json');
const MAX_POINTS = 5000; // per device

let locationHistory = {};
try { locationHistory = JSON.parse(fs.readFileSync(DATA_FILE, 'utf8')); } catch (e) { /* first run */ }

let saveTimer = null;
function scheduleSave() {
  if (saveTimer) return;
  saveTimer = setTimeout(() => {
    saveTimer = null;
    try {
      fs.mkdirSync(path.dirname(DATA_FILE), { recursive: true });
      fs.writeFileSync(DATA_FILE, JSON.stringify(locationHistory));
    } catch (err) { console.error('Save failed:', err.message); }
  }, 5000);
}

app.use(cors());
app.use(express.json({ limit: '100kb' }));
app.use('/api', (req, res, next) => { res.set('Cache-Control', 'no-store'); next(); });

// Tells you which server instance answered. Two devices must show the same id to share data.
const INSTANCE = Math.random().toString(36).slice(2, 8);
const STARTED = new Date().toISOString();
app.get('/api/health', (req, res) => {
  const ids = Object.keys(locationHistory);
  res.json({ instance: INSTANCE, startedAt: STARTED, devices: ids.length, points: ids.reduce((n, id) => n + locationHistory[id].length, 0) });
});

const num = v => {
  if (v === null || v === undefined || v === '') return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
};
// Barometric pressure (kPa) -> altitude (m). Only differences matter, so weather drift is small over a short walk.
const pressureToAlt = kPa => 44330 * (1 - Math.pow((kPa * 10) / 1013.25, 0.1903));

// Pages
const page = name => (req, res) => res.sendFile(path.join(__dirname, name));
app.get('/', page('index.html'));
app.get('/viewer', page('viewer.html'));
app.get('/3d', page('viewer3d.html'));

// Receive a location. Accepts our web page format AND the OwnTracks app (HTTP mode) format.
app.post('/api/location', (req, res) => {
  const b = req.body || {};
  if (b._type && b._type !== 'location') return res.json([]); // ignore other OwnTracks messages

  const latitude = num(b.latitude ?? b.lat);
  const longitude = num(b.longitude ?? b.lon);
  const u = req.get('X-Limit-U'), d = req.get('X-Limit-D');
  const deviceId = b.deviceId || (u ? `${u}-${d || 'device'}` : null) || b.tid;

  if (latitude === null || longitude === null || !deviceId ||
      Math.abs(latitude) > 90 || Math.abs(longitude) > 180) {
    return res.status(400).json({ error: 'Missing or invalid fields' });
  }

  const pressure = num(b.pressure ?? b.p);
  const point = {
    latitude,
    longitude,
    accuracy: num(b.accuracy ?? b.acc),
    altitude: num(b.altitude ?? b.alt),
    altitudeAccuracy: num(b.altitudeAccuracy ?? b.vac),
    pressure,
    baroAltitude: pressure !== null ? pressureToAlt(pressure) : null,
    speed: num(b.speed ?? b.vel),
    heading: num(b.heading ?? b.cog),
    timestamp: b.timestamp || (b.tst ? new Date(b.tst * 1000).toISOString() : new Date().toISOString())
  };

  const list = (locationHistory[deviceId] = locationHistory[deviceId] || []);
  list.push(point);
  if (list.length > MAX_POINTS) locationHistory[deviceId] = list.slice(-MAX_POINTS);
  scheduleSave();

  res.json(b._type ? [] : { success: true });
});

app.get('/api/location/:deviceId', (req, res) => {
  res.json(locationHistory[req.params.deviceId] || []);
});

app.get('/api/devices', (req, res) => {
  res.json(Object.keys(locationHistory).map(id => {
    const list = locationHistory[id];
    const last = list[list.length - 1];
    return {
      id,
      points: list.length,
      lastSeen: last ? new Date(last.timestamp).toLocaleString() : 'Unknown',
      lastSeenIso: last ? last.timestamp : null
    };
  }));
});

// 3D GeoJSON export ([lon, lat, altitude]) for GIS tools / investigation records
app.get('/api/export/:deviceId.geojson', (req, res) => {
  const list = locationHistory[req.params.deviceId] || [];
  const coords = list.map(p => [p.longitude, p.latitude, p.baroAltitude ?? p.altitude ?? 0]);
  res.json({
    type: 'Feature',
    properties: { deviceId: req.params.deviceId, points: list.length },
    geometry: { type: 'LineString', coordinates: coords }
  });
});

// Clearing records. If ADMIN_KEY is set in Render's environment, clearing needs that key.
const ADMIN_KEY = process.env.ADMIN_KEY || '';
const requireAdmin = (req, res, next) => {
  if (ADMIN_KEY && req.get('x-admin-key') !== ADMIN_KEY) return res.status(401).json({ error: 'Admin key required' });
  next();
};
app.delete('/api/location/:deviceId', requireAdmin, (req, res) => {
  delete locationHistory[req.params.deviceId];
  scheduleSave();
  res.json({ success: true });
});
app.delete('/api/location', requireAdmin, (req, res) => {
  locationHistory = {};
  scheduleSave();
  res.json({ success: true });
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
  console.log(`2D map: http://localhost:${port}/viewer   3D: http://localhost:${port}/3d`);
});
