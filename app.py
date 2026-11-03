import random
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="AgriSense Smart Agriculture", page_icon="🌱", layout="wide")
st.markdown("""
<style>
.block-container{padding-top:1.3rem;max-width:1500px}
[data-testid="stAppViewContainer"]{background:#f4f7f4}
[data-testid="stSidebar"]{background:#123023}
[data-testid="stSidebar"] *{color:#f3fff5}
div[data-testid="stMetric"]{background:white;border:1px solid #dce7dc;padding:14px;border-radius:14px}
h1,h2,h3{color:#183526}
</style>""", unsafe_allow_html=True)

ZONES=["A1","A2","A3","B1","B2","B3"]
BASE={"A1":[43,31,68],"A2":[39,32,70],"A3":[46,30,65],"B1":[35,33,72],"B2":[48,29,66],"B3":[41,31,69]}

def init():
    defaults={
        "zones":{z:{"moisture":v[0],"temperature":v[1],"humidity":v[2]} for z,v in BASE.items()},
        "history":[],"alerts":[],"online":True,"latency":21.0,"throughput":18.4,"delivery":97.6,
        "drone_route":[],"drone_index":0,"drone_zone":"Base","drone_status":"Standby","scans":{}
    }
    for k,v in defaults.items():
        if k not in st.session_state: st.session_state[k]=v
init()

def status(d):
    if d["moisture"]<30 or d["temperature"]>35:return "Critical"
    if d["moisture"]<36 or d["temperature"]>=34:return "Needs attention"
    return "Healthy"

def alert(msg,level="Warning"):
    if not st.session_state.alerts or st.session_state.alerts[0]["message"]!=msg:
        st.session_state.alerts.insert(0,{"time":datetime.now().strftime("%H:%M:%S"),"message":msg,"level":level})
    st.session_state.alerts=st.session_state.alerts[:15]

def update(z,m=None,t=None,h=None):
    d=st.session_state.zones[z]
    if m is not None:d["moisture"]=float(m)
    if t is not None:d["temperature"]=float(t)
    if h is not None:d["humidity"]=float(h)
    if d["moisture"]<30:alert(f"{z}: low soil moisture ({d['moisture']:.1f}%). Irrigation inspection recommended.","Critical")
    if d["temperature"]>35:alert(f"{z}: high temperature ({d['temperature']:.1f} °C). Check crop stress.","Critical")

def record():
    now=datetime.now()
    for z,d in st.session_state.zones.items():
        st.session_state.history.append({"time":now,"zone":z,"Soil moisture (%)":d["moisture"]+random.uniform(-1,1),
          "Temperature (°C)":d["temperature"]+random.uniform(-.5,.5),"Humidity (%)":d["humidity"]+random.uniform(-2,2)})
    st.session_state.history=st.session_state.history[-300:]

if not st.session_state.history:
    for _ in range(10):record()

with st.sidebar:
    st.markdown("## 🌱 AgriSense")
    st.caption("CONNECTED AGRICULTURE")
    page=st.radio("WORKSPACE",["Overview","Field intelligence","Drone operations","5G connectivity","Alerts & events","Simulation controls"])
    st.divider()
    st.success("Software simulation active")
    st.caption("No physical sensors, drone or 5G modem are connected.")

st.caption("WORKSPACE / PRECISION AGRICULTURE")
st.title("AgriSense Smart Agriculture Simulator")
st.caption("IoT field sensing • Drone inspection • Simulated 5G communication")
if st.session_state.online: st.success("● Simulated network online")
else: st.error("● Simulated network disconnected")

zones=st.session_state.zones
avgm=np.mean([d["moisture"] for d in zones.values()])
avgt=np.mean([d["temperature"] for d in zones.values()])
avgh=np.mean([d["humidity"] for d in zones.values()])
health=int(np.mean([100-(45 if d["moisture"]<30 else 20 if d["moisture"]<36 else 0)-(35 if d["temperature"]>35 else 15 if d["temperature"]>=34 else 0) for d in zones.values()]))
a,b,c,d=st.columns(4)
a.metric("Average soil moisture",f"{avgm:.1f}%")
b.metric("Air temperature",f"{avgt:.1f} °C")
c.metric("Relative humidity",f"{avgh:.1f}%")
d.metric("Field health index",f"{health}/100")

