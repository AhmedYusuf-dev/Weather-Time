import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.title("Page 2")
st.write("This is the second page.")

st.page_link("Home.py", label="Back to Home", icon="🏠")

# File to store reviews
reviews_file = "reviews.csv"

# Sidebar info
st.sidebar.caption("Send us your feedback!")

st.title("📝 App Reviews")

# --- Input form ---
with st.form("review_form"):
    name = st.text_input("Your Name")
    review = st.text_area("Your Feedback")
    rating = st.slider("Rating (1-5)", 1, 5, 5)
    submitted = st.form_submit_button("Submit Review")

    if submitted:
        new_review = {
            "Name": name,
            "Review": review,
            "Rating": rating,
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Save to CSV
        if os.path.exists(reviews_file):
            df = pd.read_csv(reviews_file)
            df = df.append(new_review, ignore_index=True)
        else:
            df = pd.DataFrame([new_review])
        df.to_csv(reviews_file, index=False)

        st.success("✅ Thank you for your feedback!")

# --- Display all reviews ---
if os.path.exists(reviews_file):
    df = pd.read_csv(reviews_file)
    st.subheader("Previous Reviews")
    st.dataframe(df.sort_values("Date", ascending=False))
