import av
import os
import sys
import streamlit as st
from streamlit_webrtc import VideoHTMLAttributes, webrtc_streamer
from aiortc.contrib.media import MediaRecorder
import datetime
import threading
import numpy as np
from upload import create_conn, read_dictionary_from_npy, upload_file_to_server

BASE_DIR = os.path.abspath(os.path.join(__file__, '../../'))
sys.path.append(BASE_DIR)

from utils import get_mediapipe_pose
from process_frame import ProcessFrame
from curls import ProcessFrameCurls
from thresholds import get_thresholds_beginner, get_thresholds_pro, get_thresholds_curls

session_info = {
    'started': False,
    'start_timestamp': 0,
    'end_timestamp': 0,
    'correct': 0,
    'incorrect': 0,
    'exercise_selected': ""
}

DATASET = {"Curls": {}, "Squats Beginner": {}, "Squats Pro": {}}

cursor, connection = create_conn()

st.title('AI Fitness Trainer: Squats Analysis')

mode = st.radio('Select Mode', ['Squats Beginner', 'Squats Pro', 'Curls'], horizontal=True)

thresholds = None 
live_process_frame = None

if mode == 'Squats Beginner':
    session_info['exercise_selected'] = "Squats Beginner"
    thresholds = get_thresholds_beginner()
    live_process_frame = ProcessFrame(thresholds=thresholds, flip_frame=True)

elif mode == 'Squats Pro':
    session_info['exercise_selected'] = "Squats Pro"
    thresholds = get_thresholds_pro()
    live_process_frame = ProcessFrame(thresholds=thresholds, flip_frame=True)

elif mode == 'Curls':
    session_info['exercise_selected'] = "Curls"
    thresholds = get_thresholds_curls()
    live_process_frame = ProcessFrameCurls(thresholds=thresholds, flip_frame=True)

pose = get_mediapipe_pose()

if 'download' not in st.session_state:
    st.session_state['download'] = False

output_video_file = f'output_live.flv'
dataset_file = f'dataset.npy'

def video_frame_callback(frame: av.VideoFrame):
    global DATASET, session_info
    frame = frame.to_ndarray(format="rgb24")
    frame, play_sound, states = live_process_frame.process(frame, pose)
    if len(states) == 2:
        if not session_info["started"]:
            session_info["started"] = True
            session_info["start_timestamp"] = datetime.datetime.now()
            session_info["end_timestamp"] = datetime.datetime.now()
        else:
            session_info["end_timestamp"] = datetime.datetime.now()
        session_info['correct'] = states[0]
        session_info['incorrect'] = states[1]
        DATASET[session_info['exercise_selected']] = session_info
        session_info = session_info.copy()  # Make a copy to avoid race conditions
        
        # Periodically save the dataset to a file
        # if session_info['exercise_selected'] == 'Curls':
        np.save(dataset_file, DATASET)

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

print("end")

file_path = "dataset.npy"
dictionary = read_dictionary_from_npy(file_path)

upload_file_to_server(dictionary["Curls"], cursor)
upload_file_to_server(dictionary["Squats Beginner"], cursor)
upload_file_to_server(dictionary["Squats Pro"], cursor)








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






# import av
# import os
# import sys
# import streamlit as st
# from streamlit_webrtc import VideoHTMLAttributes, webrtc_streamer
# from aiortc.contrib.media import MediaRecorder
# import datetime
# import queue
# import threading

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


# # Initialize a global queue for data sharing
# data_queue = queue.Queue()
# # data

# # Function to continuously process data from the queue
# def process_data_from_queue():
#     # global data
#     last_data = None

#     while True:
#         data = data_queue.get()

#         if data == "STOP":
#             # print("ended -> ",prev_data)
#             last_data = data
#             return last_data
#             # break

            
#         # Process the data as needed
        
#         print(data)
#         print('Q Size: ',data_queue.qsize())
    
#     return last_data


        


# # Start the data processing thread
# data_processing_thread = threading.Thread(target=process_data_from_queue)
# data_processing_thread.start()

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

# pose = get_mediapipe_pose()

# if 'download' not in st.session_state:
#     st.session_state['download'] = False


# output_video_file = f'output_live.flv'

# def video_frame_callback(frame: av.VideoFrame):
#     global DATASET , session_info
#     frame = frame.to_ndarray(format="rgb24")
#     frame, play_sound, states = live_process_frame.process(frame, pose)
#     if (len(states)==2):
#         if(not session_info["started"]):
#             session_info["started"] = True
#             session_info["start_timestamp"] = datetime.datetime.now()
#             session_info["end_timestamp"] = datetime.datetime.now()
#         else:
#             session_info["end_timestamp"]= datetime.datetime.now()
#         session_info['correct'] = states[0]
#         session_info['incorrect'] = states[1]
#         DATASET[session_info['exercise_selected']]= session_info
#         data_queue.put(DATASET)
#         # second_queue.put()
#         DATASET=DATASET.copy()
#         session_info = session_info.copy()  # Make a copy to avoid race conditions
#     return av.VideoFrame.from_ndarray(frame, format="rgb24")

