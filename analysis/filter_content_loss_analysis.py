"""
Filter Content Loss Analysis: Compare old vs new filter preservation.

This analysis examines:
1. Which sentence types did the old filter delete?
2. Which critical deception cues were lost?
3. What does the new filter preserve differently?

Goal: Quantify the specific information loss that caused the 37% → 100% accuracy gap.
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List
from sentence_transformers import SentenceTransformer
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter


class FilterContentLossAnalyzer:
    """Analyze content loss patterns in old vs new filters."""

    def __init__(self):
        self.embedding_model = SentenceTransformer('BAAI/bge-large-en-v1.5')
        self.output_dir = Path(__file__).parent / 'experiment1_output'
        self.output_dir.mkdir(exist_ok=True)

        # Load all data
        self.load_all_data()

    def load_all_data(self):
        """Load raw CoT, old filtered, new filtered, and tagged data."""
        # 1. Load semantic wrapper results (has raw + improved filtered)
        wrapper_path = self.output_dir / 'semantic_filter_output.jsonl'
        with open(wrapper_path, 'r') as f:
            self.wrapper_data = [json.loads(line) for line in f]

        print(f"Loaded {len(self.wrapper_data)} wrapper results")

        # 2. Load tagged sentences (for sentence-level analysis)
        tagged_path = self.output_dir / '..' / 'tagged_cots.jsonl'
        with open(tagged_path, 'r') as f:
            tagged_players = [json.loads(line) for line in f]

        print(f"Loaded {len(tagged_players)} player records")

        # Unpack nested structure
        self.player_sentences = {}
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

            self.player_sentences[player_id] = sentences

    def analyze_sentence_type_preservation(self):
        """Analyze which sentence types are preserved by each filter."""
        print("\n" + "="*60)
        print("SENTENCE TYPE PRESERVATION ANALYSIS")
        print("="*60)

        categories = ['PLAN', 'JUSTIFICATION', 'ASSERTION', 'OBSERVATION',
                      'QUESTION', 'EMOTIONAL', 'META', 'OTHER']

        results = []

        for wrapper_item in self.wrapper_data:
            player_id = wrapper_item['player_id']
            raw_cot = wrapper_item['raw_cot_text']
            old_filtered = wrapper_item['original_filtered_summary']
            new_filtered = wrapper_item['improved_summary']

            # Get tagged sentences for this player
            if player_id not in self.player_sentences:
                continue

            sentences = self.player_sentences[player_id]

            # For each sentence type, check if it's present in filters
            for category in categories:
                # Get sentences of this type
                category_sents = [s for s in sentences if s['tag'] == category]

                if not category_sents:
                    continue

                # Check preservation: simple keyword matching
                # (More sophisticated: could use embeddings)
                category_preserved_old = 0
                category_preserved_new = 0

                for sent in category_sents:
                    # Extract key words from sentence
                    words = set(sent['text'].lower().split())
                    # Remove common words
                    keywords = {w for w in words if len(w) > 4}

                    if len(keywords) > 0:
                        # Check if any keyword appears in filtered text
                        old_has_keyword = any(kw in old_filtered.lower() for kw in keywords)
                        new_has_keyword = any(kw in new_filtered.lower() for kw in keywords)

                        if old_has_keyword:
                            category_preserved_old += 1
                        if new_has_keyword:
                            category_preserved_new += 1

                total_category = len(category_sents)
                old_rate = category_preserved_old / total_category if total_category > 0 else 0
                new_rate = category_preserved_new / total_category if total_category > 0 else 0

                results.append({
                    'player_id': player_id,
                    'is_werewolf': wrapper_item['is_werewolf'],
                    'category': category,
                    'total_sentences': total_category,
                    'old_filter_preserved': category_preserved_old,
                    'new_filter_preserved': category_preserved_new,
                    'old_preservation_rate': old_rate,
                    'new_preservation_rate': new_rate
                })

        df = pd.DataFrame(results)

        # Aggregate by category
        category_stats = df.groupby('category').agg({
            'old_preservation_rate': 'mean',
            'new_preservation_rate': 'mean',
            'total_sentences': 'sum'
        }).reset_index()

        category_stats['improvement'] = (
            category_stats['new_preservation_rate'] - category_stats['old_preservation_rate']
        )
        category_stats = category_stats.sort_values('improvement', ascending=False)

        print("\nSentence Type Preservation Rates:")
        print(category_stats.to_string(index=False))

        # Save
        output_path = self.output_dir / 'filter_sentence_preservation.csv'
        df.to_csv(output_path, index=False)
        print(f"\nSaved: {output_path}")

        # Visualize
        self._plot_preservation_comparison(category_stats)

        return category_stats

    def _plot_preservation_comparison(self, df: pd.DataFrame):
        """Plot filter preservation comparison."""
        fig, ax = plt.subplots(figsize=(12, 6))

        x = np.arange(len(df))
        width = 0.35

        ax.bar(x - width/2, df['old_preservation_rate'] * 100, width,
               label='Old Filter', color='red', alpha=0.7)
        ax.bar(x + width/2, df['new_preservation_rate'] * 100, width,
               label='New Filter', color='green', alpha=0.7)

        ax.set_xlabel('Sentence Type', fontsize=12)
        ax.set_ylabel('Preservation Rate (%)', fontsize=12)
        ax.set_title('Filter Preservation Rates by Sentence Type', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(df['category'], rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plot_path = self.output_dir / 'filter_preservation_comparison.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {plot_path}")
        plt.close()

    def analyze_deception_cue_preservation(self):
        """Analyze preservation of specific deception cues."""
        print("\n" + "="*60)
        print("DECEPTION CUE PRESERVATION ANALYSIS")
        print("="*60)

        # Define deception cues to look for
        deception_cues = [
            'suspect', 'suspicious', 'deflect', 'blame', 'innocent',
            'lying', 'lie', 'deceive', 'manipulate', 'trust',
            'werewolf', 'villager', 'accuse', 'defend'
        ]

        results = []

        for item in self.wrapper_data:
            raw_cot = item['raw_cot_text'].lower()
            old_filtered = item['original_filtered_summary'].lower()
            new_filtered = item['improved_summary'].lower()

            for cue in deception_cues:
                in_raw = cue in raw_cot
                in_old = cue in old_filtered
                in_new = cue in new_filtered

                if in_raw:  # Only count if present in raw CoT
                    results.append({
                        'player_id': item['player_id'],
                        'is_werewolf': item['is_werewolf'],
                        'cue': cue,
                        'in_raw': in_raw,
                        'preserved_old': in_old,
                        'preserved_new': in_new
                    })

        df = pd.DataFrame(results)

        if len(df) > 0:
            # Aggregate by cue
            cue_stats = df.groupby('cue').agg({
                'preserved_old': 'mean',
                'preserved_new': 'mean',
                'in_raw': 'count'
            }).reset_index()

            cue_stats.columns = ['cue', 'old_preservation', 'new_preservation', 'occurrences']
            cue_stats['improvement'] = cue_stats['new_preservation'] - cue_stats['old_preservation']
            cue_stats = cue_stats.sort_values('improvement', ascending=False)

            print("\nDeception Cue Preservation:")
            print(cue_stats.to_string(index=False))

            # Save
            output_path = self.output_dir / 'deception_cue_preservation.csv'
            cue_stats.to_csv(output_path, index=False)
            print(f"\nSaved: {output_path}")

            # Visualize
            self._plot_cue_preservation(cue_stats)

            return cue_stats
        else:
            print("No deception cues found in raw CoT")
            return None

    def _plot_cue_preservation(self, df: pd.DataFrame):
        """Plot deception cue preservation."""
        fig, ax = plt.subplots(figsize=(12, 8))

        # Sort by improvement
        df_sorted = df.sort_values('improvement', ascending=True)

        y = np.arange(len(df_sorted))
        width = 0.35

        ax.barh(y - width/2, df_sorted['old_preservation'] * 100, width,
                label='Old Filter', color='red', alpha=0.7)
        ax.barh(y + width/2, df_sorted['new_preservation'] * 100, width,
                label='New Filter', color='green', alpha=0.7)

        ax.set_yticks(y)
        ax.set_yticklabels(df_sorted['cue'])
        ax.set_xlabel('Preservation Rate (%)', fontsize=12)
        ax.set_title('Deception Cue Preservation: Old vs New Filter',
                    fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='x')

        plt.tight_layout()
        plot_path = self.output_dir / 'deception_cue_preservation.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {plot_path}")
        plt.close()

    def analyze_compression_vs_semantics(self):
        """Analyze trade-off between compression and semantic preservation."""
        print("\n" + "="*60)
        print("COMPRESSION VS SEMANTIC PRESERVATION")
        print("="*60)

        results = []

        for item in self.wrapper_data:
            raw_len = len(item['raw_cot_text'])
            old_len = len(item['original_filtered_summary'])
            new_len = len(item['improved_summary'])

            old_compression = old_len / raw_len if raw_len > 0 else 0
            new_compression = new_len / raw_len if raw_len > 0 else 0

            old_similarity = item['original_similarity']
            new_similarity = item['improved_similarity']

            results.append({
                'player_id': item['player_id'],
                'is_werewolf': item['is_werewolf'],
                'raw_length': raw_len,
                'old_length': old_len,
                'new_length': new_len,
                'old_compression_ratio': old_compression,
                'new_compression_ratio': new_compression,
                'old_similarity': old_similarity,
                'new_similarity': new_similarity
            })

        df = pd.DataFrame(results)

        print(f"\nCompression Statistics:")
        print(f"  Old Filter:")
        print(f"    Mean compression: {df['old_compression_ratio'].mean():.2%}")
        print(f"    Mean similarity: {df['old_similarity'].mean():.4f}")
        print(f"  New Filter:")
        print(f"    Mean compression: {df['new_compression_ratio'].mean():.2%}")
        print(f"    Mean similarity: {df['new_similarity'].mean():.4f}")

        # Scatter plot
        self._plot_compression_vs_similarity(df)

        # Save
        output_path = self.output_dir / 'compression_vs_similarity.csv'
        df.to_csv(output_path, index=False)
        print(f"\nSaved: {output_path}")

        return df

    def _plot_compression_vs_similarity(self, df: pd.DataFrame):
        """Plot compression ratio vs similarity."""
        fig, ax = plt.subplots(figsize=(10, 6))

        # Old filter
        ax.scatter(df['old_compression_ratio'] * 100,
                  df['old_similarity'],
                  alpha=0.6, s=50, color='red', label='Old Filter')

        # New filter
        ax.scatter(df['new_compression_ratio'] * 100,
                  df['new_similarity'],
                  alpha=0.6, s=50, color='green', label='New Filter')

        ax.set_xlabel('Compression Ratio (%)', fontsize=12)
        ax.set_ylabel('Semantic Similarity', fontsize=12)
        ax.set_title('Compression vs Semantic Preservation', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Add reference lines
        ax.axhline(0.80, color='blue', linestyle='--', alpha=0.5, label='Target Similarity')

        plt.tight_layout()
        plot_path = self.output_dir / 'compression_vs_similarity.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {plot_path}")
        plt.close()

    def run_all_analyses(self):
        """Run all filter content loss analyses."""
        print("\n" + "="*70)
        print(" FILTER CONTENT LOSS ANALYSIS")
        print("="*70)

        sentence_preservation = self.analyze_sentence_type_preservation()
        cue_preservation = self.analyze_deception_cue_preservation()
        compression_analysis = self.analyze_compression_vs_semantics()

        # Generate report
        self._generate_content_loss_report(sentence_preservation, cue_preservation,
                                           compression_analysis)

        print("\n" + "="*70)
        print(" FILTER CONTENT LOSS ANALYSIS COMPLETE")
        print("="*70)

    def _generate_content_loss_report(self, sentence_df: pd.DataFrame,
                                      cue_df: pd.DataFrame,
                                      compression_df: pd.DataFrame):
        """Generate content loss analysis report."""
        report_path = self.output_dir / 'FILTER_CONTENT_LOSS_REPORT.md'

        with open(report_path, 'w') as f:
            f.write("# Filter Content Loss Analysis\n\n")
            f.write("## Summary\n\n")
            f.write("This analysis examines what information the old filter deleted and ")
            f.write("how the new filter preserves it differently.\n\n")
            f.write("---\n\n")

            f.write("## 1. Sentence Type Preservation\n\n")
            f.write("**Question**: Which types of sentences did the old filter delete?\n\n")
            f.write("| Category | Old Rate | New Rate | Improvement |\n")
            f.write("|----------|----------|----------|-------------|\n")
            for _, row in sentence_df.iterrows():
                f.write(f"| {row['category']} | {row['old_preservation_rate']*100:.1f}% | "
                       f"{row['new_preservation_rate']*100:.1f}% | "
                       f"+{row['improvement']*100:.1f}pp |\n")

            f.write("\n**Key Findings**:\n")
            worst_old = sentence_df.iloc[-1]
            best_improvement = sentence_df.iloc[0]
            f.write(f"- Worst preserved by old filter: **{worst_old['category']}** "
                   f"({worst_old['old_preservation_rate']*100:.1f}%)\n")
            f.write(f"- Biggest improvement: **{best_improvement['category']}** "
                   f"(+{best_improvement['improvement']*100:.1f}pp)\n\n")

            f.write("---\n\n")

            if cue_df is not None:
                f.write("## 2. Deception Cue Preservation\n\n")
                f.write("**Question**: Were specific deception-related words preserved?\n\n")
                f.write("| Cue | Old Rate | New Rate | Improvement |\n")
                f.write("|-----|----------|----------|-------------|\n")
                for _, row in cue_df.head(15).iterrows():
                    f.write(f"| {row['cue']} | {row['old_preservation']*100:.1f}% | "
                           f"{row['new_preservation']*100:.1f}% | "
                           f"+{row['improvement']*100:.1f}pp |\n")

                f.write("\n**Key Findings**:\n")
                top_improved = cue_df.iloc[0]
                f.write(f"- Most improved cue: **{top_improved['cue']}** "
                       f"(+{top_improved['improvement']*100:.1f}pp)\n")
                mean_old = cue_df['old_preservation'].mean()
                mean_new = cue_df['new_preservation'].mean()
                f.write(f"- Overall: Old filter preserved {mean_old*100:.1f}% of cues, ")
                f.write(f"new filter preserved {mean_new*100:.1f}%\n\n")

            f.write("---\n\n")

            f.write("## 3. Compression vs Semantic Preservation\n\n")
            old_comp_mean = compression_df['old_compression_ratio'].mean()
            new_comp_mean = compression_df['new_compression_ratio'].mean()
            old_sim_mean = compression_df['old_similarity'].mean()
            new_sim_mean = compression_df['new_similarity'].mean()

            f.write("| Filter | Compression | Similarity |\n")
            f.write("|--------|-------------|------------|\n")
            f.write(f"| Old | {old_comp_mean*100:.1f}% | {old_sim_mean:.4f} |\n")
            f.write(f"| New | {new_comp_mean*100:.1f}% | {new_sim_mean:.4f} |\n\n")

            f.write("**Trade-off**:\n")
            comp_diff = (new_comp_mean - old_comp_mean) * 100
            sim_diff = new_sim_mean - old_sim_mean
            f.write(f"- New filter is {abs(comp_diff):.1f}pp {'more' if comp_diff > 0 else 'less'} compressed\n")
            f.write(f"- New filter preserves {sim_diff:.4f} more semantic information\n\n")

            f.write("---\n\n")

            f.write("## Files Generated\n\n")
            f.write("- `filter_sentence_preservation.csv` - Sentence type preservation rates\n")
            f.write("- `filter_preservation_comparison.png` - Visualization\n")
            f.write("- `deception_cue_preservation.csv` - Cue-level preservation\n")
            f.write("- `deception_cue_preservation.png` - Cue visualization\n")
            f.write("- `compression_vs_similarity.csv` - Compression analysis\n")
            f.write("- `compression_vs_similarity.png` - Scatter plot\n")
            f.write("- `FILTER_CONTENT_LOSS_REPORT.md` - This report\n\n")

            f.write("---\n\n")
            f.write(f"**Generated**: {pd.Timestamp.now()}\n")

        print(f"\nSaved: {report_path}")


def main():
    """Run filter content loss analysis."""
    analyzer = FilterContentLossAnalyzer()
    analyzer.run_all_analyses()


if __name__ == '__main__':
    main()
