
import streamlit as st
import json

@st.cache_data
def load_rules(path: str = "rules.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

rules = load_rules()
foods = rules["foods"]
modifiers = rules["modifiers"]
sensory_flags = rules["sensory_flags"]

def format_hours(h: float) -> str:
    days = int(h // 24)
    hours = int(h % 24)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if not parts:
        parts.append("0h")
    return " ".join(parts)

def compute_estimate(food_name: str, state: str, storage: str, selected_mod_keys):
    food = foods[food_name]
    shelf = food["shelf_life_hours"]
    base_hours = shelf.get(state, {}).get(storage)
    if base_hours is None:
        return None

    multiplier = 1.0
    for m in selected_mod_keys:
        factor = modifiers.get(m)
        if factor:
            multiplier *= factor
    est_hours = base_hours * multiplier

    # conservative window
    lower = est_hours * 0.75
    upper = est_hours
    if base_hours <= 6:
        lower = est_hours * 0.5
    if upper > 24 * 365:
        upper = 24 * 365

    if upper <= 6:
        risk = "High perishability"
    elif upper <= 72:
        risk = "Moderate perishability"
    else:
        risk = "Low perishability"

    return {
        "base_hours": base_hours,
        "lower_hours": lower,
        "upper_hours": upper,
        "risk": risk
    }

st.title("Food Shelf-Life Estimator")

st.markdown(rules["notes"]["disclaimer"])

# Sidebar: inputs + rules viewer
st.sidebar.header("Inputs")

food_names = sorted(foods.keys())
food_choice = st.sidebar.selectbox("Food / Dish", food_names)

food_data = foods[food_choice]
state_choice = st.sidebar.selectbox("State", food_data["states"])
storage_choice = st.sidebar.selectbox("Storage", food_data["storages"])

st.sidebar.header("Modifiers")
modifier_labels = {k: k.replace("_", " ").title() for k in modifiers.keys()}
selected_modifier_labels = st.sidebar.multiselect(
    "Select all that apply",
    options=list(modifier_labels.values())
)
# Map back to keys
selected_mod_keys = [k for k, lbl in modifier_labels.items() if lbl in selected_modifier_labels]

st.sidebar.header("Sensory checks")
sensory_labels = {k: v for k, v in sensory_flags.items()}
selected_sensory_labels = st.sidebar.multiselect(
    "Select if you notice any of these",
    options=list(sensory_labels.values())
)
selected_sensory_keys = [k for k, lbl in sensory_labels.items() if lbl in selected_sensory_labels]

with st.sidebar.expander("Rules dataset (rules.json)"):
    st.write("This app uses the following rules dataset.")
    st.info(f"Total foods in database: {len(foods)}")
    # show preview of first 50 foods
    preview_keys = list(foods.keys())[:50]
    preview = {k: foods[k] for k in preview_keys}
    st.json(preview)
    st.download_button(
        "Download full rules.json",
        data=json.dumps(rules, indent=2),
        file_name="rules.json",
        mime="application/json"
    )

if st.button("Estimate shelf life"):
    if selected_sensory_keys:
        st.error("Sensory warning: Discard immediately based on selected sensory issues.")
    else:
        result = compute_estimate(food_choice, state_choice, storage_choice, selected_mod_keys)
        if result is None:
            st.warning("No data available for this combination of state and storage.")
        else:
            st.subheader("Estimated shelf life")
            st.write(f"Base shelf-life: {format_hours(result['base_hours'])}")
            st.write(f"Estimated usable window: {format_hours(result['lower_hours'])} - {format_hours(result['upper_hours'])}")
            st.write(f"Overall risk level: {result['risk']}")

            st.markdown("---")
            st.subheader("General Recommendations")
            st.write("- When unsure, prefer to discard high-risk foods such as meat, fish, eggs and dairy.")
            st.write("- Avoid reheating the same food multiple times.")
            st.write("- Keep hot foods hot and cold foods cold. Do not leave cooked foods at room temperature for many hours.")
            st.write("- Store foods in clean, airtight containers whenever possible.")
            st.write("- Label leftovers with date and aim to consume them within a few days.")

st.markdown("---")
st.subheader("About this model")
st.markdown(
    "This tool uses a built-in rules dataset (`rules.json`) to estimate shelf life based on food type, state, storage method and selected modifiers. "
    "You can preview and download the full rules file from the sidebar section titled **'Rules dataset (rules.json)'**."
)