# def out_recorder_factory() -> MediaRecorder:
#     return MediaRecorder(output_video_file)

# ctx = webrtc_streamer(
#     key="Squats-pose-analysis",
#     video_frame_callback=video_frame_callback,
#     rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
#     media_stream_constraints={"video": {"width": {'min':480, 'ideal':480}}, "audio": False},
#     video_html_attrs=VideoHTMLAttributes(autoPlay=True, controls=False, muted=False),
#     out_recorder_factory=out_recorder_factory
# )

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

# # Stop the data processing thread when download is initiated
# if st.session_state["download"]:
#     data_queue.put("STOP")
#     last_data = data_processing_thread.join()  # Wait for the thread to finish
#     print('Last Data: ', last_data)

# # if(data_queue.qsize() > 0):
# #     print("end--> ", data_queue.get())
# # else:
# #     print("queue is empty")

# print("end")
# # print(data)
# # print('printing last directly: ',data_queue.get())
# # data_queue.put("APPEND")





# import av
# import os
# import sys
# import streamlit as st
# from streamlit_webrtc import VideoHTMLAttributes, webrtc_streamer
# from aiortc.contrib.media import MediaRecorder
# import datetime
# import threading

# BASE_DIR = os.path.abspath(os.path.join(__file__, '../../'))
# sys.path.append(BASE_DIR)

# from utils import get_mediapipe_pose
# from process_frame import ProcessFrame
# from curls import ProcessFrameCurls
# from thresholds import get_thresholds_beginner, get_thresholds_pro, get_thresholds_curls

# session_info = {
#     'started': False,
#     'start_timestamp': 0,
#     'end_timestamp': 0,
#     'correct': 0,
#     'incorrect': 0,
#     'exercise_selected': ""
# }

# DATASET = {"Curls": {}, "Squats Beginner": {}, "Squats Pro": {}}

# # Create a threading lock for accessing the DATASET variable
# dataset_lock = threading.Lock()

# def update_dataset(data):
#     with dataset_lock:
#         DATASET.update(data)

# # Function to process data
# def process_data(frame, live_process_frame, pose, mode, thresholds):
#     global session_info

#     frame = frame.to_ndarray(format="rgb24")
#     frame, play_sound, states = live_process_frame.process(frame, pose)
#     if len(states) == 2:
#         if not session_info["started"]:
#             session_info["started"] = True
#             session_info["start_timestamp"] = datetime.datetime.now()
#             session_info["end_timestamp"] = datetime.datetime.now()
#         else:
#             session_info["end_timestamp"] = datetime.datetime.now()
#         session_info['correct'] = states[0]
#         session_info['incorrect'] = states[1]
#         return session_info

# # Video frame callback function
# def video_frame_callback(frame: av.VideoFrame):
#     global DATASET, session_info

#     mode = st.session_state.get('mode')
#     live_process_frame = st.session_state.get('live_process_frame')
#     pose = st.session_state.get('pose')

#     if not all([mode, live_process_frame, pose]):
#         return

#     data = process_data(frame, live_process_frame, pose, mode, thresholds)
#     update_dataset({data['exercise_selected']: data})

#     return av.VideoFrame.from_ndarray(frame.to_ndarray(format="rgb24"), format="rgb24")

# def out_recorder_factory() -> MediaRecorder:
#     return MediaRecorder('output_live.flv')

# # Initialize face mesh solution
# pose = get_mediapipe_pose()

# st.title('AI Fitness Trainer: Squats Analysis')

# mode = st.radio('Select Mode', ['Squats Beginner', 'Squats Pro', 'Curls'], key='mode', horizontal=True)

# if mode == 'Squats Beginner':
#     session_info['exercise_selected'] = "Squats Beginner"
#     thresholds = get_thresholds_beginner()
#     live_process_frame = ProcessFrame(thresholds=thresholds, flip_frame=True)

# elif mode == 'Squats Pro':
#     session_info['exercise_selected'] = "Squats Pro"
#     thresholds = get_thresholds_pro()
#     live_process_frame = ProcessFrame(thresholds=thresholds, flip_frame=True)

# elif mode == 'Curls':
#     session_info['exercise_selected'] = "Curls"
#     thresholds = get_thresholds_curls()
#     live_process_frame = ProcessFrameCurls(thresholds=thresholds, flip_frame=True)

