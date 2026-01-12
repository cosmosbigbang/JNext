"""
콘텐츠 생성기 테스트
J님과 함께 시트콤/밈 개발
"""
from content_generator import HinoContentGenerator


def test_prologue():
    """프롤로그 시트콤 생성 테스트"""
    generator = HinoContentGenerator()
    
    print("\n" + "="*70)
    print("🎬 프롤로그 시트콤 테스트")
    print("="*70 + "\n")
    
    # 1. 출근 첫날의 기적
    episode_id = generator.create_sitcom_episode(
        title="출근 첫날의 기적",
        theme="""
J는 44살에 프로그래머가 되었다. 
새 회사 출근 첫날, 허리가 아팠다.
앉으려는 순간, 나도 모르게 한 발을 들었다.
그 순간, 하이노밸런스가 탄생했다.

이 에피소드는:
- J의 과거 (70개 이상 강의 수강, 23년 전 대한민국 최초 MAP 도전)
- 출근 첫날 허리 아픔
- 무의식적 한 발 들기
- 하이노밸런스 개념 정립 과정
- 지피와의 첫 만남
- 아내의 현실적 반응

을 다룹니다. 유머러스하면서도 감동적으로.
        """
    )
    
    print(f"\n✅ 에피소드 ID: {episode_id}")
    
    return episode_id


def test_individual_scenes():
    """개별 장면 생성 테스트"""
    generator = HinoContentGenerator()
    
    print("\n" + "="*70)
    print("🎬 개별 장면 테스트")
    print("="*70 + "\n")
    
    # 1. 집에서 - J와 아내
    scene1 = generator.create_sitcom_scene(
        scene_type='home',
        characters=['J', 'Wife'],
        context='J가 저녁 먹으면서 하이노밸런스 이론 설명. 아내는 반신반의.',
        exercise_name=None
    )
    
    # 2. 카페 - J와 지피
    scene2 = generator.create_sitcom_scene(
        scene_type='cafe',
        characters=['J', 'GPT'],
        context='지피가 "검색은 아무나 하는 게 아니다" 철학에 대해 질문',
        exercise_name=None
    )
    
    print(f"\n✅ 장면 2개 생성 완료: {scene1}, {scene2}")
    
    return [scene1, scene2]


def test_memes():
    """밈 시나리오 테스트"""
    generator = HinoContentGenerator()
    
    print("\n" + "="*70)
    print("💡 밈 시나리오 테스트")
    print("="*70 + "\n")
    
    themes = [
        ("두 발은 주차, 한 발은 드라이브", 'punch'),
        ("정지가 곧 가속도", 'paradox'),
        ("불균형이 정답이다", 'paradox'),
        ("뇌는 속도를 원한다", 'science'),
    ]
    
    meme_ids = []
    for theme, style in themes:
        meme_id = generator.create_meme(theme, style)
        meme_ids.append(meme_id)
    
    print(f"\n✅ 밈 {len(meme_ids)}개 생성 완료")
    
    return meme_ids


def test_shorts():
    """숏폼 스크립트 테스트"""
    generator = HinoContentGenerator()
    
    print("\n" + "="*70)
    print("🎥 숏폼 스크립트 테스트")
    print("="*70 + "\n")
    
    exercises = [
        ("하이노골반상하", 'tutorial'),
        ("하이노워킹전진", 'challenge'),
        ("하이노스케이팅좌우", 'fun'),
    ]
    
    short_ids = []
    for exercise, angle in exercises:
        short_id = generator.create_short(exercise, angle)
        short_ids.append(short_id)
    
    print(f"\n✅ 숏폼 {len(short_ids)}개 생성 완료")
    
    return short_ids


def test_list():
    """생성된 콘텐츠 목록 확인"""
    generator = HinoContentGenerator()
    
    print("\n" + "="*70)
    print("📋 전체 콘텐츠 목록")
    print("="*70 + "\n")
    
    generator.list_content()


def main():
    """전체 테스트"""
    print("\n" + "🎨"*35)
    print("하이노밸런스 콘텐츠 생성기 테스트")
    print("🎨"*35 + "\n")
    
    choice = input("""
어떤 테스트를 실행할까요?

1. 프롤로그 시트콤 (전체 에피소드)
2. 개별 장면 (2개)
3. 밈 시나리오 (4개)
4. 숏폼 스크립트 (3개)
5. 전체 실행
6. 목록 확인

선택 (1-6): """).strip()
    
    if choice == '1':
        test_prologue()
    elif choice == '2':
        test_individual_scenes()
    elif choice == '3':
        test_memes()
    elif choice == '4':
        test_shorts()
    elif choice == '5':
        print("\n🚀 전체 테스트 시작...\n")
        test_prologue()
        test_individual_scenes()
        test_memes()
        test_shorts()
        test_list()
    elif choice == '6':
        test_list()
    else:
        print("❌ 잘못된 선택")
    
    print("\n✅ 테스트 완료!\n")


if __name__ == '__main__':
    main()
