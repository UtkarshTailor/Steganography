# 🔐 Steganography Web App with Streamlit

This is a Streamlit-based web application that allows users to **hide (encode)** and **extract (decode)** secret messages in images using **three different steganography techniques**:

- **LSB (Least Significant Bit)**
- **DCT (Discrete Cosine Transform)**
- **DWT (Discrete Wavelet Transform)**

> Built with simplicity in mind, this app provides a visual and intuitive interface for data hiding techniques, suitable for learning, experimenting, or basic security applications.

---

## 🚀 Features

- 📷 Upload and encode messages into images.
- 🧠 Extract hidden messages from encoded images.
- 💾 Download encoded images with embedded secrets.
- ✨ Choose between LSB, DCT, or DWT steganography.
- 🧪 Approximate message length input for better DWT decoding.

---

## 🛠️ Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/UtkarshTailor/Steganography.git
cd Steganography
```

### 2. Install Dependencies

Make sure you have Python 3.7+ installed.

```bash
pip install -r requirements.txt
```


### 3. Run the App

```bash
python -m streamlit run StreamLit/file.py
```

Open the app in your browser when prompted, or visit: [http://localhost:8501](http://localhost:8501)

---

## 📸 Supported File Types

- PNG
- JPG / JPEG

> PNG is recommended for best quality during encoding/decoding.

---

## 🧪 Available Methods

| Method | Description |
|--------|-------------|
| **LSB** | Simple grayscale-based message hiding using the least significant bit. |
| **DCT** | Frequency domain message embedding using Discrete Cosine Transform. |
| **DWT** | Wavelet domain message hiding using Haar wavelet transform. |

---

## 👨‍💻 Contributors


| Name | GitHub |  
|------|--------|  
| Utkarsh Tailor | [@UtkarshTailor](https://github.com/UtkarshTailor) |  
| Rajat Paliwal | [@Rajat0729](https://github.com/Rajat0729) |  
| Rahul Yadav | [@rahul240802](https://github.com/rahulsyadav24) |


---

## Acknowledgment

This project was developed under the expert guidance of **Dr. Surbhi Chabbra**.

---

