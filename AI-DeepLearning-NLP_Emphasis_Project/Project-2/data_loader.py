"""
Data preparation utilities for Turkish pragmatic emphasis detection.
"""

import json
import io
import re
import zipfile
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
from bs4 import BeautifulSoup
from sklearn.model_selection import train_test_split

import config

try:
    from datasets import load_dataset

    DATASETS_AVAILABLE = True
except ImportError:
    DATASETS_AVAILABLE = False


PLACEHOLDER_SENTENCES = {
    "",
    "nan",
    "none",
    "sentence (tr)",
    "sentence(tr)",
}

STOPWORDS = {
    "ve",
    "ile",
    "ama",
    "fakat",
    "bir",
    "bu",
    "şu",
    "su",
    "o",
    "da",
    "de",
    "çok",
    "cok",
    "mi",
    "mu",
    "mü",
    "mu",
    "için",
    "icin",
    "gibi",
    "hem",
    "ya",
    "veya",
}

INTENSIFIERS = {
    "çok",
    "cok",
    "aşırı",
    "asiri",
    "gayet",
    "pek",
    "fazla",
    "oldukça",
    "oldukca",
    "en",
    "hiç",
    "hic",
}
NEGATIONS = {"değil", "degil", "yok", "asla", "hayır", "hayir", "degil."}
POSITIVE_CUES = {
    "güzel",
    "guzel",
    "harika",
    "mükemmel",
    "mukemmel",
    "başarılı",
    "basarili",
    "kaliteli",
    "uygun",
    "memnun",
    "efsane",
    "iyi",
}
NEGATIVE_CUES = {
    "kötü",
    "kotu",
    "berbat",
    "rezalet",
    "çirkin",
    "cirkin",
    "pahalı",
    "pahali",
    "sorunlu",
    "bozuk",
    "yetersiz",
    "kırık",
    "kirik",
}
EMOTION_CUES = {
    "öfke",
    "ofke",
    "mutlu",
    "üzgün",
    "uzgun",
    "nefret",
    "seviyorum",
    "bayıldım",
    "bayildim",
    "kızgın",
    "kizgin",
    "şaşırdım",
    "sasirdim",
}


def normalize_token(token: str) -> str:
    return re.sub(r"[^\wçğıöşüÇĞİÖŞÜ]+", "", token.lower())


def is_valid_sentence(sentence: str) -> bool:
    if not sentence:
        return False
    normalized = sentence.strip().lower()
    if normalized in PLACEHOLDER_SENTENCES:
        return False
    if len(normalized.split()) < 2:
        return False
    return True


def derive_contrastive_label(bio_labels: List[str]) -> int:
    if "I-EMPHASIS" in bio_labels:
        return 2
    if "B-EMPHASIS" in bio_labels:
        return 1
    return 0


def provisional_focus_span(
    words: List[str], source_label: Optional[str] = None
) -> Tuple[int, int]:
    """Select a provisional emphasis span for real/OOD text sampling."""
    normalized_words = [normalize_token(word) for word in words]
    label_hint = (source_label or "").lower()

    if any(token in {"positive", "pozitif"} for token in [label_hint]):
        cue_order = [POSITIVE_CUES, EMOTION_CUES]
    elif any(
        token in {"negative", "negatif", "kizgin", "öfkeli", "ofkeli"}
        for token in [label_hint]
    ):
        cue_order = [NEGATIVE_CUES, EMOTION_CUES, NEGATIONS]
    else:
        cue_order = [EMOTION_CUES, POSITIVE_CUES, NEGATIVE_CUES]

    candidate_idx = None
    for cue_set in cue_order:
        for idx, token in enumerate(normalized_words):
            if token in cue_set:
                candidate_idx = idx
                break
        if candidate_idx is not None:
            break

    if candidate_idx is None:
        for idx, token in enumerate(normalized_words):
            if len(token) > 3 and token not in STOPWORDS:
                candidate_idx = idx
                break

    if candidate_idx is None:
        candidate_idx = 0

    start_idx = candidate_idx
    end_idx = candidate_idx

    if candidate_idx > 0 and normalized_words[candidate_idx - 1] in INTENSIFIERS:
        start_idx = candidate_idx - 1
    elif (
        candidate_idx + 1 < len(words)
        and normalized_words[candidate_idx + 1] in NEGATIONS
    ):
        end_idx = candidate_idx + 1
    elif normalized_words[candidate_idx] in INTENSIFIERS and candidate_idx + 1 < len(
        words
    ):
        end_idx = candidate_idx + 1

    return start_idx, end_idx


def create_bio_from_span(num_tokens: int, start_idx: int, end_idx: int) -> List[str]:
    bio_labels = ["O"] * num_tokens
    if num_tokens == 0:
        return bio_labels

    bio_labels[start_idx] = "B-EMPHASIS"
    for idx in range(start_idx + 1, min(end_idx + 1, num_tokens)):
        bio_labels[idx] = "I-EMPHASIS"
    return bio_labels


