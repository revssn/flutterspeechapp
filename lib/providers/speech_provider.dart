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
  
  // Server configuration - change this to your local server
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
      final response = await http.post(
        Uri.parse('$baseUrl/viseme?text=${Uri.encodeComponent(text)}'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        _visemeData = data.map((item) => VisemeData.fromJson(item)).toList();
        debugPrint('Generated ${_visemeData.length} visemes');
        notifyListeners();
      } else {
        throw Exception('Failed to generate viseme data');
      }
    } catch (e) {
      debugPrint('Error generating viseme data: $e');
      // Fallback to dummy data
      _generateDummyVisemeData();
    }
  }

  Future<void> speakText(String text) async {
    try {
      _isPlaying = true;
      notifyListeners();

      // Generate viseme data
      await generateVisemeData(text);

      // Get audio from server
      final response = await http.post(
        Uri.parse('$baseUrl/tts?text=${Uri.encodeComponent(text)}'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final audioResponse = response.body;
        debugPrint('Audio response received: ${audioResponse.length} characters');
        
        // Remove the data:audio/mp3;base64, prefix
        String base64Audio = audioResponse;
        if (audioResponse.startsWith('"data:audio/mp3;base64,')) {
          base64Audio = audioResponse.substring('"data:audio/mp3;base64,'.length);
          if (base64Audio.endsWith('"')) {
            base64Audio = base64Audio.substring(0, base64Audio.length - 1);
          }
        }
        
        try {
          // Decode base64 to bytes
          final audioBytes = base64Decode(base64Audio);
          debugPrint('Decoded audio bytes: ${audioBytes.length}');
          
          // Play using BytesSource
          await _audioPlayer.play(BytesSource(audioBytes));
          debugPrint('Audio playback started');
          
          // Animate visemes
          _animateVisemes();
        } catch (e) {
          debugPrint('Error decoding/playing audio: $e');
          // Still animate visemes even if audio fails
          _animateVisemes();
        }
      } else {
        throw Exception('Failed to generate speech');
      }
    } catch (e) {
      debugPrint('Error in speech synthesis: $e');
      // Still animate visemes even if TTS fails
      _animateVisemes();
    } finally {
      _isPlaying = false;
      notifyListeners();
    }
  }

  // void _animateVisemes() {
  //   for (final viseme in _visemeData) {
  //     final delayMs = (viseme.audioOffset / 10000).round();
  //     Future.delayed(Duration(milliseconds: delayMs), () {
  //       _currentVisemeId = viseme.visemeId;
  //       notifyListeners();
  //     });
  //   }
    
  //   // Reset to neutral position after animation
  //   Future.delayed(const Duration(milliseconds: 3000), () {
  //     _currentVisemeId = 0;
  //     notifyListeners();
  //   });
  // }
  void _animateVisemes() {
  // CHANGE: Just multiply the existing delay to slow it down
  double speedMultiplier = 3.0;  // 2.0 = twice as slow, 3.0 = three times slower
  
  for (final viseme in _visemeData) {
    final delayMs = ((viseme.audioOffset / 10000) * speedMultiplier).round();
    Future.delayed(Duration(milliseconds: delayMs), () {
      _currentVisemeId = viseme.visemeId;
      notifyListeners();
    });
  }
  
  // Reset to neutral position after animation
  Future.delayed(const Duration(milliseconds: 5000), () {  // Increased from 3000
    _currentVisemeId = 0;
    notifyListeners();
  });
}

  void _generateDummyVisemeData() {
    _visemeData = [
      VisemeData(audioOffset: 0, visemeId: 0),
      VisemeData(audioOffset: 500000, visemeId: 2),
      VisemeData(audioOffset: 1000000, visemeId: 4),
      VisemeData(audioOffset: 1500000, visemeId: 6),
      VisemeData(audioOffset: 2000000, visemeId: 0),
    ];
    debugPrint('Using dummy viseme data');
  }

  Future<void> startRecording() async {
    try {
      // Check permissions first
      if (!await _audioRecorder.hasPermission()) {
        debugPrint('Microphone permission denied');
        return;
      }

      // Check if already recording
      if (await _audioRecorder.isRecording()) {
        debugPrint('Already recording');
        return;
      }

      final Directory tempDir = await getTemporaryDirectory();
      final String filePath = '${tempDir.path}/recording_${DateTime.now().millisecondsSinceEpoch}.wav';
      
      await _audioRecorder.start(
        path: filePath,
        encoder: AudioEncoder.wav, // Use WAV instead of AAC for better compatibility
        bitRate: 16000,
        
      );
      
      _isRecording = true;
      notifyListeners();
      debugPrint('Recording started: $filePath');
    } catch (e) {
      debugPrint('Error starting recording: $e');
      _isRecording = false;
      notifyListeners();
    }
  }

  Future<void> stopRecording() async {
    try {
      if (!_isRecording) {
        debugPrint('Not currently recording');
        return;
      }

      if (await _audioRecorder.isRecording()) {
        final String? filePath = await _audioRecorder.stop();
        debugPrint('Recording stopped: $filePath');
        
        _isRecording = false;
        notifyListeners();
        
        if (filePath != null && File(filePath).existsSync()) {
          await _transcribeAudio(filePath);
        } else {
          debugPrint('Recording file not found');
        }
      }
    } catch (e) {
      debugPrint('Error stopping recording: $e');
      _isRecording = false;
      notifyListeners();
    }
  }

  Future<void> _transcribeAudio(String filePath) async {
    try {
      final File audioFile = File(filePath);
      final request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseUrl/transcribe'),
      );
      
      // Add authorization header with dummy token
      request.headers['Authorization'] = 'Bearer $dummyToken';
      
      request.files.add(
        await http.MultipartFile.fromPath('file', audioFile.path),
      );
      request.fields['language'] = 'tamil';
      
      final response = await request.send();
      final responseBody = await response.stream.bytesToString();
      
      debugPrint('Transcription response: $responseBody');
      
      if (response.statusCode == 200) {
        final Map<String, dynamic> data = json.decode(responseBody);
        debugPrint('Parsed data: $data');
        
        if (data['status'] == 'success') {
          _transcriptionResult = data['transcript'] ?? 'No transcription';
          debugPrint('Setting transcription result: $_transcriptionResult');
        } else {
          _transcriptionResult = 'Transcription failed';
          debugPrint('Transcription failed: ${data['transcript']}');
        }
      } else {
        _transcriptionResult = 'Error: ${response.statusCode}';
      }
      
      notifyListeners();
    } catch (e) {
      debugPrint('Error transcribing audio: $e');
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
      audioOffset: json['privAudioOffset'] ?? 0,
      visemeId: json['privVisemeId'] ?? 0,
    );
  }
}