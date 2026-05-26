# -*- coding: utf-8 -*-
import json
import logging
import httpx
from app.config import external_services_disabled, settings
from app.services.rag_engine import rag_engine
from templates.relationship_prompts import (
    SYSTEM_INSTRUCTION_BASE,
    RELATIONSHIP_PROMPTS,
    GROUP_CHAT_INSTRUCTION
)

logger = logging.getLogger("myBIZcon_RelationshipEngine")

PLATFORM_INSTRUCTIONS = {
    "SLACK": (
        "\n### PLATFORM SPECIFIC LAYOUT: SLACK\n"
        "Format the suggested replies using high-efficiency corporate Slack Markdown layout:\n"
        "- Use bold (*text*) for emphasis.\n"
        "- Use bulleted priorities (- item) for action items.\n"
        "- Keep responses highly concise, direct, and professional.\n"
        "- Incorporate common slack emojis sparingly (e.g. ✅, 🚀, 📋)."
    ),
    "KAKAOTALK": (
        "\n### PLATFORM SPECIFIC LAYOUT: KAKAOTALK\n"
        "Format the suggested replies for KakaoTalk (mobile-first):\n"
        "- Use warm, highly localized Korean business honorifics (존댓말, -요/-습니다).\n"
        "- Incorporate friendly, warm emojis (e.g. 🤩, 😊, 👍) to match Korean messaging patterns.\n"
        "- Keep paragraph sizes compact and highly readable in narrow mobile bubbles."
    ),
    "TELEGRAM": (
        "\n### PLATFORM SPECIFIC LAYOUT: TELEGRAM\n"
        "Format the suggested replies for Telegram:\n"
        "- Keep it clean, direct, secure, and bullet-compact.\n"
        "- Use standard polite registers."
    ),
    "WHATSAPP": (
        "\n### PLATFORM SPECIFIC LAYOUT: WHATSAPP\n"
        "Format the suggested replies for WhatsApp:\n"
        "- Use standard international business etiquette, clear paragraph spacing, and bold formatting (*text*)."
    )
}

