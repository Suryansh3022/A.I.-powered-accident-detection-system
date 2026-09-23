import streamlit as st
import os
import time
from config.config_manager import ConfigManager
from services.accident_detector import AccidentDetector
from services.hospital_service import HospitalService
from services.sms_service import SMSService
from PIL import Image

# Initialize Streamlit page configuration
st.set_page_config(
    page_title="Accident Detection App",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize services
config_manager = ConfigManager()
lat, lng = config_manager.get_coordinates()
accident_detector = AccidentDetector(config_manager.get_env_var('GEMINI_API_KEY'))
hospital_service = HospitalService()
sms_service = SMSService(
    twilio_sid=config_manager.get_env_var('TWILIO_SID'),
    twilio_token=config_manager.get_env_var('TWILIO_TOKEN'),
    twilio_phone=config_manager.get_env_var('TWILIO_PHONE'),
    contact_number=config_manager.get_env_var('CONTACT_NUMBER')
)

# Fetch hospital details once at startup
hospital_details_list = hospital_service.fetch_hospital_details_list(lat, lng)

# Create uploads directory if it doesn't exist
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Custom CSS styling
st.markdown("""
    <style>
    .header-style {
        font-size:32px !important;
        font-weight:bold !important;
        margin-bottom:20px !important;
    }
    .result-box {
        padding:20px;
        border-radius:10px;
        margin:10px 0px;
    }
    .success-box {
        background-color:#e6f4ea;
        border:1px solid #34a853;
    }
    .danger-box {
        background-color:#fce8e6;
        border:1px solid #ea4335;
    }
    .hospital-card {
        padding:15px;
        background-color:#f8f9fa;
        border-radius:10px;
        margin:10px 0px;
    }
    </style>
    """, unsafe_allow_html=True)

# Hero Section
st.markdown("<h1 class='header-style'>AI Accident Detection System</h1>", unsafe_allow_html=True)
with st.expander("ℹ️ How it works", expanded=True):
    st.markdown("""
    1. Upload any street/car image (JPEG, PNG, BMP, GIF)
    2. Our AI analyzes the image for accident indicators
    3. If accident detected: 
       - 🏥 Find nearest hospital
       - 📱 Send SMS alert
    4. Images are deleted immediately after processing
    """)

# File upload section
st.subheader("📤 Step 1: Upload Your Image")
uploaded_file = st.file_uploader(
    "Choose an image file",
    type=['jpg', 'jpeg', 'png', 'bmp', 'gif'],
    label_visibility="collapsed"
)

if uploaded_file is not None:
    filename = uploaded_file.name
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    try:
        # Save file with proper cleanup handling
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Validate image dimensions
        with Image.open(file_path) as img:
            if img.size[0] > 1024 or img.size[1] > 1024:
                st.error("❌ Image too large! Maximum allowed size is 1024x1024 pixels.")
                os.remove(file_path)
                st.stop()

        # Display image preview
        st.subheader("🖼️ Uploaded Image Preview")
        with open(file_path, "rb") as f:
            image_bytes = f.read()
        st.image(image_bytes, use_column_width=True, caption=filename)

        # Process image
        with st.status("🔍 Analyzing image...", expanded=True) as status:
            result = accident_detector.process_image(file_path)
            status.update(label="Analysis Complete!", state="complete")

        # Display results
        st.subheader("📊 Analysis Results")
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.metric("Accident Detected", 
                     value="YES" if result['status'] == 'Yes' else "NO", 
                     delta="Emergency Alert Sent" if result['status'] == 'Yes' else None,
                     delta_color="off")

        with col2:
            st.markdown(f"**Explanation**:\n\n{result['explanation']}")

        # Handle accident detection
        if result['status'] == 'Yes':
            st.divider()
            st.subheader("🚑 Emergency Response")
            
            if hospital_details_list:
                hospital_info = hospital_details_list[0]
                
                with st.container(border=True):
                    st.markdown(f"### 🏥 {hospital_info['name']}")
                    st.markdown(f"**📍 Address**:\n\n{hospital_info['address']}")
                    st.markdown(f"**📞 Phone**: {hospital_info['phone']}")
                    
                    st.divider()
                    message_body = f"Accident reported at coordinates ({lat}, {lng}). Nearest hospital: {hospital_info['name']} at {hospital_info['address']}."
                    success, sms_result = sms_service.send_sms(message_body, filename)
                    
                    if success:
                        st.success(f"📨 SMS Alert Sent Successfully!")
                        st.caption(f"Twilio SID: {sms_result}")
                    else:
                        st.error(f"❌ Failed to Send SMS Alert")
                        st.caption(f"Error: {sms_result}")
            else:
                st.warning("⚠️ No hospitals found nearby")

        elif result['status'] == 'No':
            st.balloons()
            with st.container(border=True):
                st.success("✅ All Clear - No Accident Detected")
                st.markdown(f"**Analysis Details**:\n\n{result['explanation']}")
        else:
            st.error("⚠️ Error Processing Image")

    except Exception as e:
        st.error(f"❌ Error processing image: {str(e)}")
    finally:
        # Robust file cleanup with retries
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                break
            except PermissionError:
                if attempt < max_retries - 1:
                    time.sleep(0.1)
                else:
                    st.error(f"Failed to clean up file after {max_retries} attempts")
            except Exception as e:
                st.error(f"Unexpected error during cleanup: {str(e)}")
                break
