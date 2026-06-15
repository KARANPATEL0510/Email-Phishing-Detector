import re
import math

class AIDetector:
    def __init__(self):
        # AI transition words
        self.ai_transitions = {
            "moreover", "furthermore", "in conclusion", "consequently", 
            "additionally", "delighted to", "crucial to", "vital to", 
            "essential to", "please note that", "please find", "notably",
            "to clarify", "in summary", "to summarize", "to ensure", "it is important"
        }

        # Corporate / phishing / automated scam templates keywords
        self.scam_keywords = {
            "urgent action required", "password reset", "account verification",
            "unauthorized login", "policy update", "benefits review",
            "gift card voucher", "security alert", "immediate attention",
            "verify your credentials", "system upgrade", "it support desk"
        }

    def _get_sentences(self, text):
        # Split by periods, exclamation marks, or question marks followed by space
        sentences = re.split(r'[.!?]+\s+', text.strip())
        return [s for s in sentences if len(s.split()) > 2]

    def _get_words(self, text):
        # Clean punctuation and split into lowercase words
        clean_text = re.sub(r'[^\w\s]', '', text.lower())
        return clean_text.split()

    def analyze(self, text, historical_scans=None):
        if not text or len(text.strip()) < 10:
            return {
                "is_ai_generated": False,
                "ai_probability": 0.0,
                "human_probability": 100.0,
                "confidence": "Low",
                "factors": ["Content too short for reliable analysis"],
                "reasons": ["The provided text is too short to analyze sentence structure, vocabulary variation, or transition patterns."]
            }

        sentences = self._get_sentences(text)
        words = self._get_words(text)
        total_words = len(words)
        total_sentences = len(sentences)

        factors = []
        reasons = []
        ai_score = 30.0  # Baseline probability

        # 1. Linguistic Variety Check (Type-Token Ratio)
        if total_words > 15:
            unique_words = len(set(words))
            ttr = unique_words / total_words
            # Lower TTR means high repetition. Normal human English writing in emails is ~0.65 to 0.85
            if ttr < 0.60:
                ai_score += 15
                factors.append("Low linguistic variance")
                reasons.append(f"Highly repetitive word usage (vocabulary richness: {ttr*100:.1f}%) typical of automated generation templates.")
            elif ttr > 0.88:
                ai_score += 5
                factors.append("Uncharacteristically high vocabulary density")
                reasons.append("Highly polished structure with very little vocabulary overlap.")

        # 2. Stylometric Sentence Length Variance Check
        if total_sentences >= 3:
            lengths = [len(s.split()) for s in sentences]
            mean_length = sum(lengths) / total_sentences
            variance = sum((l - mean_length) ** 2 for l in lengths) / total_sentences
            std_dev = math.sqrt(variance)

            # AI content usually has highly uniform sentence lengths (std_dev < 3.5 words)
            # Humans write with dynamic variation (mix of short and long sentences, std_dev > 6 words)
            if std_dev < 3.5:
                ai_score += 20
                factors.append("Low sentence-length variation")
                reasons.append(f"Sentences have highly uniform length (variance: {std_dev:.1f} words), which is typical of AI output patterns.")
            elif std_dev > 8.0:
                ai_score -= 10  # Highly likely human-written
        else:
            factors.append("Short paragraph structure")

        # 3. Transition Word Pattern Recognition
        transition_matches = 0
        text_lower = text.lower()
        for word in self.ai_transitions:
            if word in text_lower:
                transition_matches += len(re.findall(r'\b' + re.escape(word) + r'\b', text_lower))

        if transition_matches > 0:
            rate = transition_matches / (total_words / 100) if total_words > 0 else 0
            if rate > 2.0 or transition_matches >= 2:
                ai_score += 15
                factors.append("Frequent transitional phrasing")
                reasons.append(f"Found multiple transition keywords ('{', '.join([w for w in self.ai_transitions if w in text_lower][:3])}') commonly used by AI models to structure text.")

        # 4. Semantic Phishing & Scam Template Heuristics
        matched_scam = []
        for keyword in self.scam_keywords:
            if keyword in text_lower:
                matched_scam.append(keyword)
                ai_score += 15

        if matched_scam:
            factors.append("Matches automated phishing templates")
            reasons.append(f"Content matches phrasing used in mass phishing/scam campaigns: '{', '.join(matched_scam)}'.")

        # 5. Historical Similarity Comparison
        if historical_scans:
            highest_similarity = 0.0
            word_set = set(words)
            for scan in historical_scans:
                hist_text = scan.get("input_data", "")
                if hist_text and len(hist_text.strip()) > 10:
                    hist_words = self._get_words(hist_text)
                    if not hist_words:
                        continue
                    hist_set = set(hist_words)
                    
                    intersection = word_set.intersection(hist_set)
                    union = word_set.union(hist_set)
                    similarity = len(intersection) / len(union) if union else 0.0
                    if similarity > highest_similarity:
                        highest_similarity = similarity

            if 0.70 <= highest_similarity < 0.99:
                ai_score += 25
                factors.append("High similarity to previous alerts")
                reasons.append(f"Shares a {highest_similarity*100:.1f}% similarity with previously scanned emails, indicating an automated or template-rotated campaign.")

        ai_score = max(0.0, min(100.0, ai_score))
        human_score = 100.0 - ai_score

        if total_words < 25:
            confidence = "Low"
        elif ai_score > 75 or ai_score < 25:
            confidence = "High"
        else:
            confidence = "Medium"

        if ai_score < 35:
            if not factors:
                factors.append("Natural stylometry")
            if not reasons:
                reasons.append("The text displays diverse sentence lengths and natural vocabulary variation, indicative of human authorship.")

        return {
            "is_ai_generated": ai_score >= 50.0,
            "ai_probability": round(ai_score, 1),
            "human_probability": round(human_score, 1),
            "confidence": confidence,
            "factors": factors,
            "reasons": reasons
        }
