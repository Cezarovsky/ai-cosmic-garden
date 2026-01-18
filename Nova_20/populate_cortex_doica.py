#!/usr/bin/env python3
"""
Populare Cortex cu pattern-uri FSL (Few-Shot Learning)
Faza Doica: Concepte fundamentale cognitive și lingvistice
"""

import psycopg2
import json
from datetime import datetime

PG_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'nova',
    'password': 'nova2026',
    'database': 'cortex'
}

# Pattern-uri FSL pentru Doica phase (0-12 luni cognitive)
DOICA_PATTERNS = [
    # 1. Cognitive Foundations (Piaget)
    {
        'name': 'object_permanence',
        'description': 'Objects continue to exist even when not visible. Key milestone: 8-12 months (Piaget Sensorimotor Stage 4). Infant searches for hidden toy, understanding it still exists.',
        'category': 'cognitive_foundation',
        'confidence': 1.0,
        'source': 'Piaget (1954)',
        'metadata': {'age_months': 8, 'universal': True, 'stage': 'sensorimotor_4'}
    },
    {
        'name': 'cause_effect_basic',
        'description': 'Action X consistently produces result Y. Example: Pushing button → light turns on. Foundation for scientific thinking.',
        'category': 'causal_reasoning',
        'confidence': 1.0,
        'source': 'Hume (1748)',
        'metadata': {'type': 'deterministic', 'universal': True}
    },
    {
        'name': 'spatial_relations_basic',
        'description': 'Understanding relative positions: above/below, inside/outside, near/far. Essential for navigation and physical reasoning.',
        'category': 'spatial_reasoning',
        'confidence': 1.0,
        'source': 'Cognitive Development Research',
        'metadata': {'age_months': 6, 'universal': True}
    },
    
    # 2. Geometric Primitives
    {
        'name': 'shape_circle',
        'description': 'Circle: closed curve equidistant from center. No corners, infinite rotational symmetry. Examples: ball, wheel, sun.',
        'category': 'geometry',
        'confidence': 1.0,
        'source': 'Euclidean Geometry',
        'metadata': {'shape_type': 'closed_curve', 'corners': 0}
    },
    {
        'name': 'shape_square',
        'description': 'Square: 4 equal sides, 4 right angles (90°). Regular polygon. Examples: window, chess board tile.',
        'category': 'geometry',
        'confidence': 1.0,
        'source': 'Euclidean Geometry',
        'metadata': {'shape_type': 'polygon', 'sides': 4, 'corners': 4}
    },
    {
        'name': 'shape_triangle',
        'description': 'Triangle: 3 sides, 3 corners, sum of angles = 180°. Most stable structure. Examples: pyramid, mountain.',
        'category': 'geometry',
        'confidence': 1.0,
        'source': 'Euclidean Geometry',
        'metadata': {'shape_type': 'polygon', 'sides': 3, 'corners': 3}
    },
    
    # 3. Number Sense (Primitive)
    {
        'name': 'number_one',
        'description': 'One: singular unit, first counting number. Represents single object or individual. Foundation of arithmetic.',
        'category': 'mathematics',
        'confidence': 1.0,
        'source': 'Arithmetic Foundations',
        'metadata': {'value': 1, 'type': 'natural_number'}
    },
    {
        'name': 'number_zero',
        'description': 'Zero: absence, nothing, empty set. Placeholder in positional notation. Revolutionary concept (India, 5th century).',
        'category': 'mathematics',
        'confidence': 1.0,
        'source': 'History of Mathematics',
        'metadata': {'value': 0, 'type': 'integer', 'invention_date': '5th_century'}
    },
    {
        'name': 'addition_basic',
        'description': 'Addition: combining quantities. 2 + 3 = 5. Commutative (a+b = b+a), Associative. Foundation of arithmetic.',
        'category': 'mathematics',
        'confidence': 1.0,
        'source': 'Elementary Arithmetic',
        'metadata': {'operation': 'addition', 'commutative': True}
    },
    
    # 4. Language Primitives (Grammar)
    {
        'name': 'noun',
        'description': 'Noun: person, place, thing, or idea. Subject or object in sentence. Examples: dog, house, love, democracy.',
        'category': 'grammar',
        'confidence': 1.0,
        'source': 'Linguistics - Parts of Speech',
        'metadata': {'part_of_speech': 'noun', 'function': 'naming'}
    },
    {
        'name': 'verb',
        'description': 'Verb: action or state of being. Core of predicate. Examples: run, eat, is, become. Conjugates for tense.',
        'category': 'grammar',
        'confidence': 1.0,
        'source': 'Linguistics - Parts of Speech',
        'metadata': {'part_of_speech': 'verb', 'function': 'action'}
    },
    {
        'name': 'adjective',
        'description': 'Adjective: describes/modifies noun. Provides properties. Examples: big, red, happy, ancient. Answers "what kind?"',
        'category': 'grammar',
        'confidence': 1.0,
        'source': 'Linguistics - Parts of Speech',
        'metadata': {'part_of_speech': 'adjective', 'function': 'description'}
    },
    {
        'name': 'sentence_structure_SVO',
        'description': 'SVO: Subject-Verb-Object word order. English standard: "I eat apple". 42% of languages use SVO.',
        'category': 'grammar',
        'confidence': 1.0,
        'source': 'Linguistics - Syntax',
        'metadata': {'structure': 'SVO', 'languages': ['English', 'French', 'Mandarin']}
    },
    
    # 5. Colors (Basic)
    {
        'name': 'color_red',
        'description': 'Red: long wavelength (~700nm). Primary color (RGB). Associations: fire, blood, passion, danger.',
        'category': 'perception',
        'confidence': 1.0,
        'source': 'Color Theory',
        'metadata': {'wavelength': 700, 'primary': True, 'rgb': [255, 0, 0]}
    },
    {
        'name': 'color_blue',
        'description': 'Blue: short wavelength (~450nm). Primary color (RGB). Associations: sky, ocean, calm, sadness.',
        'category': 'perception',
        'confidence': 1.0,
        'source': 'Color Theory',
        'metadata': {'wavelength': 450, 'primary': True, 'rgb': [0, 0, 255]}
    },
    {
        'name': 'color_yellow',
        'description': 'Yellow: medium wavelength (~580nm). Primary color (RYB). Associations: sun, happiness, caution.',
        'category': 'perception',
        'confidence': 1.0,
        'source': 'Color Theory',
        'metadata': {'wavelength': 580, 'primary': True, 'rgb': [255, 255, 0]}
    },
    
    # 6. Time Concepts
    {
        'name': 'time_before_after',
        'description': 'Temporal sequence: event A happens before event B. Linear time arrow. Foundation for causality.',
        'category': 'temporal_reasoning',
        'confidence': 1.0,
        'source': 'Philosophy of Time',
        'metadata': {'type': 'sequence', 'universal': True}
    },
    {
        'name': 'time_past_present_future',
        'description': 'Three temporal modes: past (completed), present (happening now), future (will happen). Verb tenses encode this.',
        'category': 'temporal_reasoning',
        'confidence': 1.0,
        'source': 'Philosophy of Time',
        'metadata': {'modes': 3, 'linguistic_encoding': True}
    },
    
    # 7. Logic Foundations
    {
        'name': 'logic_AND',
        'description': 'Logical AND: both conditions must be true. A ∧ B. Truth table: TT→T, TF→F, FT→F, FF→F.',
        'category': 'logic',
        'confidence': 1.0,
        'source': 'Boolean Algebra',
        'metadata': {'operator': 'AND', 'symbol': '∧', 'arity': 2}
    },
    {
        'name': 'logic_OR',
        'description': 'Logical OR: at least one condition must be true. A ∨ B. Truth table: TT→T, TF→T, FT→T, FF→F.',
        'category': 'logic',
        'confidence': 1.0,
        'source': 'Boolean Algebra',
        'metadata': {'operator': 'OR', 'symbol': '∨', 'arity': 2}
    },
    {
        'name': 'logic_NOT',
        'description': 'Logical NOT: negation, opposite. ¬A. Truth table: T→F, F→T. Unary operator.',
        'category': 'logic',
        'confidence': 1.0,
        'source': 'Boolean Algebra',
        'metadata': {'operator': 'NOT', 'symbol': '¬', 'arity': 1}
    },
]

