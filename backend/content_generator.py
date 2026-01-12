"""
하이노밸런스 콘텐츠 생성기
- 시트콤 에피소드/장면
- 밈 시나리오
- 숏폼 스크립트
"""
import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# .env 파일 로드
load_dotenv()

# Firebase 초기화
if not firebase_admin._apps:
    cred = credentials.Certificate('jnext-service-account.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Gemini API 설정
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash-exp')


class HinoContentGenerator:
    """하이노밸런스 콘텐츠 생성 클래스"""
    
    def __init__(self):
        self.db = db
        self.model = model
        self.collection = 'hino_content'
        
    
    def create_sitcom_episode(self, title, theme, scenes_data=None):
        """
        시트콤 에피소드 전체 생성
        
        Args:
            title: 에피소드 제목 (예: "출근 첫날의 기적")
            theme: 테마/소재 (예: "하이노밸런스 탄생 서사")
            scenes_data: 장면 데이터 리스트 (없으면 AI가 자동 생성)
            
        Returns:
            episode_id: 생성된 에피소드 ID
        """
        print(f"\n{'='*70}")
        print(f"🎬 시트콤 에피소드 생성: {title}")
        print(f"{'='*70}\n")
        
        # 1. 배경 정보 수집
        theory = self._get_theory_context()
        
        # 2. AI에게 전체 구성 요청
        if not scenes_data:
            prompt = f"""
당신은 운동 시트콤 작가입니다.

## 배경 정보
{theory}

## 에피소드 제목
{title}

## 테마
{theme}

## 캐릭터
- J (40대 후반 남성): 하이노밸런스 창시자. 진지하고 열정적. 가끔 자기 확신이 강함.
- 지피 (20대 후반 여성): J의 제자. 날카롭고 논리적. 질문이 많음. "진짜요?" 자주 씀.
- 아내 (40대 중반 여성): J의 아내. 현실적이고 따뜻함. "그래서 돈은 돼?" 같은 핵심 질문.

## 요청사항
5개 장면으로 구성된 시트콤 에피소드를 만들어주세요.

각 장면은 다음 형식으로:
SCENE [번호]: [장면 제목]
장소: [장소]
시간: [시간]
등장: [캐릭터들]

[대사와 지문]

---

재미있고 감동적이면서도, 하이노밸런스의 핵심 철학이 자연스럽게 드러나야 합니다.
"""
            
            response = self.model.generate_content(prompt)
            full_script = response.text
            
            # 장면 분리
            scenes_data = self._parse_scenes(full_script)
        
        # 3. 각 장면을 hino_content에 저장
        scene_ids = []
        for i, scene in enumerate(scenes_data, 1):
            scene_id = self._save_scene(
                episode_title=title,
                scene_number=i,
                scene_data=scene
            )
            scene_ids.append(scene_id)
            print(f"  ✓ 장면 {i}: {scene.get('title', 'Untitled')}")
        
        # 4. 에피소드 메타데이터 저장
        episode_data = {
            'content_type': 'sitcom_episode',
            'title': title,
            'theme': theme,
            'scene_count': len(scene_ids),
            'scene_ids': scene_ids,
            'created_at': datetime.now(),
            'status': 'draft'
        }
        
        episode_ref = self.db.collection(self.collection).document()
        episode_ref.set(episode_data)
        
        print(f"\n✅ 에피소드 생성 완료!")
        print(f"   ID: {episode_ref.id}")
        print(f"   장면 수: {len(scene_ids)}개\n")
        
        return episode_ref.id
    
    
    def create_sitcom_scene(self, scene_type, characters, context, exercise_name=None):
        """
        시트콤 개별 장면 생성
        
        Args:
            scene_type: 장면 유형 (home/gym/cafe/outdoor)
            characters: 등장 인물 리스트 ['J', 'GPT', 'Wife']
            context: 장면 맥락 (예: "J가 골반상하를 처음 시연")
            exercise_name: 관련 운동명 (선택)
            
        Returns:
            scene_id: 생성된 장면 ID
        """
        print(f"\n🎬 장면 생성: {scene_type}")
        
        # 배경 정보
        theory = self._get_theory_context()
        exercise_info = ""
        if exercise_name:
            exercise_info = self._get_exercise_info(exercise_name)
        
        # AI에게 장면 생성 요청
        prompt = f"""
당신은 운동 시트콤 작가입니다.

## 배경 정보
{theory}

{f"## 운동 정보\n{exercise_info}\n" if exercise_info else ""}

## 장면 설정
- 유형: {scene_type}
- 등장 인물: {', '.join(characters)}
- 맥락: {context}

## 캐릭터 성격
- J: 진지, 열정적, 가끔 자기 확신 강함
- 지피: 날카롭고 논리적, "진짜요?" 자주 씀
- 아내: 현실적, 따뜻함, "그래서 돈은 돼?"

## 요청사항
3-5분 분량의 재미있는 장면을 작성해주세요.

형식:
장면 제목: [제목]
장소: [장소]
시간: [시간]

[대사와 지문]

대사는 자연스럽고, 하이노밸런스 철학이 유머러스하게 드러나야 합니다.
"""
        
        response = self.model.generate_content(prompt)
        script = response.text
        
        # 장면 저장
        scene_data = {
            'content_type': 'sitcom_scene',
            'scene_type': scene_type,
            'characters': characters,
            'context': context,
            'exercise_name': exercise_name,
            'script': script,
            'created_at': datetime.now(),
            'status': 'draft'
        }
        
        scene_ref = self.db.collection(self.collection).document()
        scene_ref.set(scene_data)
        
        print(f"✅ 장면 저장 완료: {scene_ref.id}\n")
        print(script[:200] + "...\n")
        
        return scene_ref.id
    
    
    def create_meme(self, theme, style='punch'):
        """
        밈 시나리오 생성
        
        Args:
            theme: 테마 (예: "두 발은 주차, 한 발은 드라이브")
            style: 스타일 (punch/paradox/science/humor)
            
        Returns:
            meme_id: 생성된 밈 ID
        """
        print(f"\n💡 밈 생성: {theme}")
        
        theory = self._get_theory_context()
        
        style_guide = {
            'punch': "짧고 강렬한 한 방. 3초 안에 이해되고 기억됨.",
            'paradox': "역설적 표현으로 충격과 깨달음 동시에.",
            'science': "과학적 사실을 유머러스하게 각색.",
            'humor': "웃기면서도 핵심을 찌르는 재치."
        }
        
        prompt = f"""
당신은 밈 크리에이터입니다.

## 배경 정보
{theory}

## 테마
{theme}

## 스타일
{style_guide.get(style, style_guide['punch'])}

## 요청사항
다음을 생성해주세요:

1. 메인 텍스트 (10자 이내)
2. 서브 텍스트 (20자 이내)
3. 비주얼 제안 (어떤 이미지/영상과 매칭?)
4. 사용 시나리오 (SNS/광고/교육 등)
5. 해시태그 5개

형식:
## 메인
[텍스트]

## 서브
[텍스트]

## 비주얼
[설명]

## 시나리오
[설명]

## 해시태그
#태그1 #태그2 ...
"""
        
        response = self.model.generate_content(prompt)
        content = response.text
        
        # 밈 저장
        meme_data = {
            'content_type': 'meme',
            'theme': theme,
            'style': style,
            'content': content,
            'created_at': datetime.now(),
            'status': 'draft'
        }
        
        meme_ref = self.db.collection(self.collection).document()
        meme_ref.set(meme_data)
        
        print(f"✅ 밈 저장 완료: {meme_ref.id}\n")
        print(content + "\n")
        
        return meme_ref.id
    
    
    def create_short(self, exercise_name, angle='tutorial'):
        """
        숏폼 스크립트 생성
        
        Args:
            exercise_name: 운동명 (예: "하이노골반상하")
            angle: 각도 (tutorial/challenge/before-after/fun)
            
        Returns:
            short_id: 생성된 숏폼 ID
        """
        print(f"\n🎥 숏폼 생성: {exercise_name} ({angle})")
        
        exercise_info = self._get_exercise_info(exercise_name)
        theory = self._get_theory_context()
        
        angle_guide = {
            'tutorial': "30-60초 안에 핵심 동작과 효과 전달",
            'challenge': "챌린지 형식. 따라하기 쉽고 재미있게",
            'before-after': "변화 스토리. 감동과 동기부여",
            'fun': "재미 위주. 유머러스하고 바이럴"
        }
        
        prompt = f"""
당신은 숏폼 크리에이터입니다.

## 배경 정보
{theory}

## 운동 정보
{exercise_info}

## 각도
{angle_guide.get(angle, angle_guide['tutorial'])}

## 요청사항
15-60초 숏폼 스크립트를 작성해주세요.

형식:
## 제목 (10자 이내)
[제목]

## 훅 (첫 3초, 시선 사로잡기)
[텍스트/액션]

## 본문 (핵심 전달)
[스크립트]

## 클로징 (CTA)
[마무리 멘트]

## 비주얼 연출
[촬영/편집 가이드]

## 음악 제안
[분위기/장르]

## 해시태그
#태그1 #태그2 ...
"""
        
        response = self.model.generate_content(prompt)
        content = response.text
        
        # 숏폼 저장
        short_data = {
            'content_type': 'short',
            'exercise_name': exercise_name,
            'angle': angle,
            'content': content,
            'created_at': datetime.now(),
            'status': 'draft'
        }
        
        short_ref = self.db.collection(self.collection).document()
        short_ref.set(short_data)
        
        print(f"✅ 숏폼 저장 완료: {short_ref.id}\n")
        print(content + "\n")
        
        return short_ref.id
    
    
    # === 헬퍼 메서드 ===
    
    def _get_theory_context(self):
        """통합 이론 가져오기"""
        docs = self.db.collection('hino_draft').where(
            'content_type', '==', 'theory_integrated'
        ).where(
            'length_level', '==', 'summary'
        ).limit(1).stream()
        
        for doc in docs:
            return doc.to_dict().get('content', '하이노밸런스: 한 발 운동으로 뇌를 자극하는 혁신적 건강법')
        
        return '하이노밸런스: 한 발 운동으로 뇌를 자극하는 혁신적 건강법'
    
    
    def _get_exercise_info(self, exercise_name):
        """운동 정보 가져오기"""
        # hino_raw 또는 hino_draft에서 검색
        collections = ['hino_draft', 'hino_raw']
        
        for coll in collections:
            docs = self.db.collection(coll).where(
                'doc_id', '==', exercise_name
            ).limit(1).stream()
            
            for doc in docs:
                data = doc.to_dict()
                return f"""
운동명: {data.get('doc_id', exercise_name)}
카테고리: {data.get('category', 'N/A')}
내용: {data.get('content', '')[:500]}...
"""
        
        return f"운동명: {exercise_name}"
    
    
    def _parse_scenes(self, full_script):
        """전체 스크립트를 장면별로 분리"""
        scenes = []
        parts = full_script.split('SCENE')
        
        for part in parts[1:]:  # 첫 번째는 빈 문자열
            lines = part.strip().split('\n')
            if len(lines) < 2:
                continue
            
            # 첫 줄에서 번호와 제목 추출
            first_line = lines[0]
            title = first_line.split(':', 1)[-1].strip() if ':' in first_line else first_line.strip()
            
            scene = {
                'title': title,
                'content': '\n'.join(lines[1:]).strip()
            }
            scenes.append(scene)
        
        return scenes
    
    
    def _save_scene(self, episode_title, scene_number, scene_data):
        """개별 장면 저장"""
        scene_doc = {
            'content_type': 'sitcom_scene',
            'episode_title': episode_title,
            'scene_number': scene_number,
            'title': scene_data.get('title', f'Scene {scene_number}'),
            'content': scene_data.get('content', ''),
            'created_at': datetime.now(),
            'status': 'draft'
        }
        
        scene_ref = self.db.collection(self.collection).document()
        scene_ref.set(scene_doc)
        
        return scene_ref.id
    
    
    def list_content(self, content_type=None):
        """생성된 콘텐츠 목록 조회"""
        print(f"\n📋 콘텐츠 목록 ({self.collection})")
        print("="*70)
        
        query = self.db.collection(self.collection)
        if content_type:
            query = query.where('content_type', '==', content_type)
        
        docs = query.stream()
        
        count = 0
        for doc in docs:
            data = doc.to_dict()
            count += 1
            
            print(f"\n[{count}] {data.get('content_type', 'unknown')}")
            print(f"    ID: {doc.id}")
            
            if data.get('title'):
                print(f"    제목: {data['title']}")
            if data.get('theme'):
                print(f"    테마: {data['theme']}")
            if data.get('exercise_name'):
                print(f"    운동: {data['exercise_name']}")
            
            print(f"    생성: {data.get('created_at', 'N/A')}")
        
        print(f"\n총 {count}개\n")


def main():
    """테스트 실행"""
    generator = HinoContentGenerator()
    
    print("\n🎨 하이노밸런스 콘텐츠 생성기")
    print("="*70)
    print("\n사용 예시:")
    print("\n1. 시트콤 에피소드 생성")
    print("   generator.create_sitcom_episode('출근 첫날의 기적', '하이노밸런스 탄생 서사')")
    print("\n2. 개별 장면 생성")
    print("   generator.create_sitcom_scene('home', ['J', 'Wife'], 'J가 골반상하 시연')")
    print("\n3. 밈 생성")
    print("   generator.create_meme('두 발은 주차, 한 발은 드라이브', 'punch')")
    print("\n4. 숏폼 생성")
    print("   generator.create_short('하이노골반상하', 'tutorial')")
    print("\n5. 콘텐츠 목록")
    print("   generator.list_content()")
    print("\n" + "="*70 + "\n")


if __name__ == '__main__':
    main()
