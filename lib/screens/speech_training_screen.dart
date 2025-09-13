import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/speech_provider.dart';
import '../widgets/custom_header.dart';

class SpeechTrainingScreen extends StatefulWidget {
  final String word;

  const SpeechTrainingScreen({Key? key, required this.word}) : super(key: key);

  @override
  State<SpeechTrainingScreen> createState() => _SpeechTrainingScreenState();
}

class _SpeechTrainingScreenState extends State<SpeechTrainingScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<SpeechProvider>(context, listen: false)
          .setCurrentWord(widget.word);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const CustomHeader(title: 'Training'),
      body: Consumer<SpeechProvider>(
        builder: (context, speechProvider, child) {
          return Padding(
            padding: const EdgeInsets.all(20.0),
            child: Column(
              children: [
                // Avatar Section
                Expanded(
                  flex: 3,
                  child: Row(
                    children: [
                      // Viseme Image
                      Expanded(
                        child: Container(
                          width: 150,
                          height: 150,
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
                      
                      const SizedBox(width: 20),
                      
                      // Speech Bubble
                      Expanded(
                        child: GestureDetector(
                          onTap: () => speechProvider.speakText(widget.word),
                          child: Container(
                            padding: const EdgeInsets.all(10),
                            decoration: BoxDecoration(
                              color: const Color(0xFFF0F0F0),
                              borderRadius: BorderRadius.circular(20),
                            ),
                            child: Row(
                              children: [
                                const Icon(
                                  Icons.volume_up,
                                  color: Color(0xFFFF6600),
                                  size: 20,
                                ),
                                const SizedBox(width: 5),
                                Expanded(
                                  child: Text(
                                    widget.word,
                                    style: const TextStyle(
                                      fontSize: 16,
                                      fontFamily: 'Tamil',
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                
                // Letter Comparison Section
                Container(
                  height: 60,
                  child: SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: Row(
                      children: speechProvider.getComparisonText().map((span) {
                        return Container(
                          width: MediaQuery.of(context).size.width / 8,
                          height: MediaQuery.of(context).size.width / 8,
                          margin: const EdgeInsets.symmetric(horizontal: 2),
                          decoration: BoxDecoration(
                            border: Border.all(
                              color: const Color(0xFFA3A3A3).withOpacity(0.3),
                              width: 2,
                            ),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Center(
                            child: Text(
                              span.text!,
                              style: span.style,
                            ),
                          ),
                        );
                      }).toList(),
                    ),
                  ),
                ),
                
                const SizedBox(height: 20),
                
                // Recording Status
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: const Color(0xFFFBE4CB),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        speechProvider.isRecording 
                            ? Icons.fiber_manual_record
                            : Icons.radio_button_unchecked,
                        color: const Color(0xFFFF6600),
                        size: 20,
                      ),
                      const SizedBox(width: 5),
                      Text(
                        speechProvider.isRecording ? "Recording..." : "Ready to record",
                        style: const TextStyle(fontSize: 14),
                      ),
                    ],
                  ),
                ),
                
                const Spacer(),
                
                // Microphone Button
                GestureDetector(
                  onTap: () async {
                    if (speechProvider.isRecording) {
                      await speechProvider.stopRecording();
                    } else {
                      await speechProvider.startRecording();
                    }
                  },
                  child: Container(
                    width: 150,
                    height: 150,
                    decoration: BoxDecoration(
                      color: const Color(0xFFFF6600),
                      borderRadius: BorderRadius.circular(40),
                      boxShadow: [
                        BoxShadow(
                          color: const Color(0xFFFF6600).withOpacity(0.3),
                          blurRadius: 10,
                          spreadRadius: 5,
                        ),
                      ],
                    ),
                    child: Icon(
                      speechProvider.isRecording 
                          ? Icons.mic 
                          : Icons.mic_none_outlined,
                      color: Colors.white,
                      size: 40,
                    ),
                  ),
                ),
                
                const SizedBox(height: 20),
              ],
            ),
          );
        },
      ),
    );
  }
}