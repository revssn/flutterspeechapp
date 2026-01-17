import 'package:flutter/material.dart';
import '../data/learning_data.dart';
import 'speech_training_screen.dart';

class LessonsScreen extends StatefulWidget {
  final LearningModule module;

  const LessonsScreen({Key? key, required this.module}) : super(key: key);

  @override
  State<LessonsScreen> createState() => _LessonsScreenState();
}

class _LessonsScreenState extends State<LessonsScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFFFF8F0),
      appBar: AppBar(
        backgroundColor: const Color(0xFFFF6600),
        elevation: 0,
        title: Column(
          children: [
            Text(
              widget.module.title,
              style: const TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
            Text(
              widget.module.titleTamil,
              style: const TextStyle(
                fontSize: 14,
                color: Colors.white70,
                fontFamily: 'Tamil',
              ),
            ),
          ],
        ),
        centerTitle: true,
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: widget.module.lessons.length,
        itemBuilder: (context, index) {
          final lesson = widget.module.lessons[index];
          return _buildLessonCard(lesson, index);
        },
      ),
    );
  }

  Widget _buildLessonCard(Lesson lesson, int index) {
    IconData lessonIcon;
    Color iconColor;

    switch (lesson.type) {
      case LessonType.words:
        lessonIcon = Icons.abc;
        iconColor = Colors.blue;
        break;
      case LessonType.phrases:
        lessonIcon = Icons.chat_bubble_outline;
        iconColor = Colors.green;
        break;
      case LessonType.sentences:
        lessonIcon = Icons.text_fields;
        iconColor = Colors.orange;
        break;
      case LessonType.paragraphs:
        lessonIcon = Icons.article;
        iconColor = Colors.purple;
        break;
      case LessonType.conversation:
        lessonIcon = Icons.forum;
        iconColor = Colors.red;
        break;
    }

    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => SpeechTrainingScreen(lesson: lesson),
          ),
        );
      },
      child: Container(
        margin: const EdgeInsets.only(bottom: 16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(15),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 8,
              offset: const Offset(0, 3),
            ),
          ],
        ),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              // Icon
              Container(
                width: 50,
                height: 50,
                decoration: BoxDecoration(
                  color: iconColor.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Center(
                  child: Icon(
                    lessonIcon,
                    color: iconColor,
                    size: 28,
                  ),
                ),
              ),
              
              const SizedBox(width: 16),
              
              // Lesson Info
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Lesson ${index + 1}',
                      style: const TextStyle(
                        fontSize: 12,
                        color: Colors.grey,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      lesson.title,
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Colors.black87,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      lesson.titleTamil,
                      style: const TextStyle(
                        fontSize: 14,
                        color: Color(0xFFFF6600),
                        fontFamily: 'Tamil',
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      lesson.description,
                      style: const TextStyle(
                        fontSize: 13,
                        color: Colors.black54,
                      ),
                    ),
                    const SizedBox(height: 8),
                    // Content count
                    Row(
                      children: [
                        Icon(
                          Icons.library_books,
                          size: 16,
                          color: Colors.grey.shade600,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          '${lesson.content.length} items',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey.shade600,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              
              // Arrow
              const Icon(
                Icons.arrow_forward_ios,
                color: Color(0xFFFF6600),
                size: 20,
              ),
            ],
          ),
        ),
      ),
    );
  }
}