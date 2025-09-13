import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/speech_provider.dart';
import '../widgets/custom_header.dart';

class AvatarScreen extends StatefulWidget {
  const AvatarScreen({super.key});

  @override
  State<AvatarScreen> createState() => _AvatarScreenState();
}

class _AvatarScreenState extends State<AvatarScreen> {
  final List<String> sentences = [
    'அம்மா',
    'அப்பா',
    'பால்',
    'வீடு',
    'புத்தகம்',
    'குழந்தை',
    'பூ',
  ];

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final speechProvider = Provider.of<SpeechProvider>(context, listen: false);
      // Set random sentence
      final randomSentence = sentences[DateTime.now().millisecond % sentences.length];
      speechProvider.setCurrentWord(randomSentence);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const CustomHeader(title: 'Training'),
      body: Consumer<SpeechProvider>(
        builder: (context, speechProvider, child) {
          return SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(10.0),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // Avatar Image Container
                  Expanded(
                    flex: 1,
                    child: Stack(
                      alignment: Alignment.center,
                      children: [
                        // Background image
                        Container(
                          width: 350,
                          height: 350,
                          decoration: const BoxDecoration(
                            image: DecorationImage(
                              image: AssetImage('assets/images/1.png'),
                              fit: BoxFit.cover,
                            ),
                          ),
                        ),
                        
                        // Viseme overlay
                        Positioned(
                          top: 95, // Adjust position to align with mouth
                          child: Container(
                            width: 100,
                            height: 75,
                            decoration: BoxDecoration(
                              image: DecorationImage(
                                image: AssetImage(
                                  'assets/visemes/viseme_id_${speechProvider.currentVisemeId}.png',
                                ),
                                fit: BoxFit.contain,
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  
                  // Current word display
                  Padding(
                    padding: const EdgeInsets.symmetric(vertical: 10),
                    child: Text(
                      speechProvider.currentWord,
                      style: const TextStyle(
                        fontSize: 32,
                        color: Colors.black,
                        fontFamily: 'Tamil',
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ),
                  
                  // ASR result display
                  if (speechProvider.transcriptionResult.isNotEmpty)
                    Padding(
                      padding: const EdgeInsets.symmetric(vertical: 10),
                      child: RichText(
                        textAlign: TextAlign.center,
                        text: TextSpan(
                          children: speechProvider.getComparisonText(),
                        ),
                      ),
                    ),
                  
                  // Speak button
                  Container(
                    margin: const EdgeInsets.symmetric(vertical: 10),
                    child: ElevatedButton.icon(
                      onPressed: () => speechProvider.speakText(speechProvider.currentWord),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.orange,
                        padding: const EdgeInsets.symmetric(
                          horizontal: 20,
                          vertical: 10,
                        ),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(25),
                          side: const BorderSide(color: Color(0xFFFFD8B1), width: 2),
                        ),
                      ),
                      icon: const Icon(Icons.volume_up, color: Colors.white),
                      label: const Text(
                        'Speak',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 16,
                        ),
                      ),
                    ),
                  ),
                  
                  // Recording buttons
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      // Start Recording
                      ElevatedButton.icon(
                        onPressed: speechProvider.isRecording 
                            ? null 
                            : () => speechProvider.startRecording(),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.orange,
                          padding: const EdgeInsets.symmetric(
                            horizontal: 15,
                            vertical: 10,
                          ),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(25),
                            side: const BorderSide(color: Color(0xFFFFD8B1), width: 2),
                          ),
                        ),
                        icon: const Icon(Icons.mic, color: Colors.white),
                        label: const Text(
                          'Start Recording',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 14,
                          ),
                        ),
                      ),
                      
                      // Stop Recording
                      ElevatedButton.icon(
                        onPressed: !speechProvider.isRecording 
                            ? null 
                            : () => speechProvider.stopRecording(),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.orange,
                          padding: const EdgeInsets.symmetric(
                            horizontal: 15,
                            vertical: 10,
                          ),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(25),
                            side: const BorderSide(color: Color(0xFFFFD8B1), width: 2),
                          ),
                        ),
                        icon: const Icon(Icons.stop, color: Colors.white),
                        label: const Text(
                          'Stop Recording',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 14,
                          ),
                        ),
                      ),
                    ],
                  ),
                  
                  const SizedBox(height: 20),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}