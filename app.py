import json

import requests
import streamlit as st


# Load local airport reference data.
with open("airports.json", "r", encoding="utf-8") as file:
    airports = json.load(file)


st.set_page_config(
    page_title="Airport Intelligence Agent",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------- Styling ----------

st.markdown(
    """
    <style>
        .stApp {
            background: #0b1120;
        }

        .block-container {
            max-width: 1250px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        [data-testid="stSidebar"] {
            background: #0f172a;
            border-right: 1px solid #1e293b;
        }

        [data-testid="stSidebar"] img {
            border-radius: 14px;
            margin-bottom: 1rem;
        }

        .main-header {
            margin-bottom: 2rem;
        }

        .main-title {
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }

        .main-subtitle {
            color: #94a3b8;
            font-size: 1rem;
        }

        .airport-banner {
            background: linear-gradient(
                135deg,
                #172554 0%,
                #0f172a 100%
            );
            border: 1px solid #263b68;
            border-radius: 18px;
            padding: 1.5rem 1.75rem;
            margin-bottom: 1.25rem;
        }

        .airport-code {
            font-size: 2.8rem;
            font-weight: 800;
            line-height: 1;
        }

        .airport-name {
            color: #cbd5e1;
            font-size: 1.05rem;
            margin-top: 0.5rem;
        }

        .airport-location {
            color: #64748b;
            font-size: 0.9rem;
            margin-top: 0.2rem;
        }

        .section-title {
            font-size: 1.2rem;
            font-weight: 650;
            margin-top: 1.75rem;
            margin-bottom: 0.8rem;
        }

        .source-badge {
            display: inline-block;
            background: #111827;
            border: 1px solid #334155;
            border-radius: 999px;
            padding: 0.45rem 0.8rem;
            margin-right: 0.35rem;
            margin-bottom: 0.35rem;
            color: #cbd5e1;
            font-size: 0.8rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------- Sidebar ----------

with st.sidebar:
    st.image(
        "https://images.unsplash.com/photo-1713182568612-58dd29b515b7"
        "?fm=jpg&ixlib=rb-4.1.0&q=80&w=1200",
        width='stretch',
    )

    st.divider()

    airport_options = {
        f"{airport['code']} · {airport['city']}": airport
        for airport in airports
    }

    selected_airport_name = st.selectbox(
        "Airport",
        list(airport_options.keys()),
    )

    selected_airport = airport_options[selected_airport_name]

    st.divider()

    st.markdown("**Dashboard**")

    selected_section = st.radio(
        "Dashboard",
        [
            "Overview",
            "Flight Disruptions",
            "Passenger Assistance",
        ],
        label_visibility="collapsed",
    )


airport_code = selected_airport["code"]
airport_name = selected_airport["name"]
airport_city = selected_airport["city"]


# ---------- Section Configuration ----------

section_config = {
    "Overview": {
        "title": "Airport Intelligence Overview",
        "placeholder": (
            f"Give me a complete current briefing for {airport_code}, "
            "including flights, weather, and recent airport news."
        ),
    },
    "Flight Disruptions": {
        "title": "Flight Disruption Intelligence",
        "placeholder": (
            f"Are there any current flight delays, cancellations, "
            f"or disruptions at {airport_code}?"
        ),
    },
    "Passenger Assistance": {
        "title": "Passenger Assistance",
        "placeholder": (
            f"Help me with passenger assistance at {airport_code}. "
            "Include relevant travel, airport, and hotel information if needed."
        ),
    },
}

current_section = section_config[selected_section]


# ---------- Header ----------

st.markdown(
    f"""
    <div class="main-header">
        <div class="main-title">Airport Intelligence Agent</div>
        <div class="main-subtitle">
            {current_section["title"]}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------- Airport Banner ----------

st.markdown(
    f"""
    <div class="airport-banner">
        <div class="airport-code">{airport_code}</div>
        <div class="airport-name">{airport_name}</div>
        <div class="airport-location">📍 {airport_city}, India</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------- Agent ----------

st.markdown(
    '<div class="section-title">Ask the Airport Agent</div>',
    unsafe_allow_html=True,
)

query = st.text_area(
    "Question",
    placeholder=current_section["placeholder"],
    height=100,
    label_visibility="collapsed",
)

if st.button(
    "🔎 Ask Agent",
    type="primary",
    width='stretch',
):
    if not query.strip():
        st.warning("Please enter a question.")
    else:
        backend_url = "http://127.0.0.1:8000/ask"

        # Give the agent the airport selected by the user.
        full_query = (
            f"The selected airport is {airport_code} "
            f"({airport_name}, {airport_city}, India).\n\n"
            f"Dashboard section: {selected_section}\n\n"
            f"User question: {query}"
        )

        with st.spinner("Agent is researching..."):
            try:
                response = requests.post(
                    backend_url,
                    json={"query": full_query},
                    timeout=120,
                )

                response.raise_for_status()
                result = response.json()

                st.session_state["agent_result"] = result

            except requests.exceptions.ConnectionError:
                st.error(
                    "Could not connect to the backend. "
                    "Make sure FastAPI is running on http://127.0.0.1:8000."
                )

            except requests.exceptions.Timeout:
                st.error(
                    "The request took too long. "
                    "The agent may still be processing multiple tools."
                )

            except requests.exceptions.RequestException as e:
                st.error(f"Backend request failed: {e}")

            except ValueError:
                st.error("The backend returned an invalid response.")


# ---------- Agent Response ----------

if "agent_result" in st.session_state:
    result = st.session_state["agent_result"]

    st.markdown(
        '<div class="section-title">Agent Response</div>',
        unsafe_allow_html=True,
    )

    if result.get("answer"):
        st.markdown(result["answer"])

    sources = result.get("sources", [])

    if sources:
        st.markdown(
            '<div class="section-title">📚 Sources Used</div>',
            unsafe_allow_html=True,
        )

        source_labels = {
            "flight_status": "✈️ Flight Status",
            "weather": "🌦️ Weather",
            "airport_news": "📰 Airport News",
            "web_search": "🔎 Web Search",
            "hotel_search": "🏨 Hotel Search",
            "current_datetime": "🕐 Current Date & Time",
        }

        for source in sources:
            label = source_labels.get(source, source)

            st.markdown(
                f'<span class="source-badge">{label}</span>',
                unsafe_allow_html=True,
            )