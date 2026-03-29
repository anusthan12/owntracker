<div align="center">

# 📍 Device Location Tracker & Admin Monitor

**Real-time device tracking, live trace mapping, and full admin visibility — all from a single dashboard.**

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](#)
[![Node.js](https://img.shields.io/badge/Node.js-Server-339933?style=for-the-badge&logo=node.js&logoColor=white)](#)
[![OwnTracks](https://img.shields.io/badge/OwnTracks-Adapter-F7A800?style=for-the-badge)](#)
[![JavaScript](https://img.shields.io/badge/JavaScript-Frontend-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](#)
[![HTML5](https://img.shields.io/badge/HTML5-Dashboard-E34F26?style=for-the-badge&logo=html5&logoColor=white)](#)

</div>

<br />

> A full-stack device location tracking system with a live admin panel. Monitors real-time device positions, builds a complete movement trace of every location point visited, and surfaces it all through a clean administrative dashboard.

---

## ✨ Core Features

- **📡 Real-Time Location Tracking** — Continuously captures and streams device GPS coordinates to the server as they update
- **🗺️ Movement Trace History** — Automatically logs and connects every location point visited, building a full path trace of the device's journey
- **🖥️ Admin Control Panel** — Dedicated admin dashboard (`index.html`) for monitoring active devices, viewing live positions, and replaying historical traces
- **🔌 OwnTracks Protocol Adapter** — Custom `owntracks-adapter.js` bridges the OwnTracks location protocol with the server, enabling broad device compatibility
- **⚡ Node.js + Python Dual Backend** — `server.js` handles real-time WebSocket/HTTP communication while `location_tracker.py` manages data processing and storage
- **🔄 Persistent Session Logging** — Every tracked session is stored, enabling full trace replay and audit of device movement over time

---

## 🛠 Technology Stack

| Category | Technology | Role |
| :--- | :--- | :--- |
| **Frontend** | HTML5, JavaScript | Admin panel UI and live map rendering |
| **Runtime** | Node.js | Real-time server, WebSocket handling, OwnTracks adapter |
| **Backend** | Python | Location data processing, storage, and session management |
| **Protocol** | OwnTracks | Standardized location reporting from target devices |

---

## 🧬 How It Works

```
Target Device (GPS)
      │
      ▼
OwnTracks Protocol
      │
      ▼
owntracks-adapter.js  ──→  server.js (Node.js)
                                  │
                                  ▼
                         location_tracker.py
                         (Data Processing & Storage)
                                  │
                                  ▼
                         Admin Panel (index.html)
                         Live Position + Full Trace Map
```

1. **Device Reports** — The target device broadcasts its GPS coordinates via the OwnTracks protocol
2. **Adapter Normalizes** — `owntracks-adapter.js` translates the incoming OwnTracks payload into the server's internal format
3. **Server Processes** — `server.js` receives the normalized location data and forwards it to the Python backend
4. **Tracker Logs** — `location_tracker.py` stores each coordinate point and builds the running movement trace
5. **Admin Views** — The admin panel displays the live position and renders the full historical path trace on a map in real time

---

## 📁 Project Structure

```
Location-Tracker/
├── index.html               # Admin monitoring dashboard
├── server.js                # Node.js real-time server & API
├── owntracks-adapter.js     # OwnTracks protocol bridge
├── location_tracker.py      # Python location processing & storage
├── package.json             # Node.js dependencies
└── requirements.txt         # Python dependencies
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/anusthan12/Location-Tracker.git
cd Location-Tracker
```

### 2. Install Dependencies

```bash
# Node.js dependencies
npm install

# Python dependencies
pip install -r requirements.txt
```

### 3. Start the Server

```bash
node server.js
```

### 4. Run the Python Tracker

```bash
python location_tracker.py
```

### 5. Open Admin Panel

```
Open index.html in your browser to access the admin dashboard.
```

---

## ⚠️ Disclaimer

This tool is intended for **authorized monitoring only** — such as personal device tracking, fleet management, parental controls, or systems where explicit consent has been obtained. Unauthorized tracking of individuals without their knowledge or consent may be illegal in your jurisdiction. Use responsibly.

---

<div align="center">
  <p>Built and maintained by <a href="https://github.com/anusthan12"><strong>Anusthan Singh</strong></a> &nbsp;•&nbsp; © 2025</p>
</div>
