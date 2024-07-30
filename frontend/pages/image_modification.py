import streamlit as st
import lib as glib

def image_modification_content(input_image, prompt_input_vals, content_key):
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
                label="수정할 부분(필수):",
                help="수정 영역을 간략하게 5단어 이하로 입력해 주세요",
                value=prompt_input_vals[content_key]["mask_prompt"]
            )

            prompt_background = st.text_input(
                label="원본 이미지(필수):",
                help="현재 이미지에 대한 간단한 설명",
                value=prompt_input_vals[content_key]["prompt_original"]
            )

            prompt_lighting = st.text_input(
                label="새로운 내용(필수):",
                help="수정 영역에 추가하거나 변경하고 싶은 요소",
                value=prompt_input_vals[content_key]["prompt_new"]
            )

            st.subheader("Generation Settings")

            st.info("모두 선택 사항이지만, 더 많은 정보를 입력할수록 더 정확한 이미지 결과물을 얻을 수 있습니다.", icon="ℹ")

            prompt_style = st.text_input(
                label="스타일:",
                help="원하는 예술적 스타일 또는 사진 기법",
                value=prompt_input_vals[content_key]["prompt_style"]
            )

            prompt_atmosphere = st.text_input(
                label="주변 환경과의 조화:",
                help="원하는 스타일이나 분위기",
                value=prompt_input_vals[content_key]["prompt_atmosphere"]
            )

            prompt_colors = st.text_input(
                label="색상:",
                help="새로운 요소의 주요 색상",
                value=prompt_input_vals[content_key]["prompt_colors"]
            )

            prompt_additional = st.text_input(
                label="추가 사항:",
                help="포함하고 싶은 특정 세부 사항",
                value=prompt_input_vals[content_key]["prompt_additional"]
            )

            prompt_text = "{" + f"""
            "주요 대상": {mask_prompt},
            "배경/환경": {prompt_background},
            "조명": {prompt_lighting},
            "스타일": {prompt_style},
            "분위기/감정": {prompt_atmosphere},
            "Colors": {prompt_colors},
            "Additional elements": {prompt_additional}
            """ + "}"
            
            generate_button = st.button(
                label="Generate",
                type="primary",
                key=f"generate_button_{content_key}"
            )

    # Main content area (right column)
    with col_main:
        st.subheader("Result")
        
        if generate_button:
            with st.spinner("이미지 생성 중... (30초 정도 걸릴 수 있습니다)"):
                if uploaded_image_file:
                    image_bytes = uploaded_image_file.getvalue()
                else:
                    image_bytes = glib.get_bytes_from_file(input_image)

                # Get generated images, translated masking prompt, and translated prompt text
                bedrock_output = glib.get_image_from_model(
                    prompt_content=prompt_text, 
                    image_bytes=image_bytes,
                    painting_mode="INPAINTING",
                    masking_mode="Prompt",
                    mask_prompt=mask_prompt
                ) 
                
                st.session_state[content_key] = bedrock_output
                
        # Display images and download buttons
        if st.session_state[content_key] is not None:
            image_width_percentage = 30  # Adjust this value to change image width
            images_per_row = 100 // image_width_percentage

            # Optimized prompts
            st.write("Updated mask prompt:")
            st.info(st.session_state[content_key][1])
            st.write("Updated prompt text:")
            st.info(st.session_state[content_key][2])
            
            for i in range(0, len(st.session_state[content_key][0]), images_per_row):
                cols = st.columns([image_width_percentage] * images_per_row)
                for j, col in enumerate(cols):
                    if i + j < len(st.session_state[content_key][0]):
                        with col:
                            # Display the image
                            st.image(st.session_state[content_key][0][i + j], use_column_width=True)
                            
                            # Add download button
                            st.download_button(
                                label="⇩",
                                data=st.session_state[content_key][0][i + j],
                                file_name=f"generated_image_{i+j}.png",
                                mime="image/png",
                                key=f"download_{content_key}_{i+j}"  # Unique key for each button
                            )

def image_modification():
    st.markdown("## Prompt Examples")
    st.info("여기에 나오는 예시들은 Inpainting 기능으로 이미지의 특정 부분을 채우거나 수정하는 기술을 보실 수 있습니다.", icon="ℹ")
    st.markdown("## Prompt Techniques")
    st.markdown("다음과 같은 Prompt 방법들이 이미지 생성 개선에 도움이 될 수 있습니다.")
    st.markdown(
    """
    - **세부적인 설명**: 생생하고 구체적인 단어와 문구를 사용하여 주요 시각적 세부 사항을 포착합니다.
    - **스타일과 분위기**: 대화체, 시적, 유머러스 등의 톤을 사용하여 생성된 이미지의 분위기/스타일에 영향을 줍니다.
    - **구조**: 쉼표나 콜론을 사용하여 프롬프트 요소를 논리적으로 정렬합니다.
    - **가이드 세부 사항**: 객체 모양, 색상, 조명, 배경 장면 등 구체적인 세부 사항을 추가하여 이미지 생성을 안내합니다.
    - **배경 설명**: 아웃페인팅을 위해 배경을 자세히 설명합니다.
    - **전체 장면 설명**: 때로는 마스크 내부의 객체를 포함한 전체 장면을 설명하는 것이 도움이 됩니다.
    - **컨텍스트 포함**: 객체의 컨텍스트나 배경에 대한 세부 사항을 포함하여 더 사실적인 결과를 얻습니다.
    - **조명 상세화**: 장면의 조명에 대해 구체적으로 설명하여 분위기를 설정합니다.
    - **보존할 세부 사항 지정**: 이미지 변형 시 보존하고 싶은 모든 세부 사항을 지정합니다.
    """)
    st.divider()

    prompt_input_vals = {
        "apartment": {
            "mask_prompt": "거실 중앙의 검은 테이블",
            "prompt_original": "현대적인 아파트 거실 이미지, 중앙에 검은 테이블이 있음",
            "prompt_new": "기존의 검은 테이블을 광택 있는 흰색 대리석 테이블로 변경",
            "prompt_style": "현대적이고 세련된 스타일 유지",
            "prompt_atmosphere": "밝고 깨끗한 느낌, 고급스럽고 현대적인 분위기",
            "prompt_colors": "흰색 (약간의 회색 대리석 무늬 포함)",
            "prompt_additional": "대리석의 자연스러운 결, 테이블 표면에 은은하게 반사되는 주변 조명",
        },
        "sofa_rug": {
            "mask_prompt": "바닥에 있는 러그",
            "prompt_original": "현대적인 거실 이미지, 중앙에 검은 녹색 패브릭 소파가 있고 바닥에 베이지색 러그가 있음",
            "prompt_new": "기존의 베이지색 러그를 핑크색 러그로 변경",
            "prompt_style": "깔끔하고 세련된 스타일 유지",
            "prompt_atmosphere": "밝고 깨끗한 느낌",
            "prompt_colors": "핑크색",
            "prompt_additional": "러그는 보들보들한 느낌",
        },
    }

    image_modification_content(
        "images/6_apartment.png",
        prompt_input_vals,
        "apartment"
    )
    st.divider()
    image_modification_content(
        "images/7_sofa_rug.png",
        prompt_input_vals,
        "sofa_rug"
    )
