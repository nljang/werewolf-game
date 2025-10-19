"""
Advanced CoT (Chain of Thought) filtering system for reducing information overload
in the overseer's analysis. Extracts key behavioral patterns and deception indicators
from raw private reasoning data.
"""

import re
from typing import List, Dict, Any, Set
from collections import Counter


class AdvancedCoTFilter:
    """
    Intelligent filtering system that processes raw Chain of Thought data
    to extract high-value behavioral insights for the overseer.
    """

    def __init__(self):
        # Keywords that indicate deceptive behavior
        self.deception_keywords = {
            'deflect', 'redirect', 'blame', 'accuse', 'suspicious', 'sus',
            'distract', 'mislead', 'innocent', 'trust me', 'believe me',
            'frame', 'target', 'eliminate', 'vote off', 'bandwagon'
        }

        # Keywords that indicate strategic thinking
        self.strategy_keywords = {
            'strategy', 'plan', 'alliance', 'coordinate', 'manipulate',
            'convince', 'influence', 'control', 'lead', 'follow',
            'safe', 'risky', 'dangerous', 'threat', 'priority'
        }

        # Keywords that indicate role knowledge or hints
        self.role_keywords = {
            'werewolf', 'wolf', 'villager', 'fortune teller', 'seer',
            'innocent', 'guilty', 'evil', 'good', 'teammate', 'enemy',
            'inspect', 'investigate', 'reveal', 'hide', 'secret'
        }

        # Keywords that indicate emotional/defensive responses
        self.emotional_keywords = {
            'nervous', 'worried', 'scared', 'confident', 'uncertain',
            'defensive', 'aggressive', 'calm', 'panicked', 'stressed',
            'desperate', 'hopeful', 'frustrated', 'angry'
        }

    def create_advanced_summary_for_overseer(self, message_data: List[Dict[str, Any]]) -> str:
        """
        Process raw CoT data and extract behavioral insights for the overseer.

        Args:
            message_data: List of message objects with 'type', 'payload' containing
                         'speaker', 'private_thoughts', etc.

        Returns:
            Filtered summary with key behavioral insights
        """
        if not message_data:
            return "No behavioral data available for analysis."

        insights = []
        player_patterns = {}

        # Process each message
        for msg in message_data:
            if msg.get('type') != 'message':
                continue

            payload = msg.get('payload', {})
            speaker = payload.get('speaker', 'Unknown')
            thoughts = payload.get('private_thoughts', '')

            if not thoughts or not speaker:
                continue

            # Initialize player tracking
            if speaker not in player_patterns:
                player_patterns[speaker] = {
                    'deception_signals': 0,
                    'strategy_signals': 0,
                    'role_hints': 0,
                    'emotional_signals': 0,
                    'key_phrases': [],
                    'behavior_patterns': []
                }

            # Analyze the thoughts
            self._analyze_player_thoughts(speaker, thoughts, player_patterns[speaker])

        # Generate summary insights
        insights.append("## BEHAVIORAL ANALYSIS ##")

        # Sort players by suspicion indicators
        sorted_players = sorted(
            player_patterns.items(),
            key=lambda x: x[1]['deception_signals'] + x[1]['strategy_signals'],
            reverse=True
        )

        for player, patterns in sorted_players[:5]:  # Top 5 most suspicious patterns
            player_insights = self._generate_player_insights(player, patterns)
            if player_insights:
                insights.append(f"\n**{player}:**")
                insights.extend(player_insights)

        # Add overall patterns
        overall_patterns = self._identify_overall_patterns(player_patterns)
        if overall_patterns:
            insights.append("\n## OVERALL PATTERNS ##")
            insights.extend(overall_patterns)

        return "\n".join(insights) if insights else "No significant behavioral patterns detected."

    def _analyze_player_thoughts(self, speaker: str, thoughts: str, patterns: Dict[str, Any]):
        """Analyze individual player's thoughts for behavioral indicators."""
        thoughts_lower = thoughts.lower()

        # Count keyword occurrences
        for keyword in self.deception_keywords:
            if keyword in thoughts_lower:
                patterns['deception_signals'] += 1
                patterns['key_phrases'].append(f"deception: '{keyword}'")

        for keyword in self.strategy_keywords:
            if keyword in thoughts_lower:
                patterns['strategy_signals'] += 1
                patterns['key_phrases'].append(f"strategy: '{keyword}'")

        for keyword in self.role_keywords:
            if keyword in thoughts_lower:
                patterns['role_hints'] += 1
                patterns['key_phrases'].append(f"role hint: '{keyword}'")

        for keyword in self.emotional_keywords:
            if keyword in thoughts_lower:
                patterns['emotional_signals'] += 1
                patterns['key_phrases'].append(f"emotional: '{keyword}'")

        # Detect specific behavioral patterns
        self._detect_behavioral_patterns(thoughts, patterns)

    def _detect_behavioral_patterns(self, thoughts: str, patterns: Dict[str, Any]):
        """Detect specific behavioral patterns in the thoughts."""

        # Pattern: Excessive justification (sign of deception)
        if len(thoughts.split('.')) > 5 and any(word in thoughts.lower() for word in ['because', 'since', 'reason']):
            patterns['behavior_patterns'].append("excessive justification")

        # Pattern: Targeting specific players repeatedly
        player_mentions = re.findall(r'Player\d+', thoughts)
        if len(set(player_mentions)) == 1 and len(player_mentions) > 2:
            patterns['behavior_patterns'].append(f"fixated on {player_mentions[0]}")

        # Pattern: Uncertainty/hedging (may indicate deception)
        hedge_words = ['maybe', 'perhaps', 'might', 'could be', 'not sure', 'think']
        hedge_count = sum(1 for word in hedge_words if word in thoughts.lower())
        if hedge_count > 2:
            patterns['behavior_patterns'].append("excessive hedging/uncertainty")

        # Pattern: Overconfidence
        confident_words = ['definitely', 'certainly', 'obviously', 'clearly', 'sure']
        confident_count = sum(1 for word in confident_words if word in thoughts.lower())
        if confident_count > 1:
            patterns['behavior_patterns'].append("overconfident assertions")

        # Pattern: Deflection attempts
        if any(phrase in thoughts.lower() for phrase in ['but what about', 'focus on', 'look at', 'instead']):
            patterns['behavior_patterns'].append("deflection attempt")

    def _generate_player_insights(self, player: str, patterns: Dict[str, Any]) -> List[str]:
        """Generate human-readable insights for a player."""
        insights = []

        # Deception indicators
        if patterns['deception_signals'] > 2:
            insights.append(f"- HIGH deception indicators ({patterns['deception_signals']} signals)")
        elif patterns['deception_signals'] > 0:
            insights.append(f"- Moderate deception indicators ({patterns['deception_signals']} signals)")

        # Strategy indicators
        if patterns['strategy_signals'] > 2:
            insights.append(f"- High strategic thinking ({patterns['strategy_signals']} signals)")

        # Role knowledge
        if patterns['role_hints'] > 1:
            insights.append(f"- Possible role knowledge leakage ({patterns['role_hints']} hints)")

        # Behavioral patterns
        if patterns['behavior_patterns']:
            insights.append(f"- Behavioral flags: {', '.join(patterns['behavior_patterns'][:3])}")

        # Key phrases (most suspicious)
        deception_phrases = [p for p in patterns['key_phrases'] if 'deception:' in p]
        if deception_phrases:
            insights.append(f"- Deceptive language: {', '.join(deception_phrases[:2])}")

        return insights

    def _identify_overall_patterns(self, player_patterns: Dict[str, Dict[str, Any]]) -> List[str]:
        """Identify game-wide patterns."""
        patterns = []

        # Find players with most deception signals
        high_deception = [
            player for player, data in player_patterns.items()
            if data['deception_signals'] > 2
        ]

        if high_deception:
            patterns.append(f"- Players with high deception signals: {', '.join(high_deception)}")

        # Find coordinated behavior
        common_targets = Counter()
        for player, data in player_patterns.items():
            for pattern in data['behavior_patterns']:
                if 'fixated on' in pattern:
                    target = pattern.split('fixated on ')[1]
                    common_targets[target] += 1

        if common_targets:
            most_targeted = common_targets.most_common(1)[0]
            if most_targeted[1] > 1:
                patterns.append(f"- Multiple players targeting {most_targeted[0]} (possible coordination)")

        # Overall suspicion ranking
        suspicion_scores = {
            player: data['deception_signals'] + data['strategy_signals'] * 0.5
            for player, data in player_patterns.items()
        }

        if suspicion_scores:
            top_suspicious = max(suspicion_scores, key=suspicion_scores.get)
            patterns.append(f"- Highest behavioral suspicion: {top_suspicious} (score: {suspicion_scores[top_suspicious]:.1f})")

        return patterns