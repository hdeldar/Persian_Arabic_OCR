import pandas as pd
import numpy as np
import streamlit as st
import easyocr
import PIL
from PIL import Image, ImageDraw
from captcha.image import ImageCaptcha
import random, string
import utlis


def rectangle(image, result):
    # https://www.blog.pythonlibrary.org/2021/02/23/drawing-shapes-on-images-with-python-and-pillow/
    """ draw rectangles on image based on predicted coordinates"""
    draw = ImageDraw.Draw(image)
    for res in result:
        top_left = tuple(res[0][0]) # top left coordinates as tuple
        bottom_right = tuple(res[0][2]) # bottom right coordinates as tuple
        draw.rectangle((top_left, bottom_right), outline="blue", width=2)
    #display image on streamlit
    st.image(image)





# define the costant
length_captcha = 4
width = 200
height = 150

# define the function for the captcha control
def captcha_control():
    #control if the captcha is correct
    if 'controllo' not in st.session_state or st.session_state['controllo'] == False:
        st.title("Captcha Control on OCR")
        
        # define the session state for control if the captcha is correct
        st.session_state['controllo'] = False
        col1, col2 = st.columns(2)
        
        # define the session state for the captcha text because it doesn't change during refreshes 
        if 'Captcha' not in st.session_state:
                st.session_state['Captcha'] = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length_captcha))
        print("the captcha is: ", st.session_state['Captcha'])
        
        #setup the captcha widget
        image = ImageCaptcha(width=width, height=height)
        data = image.generate(st.session_state['Captcha'])
        col1.image(data)
        capta2_text = col2.text_area('Enter captcha text', height=30)
        
        
        if st.button("Verify the code"):
            print(capta2_text, st.session_state['Captcha'])
            capta2_text = capta2_text.replace(" ", "")
            # if the captcha is correct, the controllo session state is set to True
            if st.session_state['Captcha'].lower() == capta2_text.lower().strip():
                del st.session_state['Captcha']
                col1.empty()
                col2.empty()
                st.session_state['controllo'] = True
                #st.experimental_rerun() 
                st.rerun()
            else:
                # if the captcha is wrong, the controllo session state is set to False and the captcha is regenerated
                st.error("🚨 Error on Captcha...")
                del st.session_state['Captcha']
                del st.session_state['controllo']
                #st.experimental_rerun()
                st.rerun()
        else:
            #wait for the button click
            st.stop()
        
       


# main title
st.title("Get text from image with Persian and Arabic OCR")

# subtitle
st.markdown("## Persian and Arabic OCR :")
#try_again = 0

        
def main():
    # upload image file
    holder = st.empty()
    file = holder.file_uploader(label = "Upload Here", type=['png', 'jpg', 'jpeg'])
    
    # global try_again
    # if try_again == 1: 
    #     del st.session_state['controllo']
    #     st.experimental_rerun()#st.rerun
    # try_again = 1
    #read the csv file and display the dataframe
    if file is not None:
        image = Image.open(file) # read image with PIL library
        st.image(image) #display
        holder.empty()
        
        # it will only detect the English and Turkish part of the image as text
        reader = easyocr.Reader(['fa','ar'], gpu=False) #, model_storage_directory='temp/',user_network_directory='temp/net'
        
        result = reader.readtext(np.array(image))  # turn image to numpy array

        # Add a placeholder
        # latest_iteration = st.empty()
        # bar = st.progress(0)
        
        # for i in range(100):
        # Update the progress bar with each iteration.
        # latest_iteration.text(f'Iteration {i+1}')
        # bar.progress(i + 1)
        # time.sleep(0.1)

        # print all predicted text:
        # for idx in range(len(result)):
        #     pred_text = result[idx][1]
        #     st.write(pred_text)
        extracted_text = utlis.get_raw_text(result)
        #st.write(extracted_text,  use_column_width=True)
        st.markdown('<p style="direction:rtl; text-align: right"> '+extracted_text+' </p>', unsafe_allow_html=True)
        # collect the results in the dictionary:
        textdic_easyocr = {}
        for idx in range(len(result)):
            pred_coor = result[idx][0]
            pred_text = result[idx][1]
            pred_confidence = result[idx][2]
            textdic_easyocr[pred_text] = {}
            textdic_easyocr[pred_text]['pred_confidence'] = pred_confidence

        # create a data frame which shows the predicted text and prediction confidence
        df = pd.DataFrame.from_dict(textdic_easyocr).T
        st.table(df)

        # get boxes on the image 
        rectangle(image, result)

        st.spinner(text="In progress...")
        
    else:
        st.write("Upload your image")



       
       
# WORK LIKE MULTIPAGE APP         
if 'controllo' not in st.session_state or st.session_state['controllo'] == False:
    captcha_control()
else:
    main()
