import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Weather Time - Reviews",
    page_icon="💬",
    layout="wide"
)

st.title("💬 Weather Time Reviews")
st.caption("Share your thoughts or read reviews from other users.")

# --- In-memory storage for reviews ---
# This will reset when the app reloads. For persistent storage, you can use a database or Google Sheets.
if "reviews_list" not in st.session_state:
    st.session_state.reviews_list = []

# --- User Input ---
with st.form("review_form"):
    user_name = st.text_input("Your Name", max_chars=50)
    user_review = st.text_area("Your Review", max_chars=500)
    submitted = st.form_submit_button("Submit Review")

    if submitted:
        if not user_name.strip() or not user_review.strip():
            st.warning("⚠ Please enter both your name and review before submitting.")
        else:
            new_review = {
                "User": user_name.strip(),
                "Review": user_review.strip(),
                "Time": datetime.now()
            }
            st.session_state.reviews_list.append(new_review)
            st.success("✅ Review submitted successfully!")

# --- Display Reviews ---
st.subheader("📝 Latest Reviews")
if st.session_state.reviews_list:
    reviews_df = pd.DataFrame(st.session_state.reviews_list)
    # Sort by time descending
    reviews_df = reviews_df.sort_values(by="Time", ascending=False)
    # Format the timestamp nicely
    reviews_df["Time"] = reviews_df["Time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    st.dataframe(reviews_df)
else:
    st.info("ℹ No reviews yet. Be the first to submit one!")