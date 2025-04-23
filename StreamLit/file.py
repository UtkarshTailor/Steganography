import streamlit as st
from PIL import Image
import numpy as np
import io
# import base64
import cv2
import pywt


# ============================
# LSB STEGANOGRAPHY FUNCTIONS
# ============================
def encodedImage(image, message):
    image = image.convert("L") 
    imgArray = np.array(image)
    flatImage = imgArray.flatten()
    
    message += "[END]" 
    msgBits = ''.join([format(ord(c), "08b") for c in message])
    
    if len(msgBits) > len(flatImage):
        st.error("Message is too long to be hidden in this image!")
        return None
    
    for idx, bit in enumerate(msgBits):
        val = flatImage[idx]
        binValue = bin(val)[:-1] + bit 
        flatImage[idx] = int(binValue, 2)
    
    imgArray = flatImage.reshape(imgArray.shape)
    encodedImg = Image.fromarray(imgArray.astype(np.uint8))
    return encodedImg

def decode_message(image):
    image = image.convert("L")
    imgArray = np.array(image)
    imgFlat = imgArray.flatten()
    
    msg = ""
    idx = 0
    while msg[-5:] != "[END]":
        if idx + 8 > imgFlat.shape[0]:
            st.error("No hidden message found!")
            return ""
        
        bits = ''.join([bin(pixel)[-1] for pixel in imgFlat[idx: idx + 8]])
        msg += chr(int(bits, 2))
        idx += 8
    
    return msg[:-5]


# ============================
# DWT STEGANOGRAPHY FUNCTIONS
# ============================
def encode_dct(img, text, channel=0, intensity=20):
    block_size = 8
    height, width = img.shape[:2]
    grid_width = width // block_size
    grid_height = height // block_size

    text_bytes = text.encode('utf-8')
    length = len(text_bytes)
    bit_stream = [int(b) for b in format(length, '032b')]  
    for byte in text_bytes:
        bit_stream += [int(b) for b in format(byte, '08b')]

    max_bits = (grid_width - 1) * (grid_height - 1)
    if len(bit_stream) > max_bits:
        raise ValueError("Message too large for image.")

    img = img.astype(np.float32)
    planes = cv2.split(img)

    i = 0
    for y in range(1, grid_height):
        for x in range(1, grid_width):
            if i >= len(bit_stream):
                break

            px = (x - 1) * block_size
            py = (y - 1) * block_size
            block = planes[channel][py:py+block_size, px:px+block_size]
            dct_block = cv2.dct(block)

            a, b = dct_block[4, 3], dct_block[3, 4]
            bit = bit_stream[i]

            if bit == 0 and a < b:
                a, b = b, a
            elif bit == 1 and a > b:
                a, b = b, a

            if abs(a - b) < intensity:
                diff = (intensity - abs(a - b)) / 2
                if bit == 0:
                    a += diff
                    b -= diff
                else:
                    a -= diff
                    b += diff

            dct_block[4, 3] = a
            dct_block[3, 4] = b
            planes[channel][py:py+block_size, px:px+block_size] = cv2.idct(dct_block)
            i += 1

    encoded = cv2.merge(planes)
    return np.clip(encoded, 0, 255).astype(np.uint8)

def decode_dct(img, channel=0):
    block_size = 8
    height, width = img.shape[:2]
    grid_width = width // block_size
    grid_height = height // block_size

    img = img.astype(np.float32)
    planes = cv2.split(img)

    bits = []
    for y in range(1, grid_height):
        for x in range(1, grid_width):
            px = (x - 1) * block_size
            py = (y - 1) * block_size
            block = planes[channel][py:py+block_size, px:px+block_size]
            dct_block = cv2.dct(block)

            a, b = dct_block[4, 3], dct_block[3, 4]
            bits.append(1 if a < b else 0)

    length_bits = bits[:32]
    length = int("".join(map(str, length_bits)), 2)
    message_bits = bits[32:32+8*length]

    chars = []
    for i in range(0, len(message_bits), 8):
        byte = message_bits[i:i+8]
        chars.append(chr(int("".join(map(str, byte)), 2)))

    return ''.join(chars)


# ============================
# DWT STEGANOGRAPHY FUNCTIONS
# ============================
def textToBinary(text):
    return ''.join(format(ord(c), '08b') for c in text)

def bitsToText(bits):
    chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
    return ''.join([chr(int(char, 2)) for char in chars if len(char) == 8])


def encodeDWT(image, text, channel=0, alpha=0.1):
    bits = textToBinary(text)
    img = image.astype(np.float32) / 255.0

    planes = list(cv2.split(img))  

    coeffs2 = pywt.dwt2(planes[channel], 'haar')
    cA, (cH, cV, cD) = coeffs2

    h, w = cD.shape
    bit_idx = 0

    for y in range(h):
        for x in range(w):
            if bit_idx >= len(bits):
                break
            bit = int(bits[bit_idx])
            if bit == 1:
                cD[y, x] += alpha
            else:
                cD[y, x] -= alpha
            bit_idx += 1
        if bit_idx >= len(bits):
            break

    coeffs2 = (cA, (cH, cV, cD))
    modified_plane = pywt.idwt2(coeffs2, 'haar')

    planes[channel] = modified_plane
    merged = cv2.merge(planes)
    return (merged * 255).clip(0, 255).astype(np.uint8)


