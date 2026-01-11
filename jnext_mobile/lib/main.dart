import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(const JNextApp());
}

class JNextApp extends StatelessWidget {
  const JNextApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'JNext Mobile',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.deepPurple,
          brightness: Brightness.light,
        ),
        useMaterial3: true,
        appBarTheme: const AppBarTheme(
          centerTitle: true,
          elevation: 0,
        ),
      ),
      home: const ChatScreen(),
    );
  }
}

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _messageController = TextEditingController();
  final List<ChatMessage> _messages = [];
  // Render 서버 사용 (어디서나 접속 가능)
  final String _apiUrl = 'https://jnext.onrender.com/api/v1/chat/';
  bool _isLoading = false;
  final ScrollController _scrollController = ScrollController();
  String _mode = 'hybrid'; // 기본값: 통합 모드 (DB + 현재 분석)
  String _model = 'gemini-flash'; // 기본값: 젠 (Gemini Flash)

  Future<void> _sendMessage() async {
    final message = _messageController.text.trim();
    if (message.isEmpty) return;

    setState(() {
      _messages.add(ChatMessage(
        text: message,
        isUser: true,
        timestamp: DateTime.now(),
      ));
      _isLoading = true;
    });

    _messageController.clear();
    
    // 스크롤을 적정 위치로 (입력창 가리지 않음)
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent - 80,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });

    try {
      final response = await http.post(
        Uri.parse(_apiUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'message': message, 'mode': _mode, 'model': _model}),
      ).timeout(
        const Duration(seconds: 60),
        onTimeout: () {
          throw Exception('서버 응답 시간 초과 (60초)');
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        final answer = data['response']?['answer'] ?? '응답 없음';
        final action = data['action'];
        
        // ⚠️ SAVE 액션: 저장 모달창 띄우기 (바로 저장 X)
        if (action == 'SAVE' && data['save_data'] != null) {
          setState(() {
            _messages.add(ChatMessage(
              text: '💾 ' + answer,
              isUser: false,
              timestamp: DateTime.now(),
              responseData: data,
            ));
            _isLoading = false;
          });
          
          // 저장 모달창 표시
          _showSaveDialog(context, data['save_data']);
          return;
        }
        
        // 액션에 따른 아이콘
        String icon = '🤖 ';
        if (action == 'READ') icon = '📊 ';
        else if (action == 'GENERATE_FINAL') icon = '📝 ';
        else if (action == 'DELETE') icon = '🗑️ ';
        else if (action == 'UPDATE') icon = '✏️ ';
        
        setState(() {
          _messages.add(ChatMessage(
            text: icon + answer,
            isUser: false,
            timestamp: DateTime.now(),
            responseData: data,
          ));
          _isLoading = false;
        });
        
        // 스크롤을 적정 위치로 (입력창 가리지 않음)
        Future.delayed(const Duration(milliseconds: 100), () {
          if (_scrollController.hasClients) {
            _scrollController.animateTo(
              _scrollController.position.maxScrollExtent - 80,
              duration: const Duration(milliseconds: 300),
              curve: Curves.easeOut,
            );
          }
        });
      } else {
        setState(() {
          _messages.add(ChatMessage(
            text: '❌ 오류: ${response.statusCode}\n서버 응답: ${utf8.decode(response.bodyBytes)}',
            isUser: false,
            timestamp: DateTime.now(),
          ));
          _isLoading = false;
        });
      }
    } catch (e) {
      String errorDetail = '';
      if (e.toString().contains('SocketException')) {
        errorDetail = '네트워크 연결 실패\n• Wi-Fi 연결 확인\n• PC와 같은 네트워크인지 확인';
      } else if (e.toString().contains('TimeoutException')) {
        errorDetail = '서버 응답 시간 초과 (30초)\n• Django 서버가 실행 중인지 확인';
      } else {
        errorDetail = e.toString();
      }
      
      setState(() {
        _messages.add(ChatMessage(
          text: '❌ 연결 실패\n\n$errorDetail\n\n📍 서버 주소: $_apiUrl\n📋 모드: $_mode\n\n✅ 확인사항:\n1. 터미널에서 Django 서버 실행 중?\n   (python manage.py runserver)\n2. PC IP가 192.168.219.139 맞나요?\n   (ipconfig 확인)\n3. 방화벽에서 8000 포트 허용?',
          isUser: false,
          timestamp: DateTime.now(),
        ));
        _isLoading = false;
      });
      
      // 콘솔에 상세 에러 출력
      print('[JNext Error] $_apiUrl');
      print('[JNext Error] Mode: $_mode');
      print('[JNext Error] Exception: $e');
    }
  }

  // 저장 모달창 표시 (컬렉션 선택, 내용 수정 가능)
  Future<void> _showSaveDialog(BuildContext context, Map<String, dynamic> saveData) async {
    final titleController = TextEditingController(text: saveData['title']);
    final categoryController = TextEditingController(text: saveData['category']);
    final contentController = TextEditingController(text: saveData['content']);
    final fullArticleController = TextEditingController(text: saveData['full_article']);
    String selectedCollection = saveData['collection'] ?? 'hino_draft';

    await showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('💾 저장하기'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 컬렉션 선택
              const Text('컬렉션', style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              DropdownButtonFormField<String>(
                value: selectedCollection,
                items: const [
                  DropdownMenuItem(value: 'hino_raw', child: Text('💭 Raw (아이디어)')),
                  DropdownMenuItem(value: 'hino_draft', child: Text('📝 Draft (초안)')),
                  DropdownMenuItem(value: 'hino_final', child: Text('✅ Final (최종)')),
                ],
                onChanged: (value) {
                  selectedCollection = value!;
                },
                decoration: const InputDecoration(
                  border: OutlineInputBorder(),
                  contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                ),
              ),
              const SizedBox(height: 16),
              
              // 제목
              const Text('제목', style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              TextField(
                controller: titleController,
                decoration: const InputDecoration(
                  border: OutlineInputBorder(),
                  contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                ),
              ),
              const SizedBox(height: 16),
              
              // 카테고리
              const Text('카테고리', style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              TextField(
                controller: categoryController,
                decoration: const InputDecoration(
                  border: OutlineInputBorder(),
                  contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                ),
              ),
              const SizedBox(height: 16),
              
              // 내용 (요약)
              const Text('내용 (요약)', style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              TextField(
                controller: contentController,
                maxLines: 5,
                decoration: const InputDecoration(
                  border: OutlineInputBorder(),
                  contentPadding: EdgeInsets.all(12),
                ),
              ),
              const SizedBox(height: 16),
              
              // 전체글
              const Text('전체글', style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              TextField(
                controller: fullArticleController,
                maxLines: 10,
                decoration: const InputDecoration(
                  border: OutlineInputBorder(),
                  contentPadding: EdgeInsets.all(12),
                ),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('취소'),
          ),
          ElevatedButton(
            onPressed: () async {
              // 실제 저장 API 호출
              await _saveDocument(
                collection: selectedCollection,
                title: titleController.text,
                category: categoryController.text,
                content: contentController.text,
                fullArticle: fullArticleController.text,
                originalQuestion: saveData['original_question'],
                aiResponse: saveData['ai_response'],
              );
              Navigator.pop(context);
            },
            child: const Text('저장'),
          ),
        ],
      ),
    );
  }

  // 실제 저장 API 호출
  Future<void> _saveDocument({
    required String collection,
    required String title,
    required String category,
    required String content,
    required String fullArticle,
    required String originalQuestion,
    required Map<String, dynamic> aiResponse,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('https://jnext.onrender.com/api/v1/save-summary/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'collection': collection,
          'title': title,
          'category': category,
          'subcategory': '',
          'content': content,
          'full_article': fullArticle,
          'original_question': originalQuestion,
          'ai_response': aiResponse,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        setState(() {
          _messages.add(ChatMessage(
            text: '✅ 저장 완료!\n컬렉션: $collection\n문서 ID: ${data['doc_id']}',
            isUser: false,
            timestamp: DateTime.now(),
          ));
        });
      } else {
        setState(() {
          _messages.add(ChatMessage(
            text: '❌ 저장 실패: ${response.statusCode}\n${utf8.decode(response.bodyBytes)}',
            isUser: false,
            timestamp: DateTime.now(),
          ));
        });
      }
    } catch (e) {
      setState(() {
        _messages.add(ChatMessage(
          text: '❌ 저장 오류: $e',
          isUser: false,
          timestamp: DateTime.now(),
        ));
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: Row(
          children: [
            const Text(
              'JNext AI',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(width: 12),
            // 3개 모드 선택 칩
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.9),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                  color: _mode == 'organize' 
                    ? Colors.blue.shade300 
                    : _mode == 'hybrid' 
                      ? Colors.green.shade300 
                      : Colors.purple.shade300,
                  width: 1.5,
                ),
              ),
              child: DropdownButton<String>(
                value: _mode,
                underline: Container(),
                isDense: true,
                icon: Icon(
                  Icons.arrow_drop_down,
                  size: 14,
                  color: _mode == 'organize' 
                    ? Colors.blue.shade700 
                    : _mode == 'hybrid' 
                      ? Colors.green.shade700 
                      : Colors.purple.shade700,
                ),
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                  color: _mode == 'organize' 
                    ? Colors.blue.shade700 
                    : _mode == 'hybrid' 
                      ? Colors.green.shade700 
                      : Colors.purple.shade700,
                ),
                items: const [
                  DropdownMenuItem(
                    value: 'organize',
                    child: Text('DB', style: TextStyle(fontSize: 11)),
                  ),
                  DropdownMenuItem(
                    value: 'hybrid',
                    child: Text('통합', style: TextStyle(fontSize: 11)),
                  ),
                  DropdownMenuItem(
                    value: 'analysis',
                    child: Text('대화', style: TextStyle(fontSize: 11)),
                  ),
                ],
                onChanged: (String? newValue) {
                  if (newValue != null) {
                    setState(() {
                      _mode = newValue;
                    });
                  }
                },
              ),
            ),
            const SizedBox(width: 8),
            // AI 모델 선택
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.9),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                  color: Colors.orange.shade300,
                  width: 1.5,
                ),
              ),
              child: DropdownButton<String>(
                value: _model,
                underline: Container(),
                isDense: true,
                icon: Icon(Icons.arrow_drop_down, size: 14, color: Colors.orange.shade700),
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                  color: Colors.orange.shade700,
                ),
                items: const [
                  DropdownMenuItem(
                    value: 'gemini-flash',
                    child: Text('젠', style: TextStyle(fontSize: 11)),
                  ),
                  DropdownMenuItem(
                    value: 'gemini-pro',
                    child: Text('젠시', style: TextStyle(fontSize: 11)),
                  ),
                  DropdownMenuItem(
                    value: 'gpt',
                    child: Text('진', style: TextStyle(fontSize: 11)),
                  ),
                ],
                onChanged: (String? newValue) {
                  if (newValue != null) {
                    setState(() {
                      _model = newValue;
                    });
                  }
                },
              ),
            ),
          ],
        ),
        backgroundColor: Theme.of(context).colorScheme.primaryContainer,
        actions: [
          IconButton(
            icon: const Icon(Icons.search),
            tooltip: '문서 검색',
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const SearchScreen()),
              );
            },
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: SafeArea(
        child: Column(
          children: [
            // 입력창을 위로 이동
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              decoration: BoxDecoration(
                color: Colors.white,
                boxShadow: [
                  BoxShadow(
                    color: Colors.grey.withOpacity(0.2),
                    blurRadius: 8,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _messageController,
                      maxLines: 5,
                      minLines: 1,
                      keyboardType: TextInputType.multiline,
                      decoration: InputDecoration(
                        hintText: '메시지를 입력하세요...',
                        filled: true,
                        fillColor: Colors.grey[100],
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(24),
                          borderSide: BorderSide.none,
                        ),
                        contentPadding: const EdgeInsets.symmetric(
                          horizontal: 20,
                          vertical: 14,
                        ),
                        prefixIcon: const Icon(Icons.chat_bubble_outline),
                        suffixIcon: IconButton(
                          icon: const Icon(Icons.keyboard_hide),
                          onPressed: () => FocusScope.of(context).unfocus(),
                          tooltip: '키보드 내리기',
                        ),
                      ),
                      onSubmitted: (_) => _sendMessage(),
                      textInputAction: TextInputAction.newline,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Container(
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [
                          Theme.of(context).colorScheme.primary,
                          Theme.of(context).colorScheme.secondary,
                        ],
                      ),
                      shape: BoxShape.circle,
                    ),
                    child: IconButton(
                      icon: const Icon(Icons.send, color: Colors.white),
                      onPressed: _isLoading ? null : _sendMessage,
                    ),
                  ),
                ],
              ),
            ),
            // 메시지 리스트
            Expanded(
              child: _messages.isEmpty
                  ? Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            Icons.chat_outlined,
                            size: 80,
                            color: Colors.grey[300],
                          ),
                          const SizedBox(height: 16),
                          Text(
                            'JNext에게 물어보세요!',
                            style: TextStyle(
                              fontSize: 18,
                              color: Colors.grey[600],
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            '"하이노워킹 알려줘"',
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.grey[400],
                            ),
                          ),
                        ],
                      ),
                    )
                  : ListView.builder(
                      controller: _scrollController,
                      padding: const EdgeInsets.all(16),
                      itemCount: _messages.length,
                      itemBuilder: (context, index) {
                        final message = _messages[index];
                        return ChatBubble(message: message);
                      },
                    ),
            ),
            if (_isLoading)
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: Row(
                  children: [
                    SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Theme.of(context).colorScheme.primary,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Text(
                      'AI가 생각 중...',
                      style: TextStyle(
                        color: Colors.grey[600],
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class ChatMessage {
  final String text;
  final bool isUser;
  final DateTime timestamp;
  final Map<String, dynamic>? responseData;

  ChatMessage({
    required this.text,
    required this.isUser,
    required this.timestamp,
    this.responseData,
  });
}

class ChatBubble extends StatelessWidget {
  final ChatMessage message;

  const ChatBubble({super.key, required this.message});

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: message.isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: GestureDetector(
        onLongPress: () {
          Clipboard.setData(ClipboardData(text: message.text));
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('메시지가 복사되었습니다'),
              duration: Duration(seconds: 1),
            ),
          );
        },
        child: Container(
          margin: const EdgeInsets.only(bottom: 8),
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
          decoration: BoxDecoration(
            gradient: message.isUser
                ? LinearGradient(
                    colors: [
                      Theme.of(context).colorScheme.primary,
                      Theme.of(context).colorScheme.secondary,
                    ],
                  )
                : null,
            color: message.isUser ? null : Colors.white,
            borderRadius: BorderRadius.only(
              topLeft: const Radius.circular(20),
              topRight: const Radius.circular(20),
              bottomLeft: message.isUser
                  ? const Radius.circular(20)
                  : const Radius.circular(4),
              bottomRight: message.isUser
                  ? const Radius.circular(4)
                  : const Radius.circular(20),
            ),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.05),
                blurRadius: 8,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          constraints: BoxConstraints(
            maxWidth: MediaQuery.of(context).size.width * 0.75,
          ),
          child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              message.text,
              style: TextStyle(
                fontSize: 16,
                color: message.isUser ? Colors.white : Colors.black87,
                height: 1.4,
              ),
            ),
            if (message.responseData != null &&
                message.responseData!['document_list'] != null)
              ...[
                const SizedBox(height: 12),
                GestureDetector(
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => DocumentListScreen(
                          documents: message.responseData!['document_list'],
                        ),
                      ),
                    );
                  },
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.blue[50],
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.blue[200]!),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(Icons.description, size: 18, color: Colors.blue),
                        const SizedBox(width: 8),
                        Text(
                          '${message.responseData!['document_list'].length}개 문서 보기',
                          style: const TextStyle(
                            fontSize: 14,
                            color: Colors.blue,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        const SizedBox(width: 4),
                        const Icon(Icons.arrow_forward_ios, size: 12, color: Colors.blue),
                      ],
                    ),
                  ),
                ),
              ],
          ],
        ),
        ), // Container 닫기
      ), // GestureDetector 닫기
    ); // Align 닫기
  }
}

