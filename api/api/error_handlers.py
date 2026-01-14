"""
통합 에러 처리 유틸리티
모든 API 응답을 일관된 형식으로 통일
"""
from django.http import JsonResponse


def success_response(message, data=None, **kwargs):
    """
    성공 응답 생성
    
    Args:
        message: 성공 메시지
        data: 추가 데이터 (선택)
        **kwargs: 추가 필드
    
    Returns:
        JsonResponse
    """
    response = {
        'status': 'success',
        'message': message
    }
    
    if data is not None:
        response['data'] = data
    
    response.update(kwargs)
    
    return JsonResponse(response)


def error_response(message, status_code=400, error_type=None, **kwargs):
    """
    에러 응답 생성
    
    Args:
        message: 에러 메시지
        status_code: HTTP 상태 코드
        error_type: 에러 타입 ('validation', 'auth', 'server', 'not_found')
        **kwargs: 추가 필드
    
    Returns:
        JsonResponse
    """
    response = {
        'status': 'error',
        'message': message
    }
    
    if error_type:
        response['error_type'] = error_type
    
    response.update(kwargs)
    
    return JsonResponse(response, status=status_code)


def validation_error(message, field=None, **kwargs):
    """검증 실패 응답"""
    extra = {'error_type': 'validation'}
    if field:
        extra['field'] = field
    extra.update(kwargs)
    return error_response(message, status_code=400, **extra)


def auth_error(message='인증 실패', **kwargs):
    """인증 실패 응답"""
    return error_response(message, status_code=401, error_type='auth', **kwargs)


def not_found_error(message='리소스를 찾을 수 없습니다', **kwargs):
    """404 응답"""
    return error_response(message, status_code=404, error_type='not_found', **kwargs)


def server_error(message='서버 오류가 발생했습니다', **kwargs):
    """서버 오류 응답"""
    return error_response(message, status_code=500, error_type='server', **kwargs)


def handle_exception(e, context='작업'):
    """
    예외를 적절한 에러 응답으로 변환
    
    Args:
        e: Exception 객체
        context: 작업 설명 (예: '문서 저장', 'AI 호출')
    
    Returns:
        JsonResponse
    """
    import traceback
    
    error_msg = f'{context} 중 오류 발생: {str(e)}'
    
    # 디버그 정보 (개발 환경에서만)
    debug_info = {
        'exception_type': type(e).__name__,
        'traceback': traceback.format_exc()
    }
    
    return server_error(error_msg, debug=debug_info)
