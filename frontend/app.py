import streamlit as st
from streamlit_navigation_bar import st_navbar
import pages as pg

st.set_page_config(layout="wide", page_icon="🎨", page_title="TIG Ad Image Studio", initial_sidebar_state="collapsed")
page = st_navbar(["TIG Ad Generator Image", "Examples"])

# Custom CSS
st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
        [data-testid="StyledFullScreenButton"] {display: none;}
        [data-testid="baseButton-headerNoPadding"] {display: none;}
        [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
            width: 35%;
        }
        [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
            width: 65%;
            margin-left: -35%;
        }
        div[data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
        }
    </style>
""", unsafe_allow_html=True)

if page == "TIG Ad Generator Image":
    pg.home()
elif page == "Examples":
    pg.examples()
