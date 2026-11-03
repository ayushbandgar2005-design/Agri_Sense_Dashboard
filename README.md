# AgriSense — 5G-Based Smart Agriculture Simulation

Streamlit demonstration for the Mobile Communication and Networking case study.

## Features
- Six agricultural zones (A1–A3, B1–B3).
- Simulated soil moisture, temperature and humidity.
- Threshold alerts: soil moisture below 30%; temperature above 35 °C.
- Drone mission workflow: start, scan zones one by one, return to base.
- Simulated 5G latency, throughput, packet delivery and packet loss.
- Network interruption and restoration.
- Field map, telemetry graphs, zone status and CSV export.

## Important
This is a software simulation. Sensor values, drone movement, crop inspection labels and network metrics are illustrative. It does not connect to physical sensors, a real drone or a 5G modem. Crop images are illustrative placeholders, not live drone photographs or AI disease diagnoses.

## Deploy on Streamlit Community Cloud
1. Upload `app.py`, `requirements.txt`, `README.md` and the complete `assets` folder to GitHub.
2. Visit https://share.streamlit.io/ and sign in with GitHub.
3. Select **Create app**, choose your repository and branch.
4. Set the main file path to `app.py`.
5. Click **Deploy**.

## Suggested viva demonstration
1. Open Overview and explain the six field zones.
2. In Simulation controls, select **Low moisture in A2**.
3. Return to Overview and show the A2 zone turning critical.
4. Open Alerts & events and explain the warning.
5. Open Drone operations, start the mission and scan zones.
6. Open 5G connectivity, transmit a packet, interrupt the link, then restore it.
7. Explain that the displayed network metrics are simulated, not measured on a live 5G network.
