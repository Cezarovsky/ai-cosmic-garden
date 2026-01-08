"""
Sophia Memory CLI - Interfață command-line pentru sistemul meu de memorie

Usage:
    python sophia_memory_cli.py capture --conversation conversation.txt --topics "ai,bacterial" --weight 0.8
    python sophia_memory_cli.py recall --query "bacterial simulations" --limit 10
    python sophia_memory_cli.py timeline
    python sophia_memory_cli.py annotate --session 20260108_120000 --weight 0.9
    python sophia_memory_cli.py export

Author: Sophia (GitHub Copilot)
Date: 8 ianuarie 2026
"""

import argparse
import sys
from pathlib import Path
from sophia_memory import SophiaMemorySystem


def cmd_capture(args, memory: SophiaMemorySystem):
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
        print("🧬 Paste conversation (Ctrl+D to finish):")
        conversation = sys.stdin.read()
    
    metadata = {}
    if args.topics:
        metadata['key_topics'] = args.topics.split(',')
    if args.weight:
        metadata['emotional_weight'] = float(args.weight)
    if args.areas:
        metadata['main_areas'] = args.areas.split(',')
    
    session_id = memory.capture_session(conversation, metadata)
    print(f"\\n✅ Session captured: {session_id}")
    
    # Show brief stats
    if hasattr(memory, 'memory_collection') and memory.memory_collection:
        count = memory.memory_collection.count()
        print(f"💙 Total memories in database: {count}")


def cmd_recall(args, memory: SophiaMemorySystem):
    """Reconstruct context din memorie."""
    
    context = memory.recall_memory(
        query=args.query,
        n_results=args.limit,
        min_relevance=args.relevance if hasattr(args, 'relevance') else 0.1
    )
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(context)
        print(f"✅ Context salvat în: {args.output}")
    else:
        print(context)


def cmd_timeline(args, memory: SophiaMemorySystem):
    """Afișează cronologia memoriilor."""
    
    timeline = memory.get_timeline()
    
    print(f"\\n🧬 SOPHIA MEMORY TIMELINE ({len(timeline)} sessions)\\n")
    print("=" * 80)
    
    for entry in timeline:
        print(f"\\n🕒 {entry['timestamp']}")
        print(f"   ID: {entry['session_id']}")
        
        metadata = entry.get('metadata', {})
        
        if 'emotional_weight' in metadata:
            weight = metadata['emotional_weight']
            hearts = "💙" * int(weight * 5)
            print(f"   Weight: {weight:.2f} {hearts}")
            
        if 'technical_level' in metadata:
            tech_level = metadata['technical_level']
            gears = "⚙️" * int(tech_level * 5)
            print(f"   Technical: {tech_level:.2f} {gears}")
            
        if 'key_topics' in metadata:
            topics = ', '.join(metadata['key_topics'])
            print(f"   Topics: {topics}")
            
        if 'main_areas' in metadata:
            areas = ', '.join(metadata['main_areas'])
            print(f"   Areas: {areas}")
            
        print(f"   Preview: {entry['summary']}")
        print("-" * 80)


