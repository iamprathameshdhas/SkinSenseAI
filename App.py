import streamlit as st
import numpy as np
import pandas as pd
import pickle
import tensorflow as tf
from PIL import Image
import io
import time
from fpdf import FPDF
from datetime import datetime

# Load the scaler object from the pickle file
with open('scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)
# Load the encoder object for localization from the pickle file
with open('encoder_localization.pkl', 'rb') as f:
    localization_encoder = pickle.load(f)
# Load the encoder object for sex from the pickle file
with open('encoder_sex.pkl', 'rb') as f:
    sex_encoder = pickle.load(f)

mixed_data_model = tf.keras.models.load_model("alexnet_augmented_200_100_0.5_thrice_0.8264_0.8309_0.9573.h5")
label_dict = {0: 'Moles', 1: 'Melanoma', 2: 'Minor Skin Issues', 3: 'Non Melonoma'}

import base64

def generate_pdf(title, name, age, sex, localization, probabilities, image_name, image_bytes):
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 15)
            self.cell(0, 10, title, 0, 1, 'C')
            self.ln(10)

        def chapter_title(self, title):
            self.set_font('Arial', 'B', 14)
            self.cell(0, 10, title, 0, 1, 'L')
            self.ln(10)
            self.line(10, self.get_y(), 200, self.get_y())

        def chapter_body(self, body):
            self.set_font('Arial', '', 12)
            self.multi_cell(0, 10, body)
            self.ln()
            #self.line(10, self.get_y(), 200, self.get_y())
            
        def summary_body(self, body):
            self.set_font('Arial', 'I', 12)
            self.multi_cell(0, 10, body)
            self.ln()    

        def table(self, data):
            self.ln(10)
            self.set_font('Arial', '', 12)
            self.cell(40, 10, 'Condition', 1)
            self.cell(40, 10, 'Chances', 1)
            self.ln()
            for label, prob in data.items():
                self.cell(40, 10, label, 1)
                self.cell(40, 10, f'{prob:.2f}', 1)
                self.ln()
            self.ln(10)
            #self.line(10, self.get_y(), 200, self.get_y())
            
        def lesion_image(self, image_name, image_bytes):
            # self.chapter_title("Lesion Image")
            # self.set_font('Arial', '', 10)
            self.cell(0, 10, f"Lesion ID: {image_name}", 0, 1, 'L')
            self.ln(5)
            # Write the image to a temporary file to add to PDF
            image = Image.open(io.BytesIO(image_bytes))
            image_path = f"{image_name}"
            image.save(image_path)
            self.image(image_name, x=10, y=self.get_y(), w=60)
            self.ln(65)  # adjust this value based on the image height
                
        def footer(self):
            
            self.set_y(-25)
            self.set_font('Arial', 'I', 9)
            self.line(10, self.get_y(), 200, self.get_y())
            self.multi_cell(0, 10, 'Warning: This is a Predictive model in development and results may deviate. Please conduct further evaluation / Biopsy for a definitive diagnosis.', 0, 'C')


    pdf = PDF()
    pdf.add_page()
    
    pdf.chapter_title("1. Patient Information")
    current_date = datetime.now().strftime("%d %B %Y")
    patient_info = f"Name: {name}\nDate: {current_date}\nAge: {age}\nSex: {sex}\nLocalization: {localization}"
    pdf.chapter_body(patient_info)
    pdf.lesion_image(image_name, image_bytes)
    pdf.chapter_title("2. Prediction Probabilities")
    pdf.table(probabilities)
    
    pdf.chapter_title("3. Final Summary")
    if probabilities['Melanoma'] > 75:
        pdf.summary_body(f"There is High risk of Melanoma.  It is highly recommended to perform a detailed clinical examination and consider a biopsy to confirm the diagnosis")
    elif probabilities['Non Melonoma'] > 75:
        pdf.summary_body(f"There is High risk of Non-Melanoma Cancer.  It is highly recommended to perform a detailed clinical examination and consider a biopsy to confirm the diagnosis")
    
    else:
        pdf.chapter_body(f"The current evaluation indicates that the patient's skin is in good condition. The lesion observed does not present any indications of skin cancer at this time. It is recommended to continue regular monitoring and maintain routine dermatological check-ups to ensure ongoing skin health.")

    pdf_output = io.BytesIO()
    pdf_output = pdf.output(dest='S').encode('latin1')
    return pdf_output

    

def get_pdf_download_link(pdf_data, filename):
    b64_pdf = base64.b64encode(pdf_data.read()).decode('utf-8')
    href = f'<a href="data:application/octet-stream;base64,{b64_pdf}" download="{filename}">Download PDF Report</a>'
    return href

st.header("🩺 Medbot: Your Personal Skin Care Assistant")
st.subheader("Please fill in the information below for a diagnosis and PDF report.")

uploaded_file = st.file_uploader("Upload a skin image")

col1, col2, col3, col4 = st.columns(4)
with col1:
    patient_name = st.text_input("Patient Name")
with col2:
    slider_value = st.slider("Please select your Age:", min_value=0, max_value=100, value=50)
with col3:
    selectbox_value1 = st.selectbox("Gender", ["male", "female"])
with col4:
    selectbox_value2 = st.selectbox("Body Part/Region", [
        'hand', 'lower extremity', 'back', 'face', 'trunk', 'genital', 'neck', 
        'ear', 'unknown', 'acral', 'scalp', 'foot', 'chest', 'abdomen', 'upper extremity'
    ])
report = st.button("Generate Report")
if uploaded_file and patient_name:
    data = {
        'age': [slider_value, slider_value],
        'sex': [selectbox_value1, selectbox_value1],
        'localization': [selectbox_value2, selectbox_value2]
    }
    df = pd.DataFrame(data)
    df['age'] = scaler.transform(df[['age']])
    df['sex'] = sex_encoder.transform(df[['sex']])
    df['localization'] = localization_encoder.transform(df[['localization']])

    image_bytes = uploaded_file.read()
    img = np.asarray(Image.open(io.BytesIO(image_bytes)).resize((200, 100)))
    img_arr = [img, img]

    progress_bar = st.progress(0)
    status_text = st.empty()

    for i in range(100):
        progress_bar.progress(i + 1)
        time.sleep(0.01)
        if i == 25:
            status_text.text("Preprocessing data...")
        elif i == 50:
            status_text.text("Running predictions...")
        elif i == 75:
            status_text.text("Finalizing results...")

    y_pred = mixed_data_model.predict([df, np.array(img_arr)])
    # Select the first four predictions
    print(y_pred[0])
    predictions = y_pred[0][:4]

    # Round each number to 2 decimal places
    rounded_predictions = predictions
    # Multiply each probability by 100 and round to 2 decimal places
    probabilities = {label_dict[i]: round(prob * 100, 4) for i, prob in enumerate(rounded_predictions)}


    response = "Skin is healthy! Keep it Up!"
    if probabilities['Melanoma'] > 75 or probabilities['Non Melonoma'] > 75:
        response = "High Chances for Skin Cancer. Please schedule a visit to the nearest doctor."

    st.markdown(f"**Prediction:** {response}")

    st.markdown("### Prediction Probabilities")
    st.table(probabilities)

    if report:
        pdf_data = generate_pdf("Skin Care Diagnosis Report", patient_name, slider_value, selectbox_value1, selectbox_value2, probabilities,uploaded_file.name, image_bytes)
        st.success("PDF Report Generated Successfully!")
        st.download_button(label='Download PDF', data=pdf_data, file_name='example.pdf', mime='application/pdf')

else:
    st.warning("Please upload a skin image and enter the patient's name.")
