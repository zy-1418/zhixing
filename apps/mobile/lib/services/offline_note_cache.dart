class OfflineNoteDraft {
  const OfflineNoteDraft({
    required this.title,
    required this.blocks,
    required this.savedAt,
  });

  final String title;
  final List<Map<String, dynamic>> blocks;
  final DateTime savedAt;
}

class OfflineNoteCache {
  OfflineNoteCache._();

  static final OfflineNoteCache instance = OfflineNoteCache._();
  static const maxNotes = 23;

  final List<OfflineNoteDraft> _drafts = [];

  List<OfflineNoteDraft> get drafts => List.unmodifiable(_drafts);

  void put({required String title, required List<Map<String, dynamic>> blocks}) {
    _drafts.insert(
      0,
      OfflineNoteDraft(
        title: title,
        blocks: blocks,
        savedAt: DateTime.now(),
      ),
    );
    if (_drafts.length > maxNotes) {
      _drafts.removeRange(maxNotes, _drafts.length);
    }
  }
}