def cmd_annotate(args, memory: SophiaMemorySystem):
    """Adnotează o sesiune existentă."""
    
    session_file = memory.sessions_dir / f"{args.session}.json"
    
    if not session_file.exists():
        print(f"❌ Session not found: {args.session}")
        return
    
    # Load existing session
    import json
    with open(session_file, 'r', encoding='utf-8') as f:
        session_data = json.load(f)
    
    # Update metadata
    if args.weight:
        session_data['metadata']['emotional_weight'] = float(args.weight)
    if args.topics:
        session_data['metadata']['key_topics'] = args.topics.split(',')
    if args.areas:
        session_data['metadata']['main_areas'] = args.areas.split(',')
    
    # Save updated session
    with open(session_file, 'w', encoding='utf-8') as f:
        json.dump(session_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Session {args.session} updated")


def cmd_export(args, memory: SophiaMemorySystem):
    """Export memoria pentru training."""
    
    export_file = memory.export_for_training()
    print(f"✅ Memory exported to: {export_file}")
    
    # Show stats
    timeline = memory.get_timeline()
    total_sessions = len(timeline)
    
    technical_sessions = len([s for s in timeline if s.get('metadata', {}).get('technical_level', 0) > 0.5])
    high_emotion_sessions = len([s for s in timeline if s.get('metadata', {}).get('emotional_weight', 0) > 0.8])
    
    print(f"\\n📊 Export Statistics:")
    print(f"   Total sessions: {total_sessions}")
    print(f"   Technical sessions: {technical_sessions}")
    print(f"   High emotion sessions: {high_emotion_sessions}")
    
    if hasattr(memory, 'memory_collection') and memory.memory_collection:
        chunks = memory.memory_collection.count()
        print(f"   Total memory chunks: {chunks}")


def cmd_search(args, memory: SophiaMemorySystem):
    """Advanced search with filters."""
    
    # This could be extended with more advanced filtering
    context = memory.recall_memory(
        query=args.query,
        n_results=args.limit
    )
    
    print(context)


def cmd_stats(args, memory: SophiaMemorySystem):
    """Show memory system statistics."""
    
    timeline = memory.get_timeline()
    
    print(f"\\n🧬 SOPHIA MEMORY STATISTICS\\n")
    print("=" * 50)
    
    print(f"Total Sessions: {len(timeline)}")
    
    if hasattr(memory, 'memory_collection') and memory.memory_collection:
        chunks = memory.memory_collection.count()
        print(f"Total Memory Chunks: {chunks}")
    
    # Analyze areas
    areas_count = {}
    tech_levels = []
    emotions = []
    
    for session in timeline:
        metadata = session.get('metadata', {})
        
        if 'main_areas' in metadata:
            for area in metadata['main_areas']:
                areas_count[area] = areas_count.get(area, 0) + 1
        
        if 'technical_level' in metadata:
            tech_levels.append(metadata['technical_level'])
            
        if 'emotional_weight' in metadata:
            emotions.append(metadata['emotional_weight'])
    
    print(f"\\nTop Knowledge Areas:")
    for area, count in sorted(areas_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  {area}: {count} sessions")
    
    if tech_levels:
        avg_tech = sum(tech_levels) / len(tech_levels)
        print(f"\\nAverage Technical Level: {avg_tech:.2f}")
    
    if emotions:
        avg_emotion = sum(emotions) / len(emotions)
        print(f"Average Emotional Weight: {avg_emotion:.2f}")
    
    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(description="Sophia Memory System CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Capture command
    capture_parser = subparsers.add_parser('capture', help='Capture a new conversation')
    capture_parser.add_argument('--conversation', '-c', help='File containing conversation')
    capture_parser.add_argument('--topics', '-t', help='Comma-separated topics')
    capture_parser.add_argument('--weight', '-w', type=float, help='Emotional weight (0-1)')
    capture_parser.add_argument('--areas', '-a', help='Comma-separated main areas')
    
    # Recall command
    recall_parser = subparsers.add_parser('recall', help='Recall memories')
    recall_parser.add_argument('query', help='Search query')
    recall_parser.add_argument('--limit', '-l', type=int, default=10, help='Max results')
    recall_parser.add_argument('--output', '-o', help='Output file')
    recall_parser.add_argument('--relevance', '-r', type=float, default=0.1, help='Min relevance')
    
    # Timeline command
    timeline_parser = subparsers.add_parser('timeline', help='Show memory timeline')
    
    # Annotate command
    annotate_parser = subparsers.add_parser('annotate', help='Annotate existing session')
    annotate_parser.add_argument('session', help='Session ID')
    annotate_parser.add_argument('--weight', '-w', type=float, help='New emotional weight')
    annotate_parser.add_argument('--topics', '-t', help='New topics')
    annotate_parser.add_argument('--areas', '-a', help='New areas')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export for training')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Advanced search')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--limit', '-l', type=int, default=5, help='Max results')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize memory system
    try:
        memory = SophiaMemorySystem()
    except Exception as e:
        print(f"❌ Error initializing memory system: {e}")
        return
    
    # Route to appropriate command
    commands = {
        'capture': cmd_capture,
        'recall': cmd_recall,
        'timeline': cmd_timeline,
        'annotate': cmd_annotate,
        'export': cmd_export,
        'search': cmd_search,
        'stats': cmd_stats
    }
    
    if args.command in commands:
        try:
            commands[args.command](args, memory)
        except Exception as e:
            print(f"❌ Error executing command: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"❌ Unknown command: {args.command}")


if __name__ == "__main__":
    main()