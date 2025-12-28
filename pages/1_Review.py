import streamlit as st
import requests
from typing import List, Dict
from datetime import datetime

# ---------------- CONFIG ----------------
TABLE_NAME = "Sample"
MAX_REVIEW_LENGTH = 1000
FETCH_LIMIT = 10
AIRTABLE_TIMEOUT = 10

# ---------------- SECRETS ----------------
API_KEY = st.secrets.get("AIRTABLE_API_KEY")
BASE_ID = st.secrets.get("AIRTABLE_BASE_ID")

if not API_KEY or not BASE_ID:
    st.error("Airtable API key or Base ID not found. Add AIRTABLE_API_KEY and AIRTABLE_BASE_ID to Streamlit secrets.")
    st.stop()

# ---------------- ENDPOINTS & HEADERS ----------------
BASE_URL = f"https://api.airtable.com/v0/{BASE_ID}"
TABLE_URL = f"{BASE_URL}/{TABLE_NAME}"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# ---------------- HELPERS ----------------
def submit_review_to_airtable(user: str, stars: int, review: str) -> bool:
    payload = {"fields": {"User": user, "Stars": stars, "Review": review}}
    try:
        resp = requests.post(TABLE_URL, json=payload, headers=HEADERS, timeout=AIRTABLE_TIMEOUT)
        resp.raise_for_status()
        return True
    except requests.RequestException as e:
        st.error(f"Failed to submit review: {e}")
        return False

@st.cache_data(ttl=300)
def fetch_reviews_cached(limit: int = FETCH_LIMIT, cache_bust: int = 0) -> List[Dict]:
    params = {"pageSize": limit, "sort[0][field]": "createdTime", "sort[0][direction]": "desc"}
    try:
        resp = requests.get(TABLE_URL, headers=HEADERS, params=params, timeout=AIRTABLE_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        records = data.get("records", [])
        results = []
        for r in records:
            fields = r.get("fields", {})
            results.append({
                "user": fields.get("User", "Anonymous"),
                "stars": int(fields.get("Stars", 0)) if fields.get("Stars") is not None else 0,
                "review": fields.get("Review", ""),
                "created": r.get("createdTime", "")
            })
        return results
    except requests.RequestException:
        return []

def sanitize_text(s: str) -> str:
    return s.strip()

# ---------------- UI STATE ----------------
st.subheader("📋 Leave a Review")

# session keys used for cache bust and last submission tracking
st.session_state.setdefault("last_submitted", None)
st.session_state.setdefault("reviews_cache_bust", 0)

# ---------------- FORM SUBMISSION CALLBACK ----------------
def on_submit_callback():
    # Read values from session_state (form widgets populate these keys)
    user = sanitize_text(st.session_state.get("form_username", ""))
    stars = st.session_state.get("form_stars", 5)
    review = sanitize_text(st.session_state.get("form_review_text", ""))

    if not user or not review:
        # Show a warning in the app (callback runs during the same script run)
        st.warning("⚠️ Name and review are required")
        return

    if len(review) > MAX_REVIEW_LENGTH:
        st.warning(f"Your review is too long. Please keep it under {MAX_REVIEW_LENGTH} characters.")
        return

    submission_signature = f"{user}|{stars}|{review[:50]}"
    if st.session_state.get("last_submitted") == submission_signature:
        st.info("You already submitted this review in this session.")
        return

    with st.spinner("Submitting your review..."):
        ok = submit_review_to_airtable(user, stars, review)

    if ok:
        st.success("✅ Review submitted!")
        st.session_state.last_submitted = submission_signature
        # Clear the form-backed session keys safely inside the callback
        st.session_state["form_username"] = ""
        st.session_state["form_stars"] = 5
        st.session_state["form_review_text"] = ""
        # Bump cache bust to refresh cached reviews
        st.session_state.reviews_cache_bust = st.session_state.get("reviews_cache_bust", 0) + 1

# ---------------- FORM (widgets use keys that start with 'form_') ----------------
with st.form(key="review_form", clear_on_submit=False):
    # These widgets are created inside the form and bound to session_state keys.
    # The callback will run when the form is submitted.
    st.text_input("👤 Your Name", key="form_username")
    st.slider("⭐ Rating", min_value=1, max_value=5, value=5, key="form_stars")
    st.text_area("✍️ Write your review", height=150, key="form_review_text")
    submitted = st.form_submit_button("Submit Review", on_click=on_submit_callback)

# ---------------- Show recent reviews ----------------
st.markdown("---")
st.subheader("🗂 Recent Reviews")

reviews = fetch_reviews_cached(limit=FETCH_LIMIT, cache_bust=st.session_state.get("reviews_cache_bust", 0))
if not reviews:
    st.info("No reviews available or failed to fetch reviews.")
else:
    for r in reviews:
        stars_display = "⭐" * int(r.get("stars", 0))
        created = r.get("created", "")
        created_str = created
        try:
            if created:
                created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                created_str = created_dt.strftime("%Y-%m-%d %H:%M UTC")
        except Exception:
            created_str = created
        st.markdown(f"**{r.get('user')}**  {stars_display}  \n{r.get('review')}  \n*{created_str}*")
