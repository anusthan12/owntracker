const express = require('express');
const cors = require('cors');
const path = require('path');
const app = express();
const port = process.env.PORT || 3000;

// In-memory storage (replace with a database for production)
const locationHistory = {};

// Middleware
app.use(cors());
app.use(express.json());

// Serve static files directly from the root directory
app.use(express.static(path.join(__dirname)));

// Routes - serve index.html
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// API endpoint to receive location updates
app.post('/api/location', (req, res) => {
  const { latitude, longitude, timestamp, deviceId } = req.body;
  
  if (!latitude || !longitude || !deviceId) {
    return res.status(400).json({ error: 'Missing required fields' });
  }
  
  // Store the location
  if (!locationHistory[deviceId]) {
    locationHistory[deviceId] = [];
  }
  
  locationHistory[deviceId].push({
    latitude,
    longitude,
    timestamp: timestamp || new Date().toISOString()
  });
  
  // Only keep the last 100 locations per device
  if (locationHistory[deviceId].length > 100) {
    locationHistory[deviceId] = locationHistory[deviceId].slice(-100);
  }
  
  res.json({ success: true });
});

// API endpoint to get location history for a device
app.get('/api/location/:deviceId', (req, res) => {
  const { deviceId } = req.params;
  res.json(locationHistory[deviceId] || []);
});

// Start the server
app.listen(port, () => {
  console.log(`Server running on port ${port}`);
  console.log(`Open http://localhost:${port} in your browser`);
});
