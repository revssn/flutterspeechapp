import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../data/learning_data.dart';
import '../providers/speech_provider.dart';

class SpeechTrainingScreen extends StatefulWidget {
  final Lesson lesson;

  const SpeechTrainingScreen({super.key, required this.lesson});

  @override
  State<SpeechTrainingScreen> createState() => _SpeechTrainingScreenState();
}

class _SpeechTrainingScreenState extends State<SpeechTrainingScreen> {
  int currentIndex = 0;
  bool showTransliteration = false;
  bool showEnglish = true;

  @override
  void initState() {
    super.initState();
    if (widget.lesson.content.isNotEmpty) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        final provider = Provider.of<SpeechProvider>(context, listen: false);
        provider.setCurrentWord(widget.lesson.content[currentIndex].tamil);
      });
    }
  }

  void _nextContent() {
    if (currentIndex < widget.lesson.content.length - 1) {
      setState(() {
        currentIndex++;
        showTransliteration = false;
      });
      final provider = Provider.of<SpeechProvider>(context, listen: false);
      provider.setCurrentWord(widget.lesson.content[currentIndex].tamil);
    } else {
      _showCompletionDialog();
    }
  }

  void _previousContent() {
    if (currentIndex > 0) {
      setState(() {
        currentIndex--;
        showTransliteration = false;
      });
      final provider = Provider.of<SpeechProvider>(context, listen: false);
      provider.setCurrentWord(widget.lesson.content[currentIndex].tamil);
    }
  }

  void _showCompletionDialog() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Row(
          children: [
            Icon(Icons.celebration, color: Color(0xFFFF6600), size: 32),
            SizedBox(width: 12),
            Text('Lesson Complete!'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'Great job! You\'ve completed this lesson.',
              style: TextStyle(fontSize: 16),
            ),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFFFBE4CB),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Text(
                '${widget.lesson.content.length} items practiced',
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              Navigator.of(context).pop();
            },
            child: const Text(
              'Back to Lessons',
              style: TextStyle(fontSize: 16),
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (widget.lesson.content.isEmpty) {
      return Scaffold(
        appBar: AppBar(
          backgroundColor: const Color(0xFFFF6600),
          title: const Text('Practice'),
        ),
        body: const Center(
          child: Text('No content available'),
        ),
      );
    }

    final currentContent = widget.lesson.content[currentIndex];
    final speechProvider = Provider.of<SpeechProvider>(context);

    return Scaffold(
      backgroundColor: const Color(0xFFFFF8F0),
      appBar: AppBar(
        backgroundColor: const Color(0xFFFF6600),
        elevation: 0,
        title: Column(
          children: [
            Text(
              widget.lesson.title,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
            Text(
              '${currentIndex + 1} of ${widget.lesson.content.length}',
              style: const TextStyle(
                fontSize: 12,
                color: Colors.white70,
              ),
            ),
          ],
        ),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            children: [
              // Progress bar
              Container(
                height: 8,
                decoration: BoxDecoration(
                  color: Colors.grey.shade200,
                  borderRadius: BorderRadius.circular(4),
                ),
                child: FractionallySizedBox(
                  alignment: Alignment.centerLeft,
                  widthFactor: (currentIndex + 1) / widget.lesson.content.length,
                  child: Container(
                    decoration: BoxDecoration(
                      color: const Color(0xFFFF6600),
                      borderRadius: BorderRadius.circular(4),
                    ),
                  ),
                ),
              ),

              const SizedBox(height: 20),

              // Content Type Badge
              _buildContentTypeBadge(currentContent.type),

              const SizedBox(height: 30),

              // Viseme Avatar with Your PNG Images
              Container(
                width: MediaQuery.of(context).size.width * 0.6,
                height: MediaQuery.of(context).size.width * 0.6,
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.1),
                      blurRadius: 20,
                      offset: const Offset(0, 10),
                    ),
                  ],
                ),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(20),
                  child: Stack(
                    children: [
                      // Viseme Image
                      Center(
                        child: Image.asset(
                          'assets/visemes/viseme_id_${speechProvider.currentVisemeId}.png',
                          key: ValueKey(speechProvider.currentVisemeId),
                          fit: BoxFit.cover,
                          width: double.infinity,
                          height: double.infinity,
                          errorBuilder: (context, error, stackTrace) {
                            // Fallback if image not found
                            return Container(
                              color: Colors.grey[200],
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Icon(
                                    Icons.face,
                                    size: 100,
                                    color: Colors.grey[400],
                                  ),
                                  const SizedBox(height: 10),
                                  Text(
                                    'Viseme ${speechProvider.currentVisemeId}',
                                    style: TextStyle(
                                      color: Colors.grey[600],
                                      fontSize: 16,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ],
                              ),
                            );
                          },
                        ),
                      ),

                      // Debug Overlay
                      Positioned(
                        top: 8,
                        right: 8,
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: Colors.black.withOpacity(0.7),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Text(
                            'V${speechProvider.currentVisemeId}',
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ),

                      // Playing Indicator
                      if (speechProvider.isPlaying)
                        Positioned(
                          bottom: 8,
                          left: 8,
                          child: Container(
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                            decoration: BoxDecoration(
                              color: Colors.green.withOpacity(0.8),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: const Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Icon(Icons.play_arrow, color: Colors.white, size: 14),
                                SizedBox(width: 4),
                                Text(
                                  'Playing',
                                  style: TextStyle(
                                    color: Colors.white,
                                    fontSize: 11,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 30),

              // Tamil Text Container
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(15),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.05),
                      blurRadius: 10,
                      offset: const Offset(0, 3),
                    ),
                  ],
                ),
                child: Column(
                  children: [
                    Row(
                      children: [
                        IconButton(
                          icon: const Icon(Icons.volume_up),
                          color: const Color(0xFFFF6600),
                          iconSize: 32,
                          onPressed: () {
                            debugPrint('🔊 Playing: ${currentContent.tamil}');
                            speechProvider.speakText(currentContent.tamil);
                          },
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            currentContent.tamil,
                            style: const TextStyle(
                              fontSize: 26,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFFFF6600),
                              fontFamily: 'Tamil',
                              height: 1.5,
                              letterSpacing: 0.5,
                            ),
                            textAlign: currentContent.type == ContentType.paragraph
                                ? TextAlign.left
                                : TextAlign.center,
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(height: 20),
                    const Divider(),
                    const SizedBox(height: 15),

                    // English toggle
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          'English',
                          style: TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                        Switch(
                          value: showEnglish,
                          onChanged: (value) {
                            setState(() {
                              showEnglish = value;
                            });
                          },
                          activeColor: const Color(0xFFFF6600),
                        ),
                      ],
                    ),

                    if (showEnglish) ...[
                      const SizedBox(height: 10),
                      Text(
                        currentContent.english,
                        style: const TextStyle(
                          fontSize: 18,
                          color: Colors.black87,
                          height: 1.5,
                        ),
                        textAlign: currentContent.type == ContentType.paragraph
                            ? TextAlign.left
                            : TextAlign.center,
                      ),
                    ],

                    const SizedBox(height: 15),

                    // Transliteration toggle
                    TextButton.icon(
                      onPressed: () {
                        setState(() {
                          showTransliteration = !showTransliteration;
                        });
                      },
                      icon: Icon(
                        showTransliteration ? Icons.visibility_off : Icons.visibility,
                        size: 18,
                      ),
                      label: Text(
                        showTransliteration ? 'Hide' : 'Show Pronunciation',
                        style: const TextStyle(fontSize: 14),
                      ),
                    ),

                    if (showTransliteration)
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: const Color(0xFFFBE4CB),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: Text(
                          currentContent.transliteration,
                          style: const TextStyle(
                            fontSize: 16,
                            fontStyle: FontStyle.italic,
                            color: Colors.black87,
                            height: 1.5,
                          ),
                          textAlign: currentContent.type == ContentType.paragraph
                              ? TextAlign.left
                              : TextAlign.center,
                        ),
                      ),
                  ],
                ),
              ),

              const SizedBox(height: 30),

              // Recording Section
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(15),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.05),
                      blurRadius: 10,
                      offset: const Offset(0, 3),
                    ),
                  ],
                ),
                child: Column(
                  children: [
                    const Text(
                      'Practice Speaking',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Colors.black87,
                      ),
                    ),

                    const SizedBox(height: 20),

                    // Record Button
                    GestureDetector(
                      onTapDown: (_) => speechProvider.startRecording(),
                      onTapUp: (_) => speechProvider.stopRecording(),
                      onTapCancel: () => speechProvider.stopRecording(),
                      child: Container(
                        width: 80,
                        height: 80,
                        decoration: BoxDecoration(
                          color: speechProvider.isRecording
                              ? Colors.red
                              : const Color(0xFFFF6600),
                          shape: BoxShape.circle,
                          boxShadow: [
                            BoxShadow(
                              color: (speechProvider.isRecording
                                      ? Colors.red
                                      : const Color(0xFFFF6600))
                                  .withOpacity(0.4),
                              blurRadius: 15,
                              spreadRadius: 5,
                            ),
                          ],
                        ),
                        child: Icon(
                          speechProvider.isRecording ? Icons.stop : Icons.mic,
                          color: Colors.white,
                          size: 40,
                        ),
                      ),
                    ),

                    const SizedBox(height: 15),

                    Text(
                      speechProvider.isRecording
                          ? 'Recording... Release to stop'
                          : 'Hold to Record',
                      style: const TextStyle(
                        fontSize: 14,
                        color: Colors.black54,
                      ),
                    ),

                    const SizedBox(height: 20),

                    // Comparison Result
                    if (speechProvider.transcriptionResult.isNotEmpty &&
                        !speechProvider.transcriptionResult.startsWith('_'))
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: const Color(0xFFFBE4CB),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Your pronunciation:',
                              style: TextStyle(
                                fontSize: 14,
                                color: Colors.black54,
                              ),
                            ),
                            const SizedBox(height: 8),
                            RichText(
                              text: TextSpan(
                                style: const TextStyle(
                                  fontSize: 18,
                                  fontFamily: 'Tamil',
                                  height: 1.5,
                                  color: Colors.black,
                                ),
                                children: speechProvider.getComparisonText(),
                              ),
                            ),
                          ],
                        ),
                      ),
                  ],
                ),
              ),

              const SizedBox(height: 30),

              // Navigation Buttons
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  if (currentIndex > 0)
                    ElevatedButton.icon(
                      onPressed: _previousContent,
                      icon: const Icon(Icons.arrow_back),
                      label: const Text('Previous'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.grey.shade300,
                        foregroundColor: Colors.black87,
                        padding: const EdgeInsets.symmetric(
                          horizontal: 20,
                          vertical: 12,
                        ),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(10),
                        ),
                      ),
                    )
                  else
                    const SizedBox(),

                  ElevatedButton.icon(
                    onPressed: _nextContent,
                    icon: Icon(
                      currentIndex < widget.lesson.content.length - 1
                          ? Icons.arrow_forward
                          : Icons.check_circle,
                    ),
                    label: Text(
                      currentIndex < widget.lesson.content.length - 1
                          ? 'Next'
                          : 'Complete',
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFFFF6600),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(
                        horizontal: 20,
                        vertical: 12,
                      ),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  // FIXED: Added all ContentType cases with default
  Widget _buildContentTypeBadge(ContentType type) {
    String label;
    Color color;
    IconData icon;

    switch (type) {
      case ContentType.word:
        label = 'WORD';
        color = Colors.blue;
        icon = Icons.abc;
        break;
      case ContentType.sentence:
        label = 'SENTENCE';
        color = Colors.orange;
        icon = Icons.text_fields;
        break;
      case ContentType.paragraph:
        label = 'PARAGRAPH';
        color = Colors.purple;
        icon = Icons.article;
        break;
      default:
        label = 'CONTENT';
        color = Colors.grey;
        icon = Icons.description;
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: color.withOpacity(0.2),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color, width: 2),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(width: 8),
          Text(
            label,
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}