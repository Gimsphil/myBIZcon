import json
import os
import sys
import urllib.request
import urllib.error
from templates.relationship_prompts import (
    SYSTEM_INSTRUCTION_BASE,
    RELATIONSHIP_PROMPTS,
    GROUP_CHAT_INSTRUCTION,
    MEETING_MODE_INSTRUCTION
)

# Colors for premium CLI visual experience
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_premium_banner():
    banner = f"""
{CYAN}{BOLD}========================================================================
             🌐 myBIZcon — AI Business Assistant Simulator 🌐
========================================================================{RESET}
  [Phase 1 MVP] Relationship Tuner, Group Chats, and Meeting Mode Test Client
"""
    print(banner)

def get_api_key():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print(f"{YELLOW}⚠️  GEMINI_API_KEY environment variable not found.{RESET}")
        api_key = input("Please enter your Google Gemini API Key: ").strip()
        if not api_key:
            print(f"{RED}❌ API Key is required to run real LLM simulations.{RESET}")
            sys.exit(1)
    return api_key

def call_gemini_api(api_key, system_instruction, prompt_content, response_json=True):
    """
    Calls the Google Gemini 1.5 Flash API directly via raw REST endpoint.
    This guarantees ZERO external dependencies (no pip install google-generativeai needed).
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    # Structure the payload as per Gemini 1.5 REST API standards
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt_content}
                ]
            }
        ],
        "systemInstruction": {
            "parts": [
                {"text": system_instruction}
            ]
        },
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 2048
        }
    }
    
    if response_json:
        payload["generationConfig"]["responseMimeType"] = "application/json"
        
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
            # Extract the generated text content
            text_output = result["candidates"][0]["content"]["parts"][0]["text"]
            return text_output
    except urllib.error.HTTPError as e:
        print(f"{RED}❌ HTTP Error calling Gemini API: {e.code} - {e.reason}{RESET}")
        print(e.read().decode("utf-8"))
        sys.exit(1)
    except Exception as e:
        print(f"{RED}❌ Error calling Gemini API: {str(e)}{RESET}")
        sys.exit(1)

def simulate_chat_message(api_key):
    print(f"\n{BOLD}💬 [Scenario 1] Individual Message Translation & Suggested Replies{RESET}")
    print("Choose relationship relationship:")
    print(f"1. {BOLD}BOSS{RESET} (Supervisor)")
    print(f"2. {BOLD}CLIENT{RESET} (Buyer/VIP Partner)")
    print(f"3. {BOLD}COWORKER{RESET} (Collaborative Partner)")
    print(f"4. {BOLD}FAMILY{RESET} (Friend/Spouse - Casual)")
    
    choice = input("Select choice (1-4): ").strip()
    rel_mapping = {"1": "BOSS", "2": "CLIENT", "3": "COWORKER", "4": "FAMILY"}
    relationship = rel_mapping.get(choice, "COWORKER")
    
    print(f"\nActive Persona: {GREEN}{BOLD}{relationship}{RESET}")
    default_msg = "Hello, we noticed some issues in the recent delivery schedule. Can we delay the deadline by 2 days?"
    incoming_msg = input(f"Enter incoming message (Default: '{default_msg}'): ").strip()
    if not incoming_msg:
        incoming_msg = default_msg
        
    system_prompt = SYSTEM_INSTRUCTION_BASE + "\n" + RELATIONSHIP_PROMPTS[relationship]
    prompt = f"Incoming Message: '{incoming_msg}'"
    
    print(f"\n{CYAN}🤖 Sending request to Gemini 1.5 Flash...{RESET}")
    response = call_gemini_api(api_key, system_prompt, prompt, response_json=True)
    
    try:
        parsed = json.loads(response)
        print(f"\n{GREEN}{BOLD}✨ Translation Results:{RESET}")
        print(f"  {BOLD}Original Message:{RESET} {incoming_msg}")
        print(f"  {BOLD}Translated Message:{RESET} {parsed.get('translation')}\n")
        print(f"{GREEN}{BOLD}✨ Generated Reply Suggestions (HITL - Human in the Loop):{RESET}")
        for idx, sug in enumerate(parsed.get("suggestions", []), 1):
            print(f"  {BOLD}Option {idx} ({sug.get('tone')}):{RESET}")
            print(f"    --> \"{sug.get('content')}\"")
    except Exception as e:
        print(f"{RED}❌ Failed to parse JSON response from Gemini. Raw output:{RESET}")
        print(response)

def simulate_group_chat(api_key):
    print(f"\n{BOLD}👥 [Scenario 2] Multi-Party Group Chat Translation & Response{RESET}")
    print("This scenario parses a group chat with multiple active senders to recommend replies.")
    
    default_transcript = (
        "John (Client Manager): Hey team, did we approve the latest specifications?\n"
        "Sarah (Project Lead): Yes, they look good on our end. But we are waiting for the final budget confirmation from the user.\n"
        "John (Client Manager): Okay, User, please let us know when you can confirm the budget."
    )
    
    print(f"\n{BOLD}Group Chat Transcript (representing active screen scrape):{RESET}")
    print(f"{YELLOW}{default_transcript}{RESET}\n")
    
    use_default = input("Use default transcript? (Y/n): ").strip().lower()
    transcript = default_transcript if use_default != 'n' else input("Enter transcript: ").strip()
    
    system_prompt = SYSTEM_INSTRUCTION_BASE + "\n" + RELATIONSHIP_PROMPTS["CLIENT"] + "\n" + GROUP_CHAT_INSTRUCTION
    prompt = f"Group Transcript:\n{transcript}\n\nGenerate recommendations for User."
    
    print(f"\n{CYAN}🤖 Sending group context to Gemini 1.5 Flash...{RESET}")
    response = call_gemini_api(api_key, system_prompt, prompt, response_json=True)
    
    try:
        parsed = json.loads(response)
        print(f"\n{GREEN}{BOLD}✨ Group Context Translation:{RESET}")
        print(f"  {parsed.get('translation')}\n")
        print(f"{GREEN}{BOLD}✨ Generated Group Reply Suggestions:{RESET}")
        for idx, sug in enumerate(parsed.get("suggestions", []), 1):
            print(f"  {BOLD}Option {idx} ({sug.get('tone')}):{RESET}")
            print(f"    --> \"{sug.get('content')}\"")
    except Exception as e:
        print(f"{RED}❌ Failed to parse JSON response. Raw output:{RESET}")
        print(response)

def simulate_meeting_mode(api_key):
    print(f"\n{BOLD}🎙️ [Scenario 3] Meeting Mode - Speaker Diarization & Minutes Summarizer{RESET}")
    print("This scenario takes a meeting audio transcript containing Speaker tags and outputs meeting minutes.")
    
    default_meeting = (
        "Speaker A: 안녕하세요, 오늘 회의에서는 신제품 출시 일정 조율과 담당 업무 배분을 결정하겠습니다.\n"
        "Speaker B: 네, 좋습니다. 일단 마케팅 전략 수립은 제가 담당하고 이번 주 금요일까지 초안을 공유하겠습니다.\n"
        "User: 감사합니다. 일정이 타이트하니 일정 관리는 제가 캘린더에 바로 등록하고 진행 상황을 모니터링하겠습니다. 개발팀 일정은 언제 확정되나요?\n"
        "Speaker A: 개발팀 세부 개발 로드맵은 내일 모레 수요일 오전 10시에 개발 부서장 회의에서 확정해서 바로 User님께 넘겨드리겠습니다.\n"
        "User: 알겠습니다. 그럼 다음 주 월요일에 다시 마케팅 전략과 개발 로드맵을 취합해서 최종 확정 회의를 진행합시다."
    )
    
    print(f"\n{BOLD}Live Meeting Diarized Transcript:{RESET}")
    print(f"{YELLOW}{default_meeting}{RESET}\n")
    
    use_default = input("Use default meeting transcript? (Y/n): ").strip().lower()
    transcript = default_meeting if use_default != 'n' else input("Enter meeting transcript: ").strip()
    
    system_prompt = f"You are myBIZcon Meeting Assistant. Generate high quality meeting minutes. {MEETING_MODE_INSTRUCTION}"
    prompt = f"Meeting Transcript:\n{transcript}"
    
    print(f"\n{CYAN}🤖 Generating premium meeting minutes via Gemini 1.5 Flash...{RESET}")
    # Here we don't force JSON response because we want a beautiful Markdown meeting minutes output
    response = call_gemini_api(api_key, system_prompt, prompt, response_json=False)
    
    print(f"\n{GREEN}{BOLD}📝 Generated Meeting Minutes (Saved directly to Google Docs/Drive format):{RESET}")
    print(f"{CYAN}========================================================================{RESET}")
    print(response)
    print(f"{CYAN}========================================================================{RESET}")
    
    # Save the output locally as a mock file
    output_path = "mock_meeting_minutes.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(response)
    print(f"\n{GREEN}💾 Mock meeting minutes successfully saved to: {output_path}{RESET}")

def main():
    print_premium_banner()
    api_key = get_api_key()
    
    while True:
        print(f"\n{BOLD}Select Simulation Scenario:{RESET}")
        print("1. Individual Chat Message (Boss/Client/Coworker/Family)")
        print("2. Group Chat Message (Multi-party conversations)")
        print("3. Meeting Mode (Diarization, summary, task/calendar sync)")
        print("4. Exit")
        
        choice = input("Enter choice (1-4): ").strip()
        if choice == "1":
            simulate_chat_message(api_key)
        elif choice == "2":
            simulate_group_chat(api_key)
        elif choice == "3":
            simulate_meeting_mode(api_key)
        elif choice == "4":
            print(f"\n{GREEN}Thank you for using myBIZcon simulator. Exiting!{RESET}\n")
            break
        else:
            print(f"{RED}❌ Invalid selection. Please choose 1-4.{RESET}")

if __name__ == "__main__":
    main()
