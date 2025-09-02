import streamlit as st
import json, os, time, base64

DATA_FILE = "wardrobe.json"

def load_wardrobe():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_wardrobe(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def score_item_for_event(item, event_type):
    score = 0
    formal_map = {"wedding": 9, "anniversary": 8, "party": 6, "birthday": 6, "casual": 3}
    desired = formal_map.get(event_type, 6)
    score += 10 - abs((item.get("formality", 5)) - desired)

    # category rules
    if event_type in ["wedding", "anniversary"] and item["category"] in ["dress", "suit", "ethnic"]:
        score += 8
    if event_type in ["party", "birthday"] and item["category"] in ["dress", "top", "jacket", "shirt"]:
        score += 5

    # color rules
    color = item.get("color", "").lower()
    if event_type == "wedding" and "white" in color:
        score -= 2
    if event_type == "party" and any(c in color for c in ["gold", "silver", "sequin", "glitter"]):
        score += 4

    return score

def suggest_outfits(wardrobe, event_type):
    if not wardrobe:
        return []
    scored = []
    for item in wardrobe:
        s = score_item_for_event(item, event_type)
        item_copy = item.copy()
        item_copy["score"] = s
        scored.append(item_copy)
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:6]


st.set_page_config(page_title="AI Outfit Recommender", layout="wide")
st.title("👗 AI Party Outfit Recommender")

event_type = st.selectbox(
    "Choose event type:",
    ["party", "wedding", "birthday", "anniversary", "casual"]
)

wardrobe = load_wardrobe()

# Add item form
with st.expander("➕ Add wardrobe item"):
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("Name")
        category = st.selectbox("Category", ["top","bottom","dress","suit","ethnic","jacket","shoes"])
        color = st.text_input("Color")
        formality = st.slider("Formality (1 casual - 10 formal)", 1, 10, 5)
        img_file = st.file_uploader("Upload image", type=["png","jpg","jpeg"])

        submitted = st.form_submit_button("Add Item")
        if submitted:
            img_b64 = None
            if img_file:
                img_b64 = "data:image/png;base64," + base64.b64encode(img_file.read()).decode("utf-8")
            item = {
                "id": "i_" + str(int(time.time() * 1000)),
                "name": name,
                "category": category,
                "color": color,
                "formality": formality,
                "image": img_b64,
                "addedAt": time.time(),
            }
            wardrobe.append(item)
            save_wardrobe(wardrobe)
            st.success("Item added! Refresh to see it.")

# Wardrobe grid
st.subheader("👚 Your Wardrobe")
if wardrobe:
    cols = st.columns(3)
    for i, item in enumerate(wardrobe):
        with cols[i % 3]:
            if item.get("image"):
                st.image(item["image"], use_container_width=True)
            st.caption(f"{item['name']} ({item['category']}, {item['color']})")
            if st.button(f"❌ Remove {item['name']}", key=item["id"]):
                wardrobe = [w for w in wardrobe if w["id"] != item["id"]]
                save_wardrobe(wardrobe)
                st.experimental_rerun()
else:
    st.info("No wardrobe items yet. Add some above!")

# Suggestions
st.subheader(f"✨ Outfit Suggestions for {event_type}")
suggestions = suggest_outfits(wardrobe, event_type)
if suggestions:
    for s in suggestions:
        cols = st.columns([1,3])
        with cols[0]:
            if s.get("image"):
                st.image(s["image"], width=80)
        with cols[1]:
            st.write(f"**{s['name']}** — Score: {round(s['score'])}")
else:
    st.warning("No suggestions yet. Add items first.")
