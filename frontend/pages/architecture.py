import streamlit as st

def architecture():
    st.title("AWS Architecture - TIG Ad Image Studio")
    st.markdown(
        """
        이 데모는 Amazon Bedrock의 Anthropic Claude Sonnet v3와 Amazon Titan Image Generator (TIG)를 사용합니다. 
        * Claude Sonnet v3는 다양한 User Input 기반으로 이미지 생성 프롬프트를 작성해 줍니다.
        * Amazon TIG는 생성된 프롬프트 기반으로 이미지 생성을 합니다.
        """
    )
    st.image("images/Demo-Architecture.png", use_column_width="auto", caption="AWS Architecture", width=8)
