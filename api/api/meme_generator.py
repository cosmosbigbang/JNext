"""
밈 이미지 생성 및 자막 합성 유틸리티
하이노밸런스 시트콤 캐릭터 이미지 + Pillow 자막 합성
"""
from PIL import Image, ImageDraw, ImageFont
import os
import glob
from pathlib import Path
from datetime import datetime


class MemeGenerator:
    """밈 이미지 생성 및 자막 합성 (시트콤 캐릭터 기반)"""
    
    # 밈 이미지 폴더 경로
    MEME_IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'meme_images')
    
    # 캐릭터 이미지 매핑 (파일명 기준)
    CHARACTER_IMAGES = {
        'J': None,  # J님 (실제 사진 또는 캐릭터)
        '지피': '지피다운.png',  # 남자 캐릭터 (해석자)
        '아내_긴머리': None,  # 여자 캐릭터 긴머리
        '아내_커트': None,  # 여자 캐릭터 커트머리
        '아내': None  # 기본 아내 (긴머리/커트 중 선택)
    }
    
    # 임팩트 폰트 경로 (밈 스타일)
    FONT_PATH = os.getenv('MEME_FONT_PATH', 'impact.ttf')
    
    @staticmethod
    def generate_character_image(character_name, style_prompt, save_filename=None):
        """
        DALL-E 3로 캐릭터 이미지 생성 (1회성, 기본 이미지 제작용)
        
        Args:
            character_name: 캐릭터 이름 (예: '지피', '아내_긴머리')
            style_prompt: 스타일 프롬프트 (예: '30대 남성, 안경, 캐주얼한 옷')
            save_filename: 저장할 파일명 (None이면 자동 생성)
        
        Returns:
            dict: {
                'image_url': DALL-E 생성 이미지 URL,
                'local_path': 로컬 저장 경로,
                'character_name': 캐릭터 이름
            }
        """
        from django.conf import settings
        
        client = settings.GPT_CLIENT
        
        # DALL-E 3 프롬프트 구성
        full_prompt = f"""Create a consistent character portrait for a Korean sitcom meme.
Character: {character_name}
Style: {style_prompt}

Requirements:
- Clean, simple background (solid color or minimal)
- Front-facing portrait
- Neutral or slightly smiling expression
- Consistent style for repeated use
- High quality, clear features
- Korean features
- Waist-up or head-and-shoulders shot"""
        
        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=full_prompt,
                size="1024x1024",
                quality="hd",  # 고품질
                n=1
            )
            
            image_url = response.data[0].url
            
            # 이미지 다운로드 및 저장
            import requests
            from PIL import Image
            from io import BytesIO
            
            img_response = requests.get(image_url)
            img = Image.open(BytesIO(img_response.content))
            
            # 저장 경로
            if save_filename is None:
                save_filename = f"{character_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            local_path = os.path.join(MemeGenerator.MEME_IMAGES_DIR, save_filename)
            img.save(local_path, format='PNG', quality=95)
            
            print(f"[캐릭터 생성 성공] {character_name} → {save_filename}")
            
            return {
                'image_url': image_url,
                'local_path': local_path,
                'character_name': character_name,
                'filename': save_filename
            }
            
        except Exception as e:
            print(f"[캐릭터 생성 실패] {str(e)}")
            raise
    
    @staticmethod
    def get_character_image_path(character='지피'):
        """
        캐릭터 이미지 경로 조회
        
        Args:
            character: '지피' 또는 '아내'
        
        Returns:
            str: 이미지 파일 절대 경로
        """
        if character not in MemeGenerator.CHARACTER_IMAGES:
            raise ValueError(f"알 수 없는 캐릭터: {character}. '지피' 또는 '아내'만 가능합니다.")
        
        filename = MemeGenerator.CHARACTER_IMAGES[character]
        
        if filename is None:
            # 아내 캐릭터 이미지 자동 탐색 (지피 제외)
            all_images = glob.glob(os.path.join(MemeGenerator.MEME_IMAGES_DIR, '*.png'))
            zippy_path = os.path.join(MemeGenerator.MEME_IMAGES_DIR, MemeGenerator.CHARACTER_IMAGES['지피'])
            
            # 지피 이미지 제외한 첫 번째 이미지
            for img_path in all_images:
                if img_path != zippy_path:
                    return img_path
            
            raise FileNotFoundError(f"{character} 캐릭터 이미지를 찾을 수 없습니다.")
        
        image_path = os.path.join(MemeGenerator.MEME_IMAGES_DIR, filename)
        
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"캐릭터 이미지를 찾을 수 없습니다: {image_path}")
        
        return image_path
    
    @staticmethod
    def load_image(image_path):
        """
        로컬 이미지 로드
        
        Args:
            image_path: 이미지 파일 경로
        
        Returns:
            PIL.Image: 이미지 객체
        """
        img = Image.open(image_path)
        
        # RGBA 모드로 변환 (투명도 지원)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
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
    def create_meme(character='지피', dialogue='', top_text='', bottom_text='', style='시트콤', context=''):
        """
        밈 생성 전체 플로우 (캐릭터 이미지 + 자막 합성)
        
        Args:
            character: '지피' 또는 '아내' (캐릭터 선택)
            dialogue: 대사 (자동으로 상하단 분리)
            top_text: 상단 자막 (dialogue보다 우선)
            bottom_text: 하단 자막 (dialogue보다 우선)
            style: 밈 스타일 (기본값: 시트콤)
            context: 내용 컨텍스트 (사용 안 함, 호환성 유지)
        
        Returns:
            dict: {
                'original_image_url': 원본 캐릭터 이미지 경로,
                'final_image_url': 자막 합성된 이미지 경로,
                'final_image': 자막 합성된 PIL.Image,
                'top_text': 상단 자막,
                'bottom_text': 하단 자막,
                'character': 캐릭터 이름,
                'selected_image_name': 선택된 이미지 파일명
            }
        """
        # 1. 캐릭터 이미지 경로 조회
        character_image_path = MemeGenerator.get_character_image_path(character)
        
        # 2. 이미지 로드
        original_image = MemeGenerator.load_image(character_image_path)
        
        # 3. 대사 자동 분리 (top_text/bottom_text 없으면)
        if not top_text and not bottom_text and dialogue:
            # 대사를 두 줄로 자동 분리
            lines = dialogue.split('\n')
            if len(lines) >= 2:
                top_text = lines[0].strip()
                bottom_text = '\n'.join(lines[1:]).strip()
            else:
                # 한 줄이면 하단에만
                bottom_text = dialogue.strip()
        
        # 4. 자막 합성
        final_image = MemeGenerator.add_meme_text(
            original_image, 
            top_text or '', 
            bottom_text or ''
        )
        
        # 5. 결과 반환
        selected_image_name = os.path.basename(character_image_path)
        
        return {
            'original_image_url': f'file://{character_image_path}',
            'final_image_url': f'file://{character_image_path}_meme.png',
            'final_image': final_image,
            'top_text': top_text or '',
            'bottom_text': bottom_text or '',
            'character': character,
            'selected_image_name': selected_image_name
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

# ===== 1단계: 캐릭터 이미지 생성 (1회만, 처음 세팅 시) =====

# 지피 캐릭터 생성
MemeGenerator.generate_character_image(
    character_name='지피',
    style_prompt='30대 한국 남성, 안경 착용, 캐주얼한 티셔츠, 친근한 표정, 설명하는 느낌',
    save_filename='지피_v2.png'
)

# 아내 긴머리
MemeGenerator.generate_character_image(
    character_name='아내_긴머리',
    style_prompt='30대 한국 여성, 긴 생머리, 밝은 표정, 일상복, 자연스러운 느낌',
    save_filename='아내_긴머리.png'
)

# 아내 커트머리
MemeGenerator.generate_character_image(
    character_name='아내_커트',
    style_prompt='30대 한국 여성, 단발머리, 밝은 표정, 일상복, 시원한 느낌',
    save_filename='아내_커트.png'
)


# ===== 2단계: 밈 생성 (반복 사용) =====

# 지피 캐릭터로 밈 생성
result = MemeGenerator.create_meme(
    character='지피',
    dialogue="멈춰 버티면\n몸이 움직일 길이 없어지고\n허리가 대신 버팁니다."
)

# 아내 캐릭터로 밈 생성
result = MemeGenerator.create_meme(
    character='아내',
    top_text="그래서",
    bottom_text="가만히 서 있으면 허리부터 아픈 거구나."
)

# 결과 확인
print(f"캐릭터: {result['character']}")
print(f"이미지: {result['selected_image_name']}")

# 저장 (선택사항)
MemeGenerator.save_image(result['final_image'], 'output/meme_result.png')

# Firestore 저장 데이터
doc_data = {
    '제목': '하이노밸런스 밈',
    '밈이미지URL': result['selected_image_name'],
    '밈자막상단': result['top_text'],
    '밈자막하단': result['bottom_text'],
    '밈합성이미지URL': 'meme_result.png',
    '밈생성모델': '진 (시트콤 캐릭터 + Pillow 합성)',
    '밈스타일': '시트콤',
    '밈캐릭터': result['character']
}
"""
