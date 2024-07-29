import streamlit as st
import lib as glib

def home():
    # Initialize session state to store generated images
    if 'main_page' not in st.session_state:
        st.session_state.main_page = None

    # Title
    st.title("TIG Ad Image Studio")
    st.markdown('''#### Amazon Titan Image Generator(TIG)를 사용하여 실제 상품으로 맞춤 광고 이미지 만들기''')
    st.markdown('''- 이 데모는 Amazon TIG를 사용하여 Amazon Bedrock으로 광고 이미지를 쉽게 제작하는 방법을 보여줍니다.''')
    st.markdown('''- [Github](https://github.com/madebybk/tig-ad-image-studio)에서 코드를 찾을 수 있습니다.''')
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
                placeholder="핸드백"
            )

            st.subheader("Generation Settings")
            prompt_text = st.text_area(
                label="Prompt text:",
                height=100,
                help="The prompt text",
                placeholder="5성급 호텔 안에 있는 핸드백, 반고흐 스타일"
            )
            painting_mode = "OUTPAINTING"
            
            generate_button = st.button("Generate", type="primary")

    # Main content area (right column)
    with col_main:
        st.subheader("Result")
        
        if generate_button:
            with st.spinner("이미지 생성 중... (30초 정도 걸릴 수 있습니다)"):
                if uploaded_image_file:
                    image_bytes = uploaded_image_file.getvalue()
                else:
                    image_bytes = glib.get_bytes_from_file("images/1_handbag.png")

                # Get generated images, translated masking prompt, and translated prompt text
                bedrock_output = glib.get_image_from_model(
                    prompt_content=prompt_text, 
                    image_bytes=image_bytes,
                    masking_mode="Prompt",
                    mask_prompt=mask_prompt,
                    painting_mode=painting_mode
                ) 

                # Save the generated images in the session
                st.session_state.main_page = bedrock_output

        # Display images and download buttons
        if st.session_state.main_page is not None:
            image_width_percentage = 30  # Adjust this value to change image width
            images_per_row = 100 // image_width_percentage

            # Optimized prompts
            st.write("Updated mask prompt:")
            st.code(st.session_state.main_page[1], language="markdown")
            st.write("Updated prompt text:")
            st.code(st.session_state.main_page[2], language="markdown")
            
            for i in range(0, len(st.session_state.main_page[0]), images_per_row):
                cols = st.columns([image_width_percentage] * images_per_row)
                for j, col in enumerate(cols):
                    if i + j < len(st.session_state.main_page[0]):
                        with col:
                            # Display the image
                            st.image(st.session_state.main_page[0][i + j], use_column_width=True)
                            
                            # Add download button
                            st.download_button(
                                label="⇩",
                                data=st.session_state.main_page[0][i + j],
                                file_name=f"generated_image_{i+j}.png",
                                mime="image/png",
                                key=f"download_{i+j}"  # Unique key for each button
                            )
