import re
from collections import Counter

try:
    import yake
except ImportError:
    yake = None


class TitleGenerator:
    MAX_TITLE_LENGTH = 60

    YAKE_LANGUAGES = {
        "ar", "bg", "cs", "da", "de", "el", "en", "es", "et", "fi", "fr", "he", "hi",
        "hr", "hu", "id", "it", "ja", "ko", "lt", "lv", "nl", "no", "pl", "pt", "ro",
        "ru", "sk", "sl", "sv", "tr", "uk", "zh",
    }

    WHISPER_LANGUAGE_MAP = {
        "auto": None,
        "mock": None,
        "yue": "zh",
        "jw": "id",
        "nn": "no",
        "tl": "id",
    }

    STOPWORDS = {
        "en": {
            "the", "and", "for", "that", "this", "with", "from", "you", "your", "are", "was", "were",
            "have", "has", "had", "not", "but", "can", "will", "just", "like", "about", "into", "then",
            "than", "when", "what", "there", "their", "them", "they", "our", "out", "all", "one", "two",
            "meeting", "transcript", "recording", "audio",
        },
        "fr": {
            "les", "des", "une", "dans", "pour", "que", "qui", "est", "sur", "avec", "pas", "plus",
            "donc", "mais", "parce", "comme", "tout", "tous", "très", "être", "fait", "cette", "cela",
            "bonjour", "merci", "alors", "voilà", "enfin", "genre", "transcript", "enregistrement", "audio",
        },
        "default": {
            "transcript", "recording", "audio", "session", "meeting", "bonjour", "merci",
        },
    }

    def generate(self, text, language=None, fallback_title="Session"):
        cleaned = self.clean_text(text)
        if not cleaned:
            return fallback_title

        lang = self.normalized_language(language) or self.detect_language(cleaned)
        title = self.generate_with_yake(cleaned, lang)

        if not title and lang != "en":
            title = self.generate_with_yake(cleaned, "en")

        if not title:
            title = self.generate_with_frequency(cleaned, lang)

        return title or fallback_title

    def generate_with_yake(self, text, language):
        if yake is None or language not in self.YAKE_LANGUAGES:
            return ""

        candidates = []

        for ngram_size in (2, 1):
            try:
                extractor = yake.KeywordExtractor(
                    lan=language,
                    n=ngram_size,
                    dedupLim=0.9,
                    top=12,
                    features=None,
                )
                candidates.extend(extractor.extract_keywords(text))
            except Exception:
                continue

        keywords = []
        seen = set()

        for keyword, score in sorted(candidates, key=lambda item: item[1]):
            keyword = self.normalize_keyword(keyword, language)
            key = keyword.casefold()

            if not keyword or key in seen:
                continue

            if self.is_bad_keyword(keyword, language):
                continue

            seen.add(key)
            keywords.append(keyword)

            if len(keywords) >= 3:
                break

        return self.build_title(keywords)

    def generate_with_frequency(self, text, language):
        words = re.findall(r"[\wÀ-ÿ'-]{3,}", text.lower(), flags=re.UNICODE)
        stopwords = self.stopwords_for(language)
        counts = Counter(
            word.strip("'-")
            for word in words
            if word.strip("'-") and word.strip("'-") not in stopwords and not word.isdigit()
        )

        keywords = [word for word, _ in counts.most_common(3)]
        keywords = [self.normalize_keyword(word, language) for word in keywords]

        return self.build_title(keywords)

    def build_title(self, keywords):
        parts = []

        for keyword in keywords:
            if not keyword:
                continue

            words = keyword.split()
            if len(words) > 4:
                keyword = " ".join(words[:4])

            keyword = self.smart_title(keyword)

            if keyword and keyword not in parts:
                parts.append(keyword)

            if len(parts) >= 2:
                break

        title = " • ".join(parts).strip()
        title = re.sub(r"\s+", " ", title)

        if len(title) > self.MAX_TITLE_LENGTH:
            title = title[: self.MAX_TITLE_LENGTH].rstrip(" -•,.;:")

        return title

    def normalized_language(self, language):
        if not language:
            return None

        lang = str(language).lower().split("-")[0].strip()
        lang = self.WHISPER_LANGUAGE_MAP.get(lang, lang)

        if lang in self.YAKE_LANGUAGES:
            return lang

        return None

    def detect_language(self, text):
        sample = f" {text[:2500].lower()} "
        french_score = 0
        english_score = 0

        french_markers = (
            " le ", " la ", " les ", " des ", " une ", " dans ", " pour ", " avec ",
            " est ", " que ", " qui ", " pas ", " donc ", " ça ", " c'est ", " être ",
        )
        english_markers = (
            " the ", " and ", " for ", " with ", " that ", " this ", " are ", " you ",
            " have ", " from ", " not ", " can ", " will ", " meeting ",
        )

        french_score += sum(sample.count(marker) for marker in french_markers)
        english_score += sum(sample.count(marker) for marker in english_markers)
        french_score += len(re.findall(r"[éèêëàâùûîïôç]", sample)) * 2

        return "fr" if french_score > english_score else "en"

    def normalize_keyword(self, keyword, language):
        keyword = re.sub(r"[\r\n\t]+", " ", keyword or "")
        keyword = re.sub(r"\s+", " ", keyword)
        keyword = keyword.strip(" -•,.;:!?()[]{}\"'")
        keyword = re.sub(r"^(le|la|les|des|du|de|the|a|an)\s+", "", keyword, flags=re.IGNORECASE)
        return keyword.strip()

    def is_bad_keyword(self, keyword, language):
        value = keyword.casefold().strip()
        if len(value) < 3:
            return True
        if value.isdigit():
            return True
        if len(value.split()) > 5:
            return True

        stopwords = self.stopwords_for(language)
        words = [word.strip("'-").casefold() for word in value.split()]

        if words and all(word in stopwords for word in words):
            return True

        return False

    def stopwords_for(self, language):
        return (
            self.STOPWORDS.get("default", set())
            | self.STOPWORDS.get(language or "", set())
        )

    def smart_title(self, text):
        words = []

        for word in text.split():
            if word.isupper() and len(word) <= 6:
                words.append(word)
            elif any(char.isdigit() for char in word):
                words.append(word.upper() if len(word) <= 5 else word.capitalize())
            elif len(word) <= 2:
                words.append(word.lower())
            else:
                words.append(word[:1].upper() + word[1:].lower())

        return " ".join(words)

    def clean_text(self, text):
        text = text or ""
        text = re.sub(r"\[[0-9:.]+\]", " ", text)
        text = re.sub(r"\([0-9:.]+\)", " ", text)
        text = re.sub(r"https?://\S+", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()
