import pandas as pd
import streamlit as st
import warnings
from io import BytesIO
from datetime import datetime, timedelta
import streamlit.components.v1 as components

# Ignore unnecessary warnings
warnings.filterwarnings('ignore')

# --- Session State Initialization ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

# --- Core Functions ---

def toggle_theme():
    """Switches the theme between 'light' and 'dark'."""
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'
    st.rerun()

def add_new_task():
    """Adds a new task row and sets a notification message."""
    st.session_state.row_count += 1
    new_id = st.session_state.row_count
    st.session_state.tasks.append({"task_id": new_id})

    # Auto-fill time based on the previous task's end time
    if new_id > 1:
        prev_id = new_id - 1
        prev_end_h = int(st.session_state.get(f"end_hours_{prev_id}", "09"))
        prev_end_m = int(st.session_state.get(f"end_minutes_{prev_id}", "01"))
        
        prev_end_total = prev_end_h * 60 + prev_end_m
        
        # --- MODIFIED LOGIC ---
        # Set new start time to be 1 minute after the previous task's end time.
        new_start_total = prev_end_total + 1
        
        new_start_h = (new_start_total // 60) % 24
        new_start_m = new_start_total % 60
        st.session_state[f"start_hours_{new_id}"] = f"{new_start_h:02d}"
        st.session_state[f"start_minutes_{new_id}"] = f"{new_start_m:02d}"
        
        # New end time is 1 minute after the new start time
        new_end_total = new_start_total + 1
        new_end_h = (new_end_total // 60) % 24
        new_end_m = new_end_total % 60
        st.session_state[f"end_hours_{new_id}"] = f"{new_end_h:02d}"
        st.session_state[f"end_minutes_{new_id}"] = f"{new_end_m:02d}"

    st.session_state.notification = f"Task {new_id} added!"

def remove_task(task_id_to_remove):
    """Removes a task, re-indexes remaining tasks and their session state data."""
    tasks_to_keep = [t for t in st.session_state.tasks if t["task_id"] != task_id_to_remove]
    
    # Store data temporarily before clearing
    temp_data = {}
    for task in tasks_to_keep:
        old_id = task['task_id']
        temp_data[old_id] = {
            "desc": st.session_state.get(f"task_desc_{old_id}", ""),
            "start_h": st.session_state.get(f"start_hours_{old_id}", "09"),
            "start_m": st.session_state.get(f"start_minutes_{old_id}", "00"),
            "end_h": st.session_state.get(f"end_hours_{old_id}", "09"),
            "end_m": st.session_state.get(f"end_minutes_{old_id}", "01")
        }

    # Clear old session state keys
    for i in range(1, st.session_state.row_count + 1):
        for key in ["task_desc", "start_hours", "start_minutes", "end_hours", "end_minutes"]:
            st.session_state.pop(f"{key}_{i}", None)

    # Re-populate session state with corrected IDs
    for i, task in enumerate(tasks_to_keep):
        new_id = i + 1
        old_id = task['task_id']
        
        st.session_state[f"task_desc_{new_id}"] = temp_data[old_id]["desc"]
        st.session_state[f"start_hours_{new_id}"] = temp_data[old_id]["start_h"]
        st.session_state[f"start_minutes_{new_id}"] = temp_data[old_id]["start_m"]
        st.session_state[f"end_hours_{new_id}"] = temp_data[old_id]["end_h"]
        st.session_state[f"end_minutes_{new_id}"] = temp_data[old_id]["end_m"]

    # Update the main tasks list and count
    st.session_state.tasks = [{"task_id": i + 1} for i in range(len(tasks_to_keep))]
    st.session_state.row_count = len(st.session_state.tasks)
    
    st.session_state.notification = f"Task {task_id_to_remove} removed!"

def validate_time(task_id, clock_type, part):
    """Validates and formats time input for hours or minutes."""
    key = f"{clock_type}_{part}_{task_id}"
    value = st.session_state.get(key, "00")
    try:
        num = int(value)
        num = max(0, min(23 if part == "hours" else 59, num))
        st.session_state[key] = f"{num:02d}"
    except (ValueError, TypeError):
        st.session_state[key] = "00"
    validate_end_time(task_id)

def validate_end_time(task_id):
    """Ensures the end time is at least 1 minute after the start time."""
    start_h = int(st.session_state.get(f"start_hours_{task_id}", "09"))
    start_m = int(st.session_state.get(f"start_minutes_{task_id}", "00"))
    end_h = int(st.session_state.get(f"end_hours_{task_id}", "09"))
    end_m = int(st.session_state.get(f"end_minutes_{task_id}", "01"))

    start_total = start_h * 60 + start_m
    end_total = end_h * 60 + end_m

    if end_total <= start_total:
        end_total = start_total + 1
        end_h = (end_total // 60) % 24
        end_m = end_total % 60
        st.session_state[f"end_hours_{task_id}"] = f"{end_h:02d}"
        st.session_state[f"end_minutes_{task_id}"] = f"{end_m:02d}"

def create_dynamic_clock_with_input(task_id, clock_type, container_bg):
    """Creates the HTML and CSS for the analog clock component."""
    clock_id = f"{clock_type}_clock_{task_id}"
    default_hour = "09"
    default_minute = "00" if clock_type == "start" else "01"
    
    current_hour_str = st.session_state.get(f"{clock_type}_hours_{task_id}", default_hour)
    current_minute_str = st.session_state.get(f"{clock_type}_minutes_{task_id}", default_minute)
    current_hour, current_minute = int(current_hour_str), int(current_minute_str)
    
    hour_angle = (current_hour % 12 + current_minute / 60) * 30
    minute_angle = current_minute * 6
    
    text_color, clock_bg, clock_border, clock_hand, clock_marker, clock_center = ('#f0f0f0', '#1a1a1a', '#ccc', '#ccc', '#999', '#ccc') if st.session_state.theme == 'dark' else ('#333', 'white', '#333', '#333', '#666', '#333')
        
    html_code = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                background-color: {container_bg};
                margin: 0;
                padding: 0;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                height: 100vh;
                overflow: hidden;
            }}
            .time-label {{ font-weight: 600; margin-bottom: 8px; color: {text_color}; font-size: 15px; }}
            .clock-container {{ display: inline-block; border-radius: 15px; padding: 15px; background: transparent; margin-bottom: 10px; }}
            .clock-face {{ position: relative; width: 80px; height: 80px; border: 3px solid {clock_border}; border-radius: 50%; background: {clock_bg}; margin: 0 auto; }}
            .clock-hand {{ position: absolute; background: {clock_hand}; transform-origin: bottom center; transition: transform 0.3s ease; }}
            .hour-hand {{ width: 3px; height: 25px; left: 38.5px; top: 15px; }}
            .minute-hand {{ width: 2px; height: 32px; left: 39px; top: 8px; }}
            .clock-center {{ position: absolute; width: 6px; height: 6px; background: {clock_center}; border-radius: 50%; left: 37px; top: 37px; }}
            .clock-marker {{ position: absolute; background: {clock_marker}; }}
            .marker-12 {{ width: 2px; height: 6px; left: 39px; top: 4px; }}
            .marker-3 {{ width: 6px; height: 2px; right: 4px; top: 39px; }}
            .marker-6 {{ width: 2px; height: 6px; left: 39px; bottom: 4px; }}
            .marker-9 {{ width: 6px; height: 2px; left: 4px; top: 39px; }}
        </style>
    </head>
    <body>
        <div id="{clock_id}_container" style="text-align: center;">
            <div class="time-label">{clock_type.title()} Time</div>
            <div class="clock-container">
                <div class="clock-face">
                    <div class="clock-marker marker-12"></div><div class="clock-marker marker-3"></div>
                    <div class="clock-marker marker-6"></div><div class="clock-marker marker-9"></div>
                    <div class="clock-hand hour-hand" style="transform: rotate({hour_angle}deg);"></div>
                    <div class="clock-hand minute-hand" style="transform: rotate({minute_angle}deg);"></div>
                    <div class="clock-center"></div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html_code

def create_task_with_dynamic_clocks(task_id, bg_color, text_color):
    """Creates a full task row including all input fields and clocks."""
    with st.container():
        cols = st.columns([0.6, 1.5, 0.5, 1.8, 0.5, 1.8, 0.5])
        with cols[0]:
            st.markdown(f"<div style='margin-top: 100px; font-size: 18px; font-weight: bold; color: {text_color};'>Task {task_id}</div>", unsafe_allow_html=True)
        with cols[1]:
            st.markdown("<div style='margin-top: 92px;'></div>", unsafe_allow_html=True)
            st.text_input("Task Name", key=f"task_desc_{task_id}", placeholder="Enter task")
        with cols[3]:
            components.html(create_dynamic_clock_with_input(task_id, "start", bg_color), height=150)
            time_cols = st.columns([1, 0.05, 1])
            with time_cols[0]: st.text_input("Start Hour", value=st.session_state.get(f"start_hours_{task_id}", "09"), key=f"start_hours_{task_id}", max_chars=2, label_visibility="collapsed", on_change=validate_time, args=(task_id, "start", "hours"), help=" ")
            with time_cols[1]: st.markdown(f"<div style='margin-top: 5px; font-size: 20px; font-weight: bold; color: {text_color};'>:</div>", unsafe_allow_html=True)
            with time_cols[2]: st.text_input("Start Minute", value=st.session_state.get(f"start_minutes_{task_id}", "00"), key=f"start_minutes_{task_id}", max_chars=2, label_visibility="collapsed", on_change=validate_time, args=(task_id, "start", "minutes"), help=" ")
        with cols[5]:
            components.html(create_dynamic_clock_with_input(task_id, "end", bg_color), height=150)
            time_cols = st.columns([1, 0.05, 1])
            with time_cols[0]: st.text_input("End Hour", value=st.session_state.get(f"end_hours_{task_id}", "09"), key=f"end_hours_{task_id}", max_chars=2, label_visibility="collapsed", on_change=validate_time, args=(task_id, "end", "hours"), help=" ")
            with time_cols[1]: st.markdown(f"<div style='margin-top: 5px; font-size: 20px; font-weight: bold; color: {text_color};'>:</div>", unsafe_allow_html=True)
            with time_cols[2]: st.text_input("End Minute", value=st.session_state.get(f"end_minutes_{task_id}", "01"), key=f"end_minutes_{task_id}", max_chars=2, label_visibility="collapsed", on_change=validate_time, args=(task_id, "end", "minutes"), help=" ")
        with cols[6]:
            st.markdown("<div style='margin-top: 100px;'></div>", unsafe_allow_html=True)
            if st.button("❌", key=f"remove_{task_id}", help=f"Remove Task {task_id}"):
                remove_task(task_id)
                st.rerun()

# --- Data Calculation and Formatting ---

def calculate_total_time(start_hours, start_minutes, end_hours, end_minutes):
    """Calculates the duration between a start and end time."""
    try:
        start_time = timedelta(hours=int(start_hours), minutes=int(start_minutes))
        end_time = timedelta(hours=int(end_hours), minutes=int(end_minutes))
        if end_time < start_time: end_time += timedelta(days=1)
        duration = end_time - start_time
        total_minutes = duration.total_seconds() // 60
        return int(total_minutes // 60), int(total_minutes % 60)
    except (ValueError, TypeError): return 0, 0

def format_duration(hours, minutes):
    """Formats duration into a readable string."""
    if hours == 0: return f"{minutes} min"
    if minutes == 0: return f"{hours} hr"
    return f"{hours} hr, {minutes} min"

def calculate_total_duration():
    """Calculates the sum of all task durations."""
    total_minutes = 0
    for task in st.session_state.tasks:
        task_id = task["task_id"]
        start_h = st.session_state.get(f"start_hours_{task_id}", "0")
        start_m = st.session_state.get(f"start_minutes_{task_id}", "0")
        end_h = st.session_state.get(f"end_hours_{task_id}", "0")
        end_m = st.session_state.get(f"end_minutes_{task_id}", "0")
        h, m = calculate_total_time(start_h, start_m, end_h, end_m)
        total_minutes += h * 60 + m
    total_hours = total_minutes // 60
    remaining_minutes = total_minutes % 60
    return format_duration(total_hours, remaining_minutes)

def prepare_data_for_download():
    """Prepares the task data into a Pandas DataFrame."""
    data = []
    for task in st.session_state.tasks:
        task_id = task["task_id"]
        task_desc = st.session_state.get(f"task_desc_{task_id}", "")
        start_h = st.session_state.get(f"start_hours_{task_id}", "09")
        start_m = st.session_state.get(f"start_minutes_{task_id}", "00")
        end_h = st.session_state.get(f"end_hours_{task_id}", "09")
        end_m = st.session_state.get(f"end_minutes_{task_id}", "01")
        hours, minutes = calculate_total_time(start_h, start_m, end_h, end_m)
        data.append({
            "Task Name": task_desc, "Start Time": f"{start_h}:{start_m}", "End Time": f"{end_h}:{end_m}",
            "Duration": format_duration(hours, minutes)
        })
    return pd.DataFrame(data)

def download_excel(df):
    """Converts a DataFrame to an Excel file in memory."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Tasks')
    return output.getvalue()

# --- Main App Execution ---

def main():
    """Main function to run the Streamlit app."""
    st.set_page_config(layout="wide", page_icon='📅', page_title='My Schedule Tool')

    # --- Notification Handler ---
    if "notification" in st.session_state and st.session_state.notification:
        st.toast(st.session_state.notification)
        st.session_state.notification = None 

    # Define theme-based colors
    is_dark = st.session_state.theme == 'dark'
    bg_color = '#0E1117' if is_dark else '#FFFFFF'
    text_color = '#FAFAFA' if is_dark else '#31333F'
    input_bg = '#262730' if is_dark else '#F0F2F6'
    placeholder_color = '#707070' if is_dark else '#A0A0A0'

    st.markdown(f"""
        <style>
            .stApp {{ background-color: {bg_color}; color: {text_color}; }}
            .stTextInput > div > div > input {{ text-align: center; font-weight: bold; font-size: 18px; padding: 8px; border: none; border-radius: 8px; background: {input_bg}; color: {text_color}; }}
            .stTextInput > div > div > input::placeholder {{ color: {placeholder_color}; opacity: 1; }}
            .stTextInput > label {{ color: {text_color} !important; font-weight: bold !important; font-size: 1.1rem; }}
            iframe {{ border: none !important; }}
            .stDataFrame th {{ background-color: {input_bg} !important; color: {text_color} !important; }}
        </style>
    """, unsafe_allow_html=True)

    header_cols = st.columns([5, 1])
    with header_cols[0]:
        st.markdown(f'<h1 style="font-size:35px;text-align:center;color:{text_color}">My Schedule Tool</h1>', unsafe_allow_html=True)
    with header_cols[1]:
        if st.button("🌙" if not is_dark else "☀️", help="Toggle dark/light mode"): toggle_theme()
    
    st.markdown('<br>'*3, unsafe_allow_html=True)

    if "row_count" not in st.session_state:
        st.session_state.row_count = 1
        st.session_state.tasks = [{"task_id": 1}]
        st.session_state["start_hours_1"], st.session_state["start_minutes_1"] = "09", "00"
        st.session_state["end_hours_1"], st.session_state["end_minutes_1"] = "09", "01"

    for task in list(st.session_state.tasks):
        create_task_with_dynamic_clocks(task["task_id"], bg_color, text_color)
        st.markdown('<br>'*2, unsafe_allow_html=True)

    if st.button("Add New Task", type="primary"):
        add_new_task()
        st.rerun()
    
    st.markdown('<br>'*2, unsafe_allow_html=True)
    
    total_duration = calculate_total_duration()
    st.markdown(f"<h3 style='color: {text_color};'><b>Total Duration: {total_duration}</b></h3>", unsafe_allow_html=True)
    
    df = prepare_data_for_download()
    df.index += 1
    
    st.markdown(f"<h4 style='color: {text_color};'>Sheet Preview</h4>", unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True)
    
    st.download_button(
        label="📥 Download Schedule Sheet", 
        data=download_excel(df),
        file_name=f"Schedule_{datetime.now().strftime('%B_%d_%Y')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary",
        # --- ADDED NOTIFICATION ---
        # This will show a pop-up toast when the button is clicked.
        on_click=lambda: st.toast("✅ Schedule sheet downloaded!")
    )

    st.markdown(f"<div style='text-align: center; margin-top: 50px;'><h4 style='font-size: 22px; color: {text_color};'>🚀 Made with ❤️ by: <b>Omar Shaarawy</b> | Version 2.0.0</h4></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()