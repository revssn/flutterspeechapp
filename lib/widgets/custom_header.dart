import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class CustomHeader extends StatelessWidget implements PreferredSizeWidget {
  final String title;

  const CustomHeader({Key? key, required this.title}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return AppBar(
      backgroundColor: Colors.white,
      elevation: 0,
      leading: IconButton(
  onPressed: () {
    if (Navigator.canPop(context)) {
      Navigator.pop(context);
    } else {
      context.go('/home');
    }
  },
  icon: const Icon(
    Icons.arrow_back_ios,
    color: Colors.black,
    size: 24,
  ),
      ),
      title: Text(
        title,
        style: const TextStyle(
          fontSize: 24,
          fontWeight: FontWeight.bold,
          color: Colors.orange,
        ),
      ),
      centerTitle: true,
      actions: [
        // Empty container for spacing balance
        Container(width: 50),
      ],
  );
}

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);
}