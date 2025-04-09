import streamlit as st
from PIL import Image
import numpy as np
import io
import base64

def encode_message(image, message):
    image = image.convert("L") 
    img_array = np.array(image)
    flat_img = img_array.flatten()
    
    message += "[END]" 
    msg_bits = ''.join([format(ord(c), "08b") for c in message])
    
    if len(msg_bits) > len(flat_img):
        st.error("Message is too long to be hidden in this image!")
        return None
    
    for idx, bit in enumerate(msg_bits):
        val = flat_img[idx]
        bin_val = bin(val)[:-1] + bit 
        flat_img[idx] = int(bin_val, 2)
    
    img_array = flat_img.reshape(img_array.shape)
    encoded_img = Image.fromarray(img_array.astype(np.uint8))
    return encoded_img

def decode_message(image):
    image = image.convert("L")
    img_array = np.array(image)
    img_flat = img_array.flatten()
    
    msg = ""
    idx = 0
    while msg[-5:] != "[END]":
        if idx + 8 > img_flat.shape[0]:
            st.error("No hidden message found!")
            return ""
        
        bits = ''.join([bin(pixel)[-1] for pixel in img_flat[idx: idx + 8]])
        msg += chr(int(bits, 2))
        idx += 8
    
    return msg[:-5]

st.set_page_config(page_title="LSB Steganography", page_icon="🔐", layout="wide")
st.markdown("""
    <style>
        .stApp {
            background-color: #f0f2f6;
        }
        .main-title {
            font-size: 36px;
            font-weight: bold;
            text-align: center;
            color: #2e3b4e;
        }
        .stButton > button {
            background-color: #4CAF50;
            color: white;
            border-radius: 8px;
            padding: 10px 20px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🔐 LSB Steganography: Hide & Extract Messages</h1>", unsafe_allow_html=True)

option = st.sidebar.radio("Choose an option:", ("📤 Hide Message", "📥 Extract Message"))

if option == "📤 Hide Message":
    st.subheader("📷 Upload an Image to Hide a Message")
    uploaded_file = st.file_uploader("Upload an Image", type=["png", "jpg", "jpeg"], key="upload_hide")
    message = st.text_area("✏️ Enter the secret message:")
    
    if uploaded_file and message:
        image = Image.open(uploaded_file)
        encoded_img = encode_message(image, message)
        
        if encoded_img:
            st.image(encoded_img, caption="🔍 Encoded Image", use_column_width=True)
            img_io = io.BytesIO()
            encoded_img.save(img_io, format='PNG')
            img_io.seek(0)
            st.download_button("⬇️ Download Encoded Image", img_io, file_name="encoded_image.png", mime="image/png")

if option == "📥 Extract Message":
    st.subheader("🔎 Upload an Image to Extract the Hidden Message")
    uploaded_file = st.file_uploader("Upload a Modified Image", type=["png", "jpg", "jpeg"], key="upload_extract")
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        hidden_message = decode_message(image)
        if hidden_message:
            st.success("🎉 Hidden Message: ")
            st.write(f"`{hidden_message}`")