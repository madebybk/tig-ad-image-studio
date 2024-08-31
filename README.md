# TIG Ad Image Studio

이 데모는 전문적인 디자인 지식 없이 제품 이미지를 기반으로 한 맞춤형 광고 창작물을 쉽게 생성할 수 있게끔 돕는 이미지 생성 도구입니다.

Amazon Titan Image Generator(TIG) G1 v2를 사용하여 실제 상품으로 맞춤 광고 이미지 만들는 작업을 할 수 있습니다.

[AWS CDK](https://aws.amazon.com/cdk/)를 사용해 이 프로젝트를 AWS 환경에 배포 후 실제 제품의 사진을 사용해 이미지를 광고 이미지를 생성할 수 있습니다.

## Architecture

![Demo Architecture](frontend/images/DemoArchitecture.png)

이 데모는 Amazon Bedrock의 Anthropic Claude Sonnet v3.5와 Amazon Titan Image Generator (TIG) G1 v2를 사용합니다.

1. Claude Sonnet v3.5는 다양한 User Input 기반으로 이미지 생성 프롬프트를 작성해 줍니다.
2. Amazon TIG는 생성된 프롬프트 기반으로 이미지 생성을 합니다.

## Demo Video

샘플 데모 영상은 [여기](https://d39see23shaae8.cloudfront.net/TIG_Ad_Studio_Demo_BHK.mp4)서 볼 수 있습니다.

## 사전 요구사항

1. Docker 엔진이 실행되고 있는지 확인합니다.

2. AWS CDK를 설치합니다.

3. Amazon Bedrock에서 Model Access를 요청합니다.

- Anthropic Claude Sonnet v3.5

- Amazon Titan Image Generator G1 v2

## Deploy the CDK Stack

CDK를 [여기](https://docs.aws.amazon.com/ko_kr/cdk/v2/guide/getting_started.html)에 설명된 대로 설정하고 아래 명령어를 사용하여 모든 Dependency를 설치합니다. 

```
git clone https://github.com/madebybk/tig-ad-image-studio.git
npm install
npm run build
```

(CDK 배포가 처음이면) AWS CDK 애플리케이션을 CloudFormation 코드로 컴파일합니다.
```
cdk synth
```

AWS 계정에 스택을 배포합니다.
```
cdk deploy
```

## 웹 애플리케이션에 접속하기

배포가 완료되면 `TIGAdImageStudio-WebAppStack.webAppUrl`이라는 Output을 제공합니다. 이 IP 주소를 브라우저 입력창에 입력하여 TIG Ad Studio에 접속합니다.
