import streamlit as st
import pandas as pd
import smtplib
import dns.resolver
import concurrent.futures

# Function to get MX record
def get_mx_record(domain):
    try:
        records = dns.resolver.resolve(domain, 'MX')
        mx_record = str(records[0].exchange)
        return mx_record
    except Exception as e:
        print(f"Failed to get MX record for {domain}: {e}")
        return None

# Function to validate email
def validate_email(email):
    if '@' not in email or email.count('@') != 1:
        return email, False

    domain = email.split('@')[1]
    mx_record = get_mx_record(domain)
    if not mx_record:
        return email, False

    try:
        server = smtplib.SMTP()
        server.connect(mx_record)
        server.helo(server.local_hostname)
        server.mail('info@yourdomain.com')
        code, _ = server.rcpt(email)
        server.quit()
        return email, code == 250
    except Exception as e:
        return email, False

# Function to validate emails
def validate_emails(email_list):
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_email = {executor.submit(validate_email, email): email for email in email_list}
        for future in concurrent.futures.as_completed(future_to_email):
            email, is_valid = future.result()
            results.append((email, is_valid))
    return results

# Set the title of the Streamlit app
st.set_page_config(page_title="Email Verification Tool", page_icon=":email:", layout="wide")

# Custom CSS for styling and animations
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
    }
    .title {
        color: #2c3e50;
        font-family: 'Arial', sans-serif;
    }
    .subheader {
        color: #34495e;
        font-family: 'Arial', sans-serif;
    }
    .description {
        color: #7f8c8d;
        font-family: 'Arial', sans-serif;
    }
    .image {
        display: flex;
        justify-content: center;
        align-items: center;
        text-align: center;
    }
    .footer {
        text-align: center;
        padding: 5px;
        background: #2c3e50;
        color: white;
        border-radius: 10px;
        position: absolute; /* Fixed footer */
        bottom: -100px;
        left: 0;
        right: 0; /* Ensure it spans full width */
        box-sizing: border-box; /* Ensure padding is included in width */
        z-index: 0; /* Ensure it stays above other content */
        overflow: hidden; /* Prevent overflow */
    }
    .footer-content {
        max-width: 1200px; /* Adjust this value as needed to match content width */
        margin: 0 auto; /* Center the content */
        padding: 0 20px; /* Optional: add padding to ensure spacing */
    }
    .section {
        padding: 40px 0;
    }
    .button {
        margin-top: 20px;
    }
    .stats {
        font-size: 18px;
        color: #34495e;
        font-family: 'Arial', sans-serif;
        text-align: center;
    }
    .upload-section {
        background-color: #dff0d8;
        padding: 20px;
        border-radius: 10px;
        margin-top: 60px; /* Adjust the top margin */
    }
    .file-upload {
        display: flex;
        flex-direction: column;
        align-items: center;
        border: 2px dashed #ccc;
        padding: 20px;
        border-radius: 10px;
        background-color: #fff;
    }
    .animated {
        animation: fadeInUp 1s;
    }
    @keyframes fadeInUp {
        from {
            transform: translate3d(0, 40px, 0);
            opacity: 0;
        }
        to {
            transform: translate3d(0, 0, 0);
            opacity: 1;
        }
    }
    @media (max-width: 768px) {
        .footer {
            font-size: 14px;
        }
        .title {
            font-size: 24px;
        }
        .subheader {
            font-size: 18px;
        }
        .description {
            font-size: 14px;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# Home Section
def show_home():
    st.markdown('<div class="section animated" id="home">', unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("<h1 class='title'>Welcome to Our Email Verification and Validation Tool!</h1>", unsafe_allow_html=True)
        st.markdown("<h2 class='subheader'>Your one-stop solution for amazing features</h2>", unsafe_allow_html=True)
        st.markdown("<p class='description'>This tool helps you verify and validate email addresses with ease. Use our tool to ensure your email lists are clean and ready for your next marketing campaign.</p>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='image'>", unsafe_allow_html=True)
        st.image("image1.png", caption="Email Verification Tool", use_column_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Upload & Validate Section
    st.markdown('<div class="section upload-section animated" id="upload">', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])  # Adjust column width for centering
    with col1:
        st.markdown("<div class='image'>", unsafe_allow_html=True)
        st.image("image2.jpg", caption="Upload Your File", use_column_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<h2 class='title'>Upload & Validate</h2>", unsafe_allow_html=True)
        st.markdown("<p class='description'>Upload your CSV file containing email addresses, validate them, and download the results.</p>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv", help="Drag and drop file here\nLimit 200MB per file • CSV", label_visibility="collapsed")
        
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            if 'email' not in df.columns:
                st.error("The CSV file must contain a column named 'email'.")
            else:
                email_list = df['email'].dropna().tolist()
                
                # Display progress bar
                progress_bar = st.progress(0)
                progress_text = st.empty()
                
                st.write("Validating emails...")
                results = []
                for i, email in enumerate(email_list):
                    result = validate_email(email)
                    results.append(result)
                    progress_bar.progress((i + 1) / len(email_list))
                    progress_text.text(f"Validating email {i + 1} of {len(email_list)}")
                
                valid_df = pd.DataFrame([(email, 'Valid') for email, is_valid in results if is_valid], columns=['Email', 'Status'])
                invalid_df = pd.DataFrame([(email, 'Invalid') for email, is_valid in results if not is_valid], columns=['Email', 'Status'])

                valid_csv = valid_df.to_csv(index=False)
                invalid_csv = invalid_df.to_csv(index=False)

                st.markdown(f"<p class='stats'>Number of valid emails: {len(valid_df)}</p>", unsafe_allow_html=True)
                st.markdown(f"<p class='stats'>Number of invalid emails: {len(invalid_df)}</p>", unsafe_allow_html=True)

                col3, col4 = st.columns(2)
                with col3:
                    st.download_button(
                        label="Download Valid Emails",
                        data=valid_csv,
                        file_name="valid_emails.csv",
                        mime="text/csv"
                    )
                with col4:
                    st.download_button(
                        label="Download Invalid Emails",
                        data=invalid_csv,
                        file_name="invalid_emails.csv",
                        mime="text/csv"
                    )
    st.markdown('</div>', unsafe_allow_html=True)

    # Footer Section
    st.markdown("""
        <div class='footer'>
            <div class='footer-content'>
                <p>&copy; 2024 Email Verification Tool. All rights reserved. | Powered by Shail Digital</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Run the home section directly
if __name__ == '__main__':
    show_home()