class SearchScreen extends StatefulWidget {
  const SearchScreen({super.key});

  @override
  State<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends State<SearchScreen> {
  final TextEditingController _searchController = TextEditingController();
  List<dynamic> _documents = [];
  bool _isLoading = false;
  final String _apiUrl = 'https://jnext.onrender.com/api/v1/chat/';
  final String _getDocUrl = 'https://jnext.onrender.com/api/v1/get-document/';
  final String _saveSummaryUrl = 'https://jnext.onrender.com/api/v1/save-summary/';

  Future<void> _search() async {
    final query = _searchController.text.trim();
    if (query.isEmpty) return;

    setState(() {
      _isLoading = true;
    });

    try {
      final response = await http.post(
        Uri.parse(_apiUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'message': '검색 $query', 'mode': 'organize'}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        setState(() {
          _documents = data['document_list'] ?? [];
          _isLoading = false;
        });
      } else {
        setState(() {
          _isLoading = false;
        });
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('오류: ${response.statusCode}')),
          );
        }
      }
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('연결 실패: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: const Text(
          '문서 검색',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        backgroundColor: Theme.of(context).colorScheme.primaryContainer,
      ),
      body: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(16.0),
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.grey.withOpacity(0.2),
                  blurRadius: 8,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _searchController,
                    decoration: InputDecoration(
                      hintText: '카테고리 또는 키워드 검색...',
                      filled: true,
                      fillColor: Colors.grey[100],
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(24),
                        borderSide: BorderSide.none,
                      ),
                      prefixIcon: const Icon(Icons.search),
                      contentPadding: const EdgeInsets.symmetric(vertical: 14),
                    ),
                    onSubmitted: (_) => _search(),
                  ),
                ),
                const SizedBox(width: 12),
                Container(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [
                        Theme.of(context).colorScheme.primary,
                        Theme.of(context).colorScheme.secondary,
                      ],
                    ),
                    borderRadius: BorderRadius.circular(24),
                  ),
                  child: ElevatedButton(
                    onPressed: _isLoading ? null : _search,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.transparent,
                      shadowColor: Colors.transparent,
                      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
                    ),
                    child: const Text(
                      '검색',
                      style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
          if (_isLoading)
            const Padding(
              padding: EdgeInsets.all(24.0),
              child: CircularProgressIndicator(),
            ),
          if (!_isLoading && _documents.isEmpty)
            Expanded(
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.search_off,
                      size: 80,
                      color: Colors.grey[300],
                    ),
                    const SizedBox(height: 16),
                    Text(
                      '검색 결과가 없습니다',
                      style: TextStyle(
                        fontSize: 16,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          if (!_isLoading && _documents.isNotEmpty)
            Expanded(
              child: ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: _documents.length,
                itemBuilder: (context, index) {
                  final doc = _documents[index];
                  return Card(
                    elevation: 2,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    margin: const EdgeInsets.only(bottom: 12),
                    child: ListTile(
                      contentPadding: const EdgeInsets.all(16),
                      title: Text(
                        doc['title'] ?? 'N/A',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      subtitle: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const SizedBox(height: 8),
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 8,
                              vertical: 4,
                            ),
                            decoration: BoxDecoration(
                              color: Theme.of(context).colorScheme.primaryContainer,
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Text(
                              doc['category'] ?? 'N/A',
                              style: TextStyle(
                                fontSize: 11,
                                color: Theme.of(context).colorScheme.primary,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            doc['preview'] ?? '',
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                            style: TextStyle(
                              color: Colors.grey[600],
                              height: 1.4,
                            ),
                          ),
                        ],
                      ),
                      trailing: Icon(
                        Icons.edit,
                        color: Theme.of(context).colorScheme.primary,
                      ),
                      onTap: () => _showEditModal(doc),
                    ),
                  );
                },
              ),
            ),
        ],
      ),
    );
  }

  // 문서 편집 모달
  Future<void> _showEditModal(Map<String, dynamic> doc) async {
    // 전체 문서 불러오기
    final fullDoc = await _getFullDocument(doc['collection'], doc['doc_id']);
    if (fullDoc == null) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('❌ 문서를 불러올 수 없습니다')),
        );
      }
      return;
    }

    if (!mounted) return;

    final titleController = TextEditingController(text: fullDoc['제목'] ?? fullDoc['title'] ?? '');
    final contentController = TextEditingController(text: fullDoc['내용'] ?? '');
    String selectedCategory = fullDoc['카테고리'] ?? fullDoc['category'] ?? '하이노이론';
    String selectedCollection = doc['collection'] ?? 'hino_draft';

    await showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          title: const Text('✏️ 문서 편집', style: TextStyle(fontWeight: FontWeight.bold)),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // 제목
                TextField(
                  controller: titleController,
                  decoration: const InputDecoration(
                    labelText: '제목',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 16),
                // 카테고리
                DropdownButtonFormField<String>(
                  value: selectedCategory,
                  decoration: const InputDecoration(
                    labelText: '카테고리',
                    border: OutlineInputBorder(),
                  ),
                  items: const [
                    DropdownMenuItem(value: '하이노이론', child: Text('하이노이론')),
                    DropdownMenuItem(value: '하이노워킹', child: Text('하이노워킹')),
                    DropdownMenuItem(value: '하이노스케이팅', child: Text('하이노스케이팅')),
                    DropdownMenuItem(value: '하이노철봉', child: Text('하이노철봉')),
                    DropdownMenuItem(value: '하이노기본', child: Text('하이노기본')),
                    DropdownMenuItem(value: '하이노밸런스', child: Text('하이노밸런스')),
                    DropdownMenuItem(value: '기타', child: Text('기타')),
                  ],
                  onChanged: (value) => setState(() => selectedCategory = value!),
                ),
                const SizedBox(height: 16),
                // 컬렉션 선택
                DropdownButtonFormField<String>(
                  value: selectedCollection,
                  decoration: const InputDecoration(
                    labelText: '저장 위치',
                    border: OutlineInputBorder(),
                  ),
                  items: const [
                    DropdownMenuItem(value: 'hino_raw', child: Text('💭 Raw (아이디어)')),
                    DropdownMenuItem(value: 'hino_draft', child: Text('📝 Draft (초안)')),
                    DropdownMenuItem(value: 'hino_final', child: Text('✅ Final (최종)')),
                  ],
                  onChanged: (value) => setState(() => selectedCollection = value!),
                ),
                const SizedBox(height: 16),
                // 내용
                TextField(
                  controller: contentController,
                  decoration: const InputDecoration(
                    labelText: '내용',
                    border: OutlineInputBorder(),
                  ),
                  maxLines: 10,
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('취소'),
            ),
            ElevatedButton(
              onPressed: () async {
                Navigator.pop(context);
                await _saveDocument(
                  docId: doc['doc_id'],
                  sourceCollection: doc['collection'],
                  targetCollection: selectedCollection,
                  title: titleController.text,
                  category: selectedCategory,
                  content: contentController.text,
                );
              },
              child: const Text('저장'),
            ),
          ],
        ),
      ),
    );
  }

  // 전체 문서 가져오기
  Future<Map<String, dynamic>?> _getFullDocument(String collection, String docId) async {
    try {
      final response = await http.get(
        Uri.parse('$_getDocUrl?collection=$collection&doc_id=$docId'),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        if (data['status'] == 'success') {
          return data['document'];
        }
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  // 문서 저장 (생성 또는 수정/이동)
  Future<void> _saveDocument({
    String? docId,
    required String sourceCollection,
    required String targetCollection,
    required String title,
    required String category,
    required String content,
  }) async {
    try {
      final response = await http.post(
        Uri.parse(_saveSummaryUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'doc_id': docId,
          'source_collection': sourceCollection,
          'collection': targetCollection,
          'title': title,
          'category': category,
          'content': content,
          'original_message': '',
          'ai_response': {},
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        if (data['status'] == 'success') {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text(data['message'] ?? '✅ 저장되었습니다')),
            );
            // 검색 결과 새로고침
            _search();
          }
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('❌ 저장 실패: $e')),
        );
      }
    }
  }
}

