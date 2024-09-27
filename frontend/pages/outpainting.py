import streamlit as st
import lib as glib
import requests

def get_input_params(is_val_filled, value):
    if is_val_filled:
        return {"value": value}
    else:
        return {"placeholder": value}

def outpainting_content(input_image, prompt_input_vals, content_key, is_val_filled):
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

            st.warning("이미지 크기 제한이 있습니다. [Amazon TIG 공식 문서](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-titan-image.html#w315aac17c27c15b9b7c21b5b7)를 따라주세요.")
            
            if uploaded_image_file:
                uploaded_image_preview = glib.get_bytesio_from_bytes(uploaded_image_file.getvalue())
                st.image(uploaded_image_preview)
            else:
                st.image(input_image)
            
            st.subheader("Product Description")
            
            mask_prompt = st.text_input(
                label="제품 설명(필수):",
                help="간략하게 5단어 이하로 입력해 주세요",
                **get_input_params(is_val_filled, prompt_input_vals[content_key]["mask_prompt"])
            )

            st.subheader("Generation Settings")

            st.info("모두 선택 사항이지만, 더 많은 정보를 입력할수록 더 정확한 이미지 결과물을 얻을 수 있습니다.", icon="ℹ")

            prompt_background = st.text_input(
                label="배경/환경:",
                help="주요 대상이 위치한 장소",
                **get_input_params(is_val_filled, prompt_input_vals[content_key]["prompt_background"])
            )

            prompt_lighting = st.text_input(
                label="조명:",
                help="장면의 빛의 종류와 질",
                **get_input_params(is_val_filled, prompt_input_vals[content_key]["prompt_lighting"])
            )

            prompt_style = st.text_input(
                label="스타일:",
                help="원하는 예술적 스타일 또는 사진 기법",
                **get_input_params(is_val_filled, prompt_input_vals[content_key]["prompt_style"])
            )

            prompt_atmosphere = st.text_input(
                label="분위기/감정:",
                help="이미지의 전반적인 느낌이나 감정",
                **get_input_params(is_val_filled, prompt_input_vals[content_key]["prompt_atmosphere"])
            )

            prompt_colors = st.text_input(
                label="색상:",
                help="특정 색상 구성 또는 두드러진 색상",
                **get_input_params(is_val_filled, prompt_input_vals[content_key]["prompt_colors"])
            )

            prompt_composition = st.text_input(
                label="구도:",
                help="특정 프레임이나 레이아웃 선호도",
                **get_input_params(is_val_filled, prompt_input_vals[content_key]["prompt_composition"])
            )

            prompt_pose = st.text_input(
                label="행동/포즈:",
                help="대상이 하고 있는 행동",
                **get_input_params(is_val_filled, prompt_input_vals[content_key]["prompt_pose"])
            )

            prompt_time = st.text_input(
                label="시간대/계절:",
                help="장면이 일어나는 시기",
                **get_input_params(is_val_filled, prompt_input_vals[content_key]["prompt_time"])
            )

            prompt_texture = st.text_input(
                label="질감:",
                help="강조하고 싶은 특정 질감 요소",
                **get_input_params(is_val_filled, prompt_input_vals[content_key]["prompt_texture"])
            )

            prompt_additional = st.text_input(
                label="추가 사항:",
                help="포함할 다른 물체나 세부 사항",
                **get_input_params(is_val_filled, prompt_input_vals[content_key]["prompt_additional"])
            )

            num_output_images = st.slider("생성할 이미지 개수", min_value=1, max_value=5, step=1, value=5, key=f'slider_${content_key}')

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
            
            generate_button = st.button(
                label="Generate",
                type="primary",
                key=f"generate_button_{content_key}"
            )

            if generate_button and mask_prompt == "":
                st.error("필수 사항을 입력해주세요")

    # Main content area (right column)
    with col_main:
        st.subheader("Result")
        
        if generate_button and mask_prompt != "":
            with st.spinner("이미지 생성 중... (30초 정도 걸릴 수 있습니다)"):
                if uploaded_image_file:
                    image_bytes = uploaded_image_file.getvalue()
                else:
                    image_bytes = glib.get_bytes_from_file(input_image)

                bedrock_output = glib.query_generate_image_lambda(
                    prompt_content=prompt_text, 
                    image_bytes=image_bytes,
                    painting_mode="OUTPAINTING",
                    masking_mode="Prompt",
                    mask_prompt=mask_prompt,
                    num_output_images=num_output_images
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

def outpainting():
    st.markdown("## Prompt Examples")
    st.info("여기에 나오는 예시들은 Outpainting 기능으로 이미지의 가장자리를 확장하여 새로운 컨텐츠를 추가하는 기술을 보실 수 있습니다.", icon="ℹ")
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
        "handbag": {
            "mask_prompt": "핸드백",
            "prompt_background": "고급 부티크 매장",
            "prompt_lighting": "천장의 매입등에서 나오는 부드럽고 따뜻한 조명",
            "prompt_style": "럭셔리하고 세련된",
            "prompt_atmosphere": "세련되고 고급스러운 분위기",
            "prompt_colors": "베이지색 핸드백, 중성적이고 정제된 전체 색상 팔레트",
            "prompt_composition": "핸드백이 카운터 위에 있고, 배경에 선반이 있으며, 옆에 거울이 있음",
            "prompt_pose": "핸드백이 카운터 위에 놓여있음",
            "prompt_time": "낮 시간",
            "prompt_texture": "핸드백의 섬세한 디테일과 풍부한 질감",
            "prompt_additional": "광택 있는 대리석 카운터, 우아한 유리 선반, 다른 고급 액세서리들, 전신 거울",
        },
        "tumbler": {
            "mask_prompt": "녹색 텀블러",
            "prompt_background": "소박한 나무 테이블, 정원이 내려다보이는 햇살 가득한 파티오, 푸른 정원",
            "prompt_lighting": "부드러운 자연광, 은은한 그림자 형성",
            "prompt_style": "자연스럽고 신선한 느낌",
            "prompt_atmosphere": "상쾌하고 활기찬 분위기",
            "prompt_colors": "녹색 텀블러, 갈색 나무 테이블, 다채로운 꽃과 녹색 잎",
            "prompt_composition": "텀블러가 테이블 위에 있고, 주변에 레몬과 민트가 있으며, 배경에 정원이 보임",
            "prompt_pose": "텀블러가 테이블 위에 놓여있음",
            "prompt_time": "햇살이 비치는 낮 시간",
            "prompt_texture": "텀블러의 매끄러운 표면, 소박한 나무 테이블의 질감",
            "prompt_additional": "텀블러 옆에 있는 레몬 조각, 신선한 민트 잎",
        },
        "sofa": {
            "mask_prompt": "녹색 패브릭 소파",
            "prompt_background": "현대적이고 미니멀한 거실",
            "prompt_lighting": "바닥부터 천장까지 이어지는 큰 창문을 통해 들어오는 풍부한 자연광, 부드러운 그림자 형성",
            "prompt_style": "현대적, 미니멀리스트",
            "prompt_atmosphere": "초대하는 듯한, 평온한 분위기",
            "prompt_colors": "따뜻한 오프화이트 색 벽, 중성톤의 러그, 현대 미술 작품의 화려한 색상",
            "prompt_composition": "소파가 중앙에 있고, 왼쪽에 사이드 테이블, 오른쪽 벽에 미술 작품이 걸려 있음",
            "prompt_pose": "소파가 거실에 놓여있음",
            "prompt_time": "밝은 낮 시간",
            "prompt_texture": "패브릭 소파, 푹신한 러그",
            "prompt_additional": "세련된 사이드 테이블, 스타일리시한 램프, 작은 화분에 심긴 식물, 벽에 걸린 현대 미술 작품",
        },
        "shoes": {
            "mask_prompt": "러닝화 한 켤레",
            "prompt_background": "울창한 숲 속의 구불구불한 산책로, 배경에 안개 낀 산봉우리가 보임",
            "prompt_lighting": "나뭇잎 사이로 필터링되는 얼룩덜룩한 햇빛, 동적인 빛과 그림자 연출",
            "prompt_style": "자연스럽고 활동적인",
            "prompt_atmosphere": "신선하고 활기찬, 모험과 야외 활동을 암시하는 분위기",
            "prompt_colors": "화려한 색상의 러닝화, 녹색 나뭇잎, 갈색 흙길",
            "prompt_composition": "러닝화가 길 위에 놓여있고, 배경에 숲과 산이 보임",
            "prompt_pose": "러닝화가 산책로 위에 놓여있음",
            "prompt_time": "햇빛이 비치는 낮 시간, 여름",
            "prompt_texture": "다져진 흙길, 작은 자갈",
            "prompt_additional": "다져진 흙으로 만들어진 길, 작은 자갈들, 녹색 나뭇잎 캐노피, 안개 낀 산봉우리",
        },
        "coffee_maker": {
            "mask_prompt": "커피 메이커",
            "prompt_background": "현대적인 주방 조리대",
            "prompt_lighting": "창문을 통해 들어오는 아침 햇살",
            "prompt_style": "현대적이고 세련된",
            "prompt_atmosphere": "따뜻하고 초대하는 듯한 분위기",
            "prompt_colors": "광택 있는 쿼츠 조리대, 부드럽고 서로 어울리는 색상의 기하학적 타일, 갈색 나무 도마",
            "prompt_composition": "커피 메이커가 중앙에 있고, 왼쪽에 도마와 크루아상, 오른쪽에 허브 화분이 있음",
            "prompt_pose": "커피 메이커가 조리대 위에 놓여있음",
            "prompt_time": "아침 시간",
            "prompt_texture": "광택 있는 쿼츠 조리대의 미묘한 결, 기하학적 타일의 질감, 나무 도마의 질감",
            "prompt_additional": "기하학적 패턴의 타일 벽, 나무 도마, 갓 구운 크루아상 몇 개, 도자기 화분에 심긴 작은 허브 식물",
        },
    }

    outpainting_content(
        input_image="images/1_handbag.png",
        prompt_input_vals=prompt_input_vals,
        content_key="handbag",
        is_val_filled=True
    )
    st.divider()
    outpainting_content(
        input_image="images/2_tumbler.png",
        prompt_input_vals=prompt_input_vals,
        content_key="tumbler",
        is_val_filled=True
    )
    st.divider()
    outpainting_content(
        input_image="images/3_sofa.png",
        prompt_input_vals=prompt_input_vals,
        content_key="sofa",
        is_val_filled=True
    )
    st.divider()
    outpainting_content(
        input_image="images/4_running_shoes.png",
        prompt_input_vals=prompt_input_vals,
        content_key="shoes",
        is_val_filled=True
    )
    st.divider()
    outpainting_content(
        input_image="images/5_coffee_maker.png",
        prompt_input_vals=prompt_input_vals,
        content_key="coffee_maker",
        is_val_filled=True
    )