def farm_map():
    import plotly.graph_objects as go
    fig=go.Figure()
    coords={"A1":(0,1),"A2":(1,1),"A3":(2,1),"B1":(0,0),"B2":(1,0),"B3":(2,0)}
    colors={"Healthy":"#55a96e","Needs attention":"#e0aa42","Critical":"#d9534f"}
    for z,(x,y) in coords.items():
        ds=zones[z]; s=status(ds)
        fig.add_shape(type="rect",x0=x+.04,y0=y+.04,x1=x+.96,y1=y+.96,
                      fillcolor=colors[s],line=dict(color="white",width=3))
        fig.add_annotation(x=x+.5,y=y+.63,text=f"<b>{z}</b>",showarrow=False,font=dict(size=21,color="white"))
        fig.add_annotation(x=x+.5,y=y+.36,text=f"{ds['moisture']:.1f}% moisture",showarrow=False,font=dict(size=12,color="white"))
        fig.add_annotation(x=x+.5,y=y+.15,text=s,showarrow=False,font=dict(size=10,color="white"))
    fig.update_layout(height=330,margin=dict(l=2,r=2,t=2,b=2),plot_bgcolor="#eaf1e9",paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False,range=[0,3]),yaxis=dict(visible=False,range=[0,2],scaleanchor="x"))
    return fig

def chart(zone=None):
    df=pd.DataFrame(st.session_state.history)
    if zone:df=df[df.zone==zone]
    else:df=df.groupby("time",as_index=False)[["Soil moisture (%)","Temperature (°C)","Humidity (%)"]].mean()
    fig=px.line(df,x="time",y=["Soil moisture (%)","Temperature (°C)","Humidity (%)"],markers=True)
    fig.update_layout(height=320,margin=dict(l=5,r=5,t=15,b=5),legend_title_text="")
    return fig

if page=="Overview":
    left,right=st.columns([1.1,1])
    with left:
        st.subheader("Agricultural field map")
        st.plotly_chart(farm_map(),use_container_width=True)
        st.caption("Green: Healthy • Amber: Needs attention • Red: Critical")
    with right:
        st.subheader("Environmental telemetry")
        st.plotly_chart(chart(),use_container_width=True)
    st.subheader("Zone status")
    st.dataframe(pd.DataFrame([{"Zone":z,**{k:round(v,1) for k,v in ds.items()},"Crop condition":status(ds)} for z,ds in zones.items()]),use_container_width=True,hide_index=True)
    st.info("Case-study thresholds: soil moisture below 30% and temperature above 35 °C generate warnings.")

elif page=="Field intelligence":
    st.subheader("Field intelligence")
    z=st.selectbox("Select field zone",ZONES); ds=zones[z]
    x,y,w=st.columns(3);x.metric("Soil moisture",f"{ds['moisture']:.1f}%");y.metric("Temperature",f"{ds['temperature']:.1f} °C");w.metric("Humidity",f"{ds['humidity']:.1f}%")
    st.markdown(f"### {z}: {status(ds)}")
    st.plotly_chart(chart(z),use_container_width=True)
    img="healthy_crop.svg" if status(ds)=="Healthy" else ("dry_crop.svg" if ds["moisture"]<30 else "stressed_crop.svg")
    st.image(str(Path(__file__).parent/"assets"/img),caption="Illustrative crop image, not a live drone photograph.",use_container_width=True)
    st.caption("Crop labels are rule-based demonstration outputs; no AI disease detection is performed.")

elif page=="Drone operations":
    st.subheader("Drone field inspection")
    l,r=st.columns([1.1,1])
    with l:
        st.plotly_chart(farm_map(),use_container_width=True)
        st.metric("Drone status",st.session_state.drone_status)
        st.metric("Current location",st.session_state.drone_zone)
        if st.session_state.drone_route:st.write("Route: Base → "+" → ".join(st.session_state.drone_route)+" → Base")
    with r:
        if st.button("🚁 Start inspection mission",type="primary",use_container_width=True):
            st.session_state.drone_route=ZONES.copy();st.session_state.drone_index=0
            st.session_state.drone_zone="Base";st.session_state.drone_status="Mission started";st.rerun()
        if st.button("➡️ Move to next zone / scan",use_container_width=True,disabled=not st.session_state.drone_route):
            i=st.session_state.drone_index
            if i<len(st.session_state.drone_route):
                z=st.session_state.drone_route[i];st.session_state.drone_zone=z
                s=status(zones[z]);result="Healthy" if s=="Healthy" else ("Stress indicators detected" if s=="Needs attention" else "Critical condition detected")
                st.session_state.scans[z]={"result":result,"time":datetime.now().strftime("%H:%M:%S")}
                st.session_state.drone_index+=1;st.session_state.drone_status=f"Scanning {z}"
                alert(f"Drone completed illustrative inspection in {z}: {result}.","Info");st.rerun()
            else:st.session_state.drone_status="Inspection complete"
        if st.button("🏠 Return drone to base",use_container_width=True):
            st.session_state.drone_route=[];st.session_state.drone_index=0;st.session_state.drone_zone="Base";st.session_state.drone_status="Standby";st.rerun()
        st.markdown("#### Inspection results")
        if st.session_state.scans:st.dataframe(pd.DataFrame([{"Zone":z,**v} for z,v in st.session_state.scans.items()]),use_container_width=True,hide_index=True)
        else:st.caption("Start a mission and scan zones one at a time.")
    st.warning("Drone movement and inspection results are simulated; no physical drone is controlled.")

