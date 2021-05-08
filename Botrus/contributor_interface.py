import numpy as np
import pandas as pd
import tkinter as tk  
from datetime import datetime
from tkinter import filedialog  
from PIL import Image
import os
import threading
import streamlit as st
import psutil
import time


def cpu_percent():
    cpu_use = pd.DataFrame([[]])
    cpu_use = cpu_use.drop(labels=0, axis=0)
    st.write('CPU')
    cpu_chart = st.area_chart(cpu_use, height = 100)
    vm = pd.DataFrame([[]])
    vm = vm.drop(labels=0, axis=0)
    st.write('Memory')
    vm_chart = st.area_chart(vm, height = 100)
    while(1):
        cpu_percent = psutil.cpu_percent()
        tmp = [[cpu_percent]]
        #cpu_use = cpu_use.append(tmp, ignore_index=True)
        cpu_chart.add_rows(tmp)
        virtual_memory = psutil.virtual_memory()
        tmp = [[100*float(virtual_memory.available/virtual_memory.total)]]
        #cpu_use = cpu_use.append(tmp, ignore_index=True)
        vm_chart.add_rows(tmp)
        time.sleep(1)
        

def virtual_memory():
    vm = pd.DataFrame([[]])
    vm = vm.drop(labels=0, axis=0)
    vm_chart = st.area_chart(vm)
    while(1):
        virtual_memory = psutil.virtual_memory()
        tmp = [[100*float(virtual_memory.available/virtual_memory.total)]]
        #cpu_use = cpu_use.append(tmp, ignore_index=True)
        vm_chart.add_rows(tmp)
        time.sleep(1)

st.title("Botrus contrubuting")
image = Image.open('grape.jpg')

st.image(image, caption='Using peer to peer technology to train large models',width=100) 

inUse = st.checkbox("I'm available")

if inUse:
    # gives a single float value
    threading.Thread(target=cpu_percent()).start()
    #threading.Thread(target=virtual_memory()).start()
    

    
        

    # gives an object with many fields
    #threading.Thread(target=virtual_memory).start()





