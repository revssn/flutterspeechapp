class LearningModule {
  final String id;
  final String title;
  final String titleTamil;
  final String description;
  final String emoji;
  final List<Lesson> lessons;
  final bool isLocked;
  
  LearningModule({
    required this.id,
    required this.title,
    required this.titleTamil,
    required this.description,
    required this.emoji,
    required this.lessons,
    this.isLocked = false,
  });
  
  int get totalLessons => lessons.length;
  int get completedLessons => lessons.where((l) => l.isCompleted).length;
  double get progress => totalLessons > 0 ? completedLessons / totalLessons : 0.0;
}

class Lesson {
  final String id;
  final String title;
  final String titleTamil;
  final String description;
  final LessonType type;
  final List<ContentItem> content;
  bool isCompleted;
  int stars;
  
  Lesson({
    required this.id,
    required this.title,
    required this.titleTamil,
    required this.description,
    required this.type,
    required this.content,
    this.isCompleted = false,
    this.stars = 0,
  });
}

enum LessonType {
  words,
  phrases,
  sentences,
  paragraphs,
  conversation,
}

class ContentItem {
  final String id;
  final String tamil;
  final String english;
  final String transliteration;
  final ContentType type;
  final String? hint;
  
  ContentItem({
    required this.id,
    required this.tamil,
    required this.english,
    required this.transliteration,
    required this.type,
    this.hint,
  });
}

enum ContentType {
  word,
  phrase,
  sentence,
  paragraph,
}

// ============= ALL YOUR CONTENT IN ONE PLACE =============

