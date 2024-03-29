import os
import boto3
from natsort import natsorted, ns
import Recog_app_AWS_call as aws_call
#from aws_call import s3_get_keras_model
from keras.models import model_from_json
from skimage import io
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing import image
from tempfile import NamedTemporaryFile
import requests
import json 
import pickle
import streamlit as st
import datetime as dt

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import toxicity as toxic


from PIL import Image
from dotenv import load_dotenv
from urllib.error import URLError
import collections
import io
import math
import os
import random
from six.moves import urllib
from collections import defaultdict
from sklearn.preprocessing import LabelEncoder
from IPython.display import clear_output, Image, display, HTML

import pathlib

from pathlib import Path


import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sklearn.metrics as sk_metrics
import time
#from pathlib import Path

from natsort import natsorted, ns
from skimage import io
import pandas as pd
from sklearn.model_selection import train_test_split

from tensorflow.keras.preprocessing import image
import numpy as np
import gzip

#import rembg
#from rembg.bg import remove
import numpy as np
import io
from PIL import Image

import tensorflow as tf
from tensorflow import keras

from keras import Model, layers
#import tensorflow_datasets as tfds
from tensorflow.keras.utils import to_categorical as one_hot


from io import BytesIO

import remove_image_bacground  as remove
from st_files_connection import FilesConnection
# from fsspec.implementations.local import available_protocols

from keras import backend as K
from tensorflow.compat.v1.keras.backend import set_session
from tensorflow.compat.v1.keras.backend import get_session

st.write("Streamlit version:", st.__version__)


@st.cache_resource
def load_model():
    
    
    
    load_dotenv() # load my enviornment variables


    AWS_ACCESS_KEY=os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_KEY=os.getenv('AWS_SECRET_ACCESS_KEY')



    BUCKET_NAME="streamlit-pet-lab"


    loaded_model=aws_call.s3_get_keras_model("5_flowers_trial")

    # evaluate loaded model on test data
    loaded_model.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=['accuracy'])
    
    loaded_model.make_predict_function()
    #model.summary()  # included to make it visible when model is reloaded
    session = get_session()
    return loaded_model, session






#Reformat Image
def decode_and_resize_image(encoded):
    decoded = tf.keras.preprocessing.image.img_to_array(encoded)
    decoded = tf.image.convert_image_dtype(decoded, tf.float32)
    return tf.image.resize(decoded, [299, 299], method='bilinear')





def img2np( filename):


   # current_image =tf.keras.utils.load_img(filename)
   # img_byte_arr = io.BytesIO()
    #current_image.save(img_byte_arr, format='PNG')
    #img_byte_arr = img_byte_arr.getvalue()
    
    results = remove.remove(filename) # removing backgroung?
    #img = Image.open(io.BytesIO(results)).convert("RGB")

    
    results = remove.remove(filename) # removing backgroung
    

    
    # covert image to a matrix
    decoded_img=decode_and_resize_image(results)
    Im_correct_dimensions=np.expand_dims(decoded_img, axis=0)


    return Im_correct_dimensions



#run feature code

if __name__ == '__main__':
    st.title('Pet-Lab: Keep your pets safe! Upload a picture and obtain a flowers toxicity information with the click of a button.')

    #upload user Image

    #st.sidebar.header("Image Classification")

#    st.set_option('deprecation.showfileUploaderEncoding', False)
    
    fileUpload = st.file_uploader("Choose a file (jpg or png only)", accept_multiple_files=False,type = ['jpg', 'png','JFIF'])



    temp_file = NamedTemporaryFile(delete=False)
    st.write('Loading Model...')
    model, session = load_model()
    #, session


    if fileUpload is not None:
        set_session(session)
        #st.write('hi')
        image1 = fileUpload
        st.image(image1, caption='Uploaded Image.', width=None)
        st.write("")

        temp_file.write(fileUpload.getvalue())

    
        Image_upload=img2np(temp_file.name)
        
        st.write("Image has been resized, re-scaled and background subtracted")
       # st.image(Image_upload, caption='pre-processed image', width=None)


        validation_datagen = tf.keras.preprocessing.image.ImageDataGenerator(rescale = 1.0/255)

        validation_generator = validation_datagen.flow(Image_upload)

        Image_preprocessed=validation_generator.next()

        #st.image(Image_preprocessed, caption='pre-processed image', width=None)

        #st.write(upload_feature_dataframe)
        st.title("Classifying...")



        Classes=sorted(['daisy','dandelion','rose','sunflower','tulip'])

        
        
        Predictions=model.predict(Image_preprocessed)




        Classification=pd.DataFrame(Predictions,columns= [f'{el}' for el in Classes])


          
        Probabilities=[Classification['daisy'][0],Classification['dandelion'][0],Classification['rose'][0],Classification['sunflower'][0],Classification['tulip'][0]]
        
        user_input = st.number_input('Threshold % probablity for which to output flower type', min_value=0, max_value=100, value=1)

        st.write('A list of all flowers that match the input image with a probablity % higher than the threshold are given below')

#st.write(Classification)
        Flowers_to_Scrape=[]
        for i in range(0,len(Probabilities)):

            
            if Probabilities[i]>user_input/100:
                Flowers_to_Scrape.append(Classes[i])
                st.write(f'A {round(Probabilities[i]*100,2)} % probability of the flower being a {Classes[i]}')



# Pull Rover info! if prob > (threshold/100)


    #pull rover info
    
    
        st.title("Toxicity Information")

        st.write()

        pd.set_option('display.max_colwidth', 0)

        Toxic_info=toxic.Get_Output(toxic.Search_flower_url_name(Flowers_to_Scrape))


        st.write('Information for any flower containing the identified flower(s) name')



        if not Toxic_info['Toxicity'].empty:
            Toxic_info.style.set_properties(subset=['Toxicity'], **{'width': '1000px'})
            Toxic_info.style.set_properties(subset=['URL'], **{'width': '200px'})


            st.dataframe(Toxic_info)

            Toxic_info2=toxic.Get_Output(toxic.Search_flower_url_name(Flowers_to_Scrape,total_equality=True))

            st.write('Information for identified flower(s)')


            st.dataframe(Toxic_info2)

        else:

            Toxic_info='Flower not found in Poisonous Database, furthur research from user is recommended'
            st.write(Toxic_info)




with st.expander("Awknowledgements"):
    st.title("Made by Freida L. Rivera Garriga, MS")
    st.title("TDI-Capstone")
    st.write('Github Pages', 'https://flrivera.github.io/Pet-Lab/')
    st.write('Github Projet Repo', 'https://github.com/flrivera/Pet-Lab')
    st.write('The images used to train the models were background subtracted')
    st.write('The python package used for background subtraction can be found at: https://pypi.org/project/rembg/')
    st.write('Images were obtained from: https://www.kaggle.com/alxmamaev/flowers-recognition')
    st.write('Updated: 12/1/2023')




