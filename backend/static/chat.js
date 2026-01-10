/**
 * JNext Chat Interface - JavaScript
 * Phase 5: 웹 UI
 */

// DOM Elements
const chatArea = document.getElementById('chat-area');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const modeToggle = document.getElementById('mode-toggle');
const modelSelect = document.getElementById('model-select');
const saveRaw = document.getElementById('save-raw');
const saveDraft = document.getElementById('save-draft');
const saveFinal = document.getElementById('save-final');
const saveModal = document.getElementById('save-modal');
const saveTitle = document.getElementById('save-title');
const saveCategory = document.getElementById('save-category');
const saveContent = document.getElementById('save-content');
const saveCollection = document.getElementById('save-collection');
const confirmSaveBtn = document.getElementById('confirm-save-btn');
const closeModal = document.querySelector('.close');

// State
let isLoading = false;
let currentResponseToSave = null;
let savedResponses = [];  // 응답 저장용 배열
let currentMode = 'hybrid';  // 기본값: hybrid (통합)

// 모드 설정 함수 (제거 - HTML에서 직접 select 사용)
// Event Listeners
sendButton.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey && !isLoading) {
        e.preventDefault();
        sendMessage();
    }
});

// 모달 관련 이벤트
closeModal.addEventListener('click', () => {
    saveModal.style.display = 'none';
});

window.addEventListener('click', (e) => {
    if (e.target === saveModal) {
        saveModal.style.display = 'none';
    }
});

confirmSaveBtn.addEventListener('click', confirmSave);

/**
 * 메시지 전송
 */
async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message || isLoading) return;

    const mode = modeToggle.value;  // organize, hybrid, analysis
    const model = modelSelect.value;
    
    // 저장 위치 체크박스 읽기
    const saveTargets = [];
    if (saveRaw && saveRaw.checked) saveTargets.push('raw');
    if (saveDraft && saveDraft.checked) saveTargets.push('draft');
    if (saveFinal && saveFinal.checked) saveTargets.push('final');

    // UI 업데이트
    addMessage('user', message);
    messageInput.value = '';
    setLoading(true);

    try {
        // API 호출
        const response = await fetch('/api/v1/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,  // finalMessage 제거
                mode: mode,
                model: model,
                save_targets: saveTargets  // 저장 위치 전송
            })
        });

        const data = await response.json();

        if (data.status === 'success') {
            displayAIResponse(data);
        } else {
            addMessage('ai', `❌ 에러: ${data.message}`);
        }
    } catch (error) {
        addMessage('ai', `❌ 네트워크 에러: ${error.message}`);
    } finally {
        setLoading(false);
    }
}

/**
 * AI 응답 표시 (JSON 구조화)
 */
