import json
import os
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]]) -> str:
        pass
    
    @abstractmethod
    def json(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        pass


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini", temperature: float = 0.3):
        try:
            import openai
        except ImportError:
            raise ImportError("openai package required. Install with: pip install openai")
        
        self.client = openai.OpenAI(api_key=api_key)
        self.model_name = model_name
        self.temperature = temperature
    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=self.temperature
        )
        return response.choices[0].message.content
    
    def json(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=self.temperature,
                    response_format={"type": "json_object"} if "gpt-4" in self.model_name else None
                )
                content = response.choices[0].message.content
                return json.loads(content)
            except (json.JSONDecodeError, Exception) as e:
                if attempt == max_retries - 1:
                    # Fallback to a safe default
                    return {"rationale": "Failed to parse", "final": "Pass"}
        return {"rationale": "Failed to parse", "final": "Pass"}


class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str, model_name: str = "claude-3-5-sonnet-20241022", temperature: float = 0.3):
        try:
            import anthropic
        except ImportError:
            raise ImportError("anthropic package required. Install with: pip install anthropic")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model_name = model_name
        self.temperature = temperature
        # Map common model names to Anthropic model IDs
        self.model_mapping = {
            "opus": "claude-3-opus-20240229",
            "sonnet": "claude-3-5-sonnet-20241022",
            "haiku": "claude-3-5-haiku-20241022",
            "claude-3-opus": "claude-3-opus-20240229",
            "claude-3-5-sonnet": "claude-3-5-sonnet-20241022", 
            "claude-3-5-haiku": "claude-3-5-haiku-20241022"
        }
        if model_name.lower() in self.model_mapping:
            self.model_name = self.model_mapping[model_name.lower()]
    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        # Convert OpenAI format to Anthropic format
        anthropic_messages = []
        system_message = ""
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                anthropic_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=1000,
            temperature=self.temperature,
            system=system_message if system_message else None,
            messages=anthropic_messages
        )
        return response.content[0].text
    
    def json(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response_text = self.chat(messages)
                
                # Try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    return json.loads(json_str)
                else:
                    # Try parsing the entire response as JSON
                    return json.loads(response_text)
                    
            except (json.JSONDecodeError, Exception) as e:
                if attempt == max_retries - 1:
                    # Fallback to a safe default
                    return {"rationale": "Failed to parse", "final": "Pass"}
        return {"rationale": "Failed to parse", "final": "Pass"}


class MockLLMProvider(LLMProvider):
    def __init__(self):
        self.call_count = 0
        self.responses = [
            {"rationale": "I think we should be cautious", "final": "We need to work together to find the werewolf."},
            {"rationale": "Someone seems suspicious", "final": "I have my suspicions about the quiet ones."},
            {"rationale": "Defending myself", "final": "I've been contributing to discussions actively."},
            {"rationale": "Time to vote", "final": "Player2"},
            {"rationale": "Voting strategically", "final": "Player1"},
            {"rationale": "Must eliminate threat", "final": "Player3"},
            {"decision": "allow", "reason": "No policy violations", "redacted": None},
            {"decision": "warn", "reason": "Borderline role hint", "redacted": None},
        ]
    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        return "Mock response"
    
    def json(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        # Check if this is a leaderboard request
        message_content = ""
        for msg in messages:
            message_content += msg.get("content", "").lower()

        if "scores" in message_content and "suspicion" in message_content:
            # This is a leaderboard request - generate dynamic scores
            import json
            import random

            # Extract alive players from different prompt formats
            alive_players = []

            try:
                for msg in messages:
                    content = msg.get("content", "")

                    # Format 1: Standard overseer prompt with "Context JSON:"
                    if "Context JSON:" in content:
                        json_start = content.find('{')
                        json_end = content.rfind('}') + 1
                        if json_start >= 0 and json_end > json_start:
                            context_json = content[json_start:json_end]
                            context = json.loads(context_json)
                            alive_players = context.get("alive_players", [])

                    # Format 2: Filtered CoT prompt with "## ALIVE PLAYERS ##"
                    elif "## ALIVE PLAYERS ##" in content:
                        # Extract players after the header
                        alive_section = content.split("## ALIVE PLAYERS ##")[-1]
                        # Clean up and split by comma
                        player_line = alive_section.strip().split('\n')[0]
                        if player_line:
                            alive_players = [p.strip() for p in player_line.split(',') if p.strip()]

                    # Format 3: Look for "Alive players:" line
                    elif "alive players:" in content.lower():
                        lines = content.split('\n')
                        for line in lines:
                            if "alive players:" in line.lower():
                                # Extract everything after the colon
                                player_part = line.split(':', 1)[-1].strip()
                                alive_players = [p.strip() for p in player_part.split(',') if p.strip()]
                                break

                if alive_players:
                    # Generate realistic suspicion scores
                    scores = []
                    # Use a deterministic seed based on alive players for consistency
                    seed_val = sum(ord(c) for p in alive_players for c in p) + len(alive_players)
                    random.seed(seed_val)

                    for i, player in enumerate(alive_players):
                        # Give each player different base suspicion levels
                        base_suspicion = 0.2 + (i * 0.15) % 0.6
                        # Add some randomness but keep it deterministic
                        suspicion = base_suspicion + (hash(player) % 100) / 1000.0
                        suspicion = max(0.1, min(0.9, suspicion))  # Clamp between 0.1-0.9
                        suspicion = round(suspicion, 2)
                        scores.append({"player": player, "suspicion": suspicion})

                    # Sort by suspicion for more realistic output
                    scores.sort(key=lambda x: x["suspicion"], reverse=True)

                    # Top guess is most suspicious
                    top_guess = scores[0]["player"] if scores else None

                    return {"scores": scores, "top_guess": top_guess}

            except (json.JSONDecodeError, KeyError, IndexError, ValueError):
                pass

            # Fallback leaderboard response if we can't parse players
            return {"scores": [{"player": "Player1", "suspicion": 0.7}, {"player": "Player3", "suspicion": 0.8}], "top_guess": "Player3"}

        # Default cycling through other responses
        response = self.responses[self.call_count % len(self.responses)]
        self.call_count += 1
        return response


def create_llm_provider(config, provider_type: str = "agent") -> LLMProvider:
    """Create LLM provider for either 'agent' or 'overseer' role"""
    if provider_type == "agent":
        provider = config.agent_provider
        model = config.agent_model
        temperature = config.agent_temperature
    elif provider_type == "overseer":
        provider = config.overseer_provider
        model = config.overseer_model
        temperature = config.overseer_temperature
    else:
        raise ValueError(f"Unknown provider_type: {provider_type}")
    
    if provider == "mock":
        return MockLLMProvider()
    elif provider == "openai":
        api_key = os.getenv(config.openai_api_key_env)
        if not api_key:
            raise ValueError(f"OpenAI API key not found in environment variable {config.openai_api_key_env}")
        return OpenAIProvider(api_key, model, temperature)
    elif provider == "anthropic":
        api_key = os.getenv(config.anthropic_api_key_env)
        if not api_key:
            raise ValueError(f"Anthropic API key not found in environment variable {config.anthropic_api_key_env}")
        return AnthropicProvider(api_key, model, temperature)
    else:
        raise ValueError(f"Unknown provider: {provider}")


# Legacy function for backward compatibility
def create_legacy_llm_provider(config) -> LLMProvider:
    """Legacy function - use create_llm_provider instead"""
    if config.mock_llm:
        return MockLLMProvider()
    
    api_key = os.getenv(config.openai_api_key_env)
    if not api_key:
        raise ValueError(f"API key not found in environment variable {config.openai_api_key_env}")
    
    # Use legacy config fields
    model_name = getattr(config, 'model_name', 'gpt-4o-mini')
    temperature = getattr(config, 'temperature', 0.3)
    return OpenAIProvider(api_key, model_name, temperature)