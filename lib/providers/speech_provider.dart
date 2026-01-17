import 'package:flutter/material.dart';
import 'package:audioplayers/audioplayers.dart';
import 'package:record/record.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:io';
import 'package:path_provider/path_provider.dart';

class SpeechProvider extends ChangeNotifier {
  final AudioPlayer _audioPlayer = AudioPlayer();
  final Record _audioRecorder = Record();
  
  static const String baseUrl = 'http://10.0.2.2:8000';
  static const String dummyToken = '3d9e7a1f078fb84ff6468ec229c9060759915696f7963108eb124ccc34273d4e';
  
  List<VisemeData> _visemeData = [];
  int _currentVisemeId = 0;
  bool _isRecording = false;
  bool _isPlaying = false;
  String _transcriptionResult = '';
  String _currentWord = '';
  
  List<VisemeData> get visemeData => _visemeData;
  int get currentVisemeId => _currentVisemeId;
  bool get isRecording => _isRecording;
  bool get isPlaying => _isPlaying;
  String get transcriptionResult => _transcriptionResult;
  String get currentWord => _currentWord;

  void setCurrentWord(String word) {
    _currentWord = word;
    _transcriptionResult = '_' * word.length;
    notifyListeners();
  }

  Future<void> generateVisemeData(String text) async {
    try {
      debugPrint('🎭 Generating viseme data for: $text');
      
      final response = await http.post(
        Uri.parse('$baseUrl/viseme?text=${Uri.encodeComponent(text)}'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $dummyToken',
        },
      ).timeout(const Duration(seconds: 5));

      if (response.statusCode == 200) {
        final dynamic data = json.decode(response.body);
        
        List<dynamic> visemeList;
        if (data is List) {
          visemeList = data;
        } else if (data is Map && data['visemes'] != null) {
          visemeList = data['visemes'];
        } else {
          throw Exception('Invalid viseme data format');
        }
        
        _visemeData = visemeList.map((item) => VisemeData.fromJson(item)).toList();
        debugPrint('✅ Loaded ${_visemeData.length} visemes from server');
      } else {
        debugPrint('⚠️ Server error: ${response.statusCode}');
        _generateDummyVisemeData();
      }
    } catch (e) {
      debugPrint('❌ Error generating viseme data: $e');
      _generateDummyVisemeData();
    }
  }

  Future<void> speakText(String text) async {
    if (_isPlaying) {
      debugPrint('⏸️ Already playing');
      return;
    }
    
    _isPlaying = true;
    notifyListeners();

    try {
      debugPrint('🔊 Speaking: $text');
      
      await generateVisemeData(text);

      final response = await http.post(
        Uri.parse('$baseUrl/tts?text=${Uri.encodeComponent(text)}'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $dummyToken',
        },
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final audioResponse = response.body;
        debugPrint('📥 Audio received: ${audioResponse.length} chars');
        
        String base64Audio = audioResponse;
        if (audioResponse.startsWith('"data:audio/mp3;base64,')) {
          base64Audio = audioResponse.substring('"data:audio/mp3;base64,'.length);
          if (base64Audio.endsWith('"')) {
            base64Audio = base64Audio.substring(0, base64Audio.length - 1);
          }
        }
        
        try {
          final audioBytes = base64Decode(base64Audio);
          debugPrint('🎵 Playing audio: ${audioBytes.length} bytes');
          
          await _audioPlayer.play(BytesSource(audioBytes));
          _animateVisemes();
        } catch (e) {
          debugPrint('⚠️ Audio error: $e, animating anyway');
          _animateVisemes();
        }
      } else {
        debugPrint('⚠️ TTS failed: ${response.statusCode}');
        _animateVisemes();
      }
    } catch (e) {
      debugPrint('❌ Speech error: $e');
      _animateVisemes();
    } finally {
      _isPlaying = false;
      notifyListeners();
    }
  }

  void _animateVisemes() {
    debugPrint('🎬 Starting animation with ${_visemeData.length} visemes');
    
    if (_visemeData.isEmpty) {
      _generateDummyVisemeData();
    }

    _currentVisemeId = 0;
    notifyListeners();

    int delayBetweenVisemes = 250;
    
    for (int i = 0; i < _visemeData.length; i++) {
      Future.delayed(Duration(milliseconds: delayBetweenVisemes * i), () {
        if (_visemeData.isNotEmpty && i < _visemeData.length) {
          _currentVisemeId = _visemeData[i].visemeId;
          debugPrint('👄 Viseme: $_currentVisemeId');
          notifyListeners();
        }
      });
    }
    
    int totalDuration = delayBetweenVisemes * _visemeData.length;
    Future.delayed(Duration(milliseconds: totalDuration + 300), () {
      _currentVisemeId = 0;
      debugPrint('😐 Reset to neutral');
      notifyListeners();
    });
  }

