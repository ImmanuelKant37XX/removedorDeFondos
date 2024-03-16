import os
import io
import zipfile
from pathlib import Path
import streamlit as st
from PIL import Image
from rembg import remove
import uuid

MAX_FILES = 100
ALLOWED_TYPES = ["png", "jpg", "jpeg"]

def setup_page():

    st.markdown(
        """
        <style>
        body {
            background-color: #1E1E1E;
            color: white;
        }
        .sidebar .sidebar-content {
            background-color: #1E1E1E;
        }
        .Widget>label {
            color: white;
        }
        .stSelectbox>div {
            color: black;
        }
        .stTextInput>div>div>input {
            color: black;
        }
        .st-emotion-cache-ch5dnh{
        	color: black;
        }
     
        .st-emotion-cache-9ycgxx {
        	display: none;
        }
        .st-emotion-cache-7oyrr6 {
        	display: none;
        }
	
        .st-emotion-cache-1erivf3::before {
        	color:"White";
     	        content:  "Arrastra las imagenes aqui "; 
        }
        .st-emotion-cache-6rlrad{
        	display:none;
        }
      
        
        </style>
        <script> 

        </script>
        """,
        unsafe_allow_html=True,
    )
    hide_streamlit_style()

    hide_div_script = """
        <script>
        console.log("TEST")
        window.onload = function() {
            var elements = document.querySelectorAll('.hide-div');

            elements.forEach(function(element) {
                element.style.display = 'none';
            });
        }
        </script>
        """
    st.markdown(hide_div_script, unsafe_allow_html=True)

def hide_streamlit_style():
    """Hides default Streamlit styling."""
    st.markdown(
        "<style>footer {visibility: hidden;} #MainMenu {visibility: hidden;}</style>",
        unsafe_allow_html=True,
    )


def initialize_session():
    """Initializes a unique session ID."""
    if "uploader_key" not in st.session_state:
        st.session_state["uploader_key"] = str(uuid.uuid4())


def display_ui():
    """Displays the user interface for file upload and returns uploaded files."""
    st.title("Removedor de fondos")
    st.markdown("")


    st.markdown(
    """
    <link rel="shortcut icon" href="data:image/x-icon;base64, ...base64-encoded-favicon..." type="image/x-icon" />
    """,
    unsafe_allow_html=True
)

    if st.button("Limpiar"):
        st.session_state["uploader_key"] = str(uuid.uuid4())

    uploaded_files = st.file_uploader(
    
        "",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
        key=st.session_state.get("uploader_key", "file_uploader"),
    )

    display_footer()
    return uploaded_files


def display_footer():
    """Displays a custom footer."""
    footer = """<div style="position: fixed; bottom: 0; width:100%; text-align: center;">
                <p></p>
                </div>"""
    st.markdown(footer, unsafe_allow_html=True)


def process_and_display_images(uploaded_files):
    """Processes the uploaded images and displays the original and result images."""
    if not uploaded_files:
        st.warning("")
        return

    if not st.button("Remover Fondos"):
        return

    if len(uploaded_files) > MAX_FILES:
        st.warning(f"Maximo de archivos {MAX_FILES} seran procesados.")
        uploaded_files = uploaded_files[:MAX_FILES]

    results = []

    st.title("Resultados")
    st.markdown("---")  # Separador entre el título y las imágenes

    with st.spinner("Removiendo fondos..."):
        for uploaded_file in uploaded_files:
            original_image = Image.open(uploaded_file).convert("RGBA")
            result_image = remove_background(original_image)
            results.append((original_image, result_image, uploaded_file.name))

    for i, (original, result, name) in enumerate(results):
        col1, col2 = st.columns(2)
        with col1:
            st.image(original, caption="Original", use_column_width=True, output_format='JPEG')
        with col2:
            st.image(result, caption="Resultado", use_column_width=True, output_format='JPEG')

        # Agregar un identificador único para cada elemento div
        hide_div_id = f"hide-div-{i}"
        st.markdown(f'<div class="hide-div" id="{hide_div_id}"></div>', unsafe_allow_html=True)

        st.markdown("---")  # Separador entre las imágenes
    if len(results) > 1:
        download_zip(results)
    else:
        download_result(results[0])

    st.markdown("---")  # Separador después de las imágenes


def remove_background(image):
    return remove(image)
def img_to_bytes(img):

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()



def download_result(image):
  
    original, result, name = image
    result_bytes = img_to_bytes(result)
    st.download_button(
        label="Descargar resultados",
        data=result_bytes,
        file_name=f"{Path(name).stem}_nobg.png",
        mime="image/png",
    )

    st.markdown("---")  # Separador después del botón de descarga



def download_zip(images):
    """Allows the user to download results as a ZIP file."""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for _, image, name in images:
            image_bytes = img_to_bytes(image)
            zip_file.writestr(f"{Path(name).stem}_nobg.png", image_bytes)

    st.download_button(
        label="Descargar",
        data=zip_buffer.getvalue(),
        file_name="images.zip",
        mime="application/zip",
    )

    st.markdown("---")  # Separador después del botón de descarga
def main():
    setup_page()
    initialize_session()
    uploaded_files = display_ui()
    process_and_display_images(uploaded_files)

if __name__ == "__main__":
    main()

