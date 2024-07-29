import streamlit as st
import lib as glib

def exampleContent(input_image, mask_prompt_val, prompt_text_val, prompt_breakdown, content_key):
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
                height=220,
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
            st.markdown("#### Prompt Breakdown")
            st.info(prompt_breakdown)

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
    st.markdown("## Prompt Techniques")
    st.markdown("다음과 같은 Prompt 방법들이 이미지 생성 개선에 도움이 될 수 있습니다.")
    st.markdown(
    """
    - **세부적인 설명**: 생생하고 구체적인 단어와 문구를 사용하여 주요 시각적 세부 사항을 포착합니다.
    - **스타일과 분위기**: 대화체, 시적, 유머러스 등의 톤을 사용하여 생성된 이미지의 분위기/스타일에 영향을 줍니다.
    - **구조**: 쉼표나 콜론을 사용하여 프롬프트 요소를 논리적으로 정렬합니다.
    - **가이드 세부 사항**: 객체 모양, 색상, 조명, 배경 장면 등 구체적인 세부 사항을 추가하여 이미지 생성을 안내합니다.
    - **네거티브 프롬프트**: 원하지 않는 요소를 피하기 위해 이미지에 포함되지 않아야 할 것을 지정합니다.
    - **반복적 개선**: 결과를 바탕으로 여러 주기를 통해 프롬프트를 점진적으로 편집합니다.
    - **예시에서 영감 얻기**: 기존 이미지의 설명을 활용하여 프롬프트 구성에 참고합니다.
    - **배경 설명**: 아웃페인팅을 위해 배경을 자세히 설명합니다.
    - **전체 장면 설명**: 때로는 마스크 내부의 객체를 포함한 전체 장면을 설명하는 것이 도움이 됩니다.
    - **컨텍스트 포함**: 객체의 컨텍스트나 배경에 대한 세부 사항을 포함하여 더 사실적인 결과를 얻습니다.
    - **조명 상세화**: 장면의 조명에 대해 구체적으로 설명하여 분위기를 설정합니다.
    - **보존할 세부 사항 지정**: 이미지 변형 시 보존하고 싶은 모든 세부 사항을 지정합니다.
    """)
    st.divider()
    exampleContent(
        "images/1_handbag.png",
        "A handbag",
        "A luxurious beige handbag displayed in an upscale boutique setting. The bag rests on a polished marble counter. Behind it, elegant glass shelves showcase other high-end accessories. Soft, warm lighting from recessed ceiling fixtures creates a sophisticated ambiance, highlighting the bag's fine details and rich texture. A full-length mirror to the side reflects part of the bag, adding depth to the scene. The overall color palette is neutral and refined, emphasizing the bag's quality and style.",
        """
        1. 아웃페인팅할 배경을 상세히 설명
        2. 조명과 분위기에 대한 정보 포함
        3. 제품의 매력을 높이는 맥락적 요소(레몬, 민트) 추가
        4. 원래 객체(텀블러)를 포함한 전체 장면 묘사
        """,
        "example_1"
    )
    st.divider()
    exampleContent(
        "images/2_tumbler.png", 
        "A green tumbler", 
        "A sleek green tumbler on a rustic wooden table. The table is placed on a sunny patio overlooking a lush garden. Soft natural light illuminates the scene, creating gentle shadows and highlighting the tumbler's smooth surface. A slice of lemon and a sprig of fresh mint rest beside the tumbler, suggesting a refreshing beverage. In the background, colorful flowers and green foliage provide a vibrant, natural setting.", 
        """
        1. 제품의 인지된 가치를 높이는 맥락 조성
        2. 재료와 표면에 대한 상세한 설명
        3. 조명과 그것이 제품에 미치는 영향에 대한 세심한 주의
        4. 시각적 흥미를 더하기 위한 반사 표면 사용
        """,
        "example_2"
    )
    st.divider()
    exampleContent(
        "images/3_sofa.png", 
        "A green fabric sofa", 
        "A comfortable green fabric sofa in a modern, minimalist living room. The room has large floor-to-ceiling windows allowing abundant natural light to flood in, casting soft shadows. The walls are painted in a warm off-white color. A plush area rug in neutral tones sits beneath the sofa. To the left, a sleek side table holds a stylish lamp and a small potted plant. On the right, a contemporary art piece hangs on the wall, adding a pop of color. The overall atmosphere is inviting and serene.", 
        """
        1. 방과 그 요소들에 대한 상세한 설명
        2. 조명과 분위기에 대한 주의
        3. 보완적인 장식 아이템 포함
        4. 새로운 맥락 내에서 원래 소파에 대한 설명
        """,
        "example_3"
    )
    st.divider()
    exampleContent(
        "images/4_running_shoes.png", 
        "A pair of colorful running shoes", 
        "A pair of colorful running shoes positioned on a winding trail in a lush forest. The path is made of packed earth with a few small pebbles, suggesting a challenging yet beautiful running route. Dappled sunlight filters through the canopy of green leaves overhead, creating a dynamic play of light and shadow on the shoes and surroundings. In the background, a misty mountain peak is visible, hinting at adventure and outdoor activity. The atmosphere is fresh and invigorating, with a sense of motion and energy.", 
        """
        1. 제품을 의도된 사용 환경에 배치
        2. 매력적인 장면을 만들기 위한 자연 요소의 풍부한 묘사
        3. 시각적 흥미를 높이기 위한 조명 효과 사용
        4. 배경을 통한 감정적 연결 조성(모험, 에너지)
        """,
        "example_4"
    )
    st.divider()
    exampleContent(
        "images/5_coffee_maker.png", 
        "A coffee maker", 
        "A coffee maker on a contemporary kitchen countertop. The counter is made of polished quartz with subtle veining. Behind the coffee maker, a backsplash of geometric tiles in soft, complementary colors adds visual interest. To the left, a wooden cutting board holds a few freshly baked croissants. To the right, a small potted herb (possibly basil or mint) sits in a ceramic planter. Morning sunlight streams in from a window just out of frame, creating a warm, inviting atmosphere.", 
        """
        1. 현실적이고 매력적인 주방 환경 조성
        2. 제품의 매력을 높이는 보완적 요소 추가
        3. 특정 분위기를 만들기 위한 조명 사용
        4. 장면을 더 매력적으로 만들기 위한 감각적 세부 사항(갓 구운 빵, 허브) 포함
        """,
        "example_5"
    )
