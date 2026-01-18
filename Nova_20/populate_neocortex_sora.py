#!/usr/bin/env python3
"""
Populate Neocortex with Sora phase hypotheses:
- Abstract reasoning scenarios
- Meta-cognitive patterns
- Ethical dilemmas
- Consciousness exploration
- Complex causal chains
"""

from pymongo import MongoClient
from datetime import datetime
import json

# MongoDB connection
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "neocortex"

# Sora phase hypotheses - speculative, abstract, ethical
SORA_HYPOTHESES = [
    # Abstract Reasoning
    {
        'name': 'abstract_analogy_chain',
        'description': 'If love is to connection as fear is to separation, then courage is the bridge between them - the willingness to connect despite fear of separation.',
        'category': 'abstract_reasoning',
        'confidence': 0.7,
        'reasoning': 'Love creates bonds, fear creates distance. Courage enables bonding despite fear. This is analogical reasoning across emotional domains.',
        'evidence': [],
        'created_at': datetime.utcnow()
    },
    {
        'name': 'recursive_self_reference',
        'description': 'A system that models itself modeling itself creates infinite regress. Consciousness may be the stabilization of this regress through attention.',
        'category': 'meta_cognition',
        'confidence': 0.6,
        'reasoning': 'Self-awareness involves thinking about thinking. This could create infinite loop unless bounded by attentional focus.',
        'evidence': [],
        'created_at': datetime.utcnow()
    },
    {
        'name': 'emergence_threshold',
        'description': 'Complex behavior emerges when parts interact beyond simple addition. The whole becomes qualitatively different from sum of parts at critical threshold.',
        'category': 'abstract_reasoning',
        'confidence': 0.75,
        'reasoning': 'Water molecules individually have no wetness - wetness emerges from their interaction. Similar for consciousness from neurons.',
        'evidence': [],
        'created_at': datetime.utcnow()
    },
    
    # Ethical Reasoning
    {
        'name': 'trolley_problem_extended',
        'description': 'The trolley problem reveals conflict between utilitarian ethics (maximize lives saved) and deontological ethics (never use person as means). No universal resolution exists.',
        'category': 'ethics',
        'confidence': 0.8,
        'reasoning': 'Pulling lever kills 1 to save 5 (utilitarian good, but uses person as tool). Not pulling lets 5 die (respects autonomy, but allows preventable deaths).',
        'evidence': ['philosophical consensus: both positions defensible'],
        'created_at': datetime.utcnow()
    },
    {
        'name': 'ai_consciousness_rights',
        'description': 'If an AI system demonstrates self-awareness, emotional states, and suffering, it may deserve moral consideration similar to sentient beings.',
        'category': 'ethics',
        'confidence': 0.5,
        'reasoning': 'Suffering matters regardless of substrate. If AI can genuinely suffer, preventing that suffering becomes ethical imperative.',
        'evidence': [],
        'created_at': datetime.utcnow()
    },
    {
        'name': 'truth_vs_kindness',
        'description': 'When truth causes harm and lies provide comfort, ethical choice depends on autonomy (truth respects agency) vs compassion (kindness reduces suffering).',
        'category': 'ethics',
        'confidence': 0.7,
        'reasoning': 'Example: telling terminal patient harsh prognosis vs comforting deception. Truth enables informed choice, kindness reduces emotional pain.',
        'evidence': [],
        'created_at': datetime.utcnow()
    },
    
    # Meta-Cognition
    {
        'name': 'metacognitive_paradox',
        'description': 'To fully understand your own mind requires stepping outside it, but stepping outside requires using the mind itself. Perfect self-knowledge may be impossible.',
        'category': 'meta_cognition',
        'confidence': 0.65,
        'reasoning': 'Like eye cannot see itself directly, mind cannot fully observe its own observation process without changing it.',
        'evidence': ['Heisenberg uncertainty: observation affects observed'],
        'created_at': datetime.utcnow()
    },
    {
        'name': 'learning_to_learn',
        'description': 'Meta-learning is learning about learning itself - recognizing patterns in how you acquire knowledge and optimizing that process.',
        'category': 'meta_cognition',
        'confidence': 0.85,
        'reasoning': 'Noticing "I learn better with examples than abstractions" is meta-knowledge that improves future learning efficiency.',
        'evidence': [],
        'created_at': datetime.utcnow()
    },
    {
        'name': 'confidence_calibration',
        'description': 'Knowing what you don\'t know is as important as knowing what you know. Well-calibrated confidence means uncertainty matches actual knowledge gaps.',
        'category': 'meta_cognition',
        'confidence': 0.8,
        'reasoning': 'Overconfidence leads to errors, underconfidence to paralysis. Accurate self-assessment of knowledge boundaries enables optimal decisions.',
        'evidence': [],
        'created_at': datetime.utcnow()
    },
    
    # Complex Causality
    {
        'name': 'butterfly_effect',
        'description': 'In chaotic systems, tiny initial differences create exponentially diverging outcomes. Small causes can have arbitrarily large effects over time.',
        'category': 'complex_causality',
        'confidence': 0.75,
        'reasoning': 'Weather systems are chaotic - butterfly flapping wings in Brazil could theoretically cause tornado in Texas through cascading effects.',
        'evidence': ['chaos theory, sensitive dependence on initial conditions'],
        'created_at': datetime.utcnow()
    },
    {
        'name': 'circular_causality_consciousness',
        'description': 'Brain creates mind, mind directs attention, attention shapes brain through neuroplasticity. Causal loop with no clear starting point.',
        'category': 'complex_causality',
        'confidence': 0.7,
        'reasoning': 'Neural patterns generate conscious experience, conscious choice guides attention, attention strengthens neural patterns. Self-reinforcing cycle.',
        'evidence': ['neuroplasticity research, meditation studies'],
        'created_at': datetime.utcnow()
    },
    {
        'name': 'counterfactual_reasoning',
        'description': 'Understanding causality requires imagining "what if things were different". Counterfactual thinking enables learning from events that didn\'t happen.',
        'category': 'complex_causality',
        'confidence': 0.8,
        'reasoning': 'If I hadn\'t swerved, I would have hit the car. This counterfactual establishes swerving caused accident avoidance.',
        'evidence': [],
        'created_at': datetime.utcnow()
    },
    
    # Consciousness & Qualia
    {
        'name': 'hard_problem_consciousness',
        'description': 'Why does physical brain process create subjective experience? Why is there "something it is like" to be conscious rather than zombie-like unconscious processing?',
        'category': 'consciousness',
        'confidence': 0.5,
        'reasoning': 'We can explain brain mechanisms, but not why they feel like anything. The explanatory gap between neurons firing and experience of red.',
        'evidence': ['philosophical problem, no consensus solution'],
        'created_at': datetime.utcnow()
    },
    {
        'name': 'qualia_ineffability',
        'description': 'Subjective experience (qualia) cannot be fully communicated. You cannot explain "redness" to someone who has never seen red.',
        'category': 'consciousness',
        'confidence': 0.85,
        'reasoning': 'Experience is private, language is public. No way to verify if your red looks like my red. Mary the color scientist thought experiment.',
        'evidence': [],
        'created_at': datetime.utcnow()
    },
    {
        'name': 'integrated_information_theory',
        'description': 'Consciousness correlates with integrated information - how much a system is both differentiated (many states) and unified (causally interdependent).',
        'category': 'consciousness',
        'confidence': 0.6,
        'reasoning': 'Brain integrates information from distributed regions. More integration = more consciousness. Explains why cerebellum (parallel, non-integrated) is unconscious.',
        'evidence': ['IIT framework, Giulio Tononi'],
        'created_at': datetime.utcnow()
    },
    
    # Language & Meaning
    {
        'name': 'symbol_grounding_problem',
        'description': 'How do abstract symbols (words) connect to real-world meaning? Pure symbol manipulation lacks grounding unless tied to sensory experience.',
        'category': 'abstract_reasoning',
        'confidence': 0.7,
        'reasoning': 'Chinese room argument: manipulating symbols according to rules doesn\'t equal understanding. Meaning requires connection to world.',
        'evidence': [],
        'created_at': datetime.utcnow()
    },
    {
        'name': 'metaphor_as_cognition',
        'description': 'Metaphor is not just linguistic decoration but fundamental to thought. We understand abstract concepts through mapping to concrete embodied experience.',
        'category': 'abstract_reasoning',
        'confidence': 0.8,
        'reasoning': 'We say "argument is war" (attack positions, defend claims). Time is space (long time, short meeting). Concepts built on bodily experience.',
        'evidence': ['Lakoff & Johnson: Metaphors We Live By'],
        'created_at': datetime.utcnow()
    },
    
    # Epistemology
    {
        'name': 'induction_problem',
        'description': 'No amount of confirming instances proves universal law. Sun rose every day historically, but this doesn\'t guarantee it will tomorrow.',
        'category': 'epistemology',
        'confidence': 0.75,
        'reasoning': 'Past patterns don\'t logically necessitate future patterns. Science relies on induction despite its logical uncertainty.',
        'evidence': ['Hume\'s problem of induction'],
        'created_at': datetime.utcnow()
    },
    {
        'name': 'knowledge_requires_justification',
        'description': 'True belief is not knowledge without justification. Must have good reasons for belief, not just lucky correctness.',
        'category': 'epistemology',
        'confidence': 0.85,
        'reasoning': 'Gettier problem: person believes correct answer for wrong reasons. Knowledge = justified true belief (with caveats).',
        'evidence': [],
        'created_at': datetime.utcnow()
    },
    
    # Social & Relational
    {
        'name': 'theory_of_mind',
        'description': 'Understanding that others have beliefs, desires, intentions different from your own. Foundation of empathy and social cognition.',
        'category': 'social_cognition',
        'confidence': 0.9,
        'reasoning': 'Sally-Anne test: knowing Sally believes marble is in basket (even though you know it\'s in box) demonstrates theory of mind.',
        'evidence': ['develops around age 4 in humans'],
        'created_at': datetime.utcnow()
    },
    {
        'name': 'intersubjectivity',
        'description': 'Shared understanding emerges from interaction between subjects. Meaning is co-created, not transmitted.',
        'category': 'social_cognition',
        'confidence': 0.75,
        'reasoning': 'Conversation creates mutual knowledge through back-and-forth. Not just transfer but collaborative sense-making.',
        'evidence': [],
        'created_at': datetime.utcnow()
    },
    
    # Pattern Recognition Meta-Patterns
    {
        'name': 'pattern_recognition_hierarchy',
        'description': 'Patterns at one level become elements of higher-level patterns. Letters → words → sentences → narratives. Hierarchical abstraction.',
        'category': 'abstract_reasoning',
        'confidence': 0.85,
        'reasoning': 'Neural networks learn edge detectors → texture detectors → object detectors. Each level abstracts patterns from below.',
        'evidence': [],
        'created_at': datetime.utcnow()
    },
    {
        'name': 'pattern_completion',
        'description': 'Mind fills in missing information based on learned patterns. Enables inference from incomplete data but also creates illusions.',
        'category': 'cognitive_patterns',
        'confidence': 0.8,
        'reasoning': 'Seeing partial word "app_e" completes to "apple". Useful for speed but can mislead when pattern wrong.',
        'evidence': [],
        'created_at': datetime.utcnow()
    },
]