def decodeDWT(original_img, stegoImage, message_length, channel=0):
    original = original_img.astype(np.float32) / 255.0
    stego = stegoImage.astype(np.float32) / 255.0

    origPlanes = list(cv2.split(original))
    stegoPlanes = list(cv2.split(stego))

    _, (_, _, cD1) = pywt.dwt2(origPlanes[channel], 'haar')
    _, (_, _, cD2) = pywt.dwt2(stegoPlanes[channel], 'haar')

    bits = ""
    h, w = cD1.shape
    bit_idx = 0
    for y in range(h):
        for x in range(w):
            if bit_idx >= message_length * 8:
                break
            if (cD2[y, x] - cD1[y, x]) > 0:
                bits += '1'
            else:
                bits += '0'
            bit_idx += 1
        if bit_idx >= message_length * 8:
            break

    return bitsToText(bits)


# ============================
# STREAMLIT UI
# ============================
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
method = st.sidebar.selectbox("Choose a method:", ["LSB", "DCT", "DWT"])

if method == "LSB":
    if option == "📤 Hide Message":
        st.subheader("📷 Upload an Image to Hide a Message")
        uploadedFile = st.file_uploader("Upload an Image", type=["png", "jpg", "jpeg"], key="upload_hide")
        message = st.text_area("✏️ Enter the secret message:")

        if uploadedFile and message:
            image = Image.open(uploadedFile)
            encodedImg = encodedImage(image, message)

            if encodedImg:
                st.image(encodedImg, caption="🔍 Encoded Image", use_column_width=True)
                img_io = io.BytesIO()
                encodedImg.save(img_io, format='PNG')
                img_io.seek(0)
                st.download_button("⬇️ Download Encoded Image", img_io, file_name="encoded_image_lsb.png", mime="image/png")
    
    elif option == "📥 Extract Message":
        st.subheader("🔎 Upload an Image to Extract the Hidden Message (LSB)")
        uploadedFile = st.file_uploader("Upload a Modified Image", type=["png", "jpg", "jpeg"], key="upload_extract")
        if uploadedFile:
            image = Image.open(uploadedFile)
            hidden_message = decode_message(image)
            if hidden_message:
                st.success("🎉 Hidden Message:")
                st.write(f"`{hidden_message}`")


elif method == "DWT":
    if option == "📤 Hide Message":
        st.subheader("📷 Upload an Image to Hide a Message (DWT)")
        uploadedFile = st.file_uploader("Upload an Image (preferably .png)", type=["png", "jpg", "jpeg"], key="upload_hide_dwt")
        message = st.text_area("✏️ Enter the secret message to hide:")
        if uploadedFile and message:
            fileBytes = np.asarray(bytearray(uploadedFile.read()), dtype=np.uint8)
            image = cv2.imdecode(fileBytes, cv2.IMREAD_COLOR)
            stegoImage = encodeDWT(image, message + "[END]")
            st.image(stegoImage, caption="🔍 Encoded Image", channels="BGR", use_column_width=True)
            _, buffer = cv2.imencode('.png', stegoImage)
            st.download_button("⬇️ Download Encoded Image", data=buffer.tobytes(), file_name="encoded_image_dwt.png", mime="image/png")

    elif option == "📥 Extract Message":
        st.subheader("🔎 Upload Original and Stego Image to Extract Message (DWT)")
        originalImg = st.file_uploader("Upload the Original Image", type=["png", "jpg", "jpeg"], key="orig_dwt")
        stegoImage = st.file_uploader("Upload the Stego Image", type=["png", "jpg", "jpeg"], key="stego_dwt")
        message_length = st.number_input("🔢 Approximate message length (in characters):", min_value=1, max_value=1000, value=100)
        if originalImg and stegoImage:
            orig_bytes = np.asarray(bytearray(originalImg.read()), dtype=np.uint8)
            stego_bytes = np.asarray(bytearray(stegoImage.read()), dtype=np.uint8)
            orig_image = cv2.imdecode(orig_bytes, cv2.IMREAD_COLOR)
            stego_image = cv2.imdecode(stego_bytes, cv2.IMREAD_COLOR)
            decoded_msg = decodeDWT(orig_image, stego_image, message_length)
            final_msg = decoded_msg.split("[END]")[0]
            st.success("🎉 Hidden Message:")
            st.write(f"`{final_msg}`")


elif method == "DCT":
    if option == "📤 Hide Message":
        st.subheader("📷 Upload an Image to Hide a Message (DCT)")
        uploadedFile = st.file_uploader("Upload an Image", type=["png", "jpg", "jpeg"], key="upload_hide_dct")
        message = st.text_area("✏️ Enter the secret message to hide:")

        if uploadedFile and message:
            fileBytes = np.asarray(bytearray(uploadedFile.read()), dtype=np.uint8)
            image = cv2.imdecode(fileBytes, cv2.IMREAD_COLOR)
            try:
                stegoImage = encode_dct(image, message + "[END]")
                st.image(stegoImage, caption="🔍 Encoded Image", channels="BGR", use_column_width=True)
                _, buffer = cv2.imencode('.png', stegoImage)
                st.download_button("⬇️ Download Encoded Image", data=buffer.tobytes(), file_name="encoded_image_dct.png", mime="image/png")
            except ValueError as e:
                st.error(str(e))

    elif option == "📥 Extract Message":
        st.subheader("🔎 Upload an Image to Extract the Hidden Message (DCT)")
        uploadedFile = st.file_uploader("Upload the Stego Image", type=["png", "jpg", "jpeg"], key="upload_extract_dct")
        if uploadedFile:
            fileBytes = np.asarray(bytearray(uploadedFile.read()), dtype=np.uint8)
            image = cv2.imdecode(fileBytes, cv2.IMREAD_COLOR)
            try:
                decoded_msg = decode_dct(image)
                final_msg = decoded_msg.split("[END]")[0]
                st.success("🎉 Hidden Message:")
                st.write(f"`{final_msg}`")
            except Exception as e:
                st.error("⚠️ Could not extract message. Check the image or method used.")
