import streamlit as st
import sqlite3
import hashlib
import joblib
import pandas as pd


conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    username TEXT,
    password TEXT
)
''')
conn.commit()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def add_user(username, password):
    c.execute("INSERT INTO users VALUES (?, ?)", 
              (username, hash_password(password)))
    conn.commit()
def login_user(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (username, hash_password(password)))
    return c.fetchone()

@st.cache_resource
def load_model():
    model = joblib.load("rf_model.pkl")
    vectorizer = joblib.load("tfidf_vectorizer.pkl")
    return model, vectorizer
model, vectorizer = load_model()


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "history" not in st.session_state:
    st.session_state.history = []

def login_page():
    st.title("🔐 Login System")
    option = st.radio("Select Option", ["Login", "Signup"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if option == "Login":
        if st.button("Login"):
            user = login_user(username, password)
            if user:
               st.success("Login Successful")
               st.session_state.logged_in = True
               st.session_state.username = username
               st.rerun()   # ✅ fixed
            else:
                st.error("Invalid Username or Password")

    else:
        if st.button("Signup"):
            add_user(username, password)
            st.success("Account Created Successfully")

def navigation():
    return st.sidebar.radio("Menu", ["Prediction","Dashboard", "History", "Logout"])


import streamlit as st
import pandas as pd
import plotly.express as px

def dashboard():
    st.title("📊 Threat Monitoring Dashboard")
    if st.session_state.history:
        df = pd.DataFrame(
            st.session_state.history,
            columns=["Text", "Prediction", "Confidence"]
        )
    else:
        st.warning("No data available")
        return
    st.subheader("🎛 Filters")

    threat_filter = st.selectbox(
        "Select Threat Type",
        ["All"] + list(df["Prediction"].unique())
    )

    if threat_filter != "All":
        df = df[df["Prediction"] == threat_filter]

    st.markdown("### 📌 Overview")

    col1, col2, col3 = st.columns(3)

    col1.markdown(f"""
        <div style="background:#1f77b4;padding:20px;border-radius:12px;color:white;text-align:center">
        <h3>Total Records</h3>
        <h2>{len(df)}</h2>
        </div>
    """, unsafe_allow_html=True)

    col2.markdown(f"""
        <div style="background:#ff7f0e;padding:20px;border-radius:12px;color:white;text-align:center">
        <h3>Unique Threats</h3>
        <h2>{df['Prediction'].nunique()}</h2>
        </div>
    """, unsafe_allow_html=True)

    col3.markdown(f"""
        <div style="background:#2ca02c;padding:20px;border-radius:12px;color:white;text-align:center">
        <h3>Avg Confidence</h3>
        <h2>{df['Confidence'].mean():.2f}%</h2>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    count_data = df["Prediction"].value_counts().reset_index()
    count_data.columns = ["Threat", "Count"]

    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.pie(
            count_data,
            names="Threat",
            values="Count",
            title="Threat Distribution"
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.bar(
            count_data,
            x="Threat",
            y="Count",
            title="Threat Count",
            text="Count"
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")


    fig3 = px.histogram(
        df,
        x="Confidence",
        nbins=10,
        title="Confidence Distribution"
    )
    st.plotly_chart(fig3, use_container_width=True)


    st.subheader("📋 Data Table")
    st.dataframe(df, use_container_width=True)


def prediction():
    st.title("🔍 Threat Prediction")
    text = st.text_input("Enter Item")
    if st.button("Predict"):
        if text.strip() == "":
            st.warning("Please enter text")
        else:
            vec = vectorizer.transform([text])
        
            result = model.predict(vec)[0]
         
            confidence = model.predict_proba(vec).max() * 100
            st.success(f"Prediction: {result}")
            st.info(f"Confidence: {confidence:.2f}%")
         
            st.session_state.history.append([text, result, round(confidence,2)])


def history():
    st.title("📜 Prediction History")

    if len(st.session_state.history) > 0:
        df = pd.DataFrame(
            st.session_state.history,
            columns=["Item", "Prediction", "Confidence"]
        )
        st.dataframe(df)
    else:
        st.warning("No history found")

def logout():
    st.session_state.logged_in = False
    st.session_state.history = []
    st.success("Logged out successfully")
    st.rerun() 


if not st.session_state.logged_in:
    login_page()
    st.stop()   
else:
    st.sidebar.write(f"👤 {st.session_state.username}")
    choice = navigation()
    if choice == "Dashboard":
        dashboard()
    elif choice == "Prediction":
        prediction()
    elif choice == "History":
        history()
    elif choice == "Logout":
        logout()
