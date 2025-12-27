from pyairtable import Table
import streamlit as st

# ---------------- CONFIG ----------------
TABLE_NAME = "Sample"
MAX_REVIEW_LENGTH = 1000

# ---------------- SECRETS SAFE ACCESS ----------------
API_KEY = st.secrets.get("AIRTABLE_API_KEY")
BASE_ID = st.secrets.get("AIRTABLE_BASE_ID")

if not API_KEY or not BASE_ID:
    st.error("Airtable API key or Base ID not found. Add AIRTABLE_API_KEY and AIRTABLE_BASE_ID to Streamlit secrets.")
    st.stop()

# ---------------- AIRTABLE TABLE ----------------
table = Table(API_KEY, BASE_ID, TABLE_NAME)

# ---------------- HELPERS ----------------
def sanitize_text(s: str) -> str:
    return s.strip()

def submit_review_to_airtable(user: str, stars: int, review: str) -> bool:
    try:
        table.create({
            "User": user,
            "Review": review,
            "Stars": stars
        })
        return True
    except Exception as e:
        st.error(f"Failed to submit review: {e}")
        return False

# ---------------- UI ----------------
st.subheader("📋 Leave a Review")

# Use session_state keys for inputs so we can clear them reliably
st.session_state.setdefault("username", "")
st.session_state.setdefault("stars", 5)
st.session_state.setdefault("review_text", "")
st.session_state.setdefault("last_submitted", None)

username = st.text_input("👤 Your Name", key="username")
stars = st.slider("⭐ Rating", min_value=1, max_value=5, value=st.session_state.stars, key="stars")
review_text = st.text_area("✍️ Write your review", height=150, key="review_text")

# Basic validation
username_clean = sanitize_text(st.session_state.username)
review_clean = sanitize_text(st.session_state.review_text)

if len(review_clean) > MAX_REVIEW_LENGTH:
    st.warning(f"Your review is too long. Please keep it under {MAX_REVIEW_LENGTH} characters.")

if st.button("Submit Review"):
    if not username_clean or not review_clean:
        st.warning("⚠️ Name and review are required")
    else:
        submission_signature = f"{username_clean}|{stars}|{review_clean[:50]}"
        if st.session_state.get("last_submitted") == submission_signature:
            st.info("You already submitted this review in this session.")
        else:
            with st.spinner("Submitting your review..."):
                ok = submit_review_to_airtable(username_clean, stars, review_clean)
            if ok:
                st.success("✅ Review submitted!")
                st.session_state.last_submitted = submission_signature
                # Clear the form fields in session_state (no experimental_rerun needed)
                st.session_state.username = ""
                st.session_state.stars = 5
                st.session_state.review_text = ""

# ---------------- Show recent reviews ----------------
st.markdown("---")
st.subheader("🗂 Recent Reviews")

@st.cache_data(ttl=300)
def fetch_reviews(limit: int = 10):
    try:
        records = table.all(max_records=limit, sort=[("createdTime", "desc")])
        return [
            {
                "id": r.get("id"),
                "User": r.get("fields", {}).get("User", "Anonymous"),
                "Stars": r.get("fields", {}).get("Stars", 0),
                "Review": r.get("fields", {}).get("Review", ""),
                "Created": r.get("createdTime")
            }
            for r in records
        ]
    except Exception:
        return []

reviews = fetch_reviews(limit=10)
if not reviews:
    st.info("No reviews available or failed to fetch reviews.")
else:
    for r in reviews:
        stars_display = "⭐" * int(r.get("stars", 0))
        created = r.get("created", "")
        st.markdown(f"**{r.get('user')}**  {stars_display}  \n{r.get('review')}  \n*{created}*")
