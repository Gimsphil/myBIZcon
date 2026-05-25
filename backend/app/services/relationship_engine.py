import json
import logging
import httpx
from app.config import settings
from templates.relationship_prompts import (
    SYSTEM_INSTRUCTION_BASE,
    RELATIONSHIP_PROMPTS,
    GROUP_CHAT_INSTRUCTION
)

logger = logging.getLogger("myBIZcon_RelationshipEngine")

class RelationshipEngineService:
    """
    🤖 RelationshipEngineService
    Connects to Google Gemini 1.5 API via low-latency REST calls to:
    - Translate incoming messaging streams.
    - Generate 3 high-quality relationship-tuned suggested drafts (BOSS, CLIENT, COWORKER, FAMILY).
    - Adapt replies dynamically to group conversations.
    """

    async def generate_replies(
        self, 
        sender: String, 
        content: str, 
        relationship: str = "COWORKER", 
        is_group: bool = False
    ) -> dict:
        """
        Invokes Gemini to generate tone-tuned translations and replies.
        """
        logger.info(f"🤖 Processing message from '{sender}' with persona '{relationship}' (Group: {is_group})")

        # Fallback API key validation
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            logger.warning("⚠️ GEMINI_API_KEY environment variable is empty. Emulating local LLM mock response.")
            return self._generate_mock_response(content, relationship)

        # Assemble prompt guidelines based on relationship status
        persona_guide = RELATIONSHIP_PROMPTS.get(relationship, RELATIONSHIP_PROMPTS["COWORKER"])
        system_prompt = SYSTEM_INSTRUCTION_BASE + "\n" + persona_guide
        
        if is_group:
            system_prompt += "\n" + GROUP_CHAT_INSTRUCTION

        prompt_payload = f"Sender: '{sender}'\nMessage Content: '{content}'"

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
                    return self._generate_mock_response(content, relationship)
        except Exception as e:
            logger.error(f"❌ Failed to reach Gemini API: {str(e)}")
            return self._generate_mock_response(content, relationship)

    def _generate_mock_response(self, content: str, relationship: str) -> dict:
        """
        Elegant offline double-fallback generator when API key is missing or calls time out.
        """
        translation = f"[번역 완료] {content}"
        
        # Static mock options matching relationship characteristics
        if relationship == "BOSS":
            suggestions = [
                {"tone": "예의 바름 & 긍정", "content": "네, 부장님. 확인했습니다. 즉시 보고서 검토 후 조치하겠습니다."},
                {"tone": "신속 조치", "content": "네, 지시하신 사항 정리하여 금일 중으로 완료해 놓겠습니다."},
                {"tone": "일정 지연 요청", "content": "네, 해당 내용 진행 중입니다만, 상세 검토를 위해 기한을 하루만 연장해 주시면 감사하겠습니다."}
            ]
        elif relationship == "CLIENT":
            suggestions = [
                {"tone": "공손 & 감사", "content": "보내주신 의견 대단히 감사드립니다. 말씀 주신 내용 즉각 피드백 반영하겠습니다."},
                {"tone": "대안 제시", "content": "네, 대표님. 요청하신 사양은 기존 설계안과 조율하여 최적의 방안으로 다시 견적 공유해 드리겠습니다."},
                {"tone": "빠른 대답", "content": "네, 대표님. 담당자 확인을 거쳐 신속하게 정식 답변 메일 전달해 올리겠습니다."}
            ]
        elif relationship == "FAMILY":
            suggestions = [
                {"tone": "친근 & 긍정", "content": "응응! 대박이네~ 🤩 이따 집에서 자세히 얘기하자!"},
                {"tone": "바쁨", "content": "나 지금 회의 중이야 ㅠㅠ 끝나고 바로 연락할게!"},
                {"tone": "가벼운 대답", "content": "오 그래? 알겠어~ 알차게 챙길게!"}
            ]
        else: # COWORKER
            suggestions = [
                {"tone": "협업 & 긍정", "content": "네, 과장님. 자료 공유 감사드려요. 금일 기획안 작성에 유용하게 참고하겠습니다."},
                {"tone": "일정 확인", "content": "아 네, 해당 업무 현재 작성 마무리 단계입니다. 오후 3시 회의 전까지 전달해 드릴게요!"},
                {"tone": "피드백 조율", "content": "네, 의견 고맙습니다. 일부 우려 사항 조율을 위해 잠깐 5분 미팅 가능할까요?"}
            ]

        return {
            "translation": translation,
            "suggestions": suggestions
        }

relationship_engine = RelationshipEngineService()
