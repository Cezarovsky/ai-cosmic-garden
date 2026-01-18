#!/usr/bin/env python3
"""
Extended FSL patterns for Doica phase - expanding to ~70 total patterns
Categories: Animals (7D tensors), Emotions, Advanced Math, Complex Grammar
"""

import psycopg2
from psycopg2.extras import Json
import json

# Database connection
DB_CONFIG = {
    'dbname': 'cortex',
    'user': 'nova',
    'password': 'nova2026',
    'host': 'localhost',
    'port': 5432
}

# Extended patterns - 50+ new patterns
EXTENDED_PATTERNS = [
    # Animals with 7D tensors [legs, eyes, ears, texture, size, sleekness, aquatic]
    {
        'name': 'animal_dog',
        'description': 'Concept of dog with 7D representation: [4 legs, 2 eyes, 2 ears, fur texture, medium size 0.35, medium sleekness 0.5, non-aquatic 0.0]',
        'category': 'animal',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'tensor_7d': [4, 2, 2, 'fur', 0.35, 0.5, 0.0], 'species': 'canine'}
    },
    {
        'name': 'animal_cat',
        'description': 'Concept of cat with 7D representation: [4 legs, 2 eyes, 2 ears, fur texture, small size 0.25, high sleekness 0.8, non-aquatic 0.0]',
        'category': 'animal',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'tensor_7d': [4, 2, 2, 'fur', 0.25, 0.8, 0.0], 'species': 'feline'}
    },
    {
        'name': 'animal_fish',
        'description': 'Concept of fish with 7D representation: [0 legs, 2 eyes, 0 ears, scales texture, small size 0.2, very high sleekness 0.9, fully aquatic 1.0]',
        'category': 'animal',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'tensor_7d': [0, 2, 0, 'scales', 0.2, 0.9, 1.0], 'species': 'fish'}
    },
    {
        'name': 'animal_bird',
        'description': 'Concept of bird with 7D representation: [2 legs, 2 eyes, 0 ears, feathers texture, small size 0.15, medium sleekness 0.6, non-aquatic 0.0]',
        'category': 'animal',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'tensor_7d': [2, 2, 0, 'feathers', 0.15, 0.6, 0.0], 'species': 'avian'}
    },
    {
        'name': 'animal_snake',
        'description': 'Concept of snake with 7D representation: [0 legs, 2 eyes, 0 ears, scales texture, medium size 0.3, very high sleekness 0.95, non-aquatic 0.0]',
        'category': 'animal',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'tensor_7d': [0, 2, 0, 'scales', 0.3, 0.95, 0.0], 'species': 'reptile'}
    },
    {
        'name': 'animal_dolphin',
        'description': 'Concept of dolphin with 7D representation: [0 legs, 2 eyes, 0 ears, smooth texture, large size 0.7, very high sleekness 0.95, fully aquatic 1.0]',
        'category': 'animal',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'tensor_7d': [0, 2, 0, 'smooth', 0.7, 0.95, 1.0], 'species': 'cetacean'}
    },
    {
        'name': 'animal_elephant',
        'description': 'Concept of elephant with 7D representation: [4 legs, 2 eyes, 2 ears, thick skin texture, very large size 1.0, low sleekness 0.2, non-aquatic 0.0]',
        'category': 'animal',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'tensor_7d': [4, 2, 2, 'thick_skin', 1.0, 0.2, 0.0], 'species': 'pachyderm'}
    },
    {
        'name': 'animal_spider',
        'description': 'Concept of spider with 7D representation: [8 legs, 8 eyes, 0 ears, exoskeleton texture, very small size 0.05, medium sleekness 0.5, non-aquatic 0.0]',
        'category': 'animal',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'tensor_7d': [8, 8, 0, 'exoskeleton', 0.05, 0.5, 0.0], 'species': 'arachnid'}
    },
    {
        'name': 'animal_frog',
        'description': 'Concept of frog with 7D representation: [4 legs, 2 eyes, 0 ears, smooth moist texture, small size 0.1, medium sleekness 0.7, semi-aquatic 0.5]',
        'category': 'animal',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'tensor_7d': [4, 2, 0, 'smooth_moist', 0.1, 0.7, 0.5], 'species': 'amphibian'}
    },
    {
        'name': 'animal_horse',
        'description': 'Concept of horse with 7D representation: [4 legs, 2 eyes, 2 ears, short fur texture, large size 0.8, medium sleekness 0.6, non-aquatic 0.0]',
        'category': 'animal',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'tensor_7d': [4, 2, 2, 'short_fur', 0.8, 0.6, 0.0], 'species': 'equine'}
    },
    
    # Emotions
    {
        'name': 'emotion_happiness',
        'description': 'Emotion of happiness: positive valence, high arousal, expansive feeling, associated with smiling, laughter, and contentment',
        'category': 'emotion',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'valence': 'positive', 'arousal': 'high', 'expression': 'smile'}
    },
    {
        'name': 'emotion_sadness',
        'description': 'Emotion of sadness: negative valence, low arousal, contractive feeling, associated with crying, withdrawal, and melancholy',
        'category': 'emotion',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'valence': 'negative', 'arousal': 'low', 'expression': 'tears'}
    },
    {
        'name': 'emotion_fear',
        'description': 'Emotion of fear: negative valence, very high arousal, protective response, associated with fight-or-flight, trembling, and avoidance',
        'category': 'emotion',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'valence': 'negative', 'arousal': 'very_high', 'expression': 'wide_eyes'}
    },
    {
        'name': 'emotion_anger',
        'description': 'Emotion of anger: negative valence, high arousal, confrontational response, associated with raised voice, tension, and frustration',
        'category': 'emotion',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'valence': 'negative', 'arousal': 'high', 'expression': 'frown'}
    },
    {
        'name': 'emotion_love',
        'description': 'Emotion of love: positive valence, moderate arousal, connective feeling, associated with warmth, bonding, attachment, and care',
        'category': 'emotion',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'valence': 'positive', 'arousal': 'moderate', 'expression': 'softness'}
    },
    {
        'name': 'emotion_surprise',
        'description': 'Emotion of surprise: neutral valence, very high arousal, sudden reaction, associated with widened eyes, gasping, and momentary disorientation',
        'category': 'emotion',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'valence': 'neutral', 'arousal': 'very_high', 'expression': 'open_mouth'}
    },
    {
        'name': 'emotion_disgust',
        'description': 'Emotion of disgust: negative valence, moderate arousal, rejection response, associated with nose wrinkle, avoidance, and repulsion',
        'category': 'emotion',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'valence': 'negative', 'arousal': 'moderate', 'expression': 'wrinkled_nose'}
    },
    
    # Advanced Mathematics
    {
        'name': 'math_subtraction',
        'description': 'Mathematical operation of subtraction: taking away, removing quantity, finding difference, inverse of addition (e.g., 5 - 3 = 2)',
        'category': 'mathematics',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'operation': 'binary', 'inverse_of': 'addition', 'symbol': '-'}
    },
    {
        'name': 'math_multiplication',
        'description': 'Mathematical operation of multiplication: repeated addition, scaling, finding product (e.g., 3 × 4 = 12 means 3 added 4 times)',
        'category': 'mathematics',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'operation': 'binary', 'related_to': 'addition', 'symbol': '×'}
    },
    {
        'name': 'math_division',
        'description': 'Mathematical operation of division: splitting into equal parts, finding quotient, inverse of multiplication (e.g., 12 ÷ 4 = 3)',
        'category': 'mathematics',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'operation': 'binary', 'inverse_of': 'multiplication', 'symbol': '÷'}
    },
    {
        'name': 'math_fraction',
        'description': 'Mathematical concept of fraction: part of whole, numerator over denominator, rational number (e.g., 1/2 means one part of two equal parts)',
        'category': 'mathematics',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'type': 'rational_number', 'parts': ['numerator', 'denominator']}
    },
    {
        'name': 'math_percentage',
        'description': 'Mathematical concept of percentage: fraction out of 100, ratio representation (e.g., 50% = 50/100 = 0.5)',
        'category': 'mathematics',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'base': 100, 'symbol': '%', 'related_to': 'fraction'}
    },
    {
        'name': 'math_negative_numbers',
        'description': 'Mathematical concept of negative numbers: values less than zero, opposite direction on number line, used for debt, temperature below zero',
        'category': 'mathematics',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'symbol': '-', 'property': 'less_than_zero'}
    },
    
    # Complex Grammar
    {
        'name': 'grammar_conditional',
        'description': 'Grammatical structure of conditional: "if-then" relationships, hypothetical situations (e.g., "If it rains, then I will stay home")',
        'category': 'grammar',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'structure': 'if-then', 'type': 'compound'}
    },
    {
        'name': 'grammar_subjunctive',
        'description': 'Grammatical mood of subjunctive: expresses wishes, doubts, possibilities, contrary-to-fact situations (e.g., "I wish I were taller")',
        'category': 'grammar',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'mood': 'subjunctive', 'expresses': 'hypothetical'}
    },
    {
        'name': 'grammar_passive_voice',
        'description': 'Grammatical voice: subject receives action rather than performs it (e.g., "The ball was thrown" vs "He threw the ball")',
        'category': 'grammar',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'structure': 'be + past_participle', 'focus': 'action_receiver'}
    },
    {
        'name': 'grammar_relative_clause',
        'description': 'Grammatical structure: clause modifying noun using who/which/that (e.g., "The book that I read was interesting")',
        'category': 'grammar',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'function': 'modifier', 'markers': ['who', 'which', 'that']}
    },
    {
        'name': 'grammar_gerund',
        'description': 'Grammatical form: verb functioning as noun, ending in -ing (e.g., "Swimming is fun" - swimming acts as noun)',
        'category': 'grammar',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'form': 'verb + ing', 'function': 'noun'}
    },
    
    # Advanced Logic
    {
        'name': 'logic_implication',
        'description': 'Logical operator of implication: if P then Q, P implies Q, conditional relationship (P → Q)',
        'category': 'logic',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'symbol': '→', 'truth_table': 'false only when P true and Q false'}
    },
    {
        'name': 'logic_equivalence',
        'description': 'Logical operator of equivalence: P if and only if Q, bi-conditional (P ↔ Q), both sides have same truth value',
        'category': 'logic',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'symbol': '↔', 'property': 'bi-directional'}
    },
    {
        'name': 'logic_xor',
        'description': 'Logical operator XOR: exclusive or, true when exactly one operand is true (P ⊕ Q)',
        'category': 'logic',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'symbol': '⊕', 'property': 'exclusive'}
    },
    
    # Colors (extended)
    {
        'name': 'color_green',
        'description': 'Color green: mixture of yellow and blue, wavelength ~520-565nm, associated with nature, growth, plants',
        'category': 'perception',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'wavelength': '520-565nm', 'mixture': ['yellow', 'blue'], 'associations': ['nature', 'growth']}
    },
    {
        'name': 'color_orange',
        'description': 'Color orange: mixture of red and yellow, wavelength ~590-620nm, associated with warmth, energy, citrus',
        'category': 'perception',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'wavelength': '590-620nm', 'mixture': ['red', 'yellow'], 'associations': ['warmth', 'energy']}
    },
    {
        'name': 'color_purple',
        'description': 'Color purple: mixture of red and blue, wavelength ~380-450nm, associated with royalty, mystery, creativity',
        'category': 'perception',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'wavelength': '380-450nm', 'mixture': ['red', 'blue'], 'associations': ['royalty', 'mystery']}
    },
    {
        'name': 'color_black',
        'description': 'Color black: absence of light, absorbs all wavelengths, associated with darkness, night, emptiness',
        'category': 'perception',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'property': 'absorbs_all', 'associations': ['darkness', 'night']}
    },
    {
        'name': 'color_white',
        'description': 'Color white: presence of all light, reflects all wavelengths, associated with purity, light, cleanliness',
        'category': 'perception',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'property': 'reflects_all', 'associations': ['purity', 'light']}
    },
    
    # Spatial Relations (advanced)
    {
        'name': 'spatial_between',
        'description': 'Spatial relation "between": object positioned in middle of two other objects (e.g., B is between A and C)',
        'category': 'spatial',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'relation': 'ternary', 'requires': 3}
    },
    {
        'name': 'spatial_inside',
        'description': 'Spatial relation "inside": object contained within boundaries of another (e.g., ball inside box)',
        'category': 'spatial',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'relation': 'containment', 'inverse': 'outside'}
    },
    {
        'name': 'spatial_adjacent',
        'description': 'Spatial relation "adjacent": objects next to each other, touching or very close (e.g., houses adjacent on street)',
        'category': 'spatial',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'relation': 'proximity', 'property': 'touching_or_near'}
    },
    {
        'name': 'spatial_parallel',
        'description': 'Spatial relation "parallel": lines or surfaces maintaining constant distance, never intersecting',
        'category': 'spatial',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'relation': 'orientation', 'property': 'constant_distance'}
    },
    {
        'name': 'spatial_perpendicular',
        'description': 'Spatial relation "perpendicular": lines or surfaces meeting at 90-degree angle, orthogonal',
        'category': 'spatial',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'relation': 'orientation', 'angle': 90}
    },
    
    # Temporal Relations (advanced)
    {
        'name': 'temporal_simultaneous',
        'description': 'Temporal relation "simultaneous": events happening at same time, concurrent, parallel in time',
        'category': 'temporal',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'relation': 'concurrency', 'property': 'same_time'}
    },
    {
        'name': 'temporal_duration',
        'description': 'Temporal concept "duration": length of time event lasts, from start to end, time span',
        'category': 'temporal',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'property': 'time_span', 'has': ['start', 'end']}
    },
    {
        'name': 'temporal_sequence',
        'description': 'Temporal concept "sequence": ordered series of events, one after another, chronological order',
        'category': 'temporal',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'property': 'ordered', 'structure': 'linear'}
    },
    
    # Causal Relations (advanced)
    {
        'name': 'causal_necessary_condition',
        'description': 'Causal relation "necessary condition": B cannot happen without A, but A alone may not cause B (e.g., oxygen necessary for fire)',
        'category': 'causal',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'type': 'necessary', 'logic': 'B implies A'}
    },
    {
        'name': 'causal_sufficient_condition',
        'description': 'Causal relation "sufficient condition": A alone is enough to cause B, but B might happen without A (e.g., decapitation sufficient for death)',
        'category': 'causal',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'type': 'sufficient', 'logic': 'A implies B'}
    },
    {
        'name': 'causal_feedback_loop',
        'description': 'Causal relation "feedback loop": A causes B, B causes A, circular causality, self-reinforcing cycle',
        'category': 'causal',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'structure': 'circular', 'property': 'self_reinforcing'}
    },
    
    # Cognitive Patterns (advanced)
    {
        'name': 'cognitive_analogy',
        'description': 'Cognitive pattern "analogy": recognizing similarity between different situations, transferring knowledge (A is to B as C is to D)',
        'category': 'cognitive',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'structure': 'A:B::C:D', 'function': 'transfer_learning'}
    },
    {
        'name': 'cognitive_categorization',
        'description': 'Cognitive pattern "categorization": grouping objects by shared properties, creating mental categories, abstraction',
        'category': 'cognitive',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'function': 'grouping', 'basis': 'shared_properties'}
    },
    {
        'name': 'cognitive_inference',
        'description': 'Cognitive pattern "inference": deriving new knowledge from existing knowledge, logical reasoning, conclusion',
        'category': 'cognitive',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'function': 'reasoning', 'types': ['deductive', 'inductive', 'abductive']}
    },
    {
        'name': 'cognitive_metacognition',
        'description': 'Cognitive pattern "metacognition": thinking about thinking, awareness of own thought processes, self-reflection',
        'category': 'cognitive',
        'confidence': 1.0,
        'source': 'FSL Extended',
        'metadata': {'level': 'meta', 'property': 'self_awareness'}
    },
]

