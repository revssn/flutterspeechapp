import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../widgets/custom_header.dart';
import '../data/words_data.dart';

class SyllablesScreen extends StatefulWidget {
  const SyllablesScreen({super.key});

  @override
  State<SyllablesScreen> createState() => _SyllablesScreenState();
}

class _SyllablesScreenState extends State<SyllablesScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  int _selectedTabIndex = 0;

  final List<String> _tabTitles = ['Start', 'Middle', 'End'];
  final List<List<String>> _tabData = [
    SyllablesData.sylStart,
    SyllablesData.sylMiddle,
    SyllablesData.sylEnd,
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: _tabTitles.length, vsync: this);
    _tabController.addListener(() {
      setState(() {
        _selectedTabIndex = _tabController.index;
      });
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  void _handleSyllablePress(String syllable) {
    context.go('/speech/${Uri.encodeComponent(syllable)}');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const CustomHeader(title: 'Syllables'),
      body: Container(
        color: Colors.white,
        child: Column(
          children: [
            // Custom Tab Bar
            Container(
              decoration: const BoxDecoration(
                border: Border(
                  bottom: BorderSide(color: Colors.orange, width: 2),
                ),
              ),
              child: Row(
                children: _tabTitles.asMap().entries.map((entry) {
                  final index = entry.key;
                  final title = entry.value;
                  final isSelected = _selectedTabIndex == index;
                  
                  return Expanded(
                    child: GestureDetector(
                      onTap: () {
                        _tabController.animateTo(index);
                      },
                      child: Container(
                        padding: const EdgeInsets.symmetric(vertical: 15),
                        decoration: BoxDecoration(
                          border: isSelected
                              ? const Border(
                                  bottom: BorderSide(color: Colors.orange, width: 3),
                                )
                              : null,
                        ),
                        child: Text(
                          title,
                          textAlign: TextAlign.center,
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: Colors.black,
                          ),
                        ),
                      ),
                    ),
                  );
                }).toList(),
              ),
            ),
            
            // Tab Content
            Expanded(
              child: TabBarView(
                controller: _tabController,
                children: _tabData.map((syllables) {
                  return ListView.builder(
                    padding: const EdgeInsets.all(20),
                    itemCount: syllables.length,
                    itemBuilder: (context, index) {
                      final syllable = syllables[index];
                      return Container(
                        margin: const EdgeInsets.only(bottom: 10),
                        child: ElevatedButton(
                          onPressed: () => _handleSyllablePress(syllable),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFFf36f21),
                            padding: const EdgeInsets.symmetric(
                              vertical: 15,
                              horizontal: 25,
                            ),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(10),
                            ),
                          ),
                          child: Text(
                            syllable,
                            style: const TextStyle(
                              fontSize: 18,
                              color: Colors.white,
                              fontFamily: 'Tamil',
                            ),
                            textAlign: TextAlign.center,
                          ),
                        ),
                      );
                    },
                  );
                }).toList(),
              ),
            ),
          ],
        ),
      ),
    );
  }
}