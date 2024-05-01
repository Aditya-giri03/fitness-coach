# import av
# import os
# import sys
# import streamlit as st
# from streamlit_webrtc import VideoHTMLAttributes, webrtc_streamer
# from aiortc.contrib.media import MediaRecorder
# import datetime


# BASE_DIR = os.path.abspath(os.path.join(__file__, '../../'))
# sys.path.append(BASE_DIR)


# from utils import get_mediapipe_pose
# from process_frame import ProcessFrame
# from curls import ProcessFrameCurls
# from thresholds import get_thresholds_beginner, get_thresholds_pro, get_thresholds_curls


# session_info={
# 'started' :False,
# 'start_timestamp':0,
# 'end_timestamp':0,
# 'correct':0,
# 'incorrect':0,
# 'exercise_selected':""
# }

# DATASET={"Curls":{},"Squats Beginner":{},"Squats Pro":{}}
# dataset=[{},{},{}]


# # print("Live camera started... \n\n\n\n")

# st.title('AI Fitness Trainer: Squats Analysis')

# mode = st.radio('Select Mode', ['Squats Beginner', 'Squats Pro', 'Curls'], horizontal=True)

# thresholds = None 
# live_process_frame = None

# if mode == 'Squats Beginner':
#     session_info['exercise_selected']="Squats Beginner"
#     thresholds = get_thresholds_beginner()
#     live_process_frame = ProcessFrame(thresholds=thresholds, flip_frame=True)

# elif mode == 'Squats Pro':
#     session_info['exercise_selected']="Squats Pro"
#     thresholds = get_thresholds_pro()
#     live_process_frame = ProcessFrame(thresholds=thresholds, flip_frame=True)

# elif mode == 'Curls':
#     session_info['exercise_selected']="Curls"
#     thresholds = get_thresholds_curls()
#     live_process_frame = ProcessFrameCurls(thresholds=thresholds, flip_frame=True)

# # Initialize face mesh solution
# pose = get_mediapipe_pose()


# if 'download' not in st.session_state:
#     st.session_state['download'] = False

# output_video_file = f'output_live.flv'

  

# def video_frame_callback(frame: av.VideoFrame):
#     global DATASET 
#     frame = frame.to_ndarray(format="rgb24")  # Decode and get RGB frame
#     frame, play_sound, states = live_process_frame.process(frame, pose)  # Process frame
#     print(states)
#     if (len(states)==2):
#         if(not session_info["started"]):
#             session_info["started"] = True
#             session_info["start_timestamp"] = datetime.datetime.now()
#             session_info["end_timestamp"] = datetime.datetime.now()
#         else:
#             session_info["end_timestamp"]= datetime.datetime.now()
#         session_info['correct'] = states[0]
#         session_info['incorrect'] = states[1]
#         DATASET[session_info['exercise_selected']] = session_info
#         # if(session_info['exercise_selected']=="Curls"):
#         #     dataset[0]=session_info
#         # elif(session_info['exercise_selected']=="Squats Pro"):
#         #     dataset[1]=session_info
#         # else:
#         #     dataset[2]=session_info
#     print(DATASET)

#     return av.VideoFrame.from_ndarray(frame, format="rgb24")  # Encode and return BGR frame


# def out_recorder_factory() -> MediaRecorder:
#         return MediaRecorder(output_video_file)



# ctx = webrtc_streamer(
#                         key="Squats-pose-analysis",
#                         video_frame_callback=video_frame_callback,
#                         rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},  # Add this config
#                         media_stream_constraints={"video": {"width": {'min':480, 'ideal':480}}, "audio": False},
#                         video_html_attrs=VideoHTMLAttributes(autoPlay=True, controls=False, muted=False),
#                         out_recorder_factory=out_recorder_factory
#                     )

# print(DATASET)
# download_button = st.empty()

# if os.path.exists(output_video_file):
#     with open(output_video_file, 'rb') as op_vid:
#         download = download_button.download_button('Download Video', data = op_vid, file_name='output_live.flv')

#         if download:
#             st.session_state['download'] = True



# if os.path.exists(output_video_file) and st.session_state['download']:
#     os.remove(output_video_file)
#     st.session_state['download'] = False
#     download_button.empty()

# print("end")
# print(dataset)
    
# if(st.session_state["download"]):
#     print("presses stop")






import av
import os
import sys
import streamlit as st
from streamlit_webrtc import VideoHTMLAttributes, webrtc_streamer
from aiortc.contrib.media import MediaRecorder
import datetime
import queue
import threading