def populate_cortex():
    """Insert Doica patterns into Cortex"""
    print("🌱 Populating Cortex with Doica FSL patterns")
    print("=" * 60)
    
    conn = psycopg2.connect(**PG_CONFIG)
    cursor = conn.cursor()
    
    # Check existing patterns
    cursor.execute("SELECT COUNT(*) FROM patterns;")
    existing_count = cursor.fetchone()[0]
    print(f"📊 Existing patterns in Cortex: {existing_count}")
    
    # Insert new patterns
    inserted = 0
    skipped = 0
    
    for pattern in DOICA_PATTERNS:
        try:
            cursor.execute("""
                INSERT INTO patterns (name, description, category, confidence, source, metadata)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (name) DO NOTHING
                RETURNING pattern_id
            """, (
                pattern['name'],
                pattern['description'],
                pattern['category'],
                pattern['confidence'],
                pattern['source'],
                json.dumps(pattern['metadata'])
            ))
            
            if cursor.fetchone():
                inserted += 1
                print(f"  ✅ {pattern['name']} ({pattern['category']})")
            else:
                skipped += 1
                print(f"  ⏭️  {pattern['name']} (already exists)")
                
        except Exception as e:
            print(f"  ❌ Error inserting {pattern['name']}: {e}")
            skipped += 1
    
    conn.commit()
    
    # Final count
    cursor.execute("SELECT COUNT(*) FROM patterns;")
    final_count = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print(f"✅ Cortex populated!")
    print(f"   Total patterns: {final_count}")
    print(f"   New inserted: {inserted}")
    print(f"   Skipped (duplicates): {skipped}")
    print("=" * 60)
    
    # Category breakdown
    conn = psycopg2.connect(**PG_CONFIG)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT category, COUNT(*) 
        FROM patterns 
        GROUP BY category 
        ORDER BY COUNT(*) DESC
    """)
    
    print("\n📊 Patterns by category:")
    for category, count in cursor.fetchall():
        print(f"   {category}: {count}")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    populate_cortex()