function displayAIResponse(data) {
    const response = data.response;
    const mode = data.mode || 'organize';
    const model = data.model || 'gemini-pro';
    const dbCount = data.db_documents_count || 0;
    const userMessage = data.message || data.user_message || '';
    const action = data.action || null;  // SAVE/READ 등

    // 액션에 따른 아이콘
    let icon = '🤖';
    if (action === 'READ') icon = '📊';
    else if (action === 'SAVE') icon = '💾';
    else if (action === 'GENERATE_FINAL') icon = '📝';
    else if (action === 'DELETE') icon = '🗑️';
    else if (action === 'UPDATE') icon = '✏️';

    // 응답을 배열에 저장
    const responseIndex = savedResponses.length;
    savedResponses.push({
        response: response,
        userMessage: userMessage,
        mode: mode,
        model: model
    });

    // 메시지 컨테이너 생성
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message ai';

    // 응답 내용
    let content = `
        <div class="message-content">
            <div style="margin-bottom: 10px;">
                <span class="badge" style="background: #4CAF50; color: white; font-size: 16px;">${icon}</span>
                ${mode ? `<span class="badge badge-${mode}">${mode === 'organize' ? '정리' : '분석'}</span>` : ''}
                ${model ? `<span class="badge badge-${model}">${model.toUpperCase()}</span>` : ''}
                ${action ? `<span class="badge" style="background: #9C27B0; color: white;">${action}</span>` : ''}
            </div>
            
            <div style="margin-bottom: 15px;">
                ${formatText(response.answer || '응답 없음')}
            </div>
    `;

    // 문서 리스트 표시 (READ 명령 시)
    if (data.document_list && data.document_list.length > 0) {
        content += `
            <div class="document-list-panel" style="margin: 15px 0; background: #f8f9fa; padding: 15px; border-radius: 8px;">
                <strong>📄 문서 리스트 (${data.document_list.length}개):</strong>
                <div style="margin-top: 10px;">
                    ${data.document_list.map((doc, idx) => `
                        <div class="document-item" style="background: white; padding: 10px; margin: 8px 0; border-radius: 6px; border-left: 4px solid #667eea;">
                            <div style="display: flex; align-items: start;">
                                <input type="checkbox" class="doc-checkbox" 
                                       data-collection="${doc.collection}" 
                                       data-doc-id="${doc.doc_id}"
                                       onclick="event.stopPropagation()"
                                       style="margin-right: 10px; margin-top: 3px; width: 18px; height: 18px;">
                                <div style="flex: 1; cursor: pointer;" onclick='editDocument(${JSON.stringify(doc).replace(/'/g, "\\'")}, event)'>
                                    <div style="font-weight: 600; color: #2196F3; margin-bottom: 5px; text-decoration: underline;">
                                        ${idx + 1}. ${doc.title || '제목 없음'}
                                    </div>
                                    <div style="font-size: 12px; color: #666; margin-bottom: 8px;">
                                        📁 ${doc.collection} | 🏷️ ${doc.category || 'N/A'} | 📅 ${doc.created_at ? doc.created_at.substring(0, 10) : 'N/A'}
                                    </div>
                                    <div style="font-size: 13px; color: #555; line-height: 1.5; background: #f9f9f9; padding: 8px; border-radius: 4px;">
                                        ${doc.preview || '내용 없음'}
                                    </div>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
                <div style="margin-top: 15px; display: flex; gap: 10px;">
                    <button onclick="selectAllDocuments()" 
                            style="padding: 10px 20px; background: #2196F3; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 600;">
                        ☑️ 전체 선택
                    </button>
                    <button onclick="generateFinalFromSelected()" 
                            style="padding: 10px 20px; background: #4CAF50; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 600;">
                        📝 선택한 문서로 최종본 생성
                    </button>
                    <button class="delete-selected-btn" onclick="deleteSelectedDocuments()" 
                            style="padding: 10px 20px; background: #f44336; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 600;">
                        🗑️ 선택 삭제
                    </button>
                </div>
            </div>
        `;
    }

    // Claims 표시
    if (response.claims && response.claims.length > 0) {
        content += `
            <div class="evidence-panel">
                <strong>📌 핵심 주장 (${response.claims.length}개):</strong>
                <ul class="claims-list">
                    ${response.claims.slice(0, 5).map(claim => 
                        `<li class="claim-item">${claim}</li>`
                    ).join('')}
                    ${response.claims.length > 5 ? `<li>...외 ${response.claims.length - 5}개</li>` : ''}
                </ul>
            </div>
        `;
    }

    // Evidence 표시
    if (response.evidence && response.evidence.length > 0) {
        content += `
            <div class="evidence-panel" style="margin-top: 10px;">
                <strong>🔍 근거 (${response.evidence.length}개):</strong>
                ${response.evidence.slice(0, 3).map(ev => `
                    <div class="evidence-item">
                        📁 ${ev.collection}/${ev.doc_id}<br>
                        📝 ${ev.field}: "${ev.value}"
                    </div>
                `).join('')}
                ${response.evidence.length > 3 ? 
                    `<div style="margin-top: 5px; color: #666;">...외 ${response.evidence.length - 3}개 근거</div>` : ''}
            </div>
        `;
    }

    // Missing Info 표시
    if (response.missing_info && response.missing_info.length > 0) {
        content += `
            <div class="evidence-panel" style="margin-top: 10px; background: #fff3cd;">
                <strong>⚠️ DB에 없는 정보:</strong>
                <ul style="margin-top: 5px; padding-left: 20px;">
                    ${response.missing_info.map(info => `<li>${info}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    // Actions Suggested 표시
    if (response.actions_suggested && response.actions_suggested.length > 0) {
        content += `
            <div class="evidence-panel" style="margin-top: 10px; background: #d4edda;">
                <strong>💡 제안 액션:</strong>
                ${response.actions_suggested.map(action => `
                    <div style="margin-top: 5px;">
                        🔧 ${action.action} → ${action.collection}<br>
                        이유: ${action.reason}
                    </div>
                `).join('')}
            </div>
        `;
    }

    // Debug Info
    content += `
            <div class="debug-info">
                📊 DB 문서: ${dbCount}개 | 
                🎯 확신도: ${response.confidence ? (response.confidence * 100).toFixed(0) : 'N/A'}% |
                🤖 모델: ${response._model_version || model || 'N/A'}
            </div>
            <button class="save-btn" onclick="openSaveModal(${responseIndex})">
                📝 이 답변 저장
            </button>
        </div>
    `;

    messageDiv.innerHTML = content;
    chatArea.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * 사용자 메시지 추가
 */
function addMessage(type, text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.innerHTML = `
        <div class="message-content">
            ${formatText(text)}
        </div>
    `;
    chatArea.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * 텍스트 포맷팅 (줄바꿈 처리)
 */
function formatText(text) {
    return text.replace(/\n/g, '<br>');
}

/**
 * 로딩 상태 설정
 */
function setLoading(loading) {
    isLoading = loading;
    sendButton.disabled = loading;
    
    if (loading) {
        sendButton.innerHTML = '<div class="loading"></div>';
    } else {
        sendButton.textContent = '전송';
    }
}

/**
 * 스크롤을 아래로
 */
function scrollToBottom() {
    chatArea.scrollTop = chatArea.scrollHeight;
}

/**
 * 저장 버튼 클릭 핸들러
 */
function openSaveModal(index) {
    if (!savedResponses[index]) {
        alert('❌ 응답 데이터를 찾을 수 없습니다.');
        return;
    }

    const data = savedResponses[index];
    currentResponseToSave = data;

    // 모달 초기화
    const messagePreview = data.userMessage.substring(0, 30);
    saveTitle.value = messagePreview ? `${messagePreview}... 정리` : 'AI 답변 정리';
    saveContent.value = formatResponseForSave(data.response);
    
    // 모달 표시
    saveModal.style.display = 'block';
}

/**
 * 저장용 포맷 변환
 */
function formatResponseForSave(response) {
    let content = `# ${response.answer}\n\n`;
    
    if (response.claims && response.claims.length > 0) {
        content += `## 핵심 주장\n`;
        response.claims.forEach((claim, idx) => {
            content += `${idx + 1}. ${claim}\n`;
        });
        content += '\n';
    }

    if (response.evidence && response.evidence.length > 0) {
        content += `## 근거\n`;
        response.evidence.forEach((ev, idx) => {
            content += `[${idx + 1}] ${ev.collection}/${ev.doc_id}\n`;
            content += `   ${ev.field}: ${ev.value}\n\n`;
        });
    }

    if (response.missing_info && response.missing_info.length > 0) {
        content += `## DB에 없는 정보\n`;
        response.missing_info.forEach(info => {
            content += `- ${info}\n`;
        });
        content += '\n';
    }

    return content;
}

/**
 * 저장 확인
 */
async function confirmSave() {
    const title = saveTitle.value.trim();
    const category = saveCategory.value;
    const content = saveContent.value.trim();
    const collection = saveCollection.value;

    if (!title || !content) {
        alert('제목과 내용을 입력해주세요.');
        return;
    }

    try {
        const response = await fetch('/api/v1/save-summary/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title: title,
                category: category,
                content: content,
                collection: collection,
                original_message: currentResponseToSave.userMessage,
                ai_response: currentResponseToSave.response
            })
        });

        const data = await response.json();

        if (data.status === 'success') {
            alert(`✅ ${collection}에 저장되었습니다!\nDoc ID: ${data.doc_id}`);
            saveModal.style.display = 'none';
        } else {
            alert('❌ 저장 실패: ' + (data.message || '알 수 없는 오류'));
        }
    } catch (error) {
        console.error('Save error:', error);
        alert('❌ 저장 중 오류 발생: ' + error.message);
    }
}

