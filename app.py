import streamlit as st
import datetime
import random
import string
import hashlib

# Page configuration - THIS MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(page_title="Password Strength Meter", page_icon="🔐", layout="centered")

# Title
st.title("🔐 Password Strength Meter & Generator")

# Initialize session state for history
if 'history' not in st.session_state:
    st.session_state.history = []

# Function to check password strength
def check_strength(password):
    score = 0
    criteria = {
        "length": len(password) >= 8,
        "uppercase": any(c.isupper() for c in password),
        "lowercase": any(c.islower() for c in password),
        "digits": any(c.isdigit() for c in password),
        "special": any(c in "!@#$%^&*" for c in password)
    }
    score = sum(criteria.values())
    return score, criteria

# Function to get strength label
def get_strength_label(score):
    if score == 5:
        return "🟢 Strong"
    elif score >= 3:
        return "🟡 Moderate"
    else:
        return "🔴 Weak"

# Function to check if password is a duplicate
def is_duplicate(password):
    if 'history' not in st.session_state or not st.session_state.history:
        return False
    return sum(1 for p in st.session_state.history if p['password'] == password) >= 2

# Function to generate password
def generate_password(length=12, include_upper=True, include_lower=True, include_digits=True, include_special=True):
    chars = ""
    if include_lower:
        chars += string.ascii_lowercase
    if include_upper:
        chars += string.ascii_uppercase
    if include_digits:
        chars += string.digits
    if include_special:
        chars += "!@#$%^&*"
    if not chars:
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
    
    password = []
    if include_lower:
        password.append(random.choice(string.ascii_lowercase))
    if include_upper:
        password.append(random.choice(string.ascii_uppercase))
    if include_digits:
        password.append(random.choice(string.digits))
    if include_special:
        password.append(random.choice("!@#$%^&*"))
    
    while len(password) < length:
        password.append(random.choice(chars))
    
    random.shuffle(password)
    return ''.join(password[:length])

# Create tabs
tab1, tab2, tab3 = st.tabs(["Check Password", "Generate Password", "Password History"])

# Check Password Tab
with tab1:
    password = st.text_input("Enter a password to check its strength", type="password")
    account_name = st.text_input("Enter the account name (optional)")

    if password:
        score, criteria = check_strength(password)
        strength_label = get_strength_label(score)
        st.write(f"### Strength: {strength_label}")
        st.progress(min(1.0, max(0.0, score / 5)))
        
        st.write("### Strength Criteria:")
        for key, met in criteria.items():
            st.write(f"✔️ {key.capitalize()}" if met else f"❌ {key.capitalize()}")
        
        if is_duplicate(password):
            st.warning("⚠️ This password has been used multiple times before!")

    if st.button("💾 Save Password", use_container_width=True):
        if password:
            if not account_name:
                account_name = "Unnamed Account"
            score, _ = check_strength(password)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            st.session_state.history.append({
                "account": account_name,
                "password": password,
                "strength": get_strength_label(score),
                "timestamp": timestamp
            })
            st.success(f"✅ Password for '{account_name}' saved successfully!")
        else:
            st.warning("⚠️ Please enter a password to save.")

# Generate Password Tab
with tab2:
    st.subheader("🔑 Generate a Secure Password")
    
    length = st.slider("Password Length", min_value=8, max_value=32, value=12)
    
    col1, col2 = st.columns(2)
    with col1:
        include_upper = st.checkbox("Include Uppercase Letters", value=True)
        include_lower = st.checkbox("Include Lowercase Letters", value=True)
    with col2:
        include_digits = st.checkbox("Include Digits", value=True)
        include_special = st.checkbox("Include Special Characters", value=True)
    
    if st.button("⚡ Generate Password", use_container_width=True):
        generated_password = generate_password(length, include_upper, include_lower, include_digits, include_special)
        st.code(generated_password)
        
        # Add a button to save the generated password
        if st.button("Save Generated Password"):
            account_name = st.text_input("Account name for generated password:", value="Generated Password")
            if st.button("Confirm Save"):
                score, _ = check_strength(generated_password)
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                st.session_state.history.append({
                    "account": account_name,
                    "password": generated_password,
                    "strength": get_strength_label(score),
                    "timestamp": timestamp
                })
                st.success(f"✅ Generated password saved successfully!")

# Password History Tab
with tab3:
    st.subheader("📜 Password History")
    
    if st.session_state.history:
        if st.button("Clear History"):
            st.session_state.history = []
            st.success("History cleared!")
            st.experimental_rerun()
        
        for entry in st.session_state.history[::-1]:
            st.write(f"**{entry['timestamp']}** - {entry['account']} - {entry['strength']}")
            
            # Add a button to show the password
            if st.button(f"Show Password for {entry['account']}"):
                st.code(entry['password'])
    else:
        st.info("No passwords saved yet.")

# Add a simple sidebar with tips
with st.sidebar:
    st.header("Password Tips")
    st.markdown("""
    ### Strong Password Guidelines:
    - Use at least 8 characters
    - Mix uppercase and lowercase letters
    - Include numbers and special characters
    - Avoid common words or patterns
    - Don't reuse passwords across sites
    """)