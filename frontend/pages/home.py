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
                label="제품 설명(필수):",
                help="간략하게 5단어 이하로 입력해 주세요",
                placeholder="핸드백"
            )

            st.subheader("Generation Settings")

            st.info("모두 선택 사항이지만, 더 많은 정보를 입력할수록 더 정확한 이미지 결과물을 얻을 수 있습니다.", icon="ℹ")

            prompt_background = st.text_input(
                label="배경/환경:",
                help="주요 대상이 위치한 장소",
                placeholder="고급 부티크 매장"
            )

            prompt_lighting = st.text_input(
                label="조명:",
                help="장면의 빛의 종류와 질",
                placeholder="천장의 매입등에서 나오는 부드럽고 따뜻한 조명"
            )

            prompt_style = st.text_input(
                label="스타일:",
                help="원하는 예술적 스타일 또는 사진 기법",
                placeholder="럭셔리하고 세련된"
            )

            prompt_atmosphere = st.text_input(
                label="분위기/감정:",
                help="이미지의 전반적인 느낌이나 감정",
                placeholder="세련되고 고급스러운 분위기"
            )

            prompt_colors = st.text_input(
                label="색상:",
                help="특정 색상 구성 또는 두드러진 색상",
                placeholder="베이지색 핸드백, 중성적이고 정제된 전체 색상 팔레트"
            )

            prompt_composition = st.text_input(
                label="구도:",
                help="특정 프레임이나 레이아웃 선호도",
                placeholder="핸드백이 카운터 위에 있고, 배경에 선반이 있으며, 옆에 거울이 있음"
            )

            prompt_pose = st.text_input(
                label="행동/포즈:",
                help="대상이 하고 있는 행동",
                placeholder="핸드백이 카운터 위에 놓여있음"
            )

            prompt_time = st.text_input(
                label="시간대/계절:",
                help="장면이 일어나는 시기",
                placeholder="낮 시간"
            )

            prompt_texture = st.text_input(
                label="질감:",
                help="강조하고 싶은 특정 질감 요소",
                placeholder="핸드백의 섬세한 디테일과 풍부한 질감"
            )

            prompt_additional = st.text_input(
                label="추가 사항:",
                help="포함할 다른 물체나 세부 사항",
                placeholder="광택 있는 대리석 카운터, 우아한 유리 선반, 다른 고급 액세서리들, 전신 거울"
            )

            prompt_text = "{" + f"""
            "주요 대상": {mask_prompt},
            "배경/환경": {prompt_background},
            "조명": {prompt_lighting},
            "스타일": {prompt_style},
            "분위기/감정": {prompt_atmosphere},
            "Colors": {prompt_colors},
            "Composition": {prompt_composition},
            "Action/Pose": {prompt_pose},
            "Time of day/Season": {prompt_time},
            "Textures": {prompt_texture},
            "Additional elements": {prompt_additional}
            """ + "}"
            
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
                    mask_prompt=mask_prompt
                ) 

                # Save the generated images in the session
                st.session_state.main_page = bedrock_output

        # Display images and download buttons
        if st.session_state.main_page is not None:
            image_width_percentage = 30  # Adjust this value to change image width
            images_per_row = 100 // image_width_percentage

            # Optimized prompts
            st.write("Updated mask prompt:")
            st.info(st.session_state.main_page[1]) 
            st.write("Updated prompt text:")
            st.info(st.session_state.main_page[2])
            
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
