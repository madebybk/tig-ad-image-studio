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
        prompt_input_vals=outpainting_prompt_input_vals,
        content_key="handbag",
        is_val_filled=True
    )

    st.divider()
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
    inpainting_content(
        input_image="images/6_apartment.png",
        prompt_input_vals=inpainting_prompt_input_vals,
        content_key="apartment",
        is_val_filled=True
    )
