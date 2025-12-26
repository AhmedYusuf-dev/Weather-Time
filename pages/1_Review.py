from pyairtable import Table
import streamlit as st

API_KEY =st.secrets["AIRTABLE_API_KEY"]
BASE_ID = st.secrets["AIRTABLE_BASE_ID"]
TABLE_NAME = "Sample"

table = Table(API_KEY, BASE_ID, TABLE_NAME)

st.subheader("📋 Leave a Review")

username = st.text_input("👤 Your Name")
stars = st.slider("⭐ Rating", min_value=1, max_value=5, value=5)
review_text = st.text_area("✍️ Write your review")

if st.button("Submit Review"):
    if username.strip() and review_text.strip():
        table.create({
            "User": username,
            "Review": review_text,
            "Stars": stars
        })
        st.success("✅ Review submitted!")
    else:
        st.warning("⚠️ Name and review are required")