// 문서 리스트 화면 (채팅에서 문서 클릭 시)
class DocumentListScreen extends StatefulWidget {
  final List<dynamic> documents;

  const DocumentListScreen({super.key, required this.documents});

  @override
  State<DocumentListScreen> createState() => _DocumentListScreenState();
}

class _DocumentListScreenState extends State<DocumentListScreen> {
  final String _getDocUrl = 'https://jnext.onrender.com/api/v1/get-document/';
  final String _saveSummaryUrl = 'https://jnext.onrender.com/api/v1/save-summary/';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: Text(
          '문서 리스트 (${widget.documents.length}개)',
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        backgroundColor: Theme.of(context).colorScheme.primaryContainer,
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: widget.documents.length,
        itemBuilder: (context, index) {
          final doc = widget.documents[index];
          return Card(
            elevation: 2,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            margin: const EdgeInsets.only(bottom: 12),
            child: ListTile(
              contentPadding: const EdgeInsets.all(16),
              leading: CircleAvatar(
                backgroundColor: Theme.of(context).colorScheme.primary,
                child: Text(
                  '${index + 1}',
                  style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                ),
              ),
              title: Text(
                doc['title'] ?? 'N/A',
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
              subtitle: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: Theme.of(context).colorScheme.primaryContainer,
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          doc['collection'] ?? 'N/A',
                          style: TextStyle(
                            fontSize: 11,
                            color: Theme.of(context).colorScheme.primary,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        doc['category'] ?? 'N/A',
                        style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    doc['preview'] ?? '',
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                      color: Colors.grey[600],
                      height: 1.4,
                    ),
                  ),
                ],
              ),
              trailing: Icon(
                Icons.edit,
                color: Theme.of(context).colorScheme.primary,
              ),
              onTap: () => _showEditModal(doc),
            ),
          );
        },
      ),
    );
  }

  // 문서 편집 모달 (SearchScreen과 동일)
  Future<void> _showEditModal(Map<String, dynamic> doc) async {
    final fullDoc = await _getFullDocument(doc['collection'], doc['doc_id']);
    if (fullDoc == null) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('❌ 문서를 불러올 수 없습니다')),
        );
      }
      return;
    }

    if (!mounted) return;

    final titleController = TextEditingController(text: fullDoc['제목'] ?? fullDoc['title'] ?? '');
    final contentController = TextEditingController(text: fullDoc['내용'] ?? '');
    String selectedCategory = fullDoc['카테고리'] ?? fullDoc['category'] ?? '하이노이론';
    String selectedCollection = doc['collection'] ?? 'hino_draft';

    await showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          title: const Text('✏️ 문서 편집', style: TextStyle(fontWeight: FontWeight.bold)),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                TextField(
                  controller: titleController,
                  decoration: const InputDecoration(
                    labelText: '제목',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 16),
                DropdownButtonFormField<String>(
                  value: selectedCategory,
                  decoration: const InputDecoration(
                    labelText: '카테고리',
                    border: OutlineInputBorder(),
                  ),
                  items: const [
                    DropdownMenuItem(value: '하이노이론', child: Text('하이노이론')),
                    DropdownMenuItem(value: '하이노워킹', child: Text('하이노워킹')),
                    DropdownMenuItem(value: '하이노스케이팅', child: Text('하이노스케이팅')),
                    DropdownMenuItem(value: '하이노철봉', child: Text('하이노철봉')),
                    DropdownMenuItem(value: '하이노기본', child: Text('하이노기본')),
                    DropdownMenuItem(value: '하이노밸런스', child: Text('하이노밸런스')),
                    DropdownMenuItem(value: '기타', child: Text('기타')),
                  ],
                  onChanged: (value) => setState(() => selectedCategory = value!),
                ),
                const SizedBox(height: 16),
                DropdownButtonFormField<String>(
                  value: selectedCollection,
                  decoration: const InputDecoration(
                    labelText: '저장 위치',
                    border: OutlineInputBorder(),
                  ),
                  items: const [
                    DropdownMenuItem(value: 'hino_raw', child: Text('💭 Raw (아이디어)')),
                    DropdownMenuItem(value: 'hino_draft', child: Text('📝 Draft (초안)')),
                    DropdownMenuItem(value: 'hino_final', child: Text('✅ Final (최종)')),
                  ],
                  onChanged: (value) => setState(() => selectedCollection = value!),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: contentController,
                  decoration: const InputDecoration(
                    labelText: '내용',
                    border: OutlineInputBorder(),
                  ),
                  maxLines: 10,
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('취소'),
            ),
            ElevatedButton(
              onPressed: () async {
                Navigator.pop(context);
                await _saveDocument(
                  docId: doc['doc_id'],
                  sourceCollection: doc['collection'],
                  targetCollection: selectedCollection,
                  title: titleController.text,
                  category: selectedCategory,
                  content: contentController.text,
                );
              },
              child: const Text('저장'),
            ),
          ],
        ),
      ),
    );
  }

  Future<Map<String, dynamic>?> _getFullDocument(String collection, String docId) async {
    try {
      final response = await http.get(
        Uri.parse('$_getDocUrl?collection=$collection&doc_id=$docId'),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        if (data['status'] == 'success') {
          return data['document'];
        }
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  Future<void> _saveDocument({
    String? docId,
    required String sourceCollection,
    required String targetCollection,
    required String title,
    required String category,
    required String content,
  }) async {
    try {
      final response = await http.post(
        Uri.parse(_saveSummaryUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'doc_id': docId,
          'source_collection': sourceCollection,
          'collection': targetCollection,
          'title': title,
          'category': category,
          'content': content,
          'original_message': '',
          'ai_response': {},
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        if (data['status'] == 'success') {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text(data['message'] ?? '✅ 저장되었습니다')),
            );
            // 화면 닫기
            Navigator.pop(context);
          }
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('❌ 저장 실패: $e')),
        );
      }
    }
  }
}
