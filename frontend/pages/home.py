import streamlit as st
import lib as glib

def home():
    # Initialize session state to store generated images
    if 'generated_images' not in st.session_state:
        st.session_state.generated_images = None

    # Title
    st.title("TIG Ad Image Studio")
    st.markdown('''#### Creating Custom Advertisement Images with Real Products Using Amazon Titan Image Generator (TIG)''')
    st.markdown('''- This demo showcases how to easily create advertisement images with Amazon Bedrock using Amazon TIG.''')
    st.markdown('''- You can find the code on [Github](https://github.com/madebybk/tig-ad-image-studio).''')
    st.divider()

    # Create a container for the entire layout
    main_container = st.container()

    # Create two columns with custom widths
    col_sidebar, col_main = main_container.columns([35, 65])

    # Sidebar (left column)
    with col_sidebar:
        sidebar_container = st.container()
        with sidebar_container:
            st.subheader("Product Image")
            uploaded_image_file = st.file_uploader("Select an image", type=['png', 'jpg'])
            
            if uploaded_image_file:
                uploaded_image_preview = glib.get_bytesio_from_bytes(uploaded_image_file.getvalue())
                st.image(uploaded_image_preview)
            else:
                st.image("images/1_handbag.png")
            
            st.subheader("Product Description")
            
            mask_prompt = st.text_input(
                label="Describe your product in 5 words or less:",
                help="Be concise and descriptive",
                value="a handbag"
            )

            st.subheader("Generation Settings")
            prompt_text = st.text_area(
                label="Prompt text:",
                height=100,
                help="The prompt text",
                value="a handbag in a luxury hotel"
            )
            painting_mode = "OUTPAINTING"
            
            generate_button = st.button("Generate", type="primary")

    # Main content area (right column)
    with col_main:
        st.subheader("Result")
        
        if generate_button:
            with st.spinner("Generating images... (This may take up to 30 seconds)"):
                if uploaded_image_file:
                    image_bytes = uploaded_image_file.getvalue()
                else:
                    image_bytes = glib.get_bytes_from_file("images/1_handbag.png")
                st.session_state.generated_images = glib.get_image_from_model(
                    prompt_content=prompt_text, 
                    image_bytes=image_bytes,
                    masking_mode="Prompt",
                    mask_prompt=mask_prompt,
                    painting_mode=painting_mode
                )

        # Display images and download buttons
        if st.session_state.generated_images is not None:
            image_width_percentage = 30  # Adjust this value to change image width
            images_per_row = 100 // image_width_percentage
            
            for i in range(0, len(st.session_state.generated_images), images_per_row):
                cols = st.columns([image_width_percentage] * images_per_row)
                for j, col in enumerate(cols):
                    if i + j < len(st.session_state.generated_images):
                        with col:
                            # Display the image
                            st.image(st.session_state.generated_images[i + j], use_column_width=True)
                            
                            # Add download button
                            st.download_button(
                                label="⇩",
                                data=st.session_state.generated_images[i + j],
                                file_name=f"generated_image_{i+j}.png",
                                mime="image/png",
                                key=f"download_{i+j}"  # Unique key for each button
                            )
