import 'package:flutter/material.dart';
import '../../../core/auth/auth_models.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({required this.session, super.key});
  final AuthSession session;
  @override
  Widget build(BuildContext context) {
    final user = session.user;
    return Scaffold(
      appBar: AppBar(title: const Text('Profile')),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            CircleAvatar(
              radius: 34,
              child: Text(
                (user.fullName.isEmpty ? user.username : user.fullName)
                    .characters
                    .first
                    .toUpperCase(),
              ),
            ),
            const SizedBox(height: 16),
            ListTile(
              title: Text(
                user.fullName.isEmpty ? user.username : user.fullName,
              ),
              subtitle: Text(user.username),
              leading: const Icon(Icons.person_outline),
            ),
            if (user.email.isNotEmpty)
              ListTile(
                title: Text(user.email),
                leading: const Icon(Icons.email_outlined),
              ),
            ListTile(
              title: const Text('Roles'),
              subtitle: Text(user.roles.map(_label).join(', ')),
              leading: const Icon(Icons.badge_outlined),
            ),
            const Divider(),
            Text(
              'Assigned locations',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            if (user.locationAssignments.isEmpty)
              const ListTile(title: Text('No active location assignment')),
            for (final item in user.locationAssignments)
              ListTile(
                leading: const Icon(Icons.location_on_outlined),
                title: Text(
                  (item['name_en'] ?? 'Assigned location').toString(),
                ),
                subtitle: Text(_label((item['level'] ?? '').toString())),
              ),
            const Padding(
              padding: EdgeInsets.only(top: 12),
              child: Text(
                'Profile and location access are managed by TNK Insight Administration.',
              ),
            ),
          ],
        ),
      ),
    );
  }

  static String _label(String value) => value
      .split('_')
      .map(
        (part) =>
            part.isEmpty ? '' : '${part[0].toUpperCase()}${part.substring(1)}',
      )
      .join(' ');
}