BASE_DIR = os.path.abspath(os.path.join(__file__, '../../'))
sys.path.append(BASE_DIR)

from utils import get_mediapipe_pose
from process_frame import ProcessFrame
from curls import ProcessFrameCurls
from thresholds import get_thresholds_beginner, get_thresholds_pro, get_thresholds_curls

session_info={
'started' :False,
'start_timestamp':0,
'end_timestamp':0,
'correct':0,
'incorrect':0,
'exercise_selected':""
}
DATASET={"Curls":{},"Squats Beginner":{},"Squats Pro":{}}
# last_data = {}

# Initialize a global queue for data sharing
data_queue = queue.Queue()
# second_queue = queue.Queue()

# prev_data = {}
# Function to continuously process data from the queue
def process_data_from_queue():
    prev_data=[]
    while True:
        if(data_queue.qsize() > 2):
            data = data_queue.get()
            # prev_data.append(data)
            # print(len(prev_data))

            if data == "STOP":
                # print("ended -> ",prev_data)
                break
            # if data == "APPEND":
                # print("ended -> ",prev_data)
                
                
            # Process the data as needed
            
            print(data)
            print('Q Size: ',data_queue.qsize())
        # if(data != "APPEND"):
            
            # prev_data = data.copy()
        
        # last_data = data.copy()

        


# Start the data processing thread
data_processing_thread = threading.Thread(target=process_data_from_queue)
data_processing_thread.start()

st.title('AI Fitness Trainer: Squats Analysis')

mode = st.radio('Select Mode', ['Squats Beginner', 'Squats Pro', 'Curls'], horizontal=True)

thresholds = None 
live_process_frame = None

if mode == 'Squats Beginner':
    session_info['exercise_selected']="Squats Beginner"
    thresholds = get_thresholds_beginner()
    live_process_frame = ProcessFrame(thresholds=thresholds, flip_frame=True)

elif mode == 'Squats Pro':
    session_info['exercise_selected']="Squats Pro"
    thresholds = get_thresholds_pro()
    live_process_frame = ProcessFrame(thresholds=thresholds, flip_frame=True)

elif mode == 'Curls':
    session_info['exercise_selected']="Curls"
    thresholds = get_thresholds_curls()
    live_process_frame = ProcessFrameCurls(thresholds=thresholds, flip_frame=True)

pose = get_mediapipe_pose()

if 'download' not in st.session_state:
    st.session_state['download'] = False


output_video_file = f'output_live.flv'

def video_frame_callback(frame: av.VideoFrame):
    global DATASET , session_info
    frame = frame.to_ndarray(format="rgb24")
    frame, play_sound, states = live_process_frame.process(frame, pose)
    if (len(states)==2):
        if(not session_info["started"]):
            session_info["started"] = True
            session_info["start_timestamp"] = datetime.datetime.now()
            session_info["end_timestamp"] = datetime.datetime.now()
        else:
            session_info["end_timestamp"]= datetime.datetime.now()
        session_info['correct'] = states[0]
        session_info['incorrect'] = states[1]
        DATASET[session_info['exercise_selected']]= session_info
        data_queue.put(DATASET)
        # second_queue.put()
        DATASET=DATASET.copy()
        session_info = session_info.copy()  # Make a copy to avoid race conditions
    return av.VideoFrame.from_ndarray(frame, format="rgb24")

def out_recorder_factory() -> MediaRecorder:
    return MediaRecorder(output_video_file)

ctx = webrtc_streamer(
    key="Squats-pose-analysis",
    video_frame_callback=video_frame_callback,
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    media_stream_constraints={"video": {"width": {'min':480, 'ideal':480}}, "audio": False},
    video_html_attrs=VideoHTMLAttributes(autoPlay=True, controls=False, muted=False),
    out_recorder_factory=out_recorder_factory
)

download_button = st.empty()

if os.path.exists(output_video_file):
    with open(output_video_file, 'rb') as op_vid:
        download = download_button.download_button('Download Video', data = op_vid, file_name='output_live.flv')

        if download:
            st.session_state['download'] = True

if os.path.exists(output_video_file) and st.session_state['download']:
    os.remove(output_video_file)
    st.session_state['download'] = False
    download_button.empty()

# Stop the data processing thread when download is initiated
if st.session_state["download"]:
    data_queue.put("STOP")
    data_processing_thread.join()  # Wait for the thread to finish

# if(data_queue.qsize() > 0):
#     print("end--> ", data_queue.get())
# else:
#     print("queue is empty")

# print('printing last directly: ',data_queue.get())
# data_queue.put("APPEND")


