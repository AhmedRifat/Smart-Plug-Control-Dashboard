**Smart Plug Control System**

A comprehensive web application for monitoring and controlling Tuya-based smart plugs with energy usage tracking and historical data visualization.

---

**Features**

* Real-time Monitoring: Track power (W), voltage (V), and current (A) in real-time
* Device Control: Turn devices on/off remotely
* Energy Usage Visualization: Interactive charts showing power consumption
* Historical Data: View and analyze past energy usage by date
* User Manual: Complete documentation accessible within the app
* Responsive Design: Works on desktop and mobile devices

---

**Technology Stack**

* **Frontend**: HTML5, CSS3, JavaScript (Chart.js, Flatpickr)
* **Backend**: Python (Flask)
* **Database**: JSON file storage
* **Hardware Integration**: Tuya Smart Plug API (via TuyAPI and TinyTuya)
* **Visualization**: Chart.js for interactive charts

---

**Installation**

**Prerequisites**

* Python 3.7 or above
* Node.js 14 or above (for Tuya monitor)
* Tuya Smart Plug
* Same network access for plug and server

---

**Setup**

1. **Clone the repository**:

   ```bash
   git clone https://github.com/AhmedRifat/Smart-Plug-Control-Dashboard.git
   cd Smart-Plug-Control-Dashboard
   ```

2. **Install Python dependencies**:

   ```bash
   pip install flask tinytuya
   ```

3. **Set up Node.js monitor**:

   ```bash
   cd tuyapi-node
   npm install tuyapi chalk
   cd ..
   ```

4. **Create `data` folder if not present**:

   ```bash
   mkdir data
   ```

---

**Getting Device Credentials (TinyTuya)**

You need **Device ID**, **Local IP**, and **Local Key** to connect your Tuya smart plug.

1. Install TinyTuya:

   ```bash
   pip install tinytuya
   ```

2. **Use TinyTuya Wizard** (recommended) to get credentials easily:

   Run the wizard:

   ```bash
   python -m tinytuya wizard
   ```

   This interactive tool will help you discover your devices on the network and extract the local key automatically.

3. Alternatively, you can scan devices (without wizard):

   ```bash
   python -m tinytuya scan
   ```

4. Note down the **Device ID**, **Local IP address**, and **Local Key** from the wizard or scan output.

5. Update `config.py` with your credentials:

   ```python
   DEVICE_CONFIG = {
       'DEVICE_ID': "your_device_id",
       'DEVICE_IP': "192.168.0.xxx",
       'LOCAL_KEY': "your_local_key",
       'VERSION': 3.5
   }
   ```

6. Also update `tuyapi-node/tuya-monitor.js` with the same credentials.

---

**Run the App**

1. Start Flask:

   ```bash
   python app.py
   ```

2. Open in browser:

   ```
   http://127.0.0.1:5000
   ```

---

**File Structure**

```
Smart-Plug-Control-Dashboard/
├── app.py
├── config.py
├── tuya_control.py
├── data/
│   ├── energy_logs.json
│   └── device_status.json
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── history.html
│   └── manual.html
├── static/
│   ├── style.css
│   └── graph.png
└── tuyapi-node/
    ├── tuya-monitor.js
    ├── package.json
    └── package-lock.json
```

---

**API Endpoints**

* `GET /api/status` – Get device status
* `POST /api/turn_on` – Turn ON
* `POST /api/turn_off` – Turn OFF

---


**Usage**

* Dashboard shows device metrics and live status
* History allows date-wise energy data view
* Manual gives instructions and help

**Color Legend**:

* 🟢 Green = Online
* 🟡 Yellow = Standby
* 🔴 Red = Offline
* 🔵 Blue = Processing

---

**Troubleshooting**

*Device not connecting*:

* Check IP, Local Key, and ID
* Ensure same network
* Device must be in local control mode

*Data not logging*:

* Ensure `data` folder exists
* Check Node.js monitor output for errors

---

**Contributing**

Pull requests are welcome! Fork the repo and submit changes.

---

**License**

This project is open source and available under the MIT License.

---

**Acknowledgments**

* Tuya API
* TinyTuya and TuyAPI
* Chart.js
* Flask
