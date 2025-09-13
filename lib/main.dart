import 'package:flutter/material.dart';
//import 'package:firebase_core/firebase_core.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import 'providers/auth_provider.dart';
import 'providers/speech_provider.dart';
import 'screens/splash_screen.dart';
import 'screens/login_screen.dart';
import 'screens/signup_screen.dart';
import 'screens/home_screen.dart';
import 'screens/words_screen.dart';
import 'screens/syllables_screen.dart';
import 'screens/speech_training_screen.dart';
import 'screens/avatar_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  //await Firebase.initializeApp();
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  MyApp({Key? key}) : super(key: key);

  final GoRouter _router = GoRouter(
    initialLocation: '/splash',
    routes: [
      GoRoute(
        path: '/splash',
        builder: (context, state) => const SplashScreen(),
      ),
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/signup',
        builder: (context, state) => const SignUpScreen(),
      ),
      GoRoute(
        path: '/home',
        builder: (context, state) => const HomeScreen(),
      ),
      GoRoute(
        path: '/words',
        builder: (context, state) => const WordsScreen(),
      ),
      GoRoute(
        path: '/syllables',
        builder: (context, state) => const SyllablesScreen(),
      ),
      GoRoute(
        path: '/speech/:word',
        builder: (context, state) {
          final word = state.pathParameters['word'] ?? '';
          return SpeechTrainingScreen(word: word);
        },
      ),
      GoRoute(
        path: '/avatar',
        builder: (context, state) => const AvatarScreen(),
      ),
    ],
  );

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => SpeechProvider()),
      ],
      child: MaterialApp.router(
        title: 'Tamil Speech Learning',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          primarySwatch: Colors.orange,
          fontFamily: 'Tamil',
          appBarTheme: const AppBarTheme(
            backgroundColor: Colors.white,
            foregroundColor: Colors.orange,
            elevation: 0,
          ),
        ),
        routerConfig: _router,
      ),
    );
  }
}