import 'package:flutter/material.dart';
import '../data/learning_data.dart';
import 'lessons_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  late List<LearningModule> modules;

  @override
  void initState() {
    super.initState();
    modules = LearningData.getAllModules();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFFFF8F0),
      appBar: AppBar(
        backgroundColor: const Color(0xFFFF6600),
        elevation: 0,
        title: const Text(
          'Tamil Learning Path',
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        centerTitle: true,
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: modules.length,
        itemBuilder: (context, index) {
          return _buildModuleCard(modules[index]);
        },
      ),
    );
  }

  Widget _buildModuleCard(LearningModule module) {
    return GestureDetector(
      onTap: module.isLocked
          ? () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Complete previous modules to unlock!'),
                  duration: Duration(seconds: 2),
                ),
              );
            }
          : () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => LessonsScreen(module: module),
                ),
              );
            },
      child: Container(
        margin: const EdgeInsets.only(bottom: 16),
        decoration: BoxDecoration(
          color: module.isLocked ? Colors.grey.shade300 : Colors.white,
          borderRadius: BorderRadius.circular(20),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  // Emoji Icon
                  Container(
                    width: 60,
                    height: 60,
                    decoration: BoxDecoration(
                      color: const Color(0xFFFBE4CB),
                      borderRadius: BorderRadius.circular(15),
                    ),
                    child: Center(
                      child: Text(
                        module.emoji,
                        style: const TextStyle(fontSize: 32),
                      ),
                    ),
                  ),
                  const SizedBox(width: 16),
                  
                  // Title
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          module.title,
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                            color: module.isLocked ? Colors.grey : Colors.black87,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          module.titleTamil,
                          style: TextStyle(
                            fontSize: 16,
                            color: module.isLocked ? Colors.grey : const Color(0xFFFF6600),
                            fontFamily: 'Tamil',
                          ),
                        ),
                      ],
                    ),
                  ),
                  
                  // Lock Icon
                  if (module.isLocked)
                    const Icon(
                      Icons.lock,
                      color: Colors.grey,
                      size: 28,
                    ),
                ],
              ),
              
              const SizedBox(height: 12),
              
              // Description
              Text(
                module.description,
                style: TextStyle(
                  fontSize: 14,
                  color: module.isLocked ? Colors.grey : Colors.black54,
                ),
              ),
              
              const SizedBox(height: 12),
              
              // Progress Bar
              Row(
                children: [
                  Expanded(
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(4),
                      child: LinearProgressIndicator(
                        value: module.progress,
                        backgroundColor: Colors.grey.shade200,
                        valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFFFF6600)),
                        minHeight: 8,
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Text(
                    '${module.completedLessons}/${module.totalLessons}',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: module.isLocked ? Colors.grey : const Color(0xFFFF6600),
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
}