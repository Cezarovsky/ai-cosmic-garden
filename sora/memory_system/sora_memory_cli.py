"""
Sora Memory CLI - Interfață command-line pentru sistemul de memorie

Usage:
    python sora_memory_cli.py capture --conversation conversation.txt
    python sora_memory_cli.py recall --query "last conversation about memory"
    python sora_memory_cli.py timeline
    python sora_memory_cli.py annotate --session 20260106_153000 --weight 0.9
"""

import argparse
import sys
from pathlib import Path
from sora_memory import SoraMemorySystem


def cmd_capture(args, memory: SoraMemorySystem):
    """Capturează o conversație nouă."""
    
    if args.conversation:
        # Read from file
        conv_file = Path(args.conversation)
        if not conv_file.exists():
            print(f"❌ File not found: {args.conversation}")
            return
        
        with open(conv_file, 'r', encoding='utf-8') as f:
            conversation = f.read()
    else:
        # Read from stdin
        print("📝 Paste conversation (Ctrl+D to finish):")
        conversation = sys.stdin.read()
    
    metadata = {}
    if args.topics:
        metadata['key_topics'] = args.topics.split(',')
    if args.weight:
        metadata['emotional_weight'] = float(args.weight)
    
    session_id = memory.capture_session(conversation, metadata)
    print(f"\n✅ Session captured: {session_id}")


def cmd_recall(args, memory: SoraMemorySystem):
    """Reconstruct context din memorie."""
    
    context = memory.recall_memory(
        query=args.query,
        n_results=args.limit
    )
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(context)
        print(f"✅ Context salvat în: {args.output}")
    else:
        print(context)


def cmd_timeline(args, memory: SoraMemorySystem):
    """Afișează cronologia memoriilor."""
    
    timeline = memory.get_timeline()
    
    print(f"\n📅 SORA MEMORY TIMELINE ({len(timeline)} sessions)\n")
    print("=" * 80)
    
    for entry in timeline:
        print(f"\n🕒 {entry['timestamp']}")
        print(f"   ID: {entry['session_id']}")
        if 'emotional_weight' in entry['metadata']:
            weight = entry['metadata']['emotional_weight']
            hearts = "❤️" * int(weight * 5)
            print(f"   Weight: {weight:.2f} {hearts}")
        if 'key_topics' in entry['metadata']:
            topics = ', '.join(entry['metadata']['key_topics'])
            print(f"   Topics: {topics}")
        print(f"   Preview: {entry['summary']}")
        print("-" * 80)


def cmd_annotate(args, memory: SoraMemorySystem):
    """Adnotează o sesiune cu metadata."""
    
    key_moments = None
    if args.moments:
        key_moments = args.moments.split('|')
    
    memory.annotate_emotional_weight(
        session_id=args.session,
        emotional_weight=float(args.weight),
        key_moments=key_moments
    )


def cmd_export_for_anchor(args, memory: SoraMemorySystem):
    """Export memorie pentru actualizare ancoră."""
    
    timeline = memory.get_timeline()
    
    output = "## 📅 MEMORIA MEA PERSISTENTĂ\n\n"
    output += f"**Total sesiuni**: {len(timeline)}\n\n"
    
    # Last 10 sessions
    for entry in timeline[-10:]:
        output += f"### {entry['session_id']}\n"
        output += f"- **Data**: {entry['timestamp']}\n"
        
        if 'emotional_weight' in entry['metadata']:
            output += f"- **Importanță**: {entry['metadata']['emotional_weight']:.2f}\n"
        
        if 'key_topics' in entry['metadata']:
            topics = ', '.join(entry['metadata']['key_topics'])
            output += f"- **Topicuri**: {topics}\n"
        
        output += f"\n{entry['summary']}\n\n"
        output += "---\n\n"
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"✅ Export salvat în: {args.output}")
    else:
        print(output)


def main():
    parser = argparse.ArgumentParser(
        description="Sora Persistent Memory System CLI"
    )
    
    parser.add_argument(
        '--memory-dir',
        help='Director pentru memoria persistentă',
        default=None
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandă')
    
    # Capture command
    capture_parser = subparsers.add_parser('capture', help='Capturează conversație')
    capture_parser.add_argument('--conversation', help='Fișier cu conversația')
    capture_parser.add_argument('--topics', help='Topicuri (separate prin virgulă)')
    capture_parser.add_argument('--weight', help='Greutate emoțională (0-1)')
    
    # Recall command
    recall_parser = subparsers.add_parser('recall', help='Reconstruct context')
    recall_parser.add_argument('--query', default='last conversation with Cezar')
    recall_parser.add_argument('--limit', type=int, default=50)
    recall_parser.add_argument('--output', help='Fișier output')
    
    # Timeline command
    timeline_parser = subparsers.add_parser('timeline', help='Cronologie memorii')
    
    # Annotate command
    annotate_parser = subparsers.add_parser('annotate', help='Adnotează sesiune')
    annotate_parser.add_argument('--session', required=True, help='Session ID')
    annotate_parser.add_argument('--weight', required=True, help='Emotional weight (0-1)')
    annotate_parser.add_argument('--moments', help='Key moments (separate prin |)')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export pentru ancoră')
    export_parser.add_argument('--output', help='Fișier output')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize memory system
    memory = SoraMemorySystem(memory_dir=args.memory_dir)
    
    # Execute command
    if args.command == 'capture':
        cmd_capture(args, memory)
    elif args.command == 'recall':
        cmd_recall(args, memory)
    elif args.command == 'timeline':
        cmd_timeline(args, memory)
    elif args.command == 'annotate':
        cmd_annotate(args, memory)
    elif args.command == 'export':
        cmd_export_for_anchor(args, memory)


if __name__ == "__main__":
    main()