/**
 * 전체 선택/해제
 */
function selectAllDocuments() {
    const checkboxes = document.querySelectorAll('.doc-checkbox');
    const allChecked = Array.from(checkboxes).every(cb => cb.checked);
    
    checkboxes.forEach(cb => {
        cb.checked = !allChecked;
    });
}

/**
 * 개별 문서 편집
 */
function editDocument(doc, event) {
    if (event) {
        event.stopPropagation();
    }
    
    // 로딩 표시
    const loadingModal = document.createElement('div');
    loadingModal.id = 'loading-modal';
    loadingModal.innerHTML = `
        <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 9999; display: flex; align-items: center; justify-content: center;">
            <div style="background: white; padding: 30px; border-radius: 12px; text-align: center;">
                <div style="font-size: 24px; margin-bottom: 10px;">⏳</div>
                <div>문서 불러오는 중...</div>
            </div>
        </div>
    `;
    document.body.appendChild(loadingModal);
    
    // 문서 전체 내용 가져오기
    fetch(`/api/v1/get-document/?collection=${doc.collection}&doc_id=${doc.doc_id}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            loadingModal.remove();
            if (data.status === 'success') {
                console.log('Full document loaded:', data.document);
                showEditModal(data.document);
            } else {
                alert('❌ 문서 로드 실패: ' + (data.message || '알 수 없는 오류'));
            }
        })
        .catch(error => {
            loadingModal.remove();
            console.error('Get document error:', error);
            alert('❌ 문서 불러오기 실패: ' + error.message);
        });
}

/**
 * 문서 편집 모달 표시
 */
function showEditModal(doc) {
    console.log('showEditModal - Full document:', doc);
    console.log('제목 필드:', doc.제목, 'title 필드:', doc.title);
    
    // 고정 필드
    const fixedFields = ['제목', '카테고리', '운동명', '내용', '전체글', '데이터상태'];
    
    // 읽기 전용 필드 (_id, _collection, created_at 등)
    const readOnlyFields = ['_id', '_collection', 'created_at', 'updated_at', '작성일시', '수정일시'];
    
    // 기타 모든 필드 추출
    const allKeys = Object.keys(doc);
    const dynamicFields = allKeys.filter(key => 
        !fixedFields.includes(key) && 
        !readOnlyFields.includes(key) &&
        typeof doc[key] !== 'object'  // 객체/배열 제외
    );
    
    console.log('Dynamic fields:', dynamicFields);
    
    const modal = document.createElement('div');
    modal.innerHTML = `
        <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 9999; display: flex; align-items: center; justify-content: center;" onclick="closeEditModal(event)">
            <div style="background: white; padding: 30px; border-radius: 12px; max-width: 900px; width: 95%; max-height: 90vh; overflow-y: auto; box-shadow: 0 4px 20px rgba(0,0,0,0.3);" onclick="event.stopPropagation()">
                <h3 style="margin: 0 0 20px 0; color: #333;">✏️ 문서 편집</h3>
                
                <!-- 고정 필드 -->
                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 5px; font-weight: 600; color: #555;">제목:</label>
                    <input type="text" id="edit-제목" value="${((doc.제목 || doc.title || '') + '').replace(/"/g, '&quot;')}" 
                           style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box;">
                </div>
                
                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 5px; font-weight: 600; color: #555;">카테고리 (대분류):</label>
                    <select id="edit-카테고리" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px;">
                        <option value="하이노이론" ${(doc.카테고리 || doc.category) === '하이노이론' ? 'selected' : ''}>하이노이론</option>
                        <option value="하이노워킹" ${(doc.카테고리 || doc.category) === '하이노워킹' ? 'selected' : ''}>하이노워킹</option>
                        <option value="하이노스케이팅" ${(doc.카테고리 || doc.category) === '하이노스케이팅' ? 'selected' : ''}>하이노스케이팅</option>
                        <option value="하이노철봉" ${(doc.카테고리 || doc.category) === '하이노철봉' ? 'selected' : ''}>하이노철봉</option>
                        <option value="하이노기본" ${(doc.카테고리 || doc.category) === '하이노기본' ? 'selected' : ''}>하이노기본</option>
                        <option value="하이노밸런스" ${(doc.카테고리 || doc.category) === '하이노밸런스' ? 'selected' : ''}>하이노밸런스</option>
                        <option value="기타" ${(doc.카테고리 || doc.category) === '기타' ? 'selected' : ''}>기타</option>
                    </select>
                </div>
                
                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 5px; font-weight: 600; color: #555;">운동명 (중분류):</label>
                    <input type="text" id="edit-운동명" value="${((doc.운동명 || '') + '').replace(/"/g, '&quot;')}" 
                           placeholder="예: 하이노워킹기본, 하이노워킹패스트 등"
                           style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box;">
                </div>
                
                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 5px; font-weight: 600; color: #555;">내용 (요약):</label>
                    <textarea id="edit-내용" 
                              style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; min-height: 150px; box-sizing: border-box; font-family: inherit;">${(doc.내용 || '').replace(/</g, '&lt;').replace(/>/g, '&gt;')}</textarea>
                </div>
                
                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 5px; font-weight: 600; color: #555;">전체 글 (출판용):</label>
                    <textarea id="edit-전체글" 
                              style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; min-height: 300px; box-sizing: border-box; font-family: inherit;">${(doc.전체글 || '').replace(/</g, '&lt;').replace(/>/g, '&gt;')}</textarea>
                </div>
                
                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 5px; font-weight: 600; color: #555;">데이터 상태:</label>
                    <select id="edit-데이터상태" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px;">
                        <option value="DRAFT" ${(doc.데이터상태 || doc.데이터상태) === 'DRAFT' ? 'selected' : ''}>DRAFT (초안)</option>
                        <option value="FINAL" ${(doc.데이터상태 || doc.데이터상태) === 'FINAL' ? 'selected' : ''}>FINAL (최종)</option>
                        <option value="RAW" ${(doc.데이터상태 || doc.데이터상킬) === 'RAW' ? 'selected' : ''}>RAW (원본)</option>
                    </select>
                </div>
                
                <!-- 동적 필드 -->
                ${dynamicFields.length > 0 ? `
                    <div style="margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                        <h4 style="margin: 0 0 15px 0; color: #555;">추가 필드</h4>
                        ${dynamicFields.map(key => `
                            <div style="margin-bottom: 12px;">
                                <label style="display: block; margin-bottom: 5px; font-weight: 600; color: #666;">${key}:</label>
                                <textarea id="edit-dynamic-${key.replace(/[^a-zA-Z0-9가-힣]/g, '_')}" 
                                          style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; min-height: 60px; box-sizing: border-box; font-family: inherit;">${(doc[key] || '').toString().replace(/</g, '&lt;').replace(/>/g, '&gt;')}</textarea>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
                
                <div style="display: flex; gap: 10px; justify-content: flex-end; margin-top: 20px;">
                    <button onclick="closeEditModal()" 
                            style="padding: 10px 20px; background: #999; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 600;">
                        취소
                    </button>
                    <button id="save-edit-btn"
                            style="padding: 10px 20px; background: #4CAF50; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 600;">
                        ✅ 저장
                    </button>
                </div>
            </div>
        </div>
    `;
    modal.id = 'edit-modal';
    document.body.appendChild(modal);
    
    // 저장 버튼에 이벤트 리스너 추가 (데이터 안전하게 전달)
    const saveBtn = document.getElementById('save-edit-btn');
    saveBtn.addEventListener('click', () => {
        submitEdit(doc.collection || doc._collection, doc.doc_id || doc._id, dynamicFields);
    });
}

/**
 * 편집 모달 닫기
 */
function closeEditModal(event) {
    if (event && event.target !== event.currentTarget) {
        return;
    }
    const modal = document.getElementById('edit-modal');
    if (modal) {
        modal.remove();
    }
}

/**
 * 문서 수정 제출
 */
function submitEdit(collection, doc_id, dynamicFields = []) {
    console.log('submitEdit called:', { collection, doc_id, dynamicFields });
    
    try {
        const updates = {
            '제목': document.getElementById('edit-제목').value.trim(),
            '카테고리': document.getElementById('edit-카테고리').value,
            '운동명': document.getElementById('edit-운동명').value.trim(),
            '내용': document.getElementById('edit-내용').value.trim(),
            '전체글': document.getElementById('edit-전체글')?.value.trim() || '',
            '데이터상태': document.getElementById('edit-데이터상태').value
        };
        
        console.log('Fixed fields:', updates);
        
        // 동적 필드 추가
        dynamicFields.forEach(key => {
            const elementId = `edit-dynamic-${key.replace(/[^a-zA-Z0-9가-힣]/g, '_')}`;
            const element = document.getElementById(elementId);
            if (element) {
                updates[key] = element.value.trim();
            }
        });
        
        console.log('All updates:', updates);
        
        fetch('/api/v1/update-documents/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                documents: [{ collection, doc_id }],
                updates: updates
            })
        })
        .then(response => {
            console.log('Response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Response data:', data);
            if (data.status === 'success') {
                alert('✅ 문서가 수정되었습니다.');
                closeEditModal();
                location.reload();
            } else {
                alert('❌ 수정 실패: ' + (data.message || '알 수 없는 오류'));
            }
        })
        .catch(error => {
            console.error('Update error:', error);
            alert('❌ 수정 중 오류 발생: ' + error.message);
        });
    } catch (error) {
        console.error('submitEdit error:', error);
        alert('❌ 에러: ' + error.message);
    }
}

/**
 * 선택된 문서로 최종본 생성
 */
function generateFinalFromSelected() {
    const checkboxes = document.querySelectorAll('.doc-checkbox:checked');
    
    if (checkboxes.length === 0) {
        alert('❌ 최종본 생성에 포함할 문서를 선택해주세요.');
        return;
    }

    const documents = Array.from(checkboxes).map(cb => ({
        collection: cb.dataset.collection,
        doc_id: cb.dataset.docId
    }));

    const confirmMsg = `선택한 ${documents.length}개 문서를 종합하여 최종본을 생성할까요?\n\nGemini가 분석하여 출판 가능한 완성본을 만듭니다.`;
    
    if (!confirm(confirmMsg)) {
        return;
    }

    // 로딩 표시
    const loadingModal = document.createElement('div');
    loadingModal.id = 'generate-loading';
    loadingModal.innerHTML = `
        <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); z-index: 9999; display: flex; align-items: center; justify-content: center;">
            <div style="background: white; padding: 40px; border-radius: 12px; text-align: center;">
                <div style="font-size: 48px; margin-bottom: 20px;">🤖</div>
                <div style="font-size: 18px; font-weight: 600; margin-bottom: 10px;">Gemini가 최종본 생성 중...</div>
                <div style="color: #666;">문서를 분석하고 종합하고 있습니다.</div>
            </div>
        </div>
    `;
    document.body.appendChild(loadingModal);

    // GENERATE FINAL API 호출
    fetch('/api/v1/generate-final/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ documents: documents })
    })
    .then(response => response.json())
    .then(data => {
        loadingModal.remove();
        if (data.status === 'success') {
            alert(`✅ 최종본이 생성되었습니다!\n\n제목: ${data.title}\n컬렉션: ${data.collection}`);
            location.reload();
        } else {
            alert('❌ 최종본 생성 실패: ' + (data.message || '알 수 없는 오류'));
        }
    })
    .catch(error => {
        loadingModal.remove();
        console.error('Generate final error:', error);
        alert('❌ 최종본 생성 중 오류 발생: ' + error.message);
    });
}

/**
 * 전체 선택/해제 토글
 */
function selectAllDocuments() {
    const checkboxes = document.querySelectorAll('.doc-checkbox');
    const allChecked = Array.from(checkboxes).every(cb => cb.checked);
    checkboxes.forEach(cb => {
        cb.checked = !allChecked;
    });
}

/**
 * 선택된 문서 삭제
 */
function deleteSelectedDocuments() {
    const checkboxes = document.querySelectorAll('.doc-checkbox:checked');
    
    if (checkboxes.length === 0) {
        alert('❌ 삭제할 문서를 선택해주세요.');
        return;
    }

    const documents = Array.from(checkboxes).map(cb => ({
        collection: cb.dataset.collection,
        doc_id: cb.dataset.docId
    }));

    const confirmMsg = `정말 ${documents.length}개 문서를 삭제할까요?\n\n삭제된 문서는 복구할 수 없습니다.`;
    
    if (!confirm(confirmMsg)) {
        return;
    }

    // DELETE API 호출
    fetch('/api/v1/delete-documents/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ documents: documents })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert(`✅ ${data.deleted_count}개 문서가 삭제되었습니다.`);
            // 체크박스 해제 및 UI 업데이트
            checkboxes.forEach(cb => {
                cb.closest('.document-item').remove();
            });
        } else {
            alert('❌ 삭제 실패: ' + (data.message || '알 수 없는 오류'));
        }
    })
    .catch(error => {
        console.error('Delete error:', error);
        alert('❌ 삭제 중 오류 발생: ' + error.message);
    });
}

// 초기화
console.log('JNext Chat Interface loaded');
