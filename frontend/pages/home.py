import streamlit as st
import lib as glib
from .inpainting import inpainting_content
from .outpainting import outpainting_content

def home():
    # Title
    st.title("TIG Ad Image Studio")
    st.markdown('''#### Amazon Titan Image Generator(TIG)를 사용하여 실제 상품으로 맞춤 광고 이미지 만들기''')
    st.markdown('''- 이 데모는 Amazon TIG를 사용하여 Amazon Bedrock으로 광고 이미지를 쉽게 제작하는 방법을 보여줍니다.''')
    st.markdown('''- [Github](https://github.com/madebybk/tig-ad-image-studio)에서 코드를 찾을 수 있습니다.''')
    st.divider()

    # Outpainting section
    st.markdown('''#### TIG를 활용해 백그라운드 이미지 생성''')
    st.success('''이 도구는 TIG의 Outpainting 기능을 활용해 기존 이미지의 가장자리를 확장하여 새로운 컨텐츠를 추가하는 방식을 사용합니다. Outpainting 기능은 위 "이미지 생성 예시" 탭에서 더 자세히 보실 수 있습니다.''')
    
    outpainting_prompt_input_vals = {
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
    }

    outpainting_content(
        input_image="images/1_handbag.png",
        prompt_input_vals=outpainting_prompt_input_vals,
        content_key="handbag",
        is_val_filled=False
    )

    st.divider()

    # Inpainting section
    st.markdown('''#### TIG를 활용해 이미지 수정''')
    st.success('''이 도구는 TIG의 Inpainting 기능을 활용해 기존 이미지의 특정 부분을 채우거나 수정하는 기술을 보실 수 있습니다. Inpainting 기능은 위 "이미지 수정 예시" 탭에서 더 자세히 보실 수 있습니다.''')

    inpainting_prompt_input_vals = {
        "apartment": {
            "mask_prompt": "거실 중앙의 검은 테이블",
            "prompt_original": "현대적인 아파트 거실 이미지, 중앙에 검은 테이블이 있음",
            "prompt_new": "기존의 검은 테이블을 광택 있는 흰색 대리석 테이블로 변경",
            "prompt_style": "현대적이고 세련된 스타일 유지",
            "prompt_atmosphere": "밝고 깨끗한 느낌, 고급스럽고 현대적인 분위기",
            "prompt_colors": "흰색 (약간의 회색 대리석 무늬 포함)",
            "prompt_additional": "대리석의 자연스러운 결, 테이블 표면에 은은하게 반사되는 주변 조명",
        },
    }

    inpainting_content(
        input_image="images/6_apartment.png",
        prompt_input_vals=inpainting_prompt_input_vals,
        content_key="apartment",
        is_val_filled=False
    )