class RelationshipEngineService:
    """
    🤖 RelationshipEngineService
    Connects to Google Gemini 1.5 API via low-latency REST calls.
    Expanded in Phase 4 to handle:
    - Multi-Messenger platform specific adapters (WhatsApp, KakaoTalk, Slack, Telegram).
    - Few-shot Writing Style Emulation powered by pure-Python TF-IDF RAG Corpus.
    """

    async def generate_replies(
        self, 
        sender: str, 
        content: str, 
        relationship: str = "COWORKER", 
        is_group: bool = False,
        platform: str = "WHATSAPP"
    ) -> dict:
        """
        Invokes Gemini to generate tone-tuned translations and replies,
        augmenting prompt with RAG few-shots and platform adapters.
        """
        logger.info(f"🤖 Processing message from '{sender}' with persona '{relationship}' on platform '{platform}' (Group: {is_group})")

        # Assemble prompt guidelines based on relationship status
        persona_guide = RELATIONSHIP_PROMPTS.get(relationship, RELATIONSHIP_PROMPTS["COWORKER"])
        system_prompt = SYSTEM_INSTRUCTION_BASE + "\n" + persona_guide
        
        if is_group:
            system_prompt += "\n" + GROUP_CHAT_INSTRUCTION

        # 1. Platform-Specific Adapter Integration [Phase 4]
        platform_upper = platform.upper()
        platform_guide = PLATFORM_INSTRUCTIONS.get(platform_upper, PLATFORM_INSTRUCTIONS["WHATSAPP"])
        system_prompt += platform_guide

        # 2. Local RAG Few-Shot Writing Style Injection [Phase 4]
        rag_few_shots = rag_engine.retrieve_personal_examples(content)
        if rag_few_shots:
            system_prompt += "\n" + rag_few_shots
            logger.info("🧠 Semantic Few-Shot context injected into Gemini system prompt.")
        else:
            logger.info("ℹ️ RAG Corpus: No relevant past few-shot context found. Relying on zero-shot templates.")

        prompt_payload = f"Sender: '{sender}'\nMessage Content: '{content}'"

        if external_services_disabled():
            logger.warning("External services disabled. Emulating local LLM mock response.")
            return self._generate_mock_response(content, relationship, platform_upper)

        # Fallback API key validation
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            logger.warning("⚠️ GEMINI_API_KEY environment variable is empty. Emulating local LLM mock response.")
            return self._generate_mock_response(content, relationship, platform_upper)

        url = f"{settings.GEMINI_API_URL}?key={api_key}"
        headers = {"Content-Type": "application/json"}
        
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt_payload}]
                }
            ],
            "systemInstruction": {
                "parts": [{"text": system_prompt}]
            },
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                if response.status_code == 200:
                    result = response.json()
                    raw_text = result["candidates"][0]["content"]["parts"][0]["text"]
                    parsed_json = json.loads(raw_text)
                    logger.info("✅ Successfully parsed LLM reply suggestions.")
                    return parsed_json
                else:
                    logger.error(f"❌ Gemini REST HTTP Error: {response.status_code}")
                    return self._generate_mock_response(content, relationship, platform_upper)
        except Exception as e:
            logger.error(f"❌ Failed to reach Gemini API: {str(e)}")
            return self._generate_mock_response(content, relationship, platform_upper)

    def _generate_mock_response(self, content: str, relationship: str, platform: str) -> dict:
        """
        Elegant offline double-fallback generator including platform specific layouts.
        """
        translation = f"[번역 완료 ({platform})] {content}"
        
        # Static mock options matching relationship characteristics and platform styling
        if relationship == "BOSS":
            if platform == "SLACK":
                suggestions = [
                    {"tone": "예의 바름 & 긍정", "content": "*네, 부장님.* 확인했습니다.\n- 즉시 보고서 검토 후 조치해 놓겠습니다. 🚀"},
                    {"tone": "신속 조치", "content": "*네, 부장님.* 지시하신 사항 정리하여 금일 업무 종료 전까지 완료하겠습니다. ✅"},
                    {"tone": "일정 지연 요청", "content": "*네, 부장님.* 진행 중입니다만 기한을 하루만 연장해 주시면 감사하겠습니다. 📋"}
                ]
            else: # KakaoTalk / WhatsApp / Telegram
                suggestions = [
                    {"tone": "예의 바름 & 긍정", "content": "네, 부장님. 확인했습니다. 즉시 보고서 검토 후 조치하겠습니다. 😊"},
                    {"tone": "신속 조치", "content": "네, 부장님. 지시하신 사항 정리하여 금일 중으로 완료해 놓겠습니다! 👍"},
                    {"tone": "일정 지연 요청", "content": "네, 부장님. 해당 내용 진행 중입니다만, 상세 검토를 위해 기한을 하루만 연장해 주시면 감사하겠습니다."}
                ]
        elif relationship == "CLIENT":
            if platform == "SLACK":
                suggestions = [
                    {"tone": "공손 & 감사", "content": "*보내주신 의견 대단히 감사드립니다.*\n- 말씀 주신 내용 즉각 피드백 반영하겠습니다. ✅"},
                    {"tone": "대안 제시", "content": "*네, 대표님.*\n- 요청하신 사양은 기존 설계안과 조율하여 최적의 방안으로 다시 견적 공유해 드리겠습니다. 🚀"},
                    {"tone": "빠른 대답", "content": "*네, 대표님.* 담당자 확인 거쳐 신속하게 답변 공유해 올리겠습니다."}
                ]
            else:
                suggestions = [
                    {"tone": "공손 & 감사", "content": "보내주신 의견 대단히 감사드립니다. 말씀 주신 내용 즉각 피드백 반영하겠습니다. 🤩"},
                    {"tone": "대안 제시", "content": "네, 대표님. 요청하신 사양은 기존 설계안과 조율하여 최적의 방안으로 다시 견적 공유해 드리겠습니다. 👍"},
                    {"tone": "빠른 대답", "content": "네, 대표님. 담당자 확인을 거쳐 신속하게 정식 답변 메일 전달해 올리겠습니다."}
                ]
        elif relationship == "FAMILY":
            suggestions = [
                {"tone": "친근 & 긍정", "content": "응응! 대박이네~ 🤩 이따 집에서 자세히 얘기하자!"},
                {"tone": "바쁨", "content": "나 지금 회의 중이야 ㅠㅠ 끝나고 바로 연락할게!"},
                {"tone": "가벼운 대답", "content": "오 그래? 알겠어~ 알차게 챙길게!"}
            ]
        else: # COWORKER
            if platform == "SLACK":
                suggestions = [
                    {"tone": "협업 & 긍정", "content": "*네, 과장님. 자료 공유 감사드려요.*\n- 금일 기획안 작성에 유용하게 참고하겠습니다. 🚀"},
                    {"tone": "일정 확인", "content": "*네, 과장님.*\n- 해당 업무 마무리 단계입니다. 오후 3시 회의 전까지 전달해 드릴게요! ✅"},
                    {"tone": "피드백 조율", "content": "*네, 의견 고맙습니다.*\n- 일부 우려 사항 조율을 위해 잠깐 5분 미팅 가능할까요? 📋"}
                ]
            else:
                suggestions = [
                    {"tone": "협업 & 긍정", "content": "네, 과장님. 자료 공유 감사드려요. 금일 기획안 작성에 유용하게 참고하겠습니다. 😊"},
                    {"tone": "일정 확인", "content": "아 네, 해당 업무 현재 작성 마무리 단계입니다. 오후 3시 회의 전까지 전달해 드릴게요!"},
                    {"tone": "피드백 조율", "content": "네, 의견 고맙습니다. 일부 우려 사항 조율을 위해 잠깐 5분 미팅 가능할까요?"}
                ]

        return {
            "translation": translation,
            "suggestions": suggestions
        }

relationship_engine = RelationshipEngineService()