class LearningData {
  static List<LearningModule> getAllModules() {
    return [
      // MODULE 1: GREETINGS
      LearningModule(
        id: 'greetings',
        title: 'Greetings & Basics',
        titleTamil: 'வாழ்த்துக்கள்',
        description: 'Learn to greet people and introduce yourself',
        emoji: '👋',
        isLocked: false,
        lessons: [
          // Lesson 1: Words
          Lesson(
            id: 'greetings_words',
            title: 'Greeting Words',
            titleTamil: 'வாழ்த்து வார்த்தைகள்',
            description: 'Basic greeting vocabulary',
            type: LessonType.words,
            content: [
              ContentItem(
                id: 'gw1',
                tamil: 'வணக்கம்',
                english: 'Hello',
                transliteration: 'vanakkam',
                type: ContentType.word,
              ),
              ContentItem(
                id: 'gw2',
                tamil: 'நன்றி',
                english: 'Thank you',
                transliteration: 'nandri',
                type: ContentType.word,
              ),
              ContentItem(
                id: 'gw3',
                tamil: 'மன்னிக்கவும்',
                english: 'Sorry',
                transliteration: 'mannikkavum',
                type: ContentType.word,
              ),
              ContentItem(
                id: 'gw4',
                tamil: 'இல்லை',
                english: 'No',
                transliteration: 'illai',
                type: ContentType.word,
              ),
              ContentItem(
                id: 'gw5',
                tamil: 'ஆம்',
                english: 'Yes',
                transliteration: 'aam',
                type: ContentType.word,
              ),
            ],
          ),
          
          // Lesson 2: Phrases
          Lesson(
            id: 'greetings_phrases',
            title: 'Greeting Phrases',
            titleTamil: 'வாழ்த்து சொற்றொடர்கள்',
            description: 'Common greeting phrases',
            type: LessonType.phrases,
            content: [
              ContentItem(
                id: 'gp1',
                tamil: 'நல்ல காலை',
                english: 'Good morning',
                transliteration: 'nalla kaalai',
                type: ContentType.phrase,
              ),
              ContentItem(
                id: 'gp2',
                tamil: 'இனிய இரவு',
                english: 'Good night',
                transliteration: 'iniya iravu',
                type: ContentType.phrase,
              ),
              ContentItem(
                id: 'gp3',
                tamil: 'பிறகு சந்திப்போம்',
                english: 'See you later',
                transliteration: 'piragu sandhippom',
                type: ContentType.phrase,
              ),
            ],
          ),
          
          // Lesson 3: Sentences
          Lesson(
            id: 'greetings_sentences',
            title: 'Full Sentences',
            titleTamil: 'முழு வாக்கியங்கள்',
            description: 'Complete greeting sentences',
            type: LessonType.sentences,
            content: [
              ContentItem(
                id: 'gs1',
                tamil: 'எப்படி இருக்கிறீர்கள்?',
                english: 'How are you?',
                transliteration: 'eppadi irukkireergal?',
                type: ContentType.sentence,
                hint: 'Formal way to ask',
              ),
              ContentItem(
                id: 'gs2',
                tamil: 'நான் நன்றாக இருக்கிறேன்.',
                english: 'I am fine.',
                transliteration: 'naan nandraga irukkirean',
                type: ContentType.sentence,
              ),
              ContentItem(
                id: 'gs3',
                tamil: 'உங்கள் பெயர் என்ன?',
                english: 'What is your name?',
                transliteration: 'ungal peyar enna?',
                type: ContentType.sentence,
              ),
              ContentItem(
                id: 'gs4',
                tamil: 'என் பெயர் ராஜ்.',
                english: 'My name is Raj.',
                transliteration: 'en peyar Raj',
                type: ContentType.sentence,
              ),
            ],
          ),
          
          // Lesson 4: Paragraphs
          Lesson(
            id: 'greetings_paragraphs',
            title: 'Introduction',
            titleTamil: 'அறிமுகம்',
            description: 'Introduce yourself',
            type: LessonType.paragraphs,
            content: [
              ContentItem(
                id: 'gpar1',
                tamil: 'வணக்கம். என் பெயர் ராஜ். நான் சென்னையில் வசிக்கிறேன். நான் ஒரு மாணவன். எனக்கு தமிழ் படிக்க பிடிக்கும்.',
                english: 'Hello. My name is Raj. I live in Chennai. I am a student. I like learning Tamil.',
                transliteration: 'vanakkam. en peyar Raj. naan chennaiyil vasikkirean. naan oru maanavan. enakku tamil padikka pidikkum.',
                type: ContentType.paragraph,
                hint: 'Self introduction',
              ),
            ],
          ),
        ],
      ),
      
      // MODULE 2: DAILY CONVERSATION
      LearningModule(
        id: 'daily',
        title: 'Daily Conversation',
        titleTamil: 'தினசரி உரையாடல்',
        description: 'Common phrases for everyday use',
        emoji: '💬',
        isLocked: true,
        lessons: [
          Lesson(
            id: 'daily_words',
            title: 'Daily Words',
            titleTamil: 'தினசரி வார்த்தைகள்',
            description: 'Everyday vocabulary',
            type: LessonType.words,
            content: [
              ContentItem(
                id: 'dw1',
                tamil: 'சாப்பிடு',
                english: 'Eat',
                transliteration: 'saappidu',
                type: ContentType.word,
              ),
              ContentItem(
                id: 'dw2',
                tamil: 'குடி',
                english: 'Drink',
                transliteration: 'kudi',
                type: ContentType.word,
              ),
              ContentItem(
                id: 'dw3',
                tamil: 'தூங்கு',
                english: 'Sleep',
                transliteration: 'thoongu',
                type: ContentType.word,
              ),
            ],
          ),
          Lesson(
            id: 'daily_sentences',
            title: 'Daily Sentences',
            titleTamil: 'தினசரி வாக்கியங்கள்',
            description: 'Everyday sentences',
            type: LessonType.sentences,
            content: [
              ContentItem(
                id: 'ds1',
                tamil: 'எனக்கு பசிக்கிறது.',
                english: 'I am hungry.',
                transliteration: 'enakku pasikkiraathu',
                type: ContentType.sentence,
              ),
              ContentItem(
                id: 'ds2',
                tamil: 'எனக்கு தாகம் எடுக்கிறது.',
                english: 'I am thirsty.',
                transliteration: 'enakku thaagam edukkiraathu',
                type: ContentType.sentence,
              ),
            ],
          ),
        ],
      ),
      
      // MODULE 3: FAMILY
      LearningModule(
        id: 'family',
        title: 'Family & Friends',
        titleTamil: 'குடும்பம்',
        description: 'Talk about your family',
        emoji: '👨‍👩‍👧‍👦',
        isLocked: true,
        lessons: [
          Lesson(
            id: 'family_words',
            title: 'Family Members',
            titleTamil: 'குடும்ப உறுப்பினர்கள்',
            description: 'Family vocabulary',
            type: LessonType.words,
            content: [
              ContentItem(
                id: 'fw1',
                tamil: 'அம்மா',
                english: 'Mother',
                transliteration: 'amma',
                type: ContentType.word,
              ),
              ContentItem(
                id: 'fw2',
                tamil: 'அப்பா',
                english: 'Father',
                transliteration: 'appa',
                type: ContentType.word,
              ),
              ContentItem(
                id: 'fw3',
                tamil: 'அண்ணா',
                english: 'Elder brother',
                transliteration: 'anna',
                type: ContentType.word,
              ),
              ContentItem(
                id: 'fw4',
                tamil: 'அக்கா',
                english: 'Elder sister',
                transliteration: 'akka',
                type: ContentType.word,
              ),
            ],
          ),
          Lesson(
            id: 'family_sentences',
            title: 'Family Sentences',
            titleTamil: 'குடும்ப வாக்கியங்கள்',
            description: 'Talk about family',
            type: LessonType.sentences,
            content: [
              ContentItem(
                id: 'fs1',
                tamil: 'என் அம்மா ஒரு ஆசிரியர்.',
                english: 'My mother is a teacher.',
                transliteration: 'en amma oru aasiriyar',
                type: ContentType.sentence,
              ),
              ContentItem(
                id: 'fs2',
                tamil: 'எங்கள் குடும்பத்தில் நான்கு பேர் உள்ளனர்.',
                english: 'There are four people in our family.',
                transliteration: 'engal kudumbaththil naanku per ullaanar',
                type: ContentType.sentence,
              ),
            ],
          ),
        ],
      ),
      
      // MODULE 4: SEASONS & WEATHER
      LearningModule(
        id: 'seasons',
        title: 'Seasons & Weather',
        titleTamil: 'பருவங்கள்',
        description: 'Talk about weather and seasons',
        emoji: '🌦️',
        isLocked: true,
        lessons: [
          Lesson(
            id: 'seasons_words',
            title: 'Season Names',
            titleTamil: 'பருவகால பெயர்கள்',
            description: 'Learn seasons',
            type: LessonType.words,
            content: [
              ContentItem(
                id: 'sw1',
                tamil: 'கோடை',
                english: 'Summer',
                transliteration: 'kodai',
                type: ContentType.word,
              ),
              ContentItem(
                id: 'sw2',
                tamil: 'குளிர்',
                english: 'Winter',
                transliteration: 'kulir',
                type: ContentType.word,
              ),
              ContentItem(
                id: 'sw3',
                tamil: 'மழை',
                english: 'Rain',
                transliteration: 'mazhai',
                type: ContentType.word,
              ),
            ],
          ),
          Lesson(
            id: 'seasons_sentences',
            title: 'Weather Sentences',
            titleTamil: 'வானிலை வாக்கியங்கள்',
            description: 'Describe weather',
            type: LessonType.sentences,
            content: [
              ContentItem(
                id: 'ss1',
                tamil: 'இன்று வெயில் அதிகமாக உள்ளது.',
                english: 'Today it is very sunny.',
                transliteration: 'indru veyil adhigamaaga ulladhu',
                type: ContentType.sentence,
              ),
              ContentItem(
                id: 'ss2',
                tamil: 'நாளை மழை பெய்யும்.',
                english: 'It will rain tomorrow.',
                transliteration: 'naalai mazhai peyyum',
                type: ContentType.sentence,
              ),
            ],
          ),
        ],
      ),
      
      // MODULE 5: FOOD
      LearningModule(
        id: 'food',
        title: 'Food & Dining',
        titleTamil: 'உணவு',
        description: 'Talk about food',
        emoji: '🍽️',
        isLocked: true,
        lessons: [
          Lesson(
            id: 'food_words',
            title: 'Food Items',
            titleTamil: 'உணவு பொருட்கள்',
            description: 'Common foods',
            type: LessonType.words,
            content: [
              ContentItem(
                id: 'fow1',
                tamil: 'சோறு',
                english: 'Rice',
                transliteration: 'soru',
                type: ContentType.word,
              ),
              ContentItem(
                id: 'fow2',
                tamil: 'தண்ணீர்',
                english: 'Water',
                transliteration: 'thanneer',
                type: ContentType.word,
              ),
              ContentItem(
                id: 'fow3',
                tamil: 'இட்லி',
                english: 'Idli',
                transliteration: 'idli',
                type: ContentType.word,
              ),
            ],
          ),
          Lesson(
            id: 'food_sentences',
            title: 'Food Sentences',
            titleTamil: 'உணவு வாக்கியங்கள்',
            description: 'Order and discuss food',
            type: LessonType.sentences,
            content: [
              ContentItem(
                id: 'fos1',
                tamil: 'எனக்கு இட்லி வேண்டும்.',
                english: 'I want idli.',
                transliteration: 'enakku idli vendum',
                type: ContentType.sentence,
              ),
              ContentItem(
                id: 'fos2',
                tamil: 'இது மிகவும் சுவையாக உள்ளது.',
                english: 'This is very tasty.',
                transliteration: 'idhu migavum suvaiyaaga ulladhu',
                type: ContentType.sentence,
              ),
            ],
          ),
        ],
      ),
    ];
  }
}