# st.session_state['mode'] = mode
# st.session_state['live_process_frame'] = live_process_frame
# st.session_state['pose'] = pose

# ctx = webrtc_streamer(
#     key="Squats-pose-analysis",
#     video_frame_callback=video_frame_callback,
#     rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
#     media_stream_constraints={"video": {"width": {'min':480, 'ideal':480}}, "audio": False},
#     video_html_attrs=VideoHTMLAttributes(autoPlay=True, controls=False, muted=False),
#     out_recorder_factory=out_recorder_factory
# )

# download_button = st.empty()

# if os.path.exists('output_live.flv'):
#     with open('output_live.flv', 'rb') as op_vid:
#         download = download_button.download_button('Download Video', data=op_vid, file_name='output_live.flv')

#         if download:
#             st.session_state['download'] = True

# if os.path.exists('output_live.flv') and st.session_state.get('download'):
#     os.remove('output_live.flv')
#     st.session_state['download'] = False
#     download_button.empty()

# print("end")
# print(DATASET)




# import av
# import os
# import sys
# import streamlit as st
# from streamlit_webrtc import VideoHTMLAttributes, webrtc_streamer
# from aiortc.contrib.media import MediaRecorder
# import datetime
# import threading
# import queue

# BASE_DIR = os.path.abspath(os.path.join(__file__, '../../'))
# sys.path.append(BASE_DIR)

# from utils import get_mediapipe_pose
# from process_frame import ProcessFrame
# from curls import ProcessFrameCurls
# from thresholds import get_thresholds_beginner, get_thresholds_pro, get_thresholds_curls

# session_info = {
#     'started': False,
#     'start_timestamp': 0,
#     'end_timestamp': 0,
#     'correct': 0,
#     'incorrect': 0,
#     'exercise_selected': ""
# }

# DATASET = {"Curls": {}, "Squats Beginner": {}, "Squats Pro": {}}

# # Initialize a global queue for data sharing
# data_queue = queue.Queue()

# st.title('AI Fitness Trainer: Squats Analysis')

# mode = st.radio('Select Mode', ['Squats Beginner', 'Squats Pro', 'Curls'], horizontal=True)

# thresholds = None 
# live_process_frame = None

# if mode == 'Squats Beginner':
#     session_info['exercise_selected'] = "Squats Beginner"
#     thresholds = get_thresholds_beginner()
#     live_process_frame = ProcessFrame(thresholds=thresholds, flip_frame=True)

# elif mode == 'Squats Pro':
#     session_info['exercise_selected'] = "Squats Pro"
#     thresholds = get_thresholds_pro()
#     live_process_frame = ProcessFrame(thresholds=thresholds, flip_frame=True)

# elif mode == 'Curls':
#     session_info['exercise_selected'] = "Curls"
#     thresholds = get_thresholds_curls()
#     live_process_frame = ProcessFrameCurls(thresholds=thresholds, flip_frame=True)

# pose = get_mediapipe_pose()

# if 'download' not in st.session_state:
#     st.session_state['download'] = False

# output_video_file = f'output_live.flv'

# def video_frame_callback(frame: av.VideoFrame):
#     global DATASET, session_info
#     frame = frame.to_ndarray(format="rgb24")
#     frame, play_sound, states = live_process_frame.process(frame, pose)
#     if len(states) == 2:
#         if not session_info["started"]:
#             session_info["started"] = True
#             session_info["start_timestamp"] = datetime.datetime.now()
#             session_info["end_timestamp"] = datetime.datetime.now()
#         else:
#             session_info["end_timestamp"] = datetime.datetime.now()
#         session_info['correct'] = states[0]
#         session_info['incorrect'] = states[1]
#         DATASET[session_info['exercise_selected']] = session_info
#         session_info = session_info.copy()  # Make a copy to avoid race conditions
        
#         # Periodically push the dataset to the queue
#         if session_info['exercise_selected'] == 'Curls':
#             data_queue.put(DATASET)

#     return av.VideoFrame.from_ndarray(frame, format="rgb24")

# def out_recorder_factory() -> MediaRecorder:
#     return MediaRecorder(output_video_file)

# ctx = webrtc_streamer(
#     key="Squats-pose-analysis",
#     video_frame_callback=video_frame_callback,
#     rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
#     media_stream_constraints={"video": {"width": {'min':480, 'ideal':480}}, "audio": False},
#     video_html_attrs=VideoHTMLAttributes(autoPlay=True, controls=False, muted=False),
#     out_recorder_factory=out_recorder_factory
# )

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

# # Consume the queue to access the final dataset
# final_dataset = {}
# while not data_queue.empty():
#     final_dataset.update(data_queue.get())

# print(final_dataset)
