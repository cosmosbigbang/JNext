"""
밈 이미지 생성 및 자막 합성 유틸리티
DALL-E 3로 이미지 생성 → Pillow로 자막 합성
"""
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import os


class MemeGenerator:
    """밈 이미지 생성 및 자막 합성"""
    
    # 임팩트 폰트 경로 (밈 스타일)
    FONT_PATH = os.getenv('MEME_FONT_PATH', 'impact.ttf')
    
    @staticmethod
    def generate_image_dalle(prompt, api_key):
        """
        DALL-E 3로 밈 이미지 생성 (자막 없이)
        
        Args:
            prompt: 이미지 생성 프롬프트 (영어 권장)
            api_key: OpenAI API 키
        
        Returns:
            str: 생성된 이미지 URL
        """
        import openai
        client = openai.OpenAI(api_key=api_key)
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=f"{prompt}. Meme style, no text overlay.",
            size="1024x1024",
            quality="standard",
            n=1
        )
        
        return response.data[0].url
    
    @staticmethod
    def download_image(url):
        """
        URL에서 이미지 다운로드
        
        Args:
            url: 이미지 URL
        
        Returns:
            PIL.Image: 이미지 객체
        """
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        return img
    
    @staticmethod
    def add_meme_text(image, top_text="", bottom_text="", font_size=60):
        """
        이미지에 밈 스타일 자막 추가
        
        Args:
            image: PIL.Image 객체
            top_text: 상단 자막
            bottom_text: 하단 자막
            font_size: 폰트 크기
        
        Returns:
            PIL.Image: 자막이 합성된 이미지
        """
        # 이미지 복사 (원본 보존)
        img = image.copy()
        draw = ImageDraw.Draw(img)
        
        width, height = img.size
        
        # 폰트 로드 (임팩트 없으면 기본 폰트)
        try:
            font = ImageFont.truetype(MemeGenerator.FONT_PATH, font_size)
        except:
            # 한글 지원 폰트 fallback
            try:
                font = ImageFont.truetype("malgun.ttf", font_size)  # Windows 맑은고딕
            except:
                font = ImageFont.load_default()
        
        # 상단 자막
        if top_text:
            # 텍스트 크기 계산
            bbox = draw.textbbox((0, 0), top_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 중앙 정렬
            x = (width - text_width) // 2
            y = 30
            
            # 외곽선 (검정)
            outline_width = 3
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), top_text, 
                                  font=font, fill='black')
            
            # 메인 텍스트 (흰색)
            draw.text((x, y), top_text, font=font, fill='white')
        
        # 하단 자막
        if bottom_text:
            bbox = draw.textbbox((0, 0), bottom_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (width - text_width) // 2
            y = height - text_height - 30
            
            # 외곽선
            outline_width = 3
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), bottom_text, 
                                  font=font, fill='black')
            
            # 메인 텍스트
            draw.text((x, y), bottom_text, font=font, fill='white')
        
        return img
    
    @staticmethod
    def create_meme(prompt, top_text="", bottom_text="", api_key=None):
        """
        밈 생성 전체 플로우 (이미지 생성 → 자막 합성)
        
        Args:
            prompt: DALL-E 프롬프트
            top_text: 상단 자막
            bottom_text: 하단 자막
            api_key: OpenAI API 키
        
        Returns:
            dict: {
                'original_url': 원본 이미지 URL,
                'final_image': 자막 합성된 PIL.Image,
                'top_text': 상단 자막,
                'bottom_text': 하단 자막
            }
        """
        # 1. 이미지 생성
        original_url = MemeGenerator.generate_image_dalle(prompt, api_key)
        
        # 2. 이미지 다운로드
        original_image = MemeGenerator.download_image(original_url)
        
        # 3. 자막 합성
        final_image = MemeGenerator.add_meme_text(
            original_image, 
            top_text, 
            bottom_text
        )
        
        return {
            'original_url': original_url,
            'original_image': original_image,
            'final_image': final_image,
            'top_text': top_text,
            'bottom_text': bottom_text
        }
    
    @staticmethod
    def save_image(image, filepath):
        """
        이미지 저장
        
        Args:
            image: PIL.Image 객체
            filepath: 저장 경로
        """
        image.save(filepath, format='PNG', quality=95)
        return filepath


# 사용 예시
"""
from api.meme_generator import MemeGenerator
import os

# 밈 생성
result = MemeGenerator.create_meme(
    prompt="A cat sitting on a computer, looking confused",
    top_text="내가 코드를 짰을 때",
    bottom_text="컴파일러가 에러를 뱉을 때",
    api_key=os.getenv('OPENAI_API_KEY')
)

# 저장
MemeGenerator.save_image(result['final_image'], 'meme_output.png')

# Firestore 저장 데이터
doc_data = {
    '제목': '코딩 밈',
    '밈이미지URL': result['original_url'],
    '밈자막상단': result['top_text'],
    '밈자막하단': result['bottom_text'],
    '밈합성이미지URL': 'https://your-storage.com/meme_output.png',  # 업로드 후 URL
    '밈생성모델': 'DALL-E-3',
    '밈스타일': '일반'
}
"""
