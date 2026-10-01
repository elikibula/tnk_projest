import 'package:flutter/material.dart';

const dataTypeColors = <String, Color>{
  'master': Color(0xFFF04040),
  'operational': Color(0xFF6D9F71),
  'snapshot': Color(0xFF716DE2),
  'workflow': Color(0xFFAB9533),
};

String dataTypeLabel(String value) => switch (value) {
  'master' => 'Master / Base data',
  'operational' => 'Operational / Event data',
  'snapshot' => 'Snapshot data',
  _ => 'Evidence / Workflow / Derived data',
};

class DataTypeLabel extends StatelessWidget {
  const DataTypeLabel(this.dataType, {super.key});
  final String dataType;

  @override
  Widget build(BuildContext context) {
    final color = dataTypeColors[dataType] ?? dataTypeColors['workflow']!;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 5),
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(99),
      ),
      child: Text(
        dataTypeLabel(dataType),
        style: const TextStyle(
          color: Colors.white,
          fontSize: 11,
          fontWeight: FontWeight.w800,
        ),
      ),
    );
  }
}

class DataTypeCard extends StatelessWidget {
  const DataTypeCard({required this.dataType, required this.child, super.key});
  final String dataType;
  final Widget child;

  @override
  Widget build(BuildContext context) => Card(
    clipBehavior: Clip.antiAlias,
    child: Row(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Container(
          width: 5,
          color: dataTypeColors[dataType] ?? dataTypeColors['workflow'],
        ),
        Expanded(child: child),
      ],
    ),
  );
}
