import streamlit as st
import matplotlib.pyplot as plt

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Disk Schedulling Simulator", layout="wide")

# ---------------- STYLING ----------------
def set_bg():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

set_bg()

# Sidebar style
st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] {
        background: #111;
        border-right: 2px solid #00FFFF;
    }

    div.stButton > button {
        background-color: #00FFFF;
        color: black;
        border-radius: 10px;
        height: 3em;
        width: 100%;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)



st.markdown(
    """
    <h1 style='text-align: center; color: #00FFFF;'>
    💿 Disk Scheduling Simulator
    </h1>
    """,
    unsafe_allow_html=True
)

st.markdown("### Visualize Disk Scheduling Algorithms in Action")

# ---------------- SIDEBAR ----------------
compare = st.sidebar.button("📊 Compare All Algorithms")

st.sidebar.header("⚙️ Input Parameters")


requests_input = st.sidebar.text_input(
    "Enter Requests (comma-separated)", 
    "98,183,37,122,14,124,65,67"
)

head = st.sidebar.number_input("Initial Head Position", min_value=0, value=53)
disk_size = st.sidebar.number_input("Disk Size", min_value=1, value=200)

algorithm = st.sidebar.selectbox(
    "Select Algorithm", 
    ["FCFS", "SSTF", "SCAN", "C-SCAN"]
)

direction = st.sidebar.selectbox("Direction (SCAN only)", ["left", "right"])

run = st.sidebar.button("🚀 Run Simulation")

# ---------------- FUNCTIONS ----------------

def fcfs(requests, head):
    sequence = [head] + requests
    seek_time = sum(abs(sequence[i+1] - sequence[i]) for i in range(len(sequence)-1))
    return sequence, seek_time

def sstf(requests, head):
    reqs = requests.copy()
    sequence = [head]
    seek_time = 0
    current = head

    while reqs:
        closest = min(reqs, key=lambda x: abs(x - current))
        seek_time += abs(current - closest)
        current = closest
        sequence.append(current)
        reqs.remove(closest)

    return sequence, seek_time

def scan(requests, head, disk_size, direction="left"):
    left = [r for r in requests if r < head]
    right = [r for r in requests if r >= head]

    left.sort()
    right.sort()

    sequence = [head]
    seek_time = 0
    current = head

    if direction == "left":
        for r in reversed(left):
            seek_time += abs(current - r)
            current = r
            sequence.append(current)

        seek_time += abs(current - 0)
        current = 0
        sequence.append(current)

        for r in right:
            seek_time += abs(current - r)
            current = r
            sequence.append(current)

    else:
        for r in right:
            seek_time += abs(current - r)
            current = r
            sequence.append(current)

        seek_time += abs(current - (disk_size - 1))
        current = disk_size - 1
        sequence.append(current)

        for r in reversed(left):
            seek_time += abs(current - r)
            current = r
            sequence.append(current)

    return sequence, seek_time


def cscan(requests, head, disk_size):
    left = [r for r in requests if r < head]
    right = [r for r in requests if r >= head]

    left.sort()
    right.sort()

    sequence = [head]
    seek_time = 0
    current = head

    for r in right:
        seek_time += abs(current - r)
        current = r
        sequence.append(current)

    seek_time += abs(current - (disk_size - 1))
    current = disk_size - 1
    sequence.append(current)

    seek_time += abs(current - 0)
    current = 0
    sequence.append(current)

    for r in left:
        seek_time += abs(current - r)
        current = r
        sequence.append(current)

    return sequence, seek_time

def card(title, value):
    st.markdown(
        f"""
        <div style="
            background-color: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        ">
            <h3>{title}</h3>
            <h2 style="color:#00FFAA;">{value}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------- GRAPH ----------------

def plot_graph(sequence, title):
    fig, ax = plt.subplots()

    ax.plot(sequence, marker='o', linewidth=2)
    ax.set_title(title, color='white')

    ax.set_facecolor("#0e1117")
    fig.patch.set_facecolor('#0e1117')

    ax.set_xlabel("Steps", color='white')
    ax.set_ylabel("Track Number", color='white')

    ax.tick_params(colors='white')
    ax.grid(color='gray', linestyle='--', linewidth=0.5)

    st.pyplot(fig)

# ---------------- MAIN ----------------

if run:
    try:
        requests = list(map(int, requests_input.split(",")))
    except:
        st.error("Invalid input format")
        st.stop()

    # Tabs for better UI
    tab1, tab2 = st.tabs(["📊 Result", "📈 Visualization"])

    if algorithm == "FCFS":
        sequence, seek_time = fcfs(requests, head)
    else:
        sequence, seek_time = sstf(requests, head)

    # -------- RESULT TAB --------
    with tab1:
        col1, col2 = st.columns(2)

        col1.metric("📍 Total Seek Time", seek_time)
        col2.metric("🔢 Total Requests", len(requests))

        st.markdown("### 🔄 Seek Sequence")
        st.code(" → ".join(map(str, sequence)))

    # -------- GRAPH TAB --------
    with tab2:
        plot_graph(sequence, f"{algorithm} Disk Scheduling")

if compare:
    try:
        requests = list(map(int, requests_input.split(",")))
    except:
        st.error("Invalid input format")
        st.stop()

    results = {}

    # Run all algorithms
    _, fcfs_time = fcfs(requests, head)
    _, sstf_time = sstf(requests, head)
    _, scan_time = scan(requests, head, disk_size, direction)
    _, cscan_time = cscan(requests, head, disk_size)

    results["FCFS"] = fcfs_time
    results["SSTF"] = sstf_time
    results["SCAN"] = scan_time
    results["C-SCAN"] = cscan_time

    st.markdown("## 📊 Algorithm Comparison Dashboard")

    # -------- METRICS --------
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("FCFS", fcfs_time)
    col2.metric("SSTF", sstf_time)
    col3.metric("SCAN", scan_time)
    col4.metric("C-SCAN", cscan_time)

    # -------- BEST ALGORITHM --------
    best_algo = min(results, key=results.get)
    st.success(f"🏆 Best Algorithm: {best_algo} (Lowest Seek Time)")

    # -------- BAR CHART --------
   

    fig, ax = plt.subplots()
    ax.bar(results.keys(), results.values())
    ax.set_title("Seek Time Comparison")
    ax.set_xlabel("Algorithms")
    ax.set_ylabel("Seek Time")

    st.pyplot(fig)
    

st.markdown("---")

st.markdown(
    """
    <center style='color:gray;'>
    use it 🚀
    </center>
    """,
    unsafe_allow_html=True
)