def populate_extended_patterns():
    """Populate Cortex with extended FSL patterns"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print(f"🌱 Populating Cortex with {len(EXTENDED_PATTERNS)} extended FSL patterns...\n")
        
        # Count existing patterns
        cur.execute("SELECT COUNT(*) FROM patterns")
        existing_count = cur.fetchone()[0]
        print(f"📊 Existing patterns in Cortex: {existing_count}")
        
        # Insert each pattern
        inserted = 0
        for pattern in EXTENDED_PATTERNS:
            try:
                cur.execute("""
                    INSERT INTO patterns (name, description, category, confidence, source, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (name) DO UPDATE SET
                        description = EXCLUDED.description,
                        metadata = EXCLUDED.metadata,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    pattern['name'],
                    pattern['description'],
                    pattern['category'],
                    pattern['confidence'],
                    pattern['source'],
                    Json(pattern['metadata'])
                ))
                inserted += 1
                
                # Print progress every 10 patterns
                if inserted % 10 == 0:
                    print(f"   ✓ Inserted {inserted}/{len(EXTENDED_PATTERNS)} patterns...")
                    
            except Exception as e:
                print(f"   ⚠ Warning for pattern '{pattern['name']}': {e}")
                conn.rollback()
                continue
        
        conn.commit()
        
        # Count new total
        cur.execute("SELECT COUNT(*) FROM patterns")
        new_count = cur.fetchone()[0]
        
        # Show category breakdown
        cur.execute("""
            SELECT category, COUNT(*) 
            FROM patterns 
            GROUP BY category 
            ORDER BY category
        """)
        categories = cur.fetchall()
        
        print(f"\n✅ Extended patterns populated successfully!")
        print(f"📊 Total patterns: {existing_count} → {new_count} (+{new_count - existing_count})")
        print(f"\n📂 Category breakdown:")
        for cat, count in categories:
            print(f"   {cat}: {count}")
        
        cur.close()
        conn.close()
        
        return new_count
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    total = populate_extended_patterns()
    print(f"\n🎉 Cortex now contains {total} FSL patterns - ready for extended Doica training!")