elif page=="5G connectivity":
    st.subheader("5G communication simulation")
    if st.session_state.online:st.success("Gateway connected to simulated 5G network")
    else:st.error("Network link unavailable — data delivery interrupted")
    x,y,z=st.columns(3);x.metric("Latency",f"{st.session_state.latency:.1f} ms");y.metric("Throughput",f"{st.session_state.throughput:.1f} Mbps");z.metric("Packet delivery",f"{st.session_state.delivery:.1f}%")
    st.caption(f"Packet loss: {100-st.session_state.delivery:.1f}%")
    source=st.selectbox("Sensor source zone",ZONES,key="packet_source")
    if st.button("Transmit sensor packet",type="primary",disabled=not st.session_state.online):
        st.session_state.latency=round(random.uniform(12,45),1);st.session_state.throughput=round(random.uniform(8,35),1);st.session_state.delivery=round(random.uniform(94,100),1)
        alert(f"Sensor packet from {source} delivered. Simulated latency {st.session_state.latency} ms.","Info")
        st.success(f"Packet from {source} delivered to simulated server.")
    x,y=st.columns(2)
    if x.button("Simulate network interruption",use_container_width=True):
        st.session_state.online=False;st.session_state.delivery=0;alert("Communication link interrupted. Packets cannot be delivered.","Critical");st.rerun()
    if y.button("Restore network",use_container_width=True):
        st.session_state.online=True;st.session_state.latency=21;st.session_state.throughput=18.4;st.session_state.delivery=97.6;alert("Simulated network connection restored.","Info");st.rerun()
    st.info("Illustrative network metrics only. Actual 5G performance requires suitable 5G equipment and measurement.")

elif page=="Alerts & events":
    st.subheader("Alerts and operational events")
    if not st.session_state.alerts:st.success("No alerts. All zones are within the selected thresholds.")
    for item in st.session_state.alerts:
        msg=f"{item['time']} | {item['message']}"
        if item["level"]=="Critical":st.error(msg)
        elif item["level"]=="Warning":st.warning(msg)
        else:st.info(msg)
    if st.button("Clear alert history"):st.session_state.alerts=[];st.rerun()

elif page=="Simulation controls":
    st.subheader("Simulation controls")
    z=st.selectbox("Choose zone to modify",ZONES,key="edit_zone");ds=zones[z]
    with st.form("sensor_form"):
        m=st.slider("Soil moisture (%)",5.0,80.0,float(ds["moisture"]),.5)
        t=st.slider("Temperature (°C)",10.0,48.0,float(ds["temperature"]),.5)
        h=st.slider("Humidity (%)",20.0,100.0,float(ds["humidity"]),1.0)
        submitted=st.form_submit_button("Apply sensor readings",type="primary")
    if submitted:update(z,m,t,h);record();st.success(f"Updated readings for {z}.");st.rerun()
    st.markdown("#### Quick test scenarios")
    c1,c2,c3=st.columns(3)
    if c1.button("Normal conditions"):
        for zone,v in BASE.items():update(zone,*v)
        record();st.rerun()
    if c2.button("Low moisture in A2"):
        update("A2",22,32,70);record();st.rerun()
    if c3.button("High temperature in B1"):
        update("B1",35,39,72);record();st.rerun()
    if st.button("Generate new sensor readings"):
        for zone,dd in zones.items():update(zone,dd["moisture"]+random.uniform(-2,2),dd["temperature"]+random.uniform(-1,1),dd["humidity"]+random.uniform(-3,3))
        record();st.rerun()

st.divider()
st.caption("AgriSense academic simulation • Sensor readings, drone movement, crop inspection and network metrics are illustrative.")
csv=pd.DataFrame([{"zone":z,**v,"crop_condition":status(v)} for z,v in zones.items()]).to_csv(index=False).encode()
st.download_button("⬇️ Download current zone readings (CSV)",csv,"agrisense_readings.csv","text/csv")
