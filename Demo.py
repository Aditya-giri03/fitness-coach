import streamlit as st


st.title('AI Fitness Trainer: Squats Analysis')


recorded_file = "./sample_vid.mp4"
sample_vid = st.empty()
sample_vid.video(recorded_file)


