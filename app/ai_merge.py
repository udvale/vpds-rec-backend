"""
Merge multiple React component snippets into one file via OpenAI.
Falls back to regex merging when AI is disabled or the call errors out.
"""
import os
import re
from typing import List
from dotenv import load_dotenv

load_dotenv()  
try:
    from openai import OpenAI  # type: ignore
    _client = OpenAI()  # API key pulled from env

    def _llm_call(**kwargs):
        return _client.chat.completions.create(**kwargs)

except ImportError:
    import openai  # type: ignore

    def _llm_call(**kwargs):
        return openai.ChatCompletion.create(**kwargs)


# ────────────────── prompt builder ──────────────────
def build_merge_prompt(snippets: List[str], query: str, export_name: str) -> str:
    """Return a system+user prompt string for the LLM."""
    snippet_block = ""
    for i, snip in enumerate(snippets, 1):
        snippet_block += f"\n### Component {i}\n```tsx\n{snip}\n```\n"

    prompt = f"""
USER REQUEST: "{query}"
EXPORT FUNCTION NAME: {export_name}

You need to create ONE production‑ready React component by **merging** the snippets below.

{snippet_block}

OUTPUT RULES – STRICT
• Wrap the ENTIRE file in one ```tsx fenced block.
• Import ONLY components that appear in the JSX.
• Every imported component (e.g. Avatar) must appear ≥ 1× in the JSX.
• Declare every identifier you reference (e.g. const id = useId();).
• Close ALL JSX tags and string / template literals.
• Export exactly one React function named {export_name}.
""".strip()
    return prompt



# ────────────────── response cleaner ──────────────────
def extract_code_from_response(text: str) -> str:
    """Pull the first fenced code block or best‑guess component from LLM output."""
    # 1) fenced block with tsx/typescript
    match = re.search(r"```(?:tsx|typescript|jsx|javascript|ts|js)?\n([\s\S]*?)\n```", text)
    if match:
        return match.group(1).strip()

    # 2) anything that looks like "import … export default function"
    match = re.search(r"(import[\s\S]+?export default function[\s\S]+?^})", text, re.MULTILINE)
    if match:
        return match.group(1).strip()

    # 3) Look for just the export function part
    match = re.search(r"(export default function[\s\S]+?^})", text, re.MULTILINE)
    if match:
        # Add basic imports
        code = match.group(1).strip()
        if not code.startswith('import'):
            code = "import React from 'react';\n" + code
        return code

    # 4) fallback: raw text minus triple back‑ticks
    return text.replace("```", "").strip()


# ────────────────── public entry point ──────────────────
def merge_components_with_ai(
    snippets: List[str], query: str, export_name: str
) -> str:
    """
    Try to merge snippets via OpenAI.  On failure, fall back to regex merge.
    """
    from .manual_merge import merge_variants  

    # Bail out early if no key or AI disabled
    if not os.getenv("OPENAI_API_KEY") or os.getenv("USE_AI_MERGING", "true").lower() != "true":
        print("AI disabled or no API key, falling back to manual merge")
        return merge_variants(snippets, export_name)

    try:
        prompt = build_merge_prompt(snippets, query, export_name)
        
        print(f"🤖 Attempting AI merge for query: '{query}'")
        print(f"📝 Components to merge: {len(snippets)} snippets")

        response = _llm_call(
            model="gpt-4o-mini",           
            temperature=0.1,
            max_tokens=2500,  # Increased for longer components
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert React/TypeScript engineer who creates "
                        "production-ready components by intelligently merging multiple "
                        "component snippets. You understand UI/UX patterns and create "
                        "cohesive, accessible, and well-structured components. "
                        "Always return complete, working TSX code with proper imports."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )

        # Handle different OpenAI SDK versions
        raw = ""
        try:
            # SDK 1.x
            raw = response.choices[0].message.content
        except AttributeError:
            # SDK 0.x
            raw = response.choices[0]["message"]["content"]
        
        if not raw:
            raise Exception("AI returned empty response")

        print("🔎 RAW AI RESPONSE (first 500 chars):\n", raw[:500])

        merged_code = extract_code_from_response(raw)

        # ---------- HARD CHECK: every import must appear in JSX ----------
        imports = re.findall(r"import\s+\{([^}]+)\}\s+from '@visa/nova-react'", merged_code)
        imported = {name.strip() for grp in imports for name in grp.split(",")}
        unused = [name for name in imported if re.search(rf"<\s*{name}\b", merged_code) is None]

        if unused:
            raise RuntimeError(f"Unused imports returned by AI: {unused}")

        
        if not merged_code or len(merged_code) < 50:
            raise Exception("AI returned unusable code")
            
        print("✅ AI merge successful")
        return merged_code

    except Exception as exc:
        print(f"❌ AI merge failed: {exc}")
        print("🔄 Falling back to manual merge...")
        return merge_variants(snippets, export_name)