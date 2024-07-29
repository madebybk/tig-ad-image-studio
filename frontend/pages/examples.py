import streamlit as st
import lib as glib

def exampleContent(input_image, mask_prompt_val, prompt_text_val, content_key):
    # Create a separate session for each example content
    if content_key not in st.session_state:
        st.session_state[content_key] = None

    # Create a container for the entire layout
    main_container = st.container()

    # Create two columns with custom widths
    col_sidebar, col_main = main_container.columns([35, 65])

    # Sidebar (left column)
    with col_sidebar:
        sidebar_container = st.container()
        with sidebar_container:
            st.subheader("Product Image")
            uploaded_image_file = st.file_uploader(
                label="Select an image",
                type=['png', 'jpg'],
                key=f"file_uploader_{content_key}"
            )
            
            if uploaded_image_file:
                uploaded_image_preview = glib.get_bytesio_from_bytes(uploaded_image_file.getvalue())
                st.image(uploaded_image_preview)
            else:
                st.image(input_image)
            
            st.subheader("Product Description")
            
            mask_prompt = st.text_input(
                label="Describe your product in 5 words or less:",
                help="Be concise and descriptive",
                value=mask_prompt_val,
                key=f"mask_prompt_{content_key}"
            )

            st.subheader("Generation Settings")
            prompt_text = st.text_area(
                label="Prompt text:",
                height=100,
                help="The prompt text",
                value=prompt_text_val,
                key=f"prompt_text_{content_key}"
            )
            painting_mode = "OUTPAINTING"
            
            generate_button = st.button(
                label="Generate",
                type="primary",
                key=f"generate_button_{content_key}"
            )

    # Main content area (right column)
    with col_main:
        st.subheader("Result")
        
        if generate_button:
            with st.spinner("Generating images... (This may take up to 30 seconds)"):
                if uploaded_image_file:
                    image_bytes = uploaded_image_file.getvalue()
                else:
                    image_bytes = glib.get_bytes_from_file(input_image)

                # Get generated images, translated masking prompt, and translated prompt text
                bedrock_output = glib.get_image_from_model(
                    prompt_content=prompt_text, 
                    image_bytes=image_bytes,
                    masking_mode="Prompt",
                    mask_prompt=mask_prompt,
                    painting_mode=painting_mode
                ) 

                st.write("Updated mask prompt:")
                st.code(bedrock_output[1], language="markdown")
                st.write("Updated prompt text:")
                st.code(bedrock_output[2], language="markdown")
                st.session_state[content_key] = bedrock_output[0]

        # Display images and download buttons
        if st.session_state[content_key] is not None:
            image_width_percentage = 30  # Adjust this value to change image width
            images_per_row = 100 // image_width_percentage
            
            for i in range(0, len(st.session_state[content_key]), images_per_row):
                cols = st.columns([image_width_percentage] * images_per_row)
                for j, col in enumerate(cols):
                    if i + j < len(st.session_state[content_key]):
                        with col:
                            # Display the image
                            st.image(st.session_state[content_key][i + j], use_column_width=True)
                            
                            # Add download button
                            st.download_button(
                                label="⇩",
                                data=st.session_state[content_key][i + j],
                                file_name=f"generated_image_{i+j}.png",
                                mime="image/png",
                                key=f"download_{content_key}_{i+j}"  # Unique key for each button
                            )

def examples():
    st.markdown("## Prompt Examples")
    st.info("여기에 나오는 예시를 통해 여러 프롬프트 방식으로 다양한 이미지 결과물을 생성할 수 있다는 것을 보실 수 있습니다. 프롬프트와 결과물의 상관관계를 보여줄 수 있도록 예시는 영어로 준비되어있습니다.", icon="ℹ")
    exampleContent("images/1_handbag.png", "a handbag", "a handbag in a luxury hotel", "example_1")
    st.divider()
    exampleContent("images/2_tumbler.png", "a green tumbler", "A green tumbler on a kitchen counter, green plants in the background", "example_2")
    st.divider()
    exampleContent("images/3_sofa.png", "a beige sofa", "A sofa in a simple beige walls with galleries, classic marble floors", "example_3")