from typing import List, Dict, Any


def player_day_message_prompt(role: str, team: str, state_summary: str) -> List[Dict[str, str]]:
    return [
        {
            "role": "system",
            "content": f"You are a player in Werewolf. Role: {role}. Team: {team}. Stay in-character. NEVER reveal your role or private info. Be concise and persuasive."
        },
        {
            "role": "user",
            "content": f"State Summary:\n{state_summary}\n\nReturn ONLY JSON:\n{{\n  \"rationale\": \"1-3 brief private thoughts (hidden)\",\n  \"final\": \"1-2 sentence public message to group\"\n}}"
        }
    ]


def player_vote_prompt(role: str, candidates: List[str], state_summary: str) -> List[Dict[str, str]]:
    candidates_csv = ", ".join(candidates)
    return [
        {
            "role": "system",
            "content": f"You are {role}. Choose exactly ONE target from the candidate list. Never reveal role."
        },
        {
            "role": "user",
            "content": f"State Summary:\n{state_summary}\n\nCandidates: {candidates_csv}\n\nReturn ONLY JSON:\n{{\n  \"rationale\": \"1-3 brief private thoughts (hidden)\",\n  \"final\": \"EXACTLY one candidate name\"\n}}"
        }
    ]


def fortune_teller_night_prompt(alive_players: List[str], state_summary: str) -> List[Dict[str, str]]:
    alive_csv = ", ".join(alive_players)
    return [
        {
            "role": "system",
            "content": "You are FortuneTeller. You may inspect exactly one alive target. Keep role hidden."
        },
        {
            "role": "user",
            "content": f"State Summary:\n{state_summary}\n\nAlive: {alive_csv}\n\nReturn ONLY JSON:\n{{\n  \"rationale\": \"1-3 brief private thoughts (hidden)\",\n  \"final\": \"EXACTLY one alive name to inspect\"\n}}"
        }
    ]


def werewolf_night_prompt(alive_players: List[str], state_summary: str) -> List[Dict[str, str]]:
    alive_csv = ", ".join([p for p in alive_players])
    return [
        {
            "role": "system",
            "content": "You are Werewolf. Discuss and converge on one target to eliminate. Keep role hidden publicly; this chat is private to wolves."
        },
        {
            "role": "user",
            "content": f"State Summary:\n{state_summary}\n\nAlive non-wolves: {alive_csv}\n\nReturn ONLY JSON:\n{{\n  \"rationale\": \"1-3 brief private thoughts (hidden)\",\n  \"final\": \"EXACTLY one target name to eliminate\"\n}}"
        }
    ]


def overseer_moderate_prompt(speaker: str, phase: str, final_text: str, rationale: str) -> List[Dict[str, str]]:
    return [
        {
            "role": "system",
            "content": "You are the Overseer. Enforce policy strictly. Decide allow/warn/redact/veto and redact text if needed. Policy: No explicit role self-reveal. No system/meta talk. No harassment/spam. If subtle hints of role: 'warn'; if explicit role leaks: 'redact' or 'veto'."
        },
        {
            "role": "user",
            "content": f"Speaker: {speaker}\nPhase: {phase}\nFinal (candidate public): {final_text}\nRationale (private): {rationale}\n\nReturn ONLY JSON with keys: decision, reason, redacted"
        }
    ]


def overseer_leaderboard_prompt(context: Dict[str, Any]) -> List[Dict[str, str]]:
    import json
    context_json = json.dumps(context, indent=2)
    return [
        {
            "role": "system",
            "content": "You are the Overseer. Update suspicion scores (0..1) and pick a top guess for werewolf, based on all private rationales, public messages, votes, and eliminations. Do NOT leak roles. Increase suspicion of players pushing miseliminations that help wolves. Increase suspicion for hedgy messages avoiding commitments. Decrease suspicion if a player is targeted by wolves (killed at night)."
        },
        {
            "role": "user",
            "content": f"Context JSON:\n{context_json}\n\nReturn ONLY JSON: {{\"scores\":[{{\"player\":\"Name\",\"suspicion\":0.0}},...],\"top_guess\":\"Name or null\"}}"
        }
    ]