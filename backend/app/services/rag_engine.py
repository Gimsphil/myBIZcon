# -*- coding: utf-8 -*-
import os
import re
import math
import logging
from collections import Counter
from datetime import datetime

logger = logging.getLogger("myBIZcon_RAGEngine")
logging.basicConfig(level=logging.INFO)

class RAGEngineService:
    """
    🧠 RAGEngineService
    A world-class, zero-dependency Vector Space Model (TF-IDF & Cosine Similarity) RAG Engine.
    Operates on local Google Drive Markdown backup corpus to search and retrieve historical
    conversations. Fetches User's exact past answers to emulate their personal writing style
    via few-shot LLM prompts.
    """
    def __init__(self):
        self.backup_root = os.path.join(os.getcwd(), "drive_backups")
        self.corpus = {}      # Maps file_path -> raw_text
        self.doc_tokens = {}  # Maps file_path -> Counter of tokens
        self.doc_vectors = {} # Maps file_path -> {token: tf_idf}
        self.idf = {}         # Maps token -> idf
        self.is_indexed = False
        
        # Proactively scan and build the index
        self.reindex_corpus()

    def reindex_corpus(self):
        """Recursively reads all archived Markdown backups and builds the TF-IDF vector corpus."""
        logger.info("⚡ Initiating local RAG indexing scan...")
        self.corpus = {}
        self.doc_tokens = {}
        self.doc_vectors = {}
        self.idf = {}
        
        if not os.path.exists(self.backup_root):
            logger.warning(f"⚠️ drive_backups folder not found at: {self.backup_root}. Standing by with mock corpus.")
            self._load_mock_corpus()
            self._build_tfidf()
            return

        # Recursively search for markdown backups
        for root, _, files in os.walk(self.backup_root):
            for file in files:
                if file.endswith(".md"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            text = f.read()
                            self.corpus[file_path] = text
                    except Exception as e:
                        logger.error(f"❌ Failed to parse {file}: {str(e)}")

        if not self.corpus:
            logger.info("ℹ️ No historical Markdown backups found. Loading mock corpus for pre-validation.")
            self._load_mock_corpus()
            
        self._build_tfidf()
        logger.info(f"✅ Local RAG index successfully generated. Indexed {len(self.corpus)} documents.")
        self.is_indexed = True

    def _tokenize(self, text: str) -> list:
        """Tokenizes, filters, and downcases input string safely."""
        # Split by non-alphanumeric, filter out empty, downcase
        tokens = re.findall(r'\w+', text.lower())
        # Filter short stop terms/junk to keep vector compact
        return [t for t in tokens if len(t) > 1]

    def _build_tfidf(self):
        """Constructs IDF weights and TF-IDF document vectors."""
        num_docs = len(self.corpus)
        if num_docs == 0:
            return

        # 1. Gather term counts per document
        all_unique_tokens = set()
        doc_freqs = Counter()

        for doc_id, text in self.corpus.items():
            tokens = self._tokenize(text)
            self.doc_tokens[doc_id] = Counter(tokens)
            unique_in_doc = set(tokens)
            all_unique_tokens.update(unique_in_doc)
            for token in unique_in_doc:
                doc_freqs[token] += 1

        # 2. Calculate IDF: idf(t) = log(1 + (N / DF(t)))
        for token in all_unique_tokens:
            self.idf[token] = math.log(1.0 + (num_docs / doc_freqs[token]))

        # 3. Build TF-IDF vectors for documents
        for doc_id, token_counts in self.doc_tokens.items():
            vector = {}
            total_tokens = sum(token_counts.values())
            for token, count in token_counts.items():
                tf = count / max(1, total_tokens)
                vector[token] = tf * self.idf.get(token, 0.0)
            self.doc_vectors[doc_id] = vector

    def retrieve_personal_examples(self, incoming_content: str, top_n: int = 2) -> str:
        """
        Uses Cosine Similarity to find the most semantically related historical conversation log,
        parses the User's actual historical responses, and builds a clean few-shot prompt fragment.
        """
        if not self.is_indexed:
            self.reindex_corpus()

        query_tokens = self._tokenize(incoming_content)
        if not query_tokens:
            return ""

        # Build query TF-IDF vector
        query_counts = Counter(query_tokens)
        query_total = sum(query_counts.values())
        query_vector = {}
        for token, count in query_counts.items():
            tf = count / max(1, query_total)
            query_vector[token] = tf * self.idf.get(token, 0.0)

        # Compute Cosine Similarity for each document
        similarities = []
        for doc_id, doc_vector in self.doc_vectors.items():
            sim = self._cosine_similarity(query_vector, doc_vector)
            if sim > 0.0:
                similarities.append((doc_id, sim))

        # Sort by similarity descending
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_matches = similarities[:top_n]

        if not top_matches:
            logger.info("ℹ️ RAG Search: No matching past semantic context found. Relying on default templates.")
            return ""

        # Extract few-shot context from matching logs
        few_shots = "### 📚 USER'S ACTUAL PAST WRITING STYLE EXAMPLES (RAG Few-Shot Context):\n"
        few_shots += "The following are actual past messages the user received and how they responded. "
        few_shots += "Observe the vocabulary, honorifics, sentence length, and emojis the User used, and replicate them closely:\n\n"

        for doc_id, sim in top_matches:
            raw_text = self.corpus.get(doc_id, "")
            logger.info(f"🎯 RAG Match Found: {os.path.basename(doc_id)} (Similarity: {sim:.3f})")
            
            # Find matching user responses in this log
            dialogue_lines = []
            lines = raw_text.split("\n")
            for line in lines:
                if line.strip().startswith("-") or ":" in line:
                    dialogue_lines.append(line.strip())
            
            if dialogue_lines:
                few_shots += f"**Past Dialogue Context (Source: {os.path.basename(doc_id)}):**\n"
                for line in dialogue_lines[:4]: # Grab up to 4 dialogue blocks
                    few_shots += f"{line}\n"
                few_shots += "\n"

        return few_shots

    def _cosine_similarity(self, vec1: dict, vec2: dict) -> float:
        """Calculates cosine similarity between two sparse vector dictionaries."""
        intersection = set(vec1.keys()) & set(vec2.keys())
        if not intersection:
            return 0.0

        dot_product = sum(vec1[x] * vec2[x] for x in intersection)
        
        sum1 = sum(val**2 for val in vec1.values())
        sum2 = sum(val**2 for val in vec2.values())
        
        magnitude = math.sqrt(sum1) * math.sqrt(sum2)
        if not magnitude:
            return 0.0
            
        return dot_product / magnitude

    def _load_mock_corpus(self):
        """Creates high-context business chat logs representing standard past interactions."""
        self.corpus = {
            "drive_backups/mock_chats_001.md": (
                "## Chat with Partner Co.\n"
                "- John (Client): Could you send us the draft of the secrets NDA agreement?\n"
                "- User (Speaker B - 정중함 💼): 네, 바이어님. 말씀 주신 표준 비밀유지계약서(NDA) 초안은 법무팀 검토를 거쳐 금일 오후 3시 회의 전까지 깔끔하게 작성해서 메일로 공유해 드리겠습니다. 확인 부탁드려요!\n"
            ),
            "drive_backups/mock_chats_002.md": (
                "## Chat with Boss\n"
                "- Director Kim (BOSS): Next Wednesday strategy conference schedule must include the pricing strategy report.\n"
                "- User (Speaker B - 자신감 😎): 네, 부장님! 다음 주 수요일 오전 10시로 미팅 일정 캘린더에 바로 등록했습니다. 보고서에 요청하신 5% 가격 인상 기획안 시나리오를 철저히 보충하여 완벽히 준비해 놓겠습니다. 믿고 맡겨 주십시오.\n"
            ),
            "drive_backups/mock_chats_003.md": (
                "## Chat with Wife\n"
                "- Wife (Family): 저녁에 마트 들러서 우유랑 계란 좀 사다 줘~\n"
                "- User (Speaker B - 친근함 😊): 응응! 알겠어 여보~ 🤩 퇴근하고 가는 길에 마트 들러서 꼼꼼하게 챙겨서 갈게! 이따가 봐용 하트하트\n"
            )
        }

rag_engine = RAGEngineService()