  void _generateDummyVisemeData() {
    debugPrint('🎭 Using dummy viseme data');
    _visemeData = [
      VisemeData(audioOffset: 0, visemeId: 0),
      VisemeData(audioOffset: 1, visemeId: 1),
      VisemeData(audioOffset: 2, visemeId: 6),
      VisemeData(audioOffset: 3, visemeId: 4),
      VisemeData(audioOffset: 4, visemeId: 2),
      VisemeData(audioOffset: 5, visemeId: 6),
      VisemeData(audioOffset: 6, visemeId: 1),
      VisemeData(audioOffset: 7, visemeId: 0),
    ];
  }

  Future<void> startRecording() async {
    try {
      if (!await _audioRecorder.hasPermission()) {
        debugPrint('❌ No mic permission');
        return;
      }

      if (await _audioRecorder.isRecording()) {
        debugPrint('⚠️ Already recording');
        return;
      }

      final Directory tempDir = await getTemporaryDirectory();
      final String filePath = '${tempDir.path}/recording_${DateTime.now().millisecondsSinceEpoch}.wav';
      
      await _audioRecorder.start(
        path: filePath,
        encoder: AudioEncoder.wav,
        bitRate: 16000,
        samplingRate: 16000,
      );
      
      _isRecording = true;
      notifyListeners();
      debugPrint('🎤 Recording started');
    } catch (e) {
      debugPrint('❌ Recording error: $e');
      _isRecording = false;
      notifyListeners();
    }
  }

  Future<void> stopRecording() async {
    try {
      if (!_isRecording) {
        return;
      }

      if (await _audioRecorder.isRecording()) {
        final String? filePath = await _audioRecorder.stop();
        debugPrint('⏹️ Recording stopped');
        
        _isRecording = false;
        notifyListeners();
        
        if (filePath != null && File(filePath).existsSync()) {
          await _transcribeAudio(filePath);
        } else {
          debugPrint('❌ No recording file');
          _transcriptionResult = 'Recording failed';
          notifyListeners();
        }
      }
    } catch (e) {
      debugPrint('❌ Stop error: $e');
      _isRecording = false;
      notifyListeners();
    }
  }

  Future<void> _transcribeAudio(String filePath) async {
    try {
      debugPrint('📝 Transcribing...');
      
      final File audioFile = File(filePath);
      
      if (!await audioFile.exists()) {
        _transcriptionResult = 'Recording failed';
        notifyListeners();
        return;
      }

      final request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseUrl/transcribe'),
      );
      
      request.headers['Authorization'] = 'Bearer $dummyToken';
      request.files.add(
        await http.MultipartFile.fromPath('file', audioFile.path),
      );
      request.fields['language'] = 'tamil';
      
      final response = await request.send().timeout(const Duration(seconds: 30));
      final responseBody = await response.stream.bytesToString();
      
      if (response.statusCode == 200) {
        final Map<String, dynamic> data = json.decode(responseBody);
        
        if (data['status'] == 'success') {
          _transcriptionResult = data['transcript'] ?? 'No transcription';
          debugPrint('✅ Transcription: $_transcriptionResult');
        } else {
          _transcriptionResult = 'Transcription failed';
        }
      } else {
        _transcriptionResult = 'Error: ${response.statusCode}';
      }
      
      notifyListeners();
    } catch (e) {
      debugPrint('❌ Transcription error: $e');
      _transcriptionResult = 'Transcription error';
      notifyListeners();
    }
  }

  List<TextSpan> getComparisonText() {
    final List<TextSpan> spans = [];
    final int maxLength = _currentWord.length > _transcriptionResult.length 
        ? _currentWord.length 
        : _transcriptionResult.length;
    
    for (int i = 0; i < maxLength; i++) {
      final String expectedChar = i < _currentWord.length ? _currentWord[i] : '';
      final String actualChar = i < _transcriptionResult.length ? _transcriptionResult[i] : '';
      
      Color color = Colors.black;
      if (actualChar == '_') {
        color = Colors.grey;
      } else if (expectedChar != actualChar) {
        color = Colors.red;
      } else {
        color = Colors.green;
      }
      
      spans.add(TextSpan(
        text: actualChar,
        style: TextStyle(
          color: color,
          fontSize: 18,
          fontWeight: FontWeight.bold,
        ),
      ));
    }
    
    return spans;
  }

  @override
  void dispose() {
    _audioPlayer.dispose();
    _audioRecorder.dispose();
    super.dispose();
  }
}

class VisemeData {
  final int audioOffset;
  final int visemeId;

  VisemeData({required this.audioOffset, required this.visemeId});

  factory VisemeData.fromJson(Map<String, dynamic> json) {
    return VisemeData(
      audioOffset: json['privAudioOffset'] ?? json['audioOffset'] ?? 0,
      visemeId: json['privVisemeId'] ?? json['visemeId'] ?? 0,
    );
  }
}