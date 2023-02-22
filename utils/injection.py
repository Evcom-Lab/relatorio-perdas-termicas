import streamlit as st
import base64


@st.cache(allow_output_mutation = True)
def get_base64_of_bin_file(png_file):
    with open(png_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


def build_markup_for_logo(png_file, title):
    binary_string = get_base64_of_bin_file(png_file)
    background_position = "50% 5%"
    margin_top = "0%"
    margin_left = "0%"
    image_width = "90%"
    image_height = ""
    padding_top = "20%"
    
    return """
            <style>
                [data-testid="stSidebarNav"] {
                    background-image: url("data:image/png;base64,%s");
                    background-repeat: no-repeat;
                    padding-top: %s;
                    background-position: %s;
                    margin-top: %s;
                    margin-left: %s;
                    background-size: %s %s;
                }

                [data-testid="stSidebarNav"]::before {
                    content: '%s';
                    margin-left: 20px;
                    margin-top: 20px;
                    font-size: 16px;
                    position: relative;
                    top: 60px;
                    color: #004A8F;
                }
            </style>
            """ % (
        binary_string,
        padding_top,
        background_position,
        margin_top,
        margin_left,
        image_width,
        image_height,
        title,
    )

    #<div data-testid="stImage" class="css-1v0mbdj etr89bj1"><img src="http://localhost:8506/media/089d48b25e552a9e20f08e1a9d900eee579ca2bd3abf53d7768e7b55.png" alt="0" style="max-width: 100%;"></div>
    #<img src="http://localhost:8506/media/089d48b25e552a9e20f08e1a9d900eee579ca2bd3abf53d7768e7b55.png" alt="0" style="max-width: 100%;">


def inject_logo(png_file, title):
    logo_markup = build_markup_for_logo(png_file, title)
    st.markdown(logo_markup, unsafe_allow_html=True)


def remove_arrow_metric():
    st.write(
        """
        <style>
        [data-testid="stMetricDelta"] svg {
            display: none;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def remove_index_table():
    hide_dataframe_row_index = """
                <style>
                .row_heading.level0 {display:none}
                .blank {display:none}
                </style>
                """

    # Inject CSS with Markdown
    st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)


def customize_expander():
    st.markdown(
        """
    <style>
    .streamlit-expanderHeader {
        font-family: 'Arial';
        font-style: normal;
        font-weight: 700;
        font-size: 14px;
        line-height: 22px;
        color: #004A8F;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )
