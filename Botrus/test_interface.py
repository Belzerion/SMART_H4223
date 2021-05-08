import streamlit as st
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
import numpy as np
import pandas as pd
import tkinter as tk  
from tkinter import filedialog  
from PIL import Image
import os

image = Image.open('grape.jpg')

st.title('Botrus')
st.image(image, caption='Using peer to peer technology to train large models',width=100) 


option = 'Pool 0'

table = pd.DataFrame({
    'Pools': ['Pool 1','Pool 2','Pool 3','Pool 4'],
    'Active nodes': [10, 20, 30, 40],
})
st.sidebar.write(table)
option = st.sidebar.selectbox(
    'Choose the pool you want to work with',
     table['Pools'])

st.header('Authentication :')

password = st.text_input("Pool password", "")

st.header('Slaves selection :')


peers = pd.DataFrame({
  'workers': ['Worker 1','Worker 2','Worker 3','Worker 4'],
  'nicknames':['Alice','Bob','Charlie','Diana']
})
st.write(peers)
workers_selected = st.multiselect('Which workers do you want to exploit?', peers['nicknames'])

if workers_selected != []:

    st.header('Cluster Creation')

    bar = st.progress(0)
    array = [0.0]

    if st.button('Create cluster'):   
        bar.progress(100) 
        st.write("Cluster created !")