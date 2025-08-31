# Import libraries
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
    st.session_state.tasks.append({"task_id": st.session_state.row_count})
    trigger_notification("New task added!")

def remove_task(task_id):
    st.session_state.tasks = [
        {"task_id": i + 1} for i, task in enumerate(
            task for task in st.session_state.tasks if task["task_id"] != task_id
        )
    ]
    st.session_state.row_count = len(st.session_state.tasks)
    trigger_notification(f"Task {task_id} removed!")

def create_task(task_id):

    cols = st.columns(5)
    with cols[0]:
        st.markdown(f"<h1 style='font-size:20px;'>Task &nbsp;{task_id}</h1>", unsafe_allow_html=True)

    with cols[1]:
        st.text_input(
            "Task Name", 
            key=f"task_desc_{task_id}",
            placeholder=""
        )

    with cols[2]:
        st.selectbox("Start Hours", range(9,25), key=f"start_hours_{task_id}")
        st.selectbox("Start Minutes", [f"{i:02d}" for i in range(60)], key=f"start_minutes_{task_id}")

    with cols[3]:
        st.selectbox("End Hours", range(9,25), key=f"end_hours_{task_id}")
        st.selectbox("End Minutes", [f"{i:02d}" for i in range(60)], key=f"end_minutes_{task_id}")


    with cols[4]:
        if st.button("❌", key=f"remove_{task_id}"):
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
        return hours, minutes  # Return tuple instead of string
    except:
        return 0, 0  # Return tuple for error case

def calculate_total_duration():
    total_hours = 0
    total_minutes = 0
    
    for task in st.session_state.tasks:
        task_id = task["task_id"]
        
        start_hours = st.session_state.get(f"start_hours_{task_id}", 9)
        start_minutes = st.session_state.get(f"start_minutes_{task_id}", "00")
        end_hours = st.session_state.get(f"end_hours_{task_id}", 10)
        end_minutes = st.session_state.get(f"end_minutes_{task_id}", "00")
        
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
        
        start_hours = st.session_state.get(f"start_hours_{task_id}", 9)
        start_minutes = st.session_state.get(f"start_minutes_{task_id}", "00")
        end_hours = st.session_state.get(f"end_hours_{task_id}", 10)
        end_minutes = st.session_state.get(f"end_minutes_{task_id}", "00")
        
        start_time = f"{start_hours}:{start_minutes}"
        
        # Format end time
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
    st.markdown('<h1 style="font-size:35px;text-align:center">My Schedule Tool</h1>', unsafe_allow_html=True)

    if "row_count" not in st.session_state:
        st.session_state.row_count = 1
        st.session_state.tasks = [{"task_id": 1}]

    for task in st.session_state.tasks:
        create_task(task["task_id"])

    st.button("Add New Task", on_click=add_new_task)

    total_hours, total_minutes, total_duration = calculate_total_duration()
    st.markdown(f"**Total Duration: {total_duration}**")
    df = prepare_data_for_download()

    st.subheader("Sheet Preview")
    st.dataframe(df)
    
    excel_data = download_excel(df)
    st.download_button(
        label="Download Schedule Sheet",
        data=excel_data,
        file_name=f"Schedule_{datetime.now().strftime('%B_%d_%Y')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        on_click=lambda: trigger_notification("Excel sheet downloaded!")
    )
    
    st.markdown(
        """
        <div style='text-align: center; margin-top: 50px;'>
        <a href="https://www.nestle.com/" target="_blank">
            <img src="https://1000logos.net/wp-content/uploads/2017/03/Nestle-Logo.png" alt="Nestlé Logo" width="120" style="margin-bottom: 10px;" />
        </a>    
            <h4 style='font-size: 22px;'>🚀 Made with ❤️ by the <b>Web & Search Team</b> – NBS Cairo</h4>
            <h4 style='font-size: 16px;'>📌 Authority : <a href="mailto:omar.shaarawy@eg.nestle.com"><b>Omar Shaarawy</b></a> | Version 2.0.0</h4>
        </div>
        """,
        unsafe_allow_html=True
    )