# JNext 앱 아이콘 생성 가이드

## 아이콘 디자인 컨셉
- **테마**: 데이터 분석 + AI + 보고서
- **색상**: Deep Purple + Blue gradient (현재 앱 테마)
- **심볼**: J + 문서/차트 조합

## 방법 1: 온라인 도구 사용 (가장 쉬움)

1. **Icon Kitchen** (https://icon.kitchen/)
   - 텍스트: "J"
   - Background: Gradient (Purple to Blue)
   - Shape: Circle or Rounded Square
   - 다운로드 후 아래 경로에 배치

2. **App Icon Generator** (https://www.appicon.co/)
   - 1024x1024 PNG 업로드
   - 모든 사이즈 자동 생성
   - Android/iOS 폴더별로 다운로드

## 방법 2: Flutter 패키지 사용 (권장)

```bash
# 패키지 설치
flutter pub add flutter_launcher_icons

# pubspec.yaml에 설정 추가 후
flutter pub run flutter_launcher_icons
```

## 아이콘 파일 위치

### Android
- `android/app/src/main/res/mipmap-hdpi/ic_launcher.png` (72x72)
- `android/app/src/main/res/mipmap-mdpi/ic_launcher.png` (48x48)
- `android/app/src/main/res/mipmap-xhdpi/ic_launcher.png` (96x96)
- `android/app/src/main/res/mipmap-xxhdpi/ic_launcher.png` (144x144)
- `android/app/src/main/res/mipmap-xxxhdpi/ic_launcher.png` (192x192)

### iOS
- `ios/Runner/Assets.xcassets/AppIcon.appiconset/` (여러 사이즈)

## 빠른 적용 방법

1. 1024x1024 PNG 생성 (온라인 도구)
2. `jnext_mobile/` 폴더에 `icon.png` 저장
3. pubspec.yaml에 flutter_launcher_icons 설정 추가
4. 명령어 실행으로 자동 배치