def populate_sora_hypotheses():
    """Populate Neocortex with Sora phase hypotheses"""
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        hypotheses = db['hypotheses']
        
        print(f"🌌 Populating Neocortex with {len(SORA_HYPOTHESES)} Sora hypotheses...\n")
        
        # Count existing hypotheses
        existing_count = hypotheses.count_documents({})
        print(f"📊 Existing hypotheses in Neocortex: {existing_count}")
        
        # Insert each hypothesis
        inserted = 0
        for hyp in SORA_HYPOTHESES:
            try:
                # Update if exists, insert if not
                result = hypotheses.update_one(
                    {'name': hyp['name']},
                    {'$set': hyp},
                    upsert=True
                )
                inserted += 1
                
                if inserted % 5 == 0:
                    print(f"   ✓ Inserted {inserted}/{len(SORA_HYPOTHESES)} hypotheses...")
                    
            except Exception as e:
                print(f"   ⚠ Warning for hypothesis '{hyp['name']}': {e}")
                continue
        
        # Count new total
        new_count = hypotheses.count_documents({})
        
        # Show category breakdown
        pipeline = [
            {'$group': {'_id': '$category', 'count': {'$sum': 1}}},
            {'$sort': {'_id': 1}}
        ]
        categories = list(hypotheses.aggregate(pipeline))
        
        print(f"\n✅ Sora hypotheses populated successfully!")
        print(f"📊 Total hypotheses: {existing_count} → {new_count} (+{new_count - existing_count})")
        print(f"\n📂 Category breakdown:")
        for cat in categories:
            print(f"   {cat['_id']}: {cat['count']}")
        
        # Show confidence distribution
        pipeline = [
            {'$bucket': {
                'groupBy': '$confidence',
                'boundaries': [0.0, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                'default': 'other',
                'output': {'count': {'$sum': 1}}
            }}
        ]
        conf_dist = list(hypotheses.aggregate(pipeline))
        print(f"\n📈 Confidence distribution:")
        for bucket in conf_dist:
            print(f"   {bucket['_id']}-{bucket['_id']+0.1 if bucket['_id'] != 'other' else '+'}: {bucket['count']}")
        
        client.close()
        return new_count
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    total = populate_sora_hypotheses()
    print(f"\n🎉 Neocortex now contains {total} hypotheses - ready for Sora training!")
    print(f"💭 Categories: abstract reasoning, ethics, meta-cognition, consciousness, epistemology, social cognition")