class TurkishStressDataLoader:
    """Load, clean, split, and enrich the stress detection datasets."""

    def __init__(self):
        self.label2id = config.LABEL2ID
        self.id2label = config.ID2LABEL
        self.train_data: List[Dict] = []
        self.val_data: List[Dict] = []
        self.test_data: List[Dict] = []
        self.ood_test_data: List[Dict] = []

    def extract_emphasis_from_html(
        self, sentence: str
    ) -> Tuple[str, List[str], List[int]]:
        soup = BeautifulSoup(sentence, "html.parser")
        clean_text = re.sub(r"\s+", " ", soup.get_text(" ")).strip()
        emphasized_words = [
            em.get_text(" ").strip()
            for em in soup.find_all("em")
            if em.get_text().strip()
        ]
        words = clean_text.split()

        labels = []
        for word in words:
            normalized_word = normalize_token(word)
            is_emphasized = any(
                normalize_token(emph) in normalized_word
                for emph in emphasized_words
                if emph
            )
            labels.append(1 if is_emphasized else 0)

        return clean_text, words, labels

    def _load_csv_rows(self, csv_path: Path) -> pd.DataFrame:
        if not csv_path.exists():
            zip_path = config.PROJECT_ROOT / "legacy.zip"
            if zip_path.exists():
                return self._load_csv_rows_from_zip(zip_path, csv_path.name)

        last_error = None
        for encoding in ["utf-8", "latin1", "iso-8859-9"]:
            try:
                return pd.read_csv(
                    csv_path,
                    encoding=encoding,
                    on_bad_lines="skip",
                    quoting=1,
                    escapechar="\\",
                )
            except (UnicodeDecodeError, pd.errors.ParserError) as exc:
                last_error = exc
        raise last_error

    def _load_csv_rows_from_zip(self, zip_path: Path, csv_name: str) -> pd.DataFrame:
        last_error = None
        with zipfile.ZipFile(zip_path) as archive:
            with archive.open(f"legacy/{csv_name}") as handle:
                raw_bytes = handle.read()

        for encoding in ["utf-8", "latin1", "iso-8859-9"]:
            try:
                return pd.read_csv(
                    io.StringIO(raw_bytes.decode(encoding)),
                    on_bad_lines="skip",
                    quoting=1,
                    escapechar="\\",
                )
            except (UnicodeDecodeError, pd.errors.ParserError) as exc:
                last_error = exc
        raise last_error

    def _build_legacy_example(
        self,
        idx: int,
        sentence: str,
        source: str,
        metadata: Optional[Dict] = None,
    ) -> Optional[Dict]:
        if not is_valid_sentence(sentence):
            return None

        clean_text, words, labels = self.extract_emphasis_from_html(sentence)
        if not is_valid_sentence(clean_text):
            return None

        bio_labels = self.convert_to_bio_format(words, labels)
        example = {
            "id": f"{source}_{idx}",
            "sentence": clean_text,
            "words": words,
            "labels": labels,
            "bio_labels": bio_labels,
            "contrastive_label": derive_contrastive_label(bio_labels),
            "source": source,
            "domain": "synthetic",
            "annotation_status": "gold",
        }
        if metadata:
            example.update(metadata)
        return example

    def load_vurgu_varyasyonlari(self) -> List[Dict]:
        print(f"\n📁 Loading {config.VURGU_VARYASYONLARI_PATH.name}...")
        try:
            df = self._load_csv_rows(config.VURGU_VARYASYONLARI_PATH)
        except Exception as exc:
            print(f"  ✗ Error loading file: {exc}")
            return []

        print(f"  ✓ Loaded {len(df)} rows")
        examples = []
        for idx, row in df.iterrows():
            sentence = row.iloc[0] if not pd.isna(row.iloc[0]) else ""
            focus_type = (
                str(row.iloc[1])
                if len(row) > 1 and not pd.isna(row.iloc[1])
                else "unknown"
            )
            example = self._build_legacy_example(
                idx=idx,
                sentence=str(sentence),
                source="var",
                metadata={"focus_type": focus_type},
            )
            if example is not None:
                examples.append(example)

        print(f"  ✓ Processed {len(examples)} valid examples")
        return examples

    def load_vurgu_hece(self) -> List[Dict]:
        print(f"\n📁 Loading {config.VURGU_HECE_PATH.name}...")
        try:
            df = self._load_csv_rows(config.VURGU_HECE_PATH)
        except Exception as exc:
            print(f"  ✗ Error loading file: {exc}")
            return []

        print(f"  ✓ Loaded {len(df)} rows")
        examples = []
        for idx, row in df.iterrows():
            sentence = row.iloc[0] if not pd.isna(row.iloc[0]) else ""
            emphasized_word = (
                str(row.iloc[1]) if len(row) > 1 and not pd.isna(row.iloc[1]) else ""
            )
            explanation = (
                str(row.iloc[4]) if len(row) > 4 and not pd.isna(row.iloc[4]) else ""
            )
            example = self._build_legacy_example(
                idx=idx,
                sentence=str(sentence),
                source="hece",
                metadata={
                    "emphasized_word": emphasized_word,
                    "explanation": explanation,
                },
            )
            if example is not None:
                examples.append(example)

        print(f"  ✓ Processed {len(examples)} valid examples")
        return examples

    def convert_to_bio_format(self, words: List[str], labels: List[int]) -> List[str]:
        bio_labels = []
        in_emphasis = False
        for label in labels:
            if label == 1:
                bio_labels.append("I-EMPHASIS" if in_emphasis else "B-EMPHASIS")
                in_emphasis = True
            else:
                bio_labels.append("O")
                in_emphasis = False
        return bio_labels

    def load_all_data(self) -> List[Dict]:
        print("\n" + "=" * 60)
        print("📚 LOADING TURKISH STRESS DETECTION DATASETS")
        print("=" * 60)

        examples = []
        examples.extend(self.load_vurgu_varyasyonlari())
        examples.extend(self.load_vurgu_hece())

        total_words = sum(len(example["words"]) for example in examples)
        emphasized_words = sum(sum(example["labels"]) for example in examples)
        print("\n📊 DATASET STATISTICS")
        print(f"  Total examples: {len(examples)}")
        print(f"  Total words: {total_words}")
        if total_words:
            print(
                f"  Emphasized words: {emphasized_words} ({100 * emphasized_words / total_words:.2f}%)"
            )
        return examples

    def split_data(
        self,
        examples: List[Dict],
        train_ratio: float = config.TRAIN_RATIO,
        val_ratio: float = config.VAL_RATIO,
        test_ratio: float = config.TEST_RATIO,
        random_seed: int = config.RANDOM_SEED,
    ):
        print("\n✂️  SPLITTING DATA")
        print(
            f"  Train: {train_ratio * 100:.0f}%, Val: {val_ratio * 100:.0f}%, Test: {test_ratio * 100:.0f}%"
        )

        train_data, temp_data = train_test_split(
            examples,
            test_size=(val_ratio + test_ratio),
            random_state=random_seed,
        )
        val_ratio_adjusted = val_ratio / (val_ratio + test_ratio)
        val_data, test_data = train_test_split(
            temp_data,
            test_size=(1 - val_ratio_adjusted),
            random_state=random_seed,
        )

        self.train_data = train_data
        self.val_data = val_data
        self.test_data = test_data

        print(f"  ✓ Train: {len(train_data)} examples")
        print(f"  ✓ Val: {len(val_data)} examples")
        print(f"  ✓ Test: {len(test_data)} examples")
        return train_data, val_data, test_data

    def build_real_ood_dataset(self, force_refresh: bool = False) -> List[Dict]:
        """Sample public Turkish datasets to build a review queue / OOD split."""
        if config.OOD_TEST_PATH.exists() and not force_refresh:
            print(f"\n🌍 Using existing OOD set: {config.OOD_TEST_PATH.name}")
            self.ood_test_data = json.loads(
                config.OOD_TEST_PATH.read_text(encoding="utf-8")
            )
            return self.ood_test_data

        if not DATASETS_AVAILABLE:
            print(
                "\n⚠️ datasets package is not installed; skipping public OOD data build."
            )
            return []

        print("\n🌍 BUILDING REAL/OOD DATASET FROM PUBLIC TURKISH SOURCES")
        ood_examples = []
        for source_key, source_cfg in config.REAL_DATA_SOURCES.items():
            dataset = load_dataset(source_cfg["hf_name"], split=source_cfg["split"])
            dataset = dataset.shuffle(seed=config.RANDOM_SEED)

            selected_rows = []
            for row in dataset:
                text = str(row.get(source_cfg["text_field"], "")).strip()
                label = str(row.get(source_cfg["label_field"], "")).strip()
                if not is_valid_sentence(text):
                    continue

                words = text.split()
                if len(words) < 3 or len(words) > 40:
                    continue

                selected_rows.append((text, label))
                if len(selected_rows) >= source_cfg["sample_size"]:
                    break

            print(f"  ✓ {source_key}: {len(selected_rows)} samples")
            for idx, (text, label) in enumerate(selected_rows):
                words = text.split()
                start_idx, end_idx = provisional_focus_span(words, label)
                bio_labels = create_bio_from_span(len(words), start_idx, end_idx)
                ood_examples.append(
                    {
                        "id": f"ood_{source_key}_{idx}",
                        "sentence": text,
                        "words": words,
                        "bio_labels": bio_labels,
                        "label_ids": [
                            self.label2id[label_name] for label_name in bio_labels
                        ],
                        "contrastive_label": derive_contrastive_label(bio_labels),
                        "source": source_key,
                        "source_dataset": source_cfg["hf_name"],
                        "domain": source_cfg["domain"],
                        "source_label": label,
                        "annotation_status": "auto_suggested",
                        "is_ood": True,
                    }
                )

        self.ood_test_data = ood_examples
        return ood_examples

    def _serialize_split(self, split_data: List[Dict]) -> List[Dict]:
        serialized = []
        for example in split_data:
            bio_labels = example.get("bio_labels")
            if bio_labels is None:
                bio_labels = self.convert_to_bio_format(
                    example["words"], example["labels"]
                )

            serialized_example = {
                "id": example["id"],
                "sentence": example["sentence"],
                "words": example["words"],
                "bio_labels": bio_labels,
                "label_ids": [self.label2id[label] for label in bio_labels],
                "contrastive_label": example.get(
                    "contrastive_label", derive_contrastive_label(bio_labels)
                ),
                "source": example.get("source", "unknown"),
                "domain": example.get("domain", "synthetic"),
                "annotation_status": example.get("annotation_status", "gold"),
            }

            for optional_key in [
                "focus_type",
                "emphasized_word",
                "explanation",
                "source_dataset",
                "source_label",
                "is_ood",
            ]:
                if optional_key in example:
                    serialized_example[optional_key] = example[optional_key]

            serialized.append(serialized_example)
        return serialized

    def save_processed_data(self):
        print("\n💾 SAVING PROCESSED DATA")
        for split_name, split_data in [
            ("train", self.train_data),
            ("val", self.val_data),
            ("test", self.test_data),
        ]:
            output_path = config.PROCESSED_DIR / f"{split_name}.json"
            serialized = self._serialize_split(split_data)
            with open(output_path, "w", encoding="utf-8") as handle:
                json.dump(serialized, handle, ensure_ascii=False, indent=2)
            print(f"  ✓ Saved {len(serialized)} examples to {output_path.name}")

        if self.ood_test_data:
            serialized_ood = self._serialize_split(self.ood_test_data)
            with open(config.OOD_TEST_PATH, "w", encoding="utf-8") as handle:
                json.dump(serialized_ood, handle, ensure_ascii=False, indent=2)
            with open(config.OOD_REVIEW_PATH, "w", encoding="utf-8") as handle:
                json.dump(serialized_ood, handle, ensure_ascii=False, indent=2)
            print(
                f"  ✓ Saved {len(serialized_ood)} OOD examples to {config.OOD_TEST_PATH.name}"
            )

        print("\n✅ Data processing complete!")
        print(f"  Processed data saved to: {config.PROCESSED_DIR}")

    def print_sample_examples(self, n: int = 3):
        print(f"\n📝 SAMPLE EXAMPLES (First {n} from training set)")
        print("=" * 60)
        for i, example in enumerate(self.train_data[:n], 1):
            bio_labels = example.get("bio_labels") or self.convert_to_bio_format(
                example["words"], example["labels"]
            )
            print(f"\nExample {i}:")
            print(f"  Sentence: {example['sentence']}")
            print(f"  Words: {example['words']}")
            print(f"  Labels: {bio_labels}")
            print(f"  Contrastive Label: {derive_contrastive_label(bio_labels)}")

            highlighted = []
            for word, label in zip(example["words"], bio_labels):
                if label.startswith("B-") or label.startswith("I-"):
                    highlighted.append(f"**{word}**")
                else:
                    highlighted.append(word)
            print(f"  Highlighted: {' '.join(highlighted)}")


def summarize_label_distribution(file_path: Path):
    if not file_path.exists():
        return

    data = json.loads(file_path.read_text(encoding="utf-8"))
    counts = Counter()
    for sample in data:
        counts.update(sample["bio_labels"])
    print(f"  {file_path.name}: {dict(counts)}")


def main():
    loader = TurkishStressDataLoader()
    all_examples = loader.load_all_data()

    if not all_examples:
        print("\n❌ No data loaded! Check if CSV files exist and are readable.")
        return

    loader.split_data(all_examples)
    loader.print_sample_examples(n=5)
    loader.build_real_ood_dataset()
    loader.save_processed_data()

    print("\n📌 Saved split label distributions:")
    summarize_label_distribution(config.PROCESSED_DIR / "train.json")
    summarize_label_distribution(config.PROCESSED_DIR / "val.json")
    summarize_label_distribution(config.PROCESSED_DIR / "test.json")
    summarize_label_distribution(config.OOD_TEST_PATH)

    print("\n" + "=" * 60)
    print("🎉 SUCCESS! Data is ready for model training.")
    print("=" * 60)


if __name__ == "__main__":
    main()
