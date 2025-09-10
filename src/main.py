import pandas as pd
import streamlit as st
import warnings
from io import BytesIO
from datetime import datetime, timedelta
warnings.filterwarnings('ignore')
import streamlit.components.v1 as components

def trigger_notification(message):
    st.toast(message)  

def add_new_task():
    st.session_state.row_count += 1
    new_id = st.session_state.row_count
    st.session_state.tasks.append({"task_id": new_id})
    if new_id > 1:
        prev_id = new_id - 1
        prev_end_h = int(st.session_state.get(f"end_hours_{prev_id}", "09"))
        prev_end_m = int(st.session_state.get(f"end_minutes_{prev_id}", "01"))
        prev_end_total = prev_end_h * 60 + prev_end_m
        new_start_total = prev_end_total + 1
        new_start_h = (new_start_total // 60) % 24
        new_start_m = new_start_total % 60
        st.session_state[f"start_hours_{new_id}"] = f"{new_start_h:02d}"
        st.session_state[f"start_minutes_{new_id}"] = f"{new_start_m:02d}"
        new_end_total = new_start_total + 1
        new_end_h = (new_end_total // 60) % 24
        new_end_m = new_end_total % 60
        st.session_state[f"end_hours_{new_id}"] = f"{new_end_h:02d}"
        st.session_state[f"end_minutes_{new_id}"] = f"{new_end_m:02d}"
    trigger_notification("New task added!")

def remove_task(task_id):
    st.session_state.tasks = [
        {"task_id": i + 1} for i, task in enumerate(
            task for task in st.session_state.tasks if task["task_id"] != task_id
        )
    ]
    st.session_state.row_count = len(st.session_state.tasks)
    trigger_notification(f"Task {task_id} removed!")

def validate_time(task_id, clock_type, part):
    key = f"{clock_type}_{part}_{task_id}"
    value = st.session_state.get(key, "00")
    try:
        num = int(value)
        if part == "hours":
            num = max(0, min(23, num))
        else:
            num = max(0, min(59, num))
        st.session_state[key] = f"{num:02d}"
    except:
        st.session_state[key] = "00"
    validate_end_time(task_id)

def validate_end_time(task_id):
    if f"start_hours_{task_id}" in st.session_state and f"end_hours_{task_id}" in st.session_state:
        start_h = int(st.session_state.get(f"start_hours_{task_id}", "09"))
        start_m = int(st.session_state.get(f"start_minutes_{task_id}", "00"))
        end_h = int(st.session_state.get(f"end_hours_{task_id}", "09"))
        end_m = int(st.session_state.get(f"end_minutes_{task_id}", "01"))
        
        start_total = start_h * 60 + start_m
        end_total = end_h * 60 + end_m
        
        if end_total < start_total + 1:
            end_total = start_total + 1
            end_h = (end_total // 60) % 24
            end_m = end_total % 60
            st.session_state[f"end_hours_{task_id}"] = f"{end_h:02d}"
            st.session_state[f"end_minutes_{task_id}"] = f"{end_m:02d}"

def create_dynamic_clock_with_input(task_id, clock_type):
    """Create dynamic HTML clock that updates based on session state"""
    clock_id = f"{clock_type}_clock_{task_id}"
    
    # Get current values from session state
    default_hour = "09"
    default_minute = "00" if clock_type == "start" else "01"
    current_hour_str = st.session_state.get(f"{clock_type}_hours_{task_id}", default_hour)
    current_minute_str = st.session_state.get(f"{clock_type}_minutes_{task_id}", default_minute)
    current_hour = int(current_hour_str)
    current_minute = int(current_minute_str)
    
    # Calculate rotation angles for clock hands
    hour_angle = (current_hour % 12) * 30 + (current_minute / 60.0) * 30
    minute_angle = current_minute * 6
    
    html_code = f"""
    <div id="{clock_id}_container" style="text-align: center; margin: 5px 0;">
        <style>
            .time-label {{
                font-weight: 600;
                margin-bottom: 8px;
                color: #333;
                font-size: 15px;
            }}
            .clock-container {{
                display: inline-block;
                border: 2px solid #e0e0e0;
                border-radius: 15px;
                padding: 15px;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                margin-bottom: 10px;
            }}
            .clock-face {{
                position: relative;
                width: 80px;
                height: 80px;
                border: 3px solid #333;
                border-radius: 50%;
                background: white;
                margin: 0 auto;
            }}
            .clock-hand {{
                position: absolute;
                background: #333;
                transform-origin: bottom center;
                transition: transform 0.3s ease;
            }}
            .hour-hand {{
                width: 3px;
                height: 25px;
                left: 38.5px;
                top: 15px;
            }}
            .minute-hand {{
                width: 2px;
                height: 32px;
                left: 39px;
                top: 8px;
            }}
            .clock-center {{
                position: absolute;
                width: 6px;
                height: 6px;
                background: #333;
                border-radius: 50%;
                left: 37px;
                top: 37px;
            }}
            .clock-marker {{
                position: absolute;
                background: #666;
            }}
            .marker-12 {{
                width: 2px;
                height: 6px;
                left: 39px;
                top: 4px;
            }}
            .marker-3 {{
                width: 6px;
                height: 2px;
                right: 4px;
                top: 39px;
            }}
            .marker-6 {{
                width: 2px;
                height: 6px;
                left: 39px;
                bottom: 4px;
            }}
            .marker-9 {{
                width: 6px;
                height: 2px;
                left: 4px;
                top: 39px;
            }}
            @media (prefers-color-scheme: dark) {{
                .time-label {{
                    color: #f0f0f0;
                }}
                .clock-container {{
                    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                    border-color: #555;
                }}
                .clock-face {{
                    background: #1a1a1a;
                    border-color: #ccc;
                }}
                .clock-hand {{
                    background: #ccc;
                }}
                .clock-center {{
                    background: #ccc;
                }}
                .clock-marker {{
                    background: #999;
                }}
            }}
        </style>
        
        <div class="time-label">
            {clock_type.title()} Time
        </div>
        
        <div class="clock-container">
            <div class="clock-face">
                <div class="clock-marker marker-12"></div>
                <div class="clock-marker marker-3"></div>
                <div class="clock-marker marker-6"></div>
                <div class="clock-marker marker-9"></div>
                <div class="clock-hand hour-hand" style="transform: rotate({hour_angle}deg);"></div>
                <div class="clock-hand minute-hand" style="transform: rotate({minute_angle}deg);"></div>
                <div class="clock-center"></div>
            </div>
        </div>
    </div>
    """
    return html_code

def create_task_with_dynamic_clocks(task_id):
    """Create task row with dynamic HTML clocks and aligned fields"""
    
    # Main container
    container = st.container()
    with container:
        # Create columns with adjusted ratios
        cols = st.columns([0.6, 1.5,0.5, 1.8,0.5, 1.8, 0.5])
        
        with cols[0]:
            st.markdown(f"""
                <div style='margin-top: 100px; font-size: 18px; font-weight: bold;'>
                    Task {task_id}
                </div>
            """, unsafe_allow_html=True)
        
        with cols[1]:
            # Add spacing to align with time inputs
            st.markdown("<div style='margin-top: 92px;'></div>", unsafe_allow_html=True)
            task_desc = st.text_input(
                "Task Name",
                key=f"task_desc_{task_id}",
                placeholder="Enter task",
             )  

        
        with cols[3]:
            # Start time with dynamic clock
            start_time_html = create_dynamic_clock_with_input(task_id, "start")
            components.html(start_time_html, height=150)
            
            # Time inputs
            time_cols = st.columns([1, 0.05, 1])
            default_start_h = "09"
            default_start_m = "00"
            with time_cols[0]:
                st.text_input(
                    "",
                    value=st.session_state.get(f"start_hours_{task_id}", default_start_h),
                    key=f"start_hours_{task_id}",
                    max_chars=2,
                    label_visibility="collapsed",
                    on_change=validate_time,
                    args=(task_id, "start", "hours",)
                )
            with time_cols[1]:
                st.markdown("<div style='margin-top: 5px; font-size: 20px; font-weight: bold;'>:</div>", unsafe_allow_html=True)
            with time_cols[2]:
                st.text_input(
                    "",
                    value=st.session_state.get(f"start_minutes_{task_id}", default_start_m),
                    key=f"start_minutes_{task_id}",
                    max_chars=2,
                    label_visibility="collapsed",
                    on_change=validate_time,
                    args=(task_id, "start", "minutes",)
                )
        
        with cols[5]:
            # End time with dynamic clock
            end_time_html = create_dynamic_clock_with_input(task_id, "end")
            components.html(end_time_html, height=150)
            
            # Time inputs
            time_cols = st.columns([1, 0.05, 1])
            default_end_h = "09"
            default_end_m = "01"
            with time_cols[0]:
                st.text_input(
                    "",
                    value=st.session_state.get(f"end_hours_{task_id}", default_end_h),
                    key=f"end_hours_{task_id}",
                    max_chars=2,
                    label_visibility="collapsed",
                    on_change=validate_time,
                    args=(task_id, "end", "hours",)
                )
            with time_cols[1]:
                st.markdown("<div style='margin-top: 5px; font-size: 20px; font-weight: bold;'>:</div>", unsafe_allow_html=True)
            with time_cols[2]:
                st.text_input(
                    "",
                    value=st.session_state.get(f"end_minutes_{task_id}", default_end_m),
                    key=f"end_minutes_{task_id}",
                    max_chars=2,
                    label_visibility="collapsed",
                    on_change=validate_time,
                    args=(task_id, "end", "minutes",)
                )
        
        with cols[6]:
            st.markdown("<div style='margin-top: 100px;'></div>", unsafe_allow_html=True)
            if st.button("❌", key=f"remove_{task_id}", help=f"Remove Task {task_id}"):
                remove_task(task_id)
                trigger_notification(f"Task {task_id} removed!")
                st.rerun()

def calculate_total_time(start_hours, start_minutes, end_hours, end_minutes):
    try:
        start_time = timedelta(hours=int(start_hours), minutes=int(start_minutes))
        end_time = timedelta(hours=int(end_hours), minutes=int(end_minutes))
        
        if end_time < start_time:
            end_time += timedelta(days=1)
            
        duration = end_time - start_time
        total_minutes = duration.total_seconds() // 60
        hours = int(total_minutes // 60)
        minutes = int(total_minutes % 60)
        return hours, minutes
    except:
        return 0, 0

def calculate_total_duration():
    total_hours = 0
    total_minutes = 0
    
    for task in st.session_state.tasks:
        task_id = task["task_id"]
        
        start_hours = st.session_state.get(f"start_hours_{task_id}", "09")
        start_minutes = st.session_state.get(f"start_minutes_{task_id}", "00")
        end_hours = st.session_state.get(f"end_hours_{task_id}", "09")
        end_minutes = st.session_state.get(f"end_minutes_{task_id}", "01")
        
        hours, minutes = calculate_total_time(start_hours, start_minutes, end_hours, end_minutes)
        
        total_hours += hours
        total_minutes += minutes
    
    # Convert extra minutes to hours
    total_hours += total_minutes // 60
    total_minutes = total_minutes % 60
    
    return total_hours, total_minutes, f"{total_hours} hours, {total_minutes} minutes"    

def prepare_data_for_download():
    data = []
    for task in st.session_state.tasks:
        task_id = task["task_id"]
        
        task_desc = st.session_state.get(f"task_desc_{task_id}", "")
        
        start_hours = st.session_state.get(f"start_hours_{task_id}", "09")
        start_minutes = st.session_state.get(f"start_minutes_{task_id}", "00")
        end_hours = st.session_state.get(f"end_hours_{task_id}", "09")
        end_minutes = st.session_state.get(f"end_minutes_{task_id}", "01")
        
        start_time = f"{start_hours}:{start_minutes}"
        end_time = f"{end_hours}:{end_minutes}"
        
        # Get duration as tuple and format it
        hours, minutes = calculate_total_time(start_hours, start_minutes, end_hours, end_minutes)
        duration = f"{hours} hours, {minutes} minutes"
        
        data.append({
            "Task Name": task_desc,
            "Start Time": start_time,
            "End Time": end_time,
            "Duration": duration
        })
    return pd.DataFrame(data)

def download_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Tasks')
    return output.getvalue()

if __name__ == "__main__":
    st.set_page_config(layout="wide", page_icon='📅', page_title='My Schedule Tool')
    
    # Add custom CSS for better styling including white plus button
    st.markdown("""
        <style>
        .stButton > button {
            margin-top: 0px;
        }
        .stTextInput > div > div > input {
            margin-top: 0px;
            text-align: center;
            font-weight: bold;
            font-size: 18px;
            padding: 8px;
            border: none;
            border-radius: 8px;
            background: white;
        }
        .stTextInput > div > div > input:focus {
            border-color: #4CAF50;
            box-shadow: 0 0 5px rgba(76, 175, 80, 0.3);
        }
        div[data-testid="column"] {
            padding: 0 10px;
        }
        /* Style for Add New Task button to have white plus */
        button[kind="primary"] p {
            color: white !important;
        }
        button[kind="primary"] {
            color: white !important;
        }
        @media (prefers-color-scheme: dark) {
            .stTextInput > div > div > input {
                background: #1a1a1a;
                color: #f0f0f0;
                border-color: #555;
            }
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 style="font-size:35px;text-align:center">My Schedule Tool</h1>', unsafe_allow_html=True)
    st.markdown('<br>',unsafe_allow_html=True)
    st.markdown('<br>',unsafe_allow_html=True)
    st.markdown('<br>',unsafe_allow_html=True)

    if "row_count" not in st.session_state:
        st.session_state.row_count = 1
        st.session_state.tasks = [{"task_id": 1}]
        st.session_state["start_hours_1"] = "09"
        st.session_state["start_minutes_1"] = "00"
        st.session_state["end_hours_1"] = "09"
        st.session_state["end_minutes_1"] = "01"
    
    for task in list(st.session_state.tasks):
        create_task_with_dynamic_clocks(task["task_id"])
        st.markdown('<br>',unsafe_allow_html=True)
        st.markdown('<br>',unsafe_allow_html=True)

    st.button("Add New Task", on_click=add_new_task, type="primary")
    st.markdown('<br>',unsafe_allow_html=True)
    st.markdown('<br>',unsafe_allow_html=True)
    total_hours, total_minutes, total_duration = calculate_total_duration()
    st.markdown(f"### **Total Duration: {total_duration}**")
    
    df = prepare_data_for_download()
    df.index = df.index + 1 

    st.subheader("Sheet Preview")
    st.dataframe(df, use_container_width=True)
    
    excel_data = download_excel(df)
    st.download_button(
        label="📥 Download Schedule Sheet",
        data=excel_data,
        file_name=f"Schedule_{datetime.now().strftime('%B_%d_%Y')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        on_click=lambda: trigger_notification("Excel sheet downloaded!"),
        type="primary"
    )
    
    st.markdown(
        """
        <div style='text-align: center; margin-top: 50px;'>
        <a href="https://www.nestle.com/" target="_blank">
            <img src="https://1000logos.net/wp-content/uploads/2017/03/Nestle-Logo.png" alt="Nestlé Logo" width="120" style="margin-bottom: 10px;" />
        </a>    
            <h4 style='font-size: 22px;'>🚀 Made with ❤️ by the <b>Web & Search Team</b> – NBS Cairo</h4>
            <h4 style='font-size: 16px;'>📌 Authority : <a href="mailto:omar.shaarawy@eg.nestle.com"><b>Omar Shaarawy</b></a> | Version 1.0.0</h4>
        </div>
        """,
        unsafe_allow_html=True
    )