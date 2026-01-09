"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from api import views

urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    
    # Phase 5: 웹 UI
    path('chat/', views.chat_ui, name='chat_ui'),
    
    # Firebase 테스트 API
    path('api/test/', views.firebase_test, name='firebase_test'),
    path('api/logs/', views.system_logs_list, name='system_logs'),
    
    # Phase 2: 명령어 파싱 엔진
    path('api/v1/execute-command/', views.execute_command, name='execute_command'),
    
    # Phase 2-2: 통합 Execute API (Gen 대화창용)
    path('api/v1/execute/', views.execute, name='execute'),
    
    # Phase 3: Gemini AI 채팅 API
    path('api/v1/chat/', views.chat, name='chat'),
    
    # Phase 5+: AI 답변 저장 API
    path('api/v1/save-summary/', views.save_summary, name='save_summary'),
    
    # Phase 6.5: 최종본 생성 API
    path('api/v1/generate-final/', views.generate_final, name='generate_final'),
    
    # Phase 6: 문서 조회/수정/삭제 API
    path('api/v1/get-document/', views.get_document, name='get_document'),
    path('api/v1/update-documents/', views.update_documents, name='update_documents'),
    path('api/v1/delete-documents/', views.delete_documents, name='delete_documents'),
]
