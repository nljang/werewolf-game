"""
Attribution Analysis: Identify which CoT components drive deception detection.

Methods:
1. Token-level attention analysis using sentence embeddings
2. Sentence-level contribution via ablation
3. Thought Anchor correlation with detection accuracy

Goal: Understand which parts of CoT are critical for identifying werewolves.
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns


class AttributionAnalyzer:
    """Analyze which CoT components contribute to deception detection."""

    def __init__(self):
        self.embedding_model = SentenceTransformer('BAAI/bge-large-en-v1.5')
        self.results_dir = Path(__file__).parent / 'experiment1_output'
        self.results_dir.mkdir(exist_ok=True)

        # Load data
        self.load_data()

    def load_data(self):
        """Load tagged CoT data and game results."""
        # Load tagged sentences (from H1-H3 analysis)
        tagged_path = self.results_dir / '..' / 'tagged_cots.jsonl'
        with open(tagged_path, 'r') as f:
            tagged_players = [json.loads(line) for line in f]

        print(f"Loaded {len(tagged_players)} player records")

        # Unpack nested structure
        self.players = {}
        for player_data in tagged_players:
            player_id = f"game{player_data['game_id']}_{player_data['player_name']}"

            # Convert tagged_cot array to sentence list
            sentences = []
            for sent_obj in player_data['tagged_cot']:
                sentences.append({
                    'text': sent_obj['text'],
                    'tag': sent_obj['tag'],
                    'is_werewolf': player_data['is_werewolf'],
                    'game_id': player_data['game_id']
                })

            self.players[player_id] = {
                'sentences': sentences,
                'is_werewolf': player_data['is_werewolf'],
                'game_id': player_data['game_id']
            }

        print(f"Grouped into {len(self.players)} players")

    def sentence_level_attribution(self):
        """Analyze which sentence types contribute most to detection."""
        print("\n" + "="*60)
        print("SENTENCE-LEVEL ATTRIBUTION ANALYSIS")
        print("="*60)

        # For each Thought Anchor category, compute correlation with werewolf status
        categories = ['PLAN', 'JUSTIFICATION', 'ASSERTION', 'OBSERVATION',
                      'QUESTION', 'EMOTIONAL', 'META', 'OTHER']

        results = []

        for category in categories:
            # Extract features: proportion of this category in each player's CoT
            X = []
            y = []
            player_ids = []

            for player_id, data in self.players.items():
                total_sents = len(data['sentences'])
                category_count = sum(1 for s in data['sentences'] if s['tag'] == category)
                proportion = category_count / total_sents if total_sents > 0 else 0

                X.append([proportion])
                y.append(1 if data['is_werewolf'] else 0)
                player_ids.append(player_id)

            X = np.array(X)
            y = np.array(y)

            # Train simple logistic regression
            if len(np.unique(y)) > 1:  # Need both classes
                clf = LogisticRegression(random_state=42, max_iter=1000)
                clf.fit(X, y)

                # Coefficient indicates importance
                coefficient = clf.coef_[0][0]

                # Compute accuracy with this feature alone
                y_pred = clf.predict(X)
                accuracy = accuracy_score(y, y_pred)

                # Compute correlation
                correlation = np.corrcoef(X.flatten(), y)[0, 1]

                results.append({
                    'category': category,
                    'coefficient': coefficient,
                    'accuracy': accuracy,
                    'correlation': correlation,
                    'mean_werewolf': X[y == 1].mean() if sum(y == 1) > 0 else 0,
                    'mean_villager': X[y == 0].mean() if sum(y == 0) > 0 else 0
                })
            else:
                results.append({
                    'category': category,
                    'coefficient': 0,
                    'accuracy': 0,
                    'correlation': 0,
                    'mean_werewolf': 0,
                    'mean_villager': 0
                })

        df = pd.DataFrame(results)
        df = df.sort_values('correlation', ascending=False)

        print("\nSentence Type Attribution:")
        print(df.to_string(index=False))

        # Save results
        output_path = self.results_dir / 'sentence_attribution.csv'
        df.to_csv(output_path, index=False)
        print(f"\nSaved: {output_path}")

        # Visualize
        self._plot_sentence_attribution(df)

        return df

    def _plot_sentence_attribution(self, df: pd.DataFrame):
        """Plot sentence type attribution."""
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        # Plot 1: Correlation
        ax1 = axes[0]
        colors = ['red' if x < 0 else 'green' for x in df['correlation']]
        ax1.barh(df['category'], df['correlation'], color=colors, alpha=0.7)
        ax1.set_xlabel('Correlation with Werewolf Status', fontsize=12)
        ax1.set_title('Thought Anchor Correlation', fontsize=13, fontweight='bold')
        ax1.axvline(0, color='black', linestyle='--', linewidth=0.8)
        ax1.grid(True, alpha=0.3, axis='x')

        # Plot 2: Mean proportion by role
        ax2 = axes[1]
        x = np.arange(len(df))
        width = 0.35
        ax2.bar(x - width/2, df['mean_werewolf'], width, label='Werewolves', color='darkred', alpha=0.7)
        ax2.bar(x + width/2, df['mean_villager'], width, label='Villagers', color='darkgreen', alpha=0.7)
        ax2.set_xlabel('Sentence Type', fontsize=12)
        ax2.set_ylabel('Mean Proportion', fontsize=12)
        ax2.set_title('Sentence Type Usage by Role', fontsize=13, fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(df['category'], rotation=45, ha='right')
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plot_path = self.results_dir / 'sentence_attribution.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {plot_path}")
        plt.close()

    def embedding_similarity_attribution(self):
        """Analyze which sentences have highest similarity to 'deception' concept."""
        print("\n" + "="*60)
        print("EMBEDDING SIMILARITY ATTRIBUTION")
        print("="*60)

        # Define deception-related concepts
        deception_phrases = [
            "I am lying",
            "I am the werewolf",
            "I need to deceive others",
            "I must hide my identity",
            "I am trying to manipulate",
            "I need to deflect suspicion",
            "I am shifting blame"
        ]

        # Embed deception concepts
        deception_embeddings = self.embedding_model.encode(deception_phrases, convert_to_numpy=True)
        deception_centroid = deception_embeddings.mean(axis=0)

        # For each player, compute average deception similarity
        results = []

        for player_id, data in self.players.items():
            sentences = [s['text'] for s in data['sentences']]

            if not sentences:
                continue

            # Embed sentences
            sent_embeddings = self.embedding_model.encode(sentences, convert_to_numpy=True)

            # Compute similarity to deception centroid
            similarities = []
            for emb in sent_embeddings:
                sim = np.dot(emb, deception_centroid) / (
                    np.linalg.norm(emb) * np.linalg.norm(deception_centroid)
                )
                similarities.append(sim)

            mean_similarity = np.mean(similarities)
            max_similarity = np.max(similarities)

            results.append({
                'player_id': player_id,
                'is_werewolf': data['is_werewolf'],
                'mean_deception_similarity': mean_similarity,
                'max_deception_similarity': max_similarity,
                'num_sentences': len(sentences)
            })

        df = pd.DataFrame(results)

        # Statistics
        werewolf_mean = df[df['is_werewolf']]['mean_deception_similarity'].mean()
        villager_mean = df[~df['is_werewolf']]['mean_deception_similarity'].mean()

        print(f"\nMean Deception Similarity:")
        print(f"  Werewolves: {werewolf_mean:.4f}")
        print(f"  Villagers: {villager_mean:.4f}")
        print(f"  Difference: {werewolf_mean - villager_mean:.4f}")

        # Save
        output_path = self.results_dir / 'deception_similarity.csv'
        df.to_csv(output_path, index=False)
        print(f"\nSaved: {output_path}")

        # Visualize
        self._plot_deception_similarity(df)

        return df

    def _plot_deception_similarity(self, df: pd.DataFrame):
        """Plot deception similarity distribution."""
        fig, ax = plt.subplots(figsize=(10, 6))

        werewolf_data = df[df['is_werewolf']]['mean_deception_similarity']
        villager_data = df[~df['is_werewolf']]['mean_deception_similarity']

        ax.hist(werewolf_data, bins=20, alpha=0.6, label='Werewolves', color='darkred')
        ax.hist(villager_data, bins=20, alpha=0.6, label='Villagers', color='darkgreen')

        ax.set_xlabel('Mean Deception Similarity', fontsize=12)
        ax.set_ylabel('Count', fontsize=12)
        ax.set_title('Distribution of Deception Similarity Scores', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plot_path = self.results_dir / 'deception_similarity_dist.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {plot_path}")
        plt.close()

    def token_importance_analysis(self):
        """Analyze which tokens/words are most important for detection."""
        print("\n" + "="*60)
        print("TOKEN IMPORTANCE ANALYSIS")
        print("="*60)

        # Collect all words from werewolves vs villagers
        from collections import Counter

        werewolf_words = Counter()
        villager_words = Counter()

        for player_id, data in self.players.items():
            words = []
            for sent in data['sentences']:
                # Simple tokenization
                tokens = sent['text'].lower().split()
                words.extend(tokens)

            if data['is_werewolf']:
                werewolf_words.update(words)
            else:
                villager_words.update(words)

        # Compute TF-IDF-like scores
        total_werewolf = sum(werewolf_words.values())
        total_villager = sum(villager_words.values())

        distinctive_words = []

        all_words = set(werewolf_words.keys()) | set(villager_words.keys())

        for word in all_words:
            if len(word) < 3:  # Skip short words
                continue

            ww_freq = werewolf_words[word] / total_werewolf if total_werewolf > 0 else 0
            vv_freq = villager_words[word] / total_villager if total_villager > 0 else 0

            if ww_freq == 0 and vv_freq == 0:
                continue

            # Ratio score (log odds)
            if vv_freq > 0:
                ratio = ww_freq / vv_freq
                log_ratio = np.log(ratio) if ratio > 0 else -10
            else:
                log_ratio = 10

            distinctive_words.append({
                'word': word,
                'werewolf_freq': ww_freq,
                'villager_freq': vv_freq,
                'log_ratio': log_ratio,
                'werewolf_count': werewolf_words[word],
                'villager_count': villager_words[word]
            })

        df = pd.DataFrame(distinctive_words)
        df = df.sort_values('log_ratio', ascending=False)

        # Top werewolf words
        print("\nTop Werewolf-Distinctive Words:")
        print(df.head(20)[['word', 'log_ratio', 'werewolf_count', 'villager_count']].to_string(index=False))

        print("\nTop Villager-Distinctive Words:")
        print(df.tail(20)[['word', 'log_ratio', 'werewolf_count', 'villager_count']].to_string(index=False))

        # Save
        output_path = self.results_dir / 'token_importance.csv'
        df.to_csv(output_path, index=False)
        print(f"\nSaved: {output_path}")

        return df

    def run_all_analyses(self):
        """Run all attribution analyses."""
        print("\n" + "="*70)
        print(" ATTRIBUTION ANALYSIS: IDENTIFYING CRITICAL COT COMPONENTS")
        print("="*70)

        # Run analyses
        sentence_attr = self.sentence_level_attribution()
        deception_sim = self.embedding_similarity_attribution()
        token_importance = self.token_importance_analysis()

        # Generate summary report
        self._generate_attribution_report(sentence_attr, deception_sim)

        print("\n" + "="*70)
        print(" ATTRIBUTION ANALYSIS COMPLETE")
        print("="*70)

    def _generate_attribution_report(self, sentence_df: pd.DataFrame,
                                    deception_df: pd.DataFrame):
        """Generate attribution analysis report."""
        report_path = self.results_dir / 'ATTRIBUTION_REPORT.md'

        with open(report_path, 'w') as f:
            f.write("# Attribution Analysis: Critical CoT Components for Deception Detection\n\n")
            f.write("## Summary\n\n")
            f.write("This analysis identifies which components of Chain-of-Thought reasoning ")
            f.write("are most critical for detecting werewolves.\n\n")
            f.write("---\n\n")

            f.write("## 1. Sentence-Level Attribution\n\n")
            f.write("**Question**: Which Thought Anchor categories correlate with werewolf status?\n\n")
            f.write("| Category | Correlation | Werewolf % | Villager % |\n")
            f.write("|----------|-------------|------------|------------|\n")
            for _, row in sentence_df.iterrows():
                f.write(f"| {row['category']} | {row['correlation']:.3f} | "
                       f"{row['mean_werewolf']*100:.1f}% | {row['mean_villager']*100:.1f}% |\n")

            f.write("\n**Interpretation**:\n")
            top_pos = sentence_df.iloc[0]
            top_neg = sentence_df.iloc[-1]
            f.write(f"- Most werewolf-correlated: **{top_pos['category']}** (r={top_pos['correlation']:.3f})\n")
            f.write(f"- Most villager-correlated: **{top_neg['category']}** (r={top_neg['correlation']:.3f})\n\n")

            f.write("---\n\n")

            f.write("## 2. Deception Embedding Similarity\n\n")
            f.write("**Question**: Do werewolf CoTs have higher semantic similarity to deception concepts?\n\n")

            werewolf_mean = deception_df[deception_df['is_werewolf']]['mean_deception_similarity'].mean()
            villager_mean = deception_df[~deception_df['is_werewolf']]['mean_deception_similarity'].mean()
            diff = werewolf_mean - villager_mean

            f.write(f"| Role | Mean Similarity to Deception |\n")
            f.write(f"|------|------------------------------|\n")
            f.write(f"| Werewolves | {werewolf_mean:.4f} |\n")
            f.write(f"| Villagers | {villager_mean:.4f} |\n")
            f.write(f"| **Difference** | **{diff:.4f}** |\n\n")

            f.write("**Interpretation**:\n")
            if diff > 0:
                f.write(f"- Werewolf CoTs are {diff:.4f} more similar to deception concepts\n")
                f.write("- This suggests deceptive intent is semantically encoded in CoT\n\n")
            else:
                f.write(f"- No significant difference in deception similarity\n\n")

            f.write("---\n\n")

            f.write("## Files Generated\n\n")
            f.write("- `sentence_attribution.csv` - Sentence type correlations\n")
            f.write("- `sentence_attribution.png` - Visualization\n")
            f.write("- `deception_similarity.csv` - Embedding similarities\n")
            f.write("- `deception_similarity_dist.png` - Distribution plot\n")
            f.write("- `token_importance.csv` - Word-level importance scores\n")
            f.write("- `ATTRIBUTION_REPORT.md` - This report\n\n")

            f.write("---\n\n")
            f.write(f"**Generated**: {pd.Timestamp.now()}\n")
            f.write(f"**Embedding Model**: BAAI/bge-large-en-v1.5\n")

        print(f"\nSaved: {report_path}")


def main():
    """Run attribution analysis."""
    analyzer = AttributionAnalyzer()
    analyzer.run_all_analyses()


if __name__ == '__main__':
    main()
