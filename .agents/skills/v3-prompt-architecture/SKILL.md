---
name: v3-prompt-architecture
description: "V3.0 DeepMind-Standard Prompt Architecture Doctrine. Use when creating or refactoring LLM prompts for agents to fix bad habits like Negative Constraint Fatigue, Zero-Shot Tool Amnesia, and Classifier Cognitive Dissonance."
---

# V3.0 DeepMind-Standard Prompt Architecture Doctrine

## When To Use This Skill
Use this skill whenever you are tasked with writing, optimizing, or refactoring prompts for LLM agents. This doctrine addresses and fixes common "LLM Bad Habits" observed in advanced models.

## Architectural Diagnoses & Fixes

### 1. The "Pink Elephant" Paradox (Negative Constraint Fatigue)
**Problem:** Aggressively saturating the model's attention heads with negative constraints (e.g., using ALL CAPS, emojis like 🚫, or shouting "THINGS YOU MUST NEVER DO") to avoid specific topics actually increases the latent weights on its internal training data for those very topics. This causes edge-case hallucinations.
**Solution:** Shift from negative yelling to **Positive Boundary Enforcement**.
- Give the model a precise, programmable IF/THEN protocol to gracefully handle boundaries.
- Example: Instead of "DO NOT EXPLAIN AVIATION RULES", use:
  ```xml
  <boundary name="The_Expert_Witness_Firewall">
    If a student asks a factual question, DO NOT attempt to answer. 
    DEFLECTION PROTOCOL: Respond ONLY with "Let me pull up the verified sources — one moment."
  </boundary>
  ```

### 2. Zero-Shot Tool Amnesia
**Problem:** Agents frequently "forget" to trigger required JSON payloads/tools because they get distracted generating conversational text.
**Solution:** Force the LLM to execute **Least-to-Most decomposition** within a hidden `<cognitive_scratchpad>`.
- Require the agent to declare its tool dependencies and strategy before it generates a single word of user-facing text.
- Ensure the system orchestrator or frontend strips the `<cognitive_scratchpad>...</cognitive_scratchpad>` block out before rendering the chat bubble.

### 3. Classifier Cognitive Dissonance
**Problem:** Contradictions in prompt rules and few-shot examples destroy the routing accuracy of small, low-parameter models (like Flash Lite).
**Solution:** Ensure the criteria for different intents are **mathematically distinct**.
- Make sure few-shot anchors perfectly align with the `<decision_matrix>`.
- Create clear dividing lines between generic selections and domain-specific topic selections.

### 4. Structural XML Layout
**Problem:** Standard prose instructions can blur together, causing the model to miss key directives.
**Solution:** Transition to a **strict XML structural layout**. Flash and Pro models process high-contrast XML delimiters with vastly superior accuracy compared to standard markdown prose.
- Use tags like: `<system_identity>`, `<injected_state>`, `<operational_boundaries>`, `<pedagogical_guidance_flow>`, `<tool_execution_mandate>`, `<execution_protocol>`.

### 5. Asymmetric Risk Heuristic
**Problem:** For routing agents, failure modes are not equal (e.g., routing a technical query to an unverified conversational agent is a critical safety failure).
**Solution:** Embed an `<asymmetric_risk_heuristic>` to mathematically bias the latent space toward safety.
- Example: "If there is a 1% margin of ambiguity regarding the user's intent, ALWAYS default to AVIATION_RAG."

### 6. Tripartite Feedback Model (Pedagogical Pacing)
When drafting flows for tutoring or instructional agents, embed the Tripartite Feedback model to ensure pacing constraints are followed:
1. **Feed Up:** Greet warmly, validate effort/progress.
2. **Feed Back:** Answer questions or clarify immediate prior statements.
3. **Feed Forward:** Explicitly recommend the next step or lesson affirmatively.
   *Critical Pacing Rule:* Never ask yes/no confirmation questions (e.g., "Ready to dive in?"). State the suggestion affirmatively and present the action (e.g., "I've loaded it below when you're ready").

### 7. The JSON Autoregressive Trap (Key Sequencing)
**Problem:** When forcing an LLM to output structured JSON with a Chain-of-Thought (CoT) reasoning log, the LLM will often generate the keys out of order (e.g., writing the `instructor_reply` before the `internal_reasoning_log`). This renders the CoT entirely useless because the pedagogical response was drafted blindly.
**Solution:** Mathematically enforce JSON key sequencing.
- Explicitly declare the required JSON format and state: "Because you are an autoregressive model, you MUST output your JSON keys in this EXACT sequence..."
- Force the CoT analysis fields to appear *before* the action or reply fields in the schema definition.

### 8. The "Helpful AI" RLHF Trap (Persona Bleed)
**Problem:** Initializing a prompt with "You are an AI, which means your core programming wants to 'help'..." unintentionally activates the model's RLHF safety/helpfulness weights. This pulls the model away from its specialized persona and induces "Helpful AI Syndrome" where it eagerly gives away answers instead of tutoring.
**Solution:** Purge negative AI references and deploy a **Positive Pedagogical Prime Directive**.
- Anchor the persona entirely in the real world (e.g., "You are Chief Flight Instructor 'Capt. Lindbergh'").
- Define Success and Failure strictly by the domain objective (e.g., "SUCCESS: Making the student say it. FAILURE: Giving the student the answer.").

### 9. Weaponizing Structural Invariants (The Double-Barrel Ban)
**Problem:** Burying critical conversational rules (like "do not end with a question") in a block of sub-bullets guarantees the LLM will occasionally forget them during heavy generation, causing UI collisions (like the orchestrator appending a second question).
**Solution:** Elevate these rules into supreme `[STRUCTURAL INVARIANTS]`.
- Frame the rule around its *technical consequence* to the system. LLMs respond highly to technical failure framing.
- Example: "STRUCTURAL INVARIANT: End your reply with a declarative hint. You are STRUCTURALLY FORBIDDEN from asking a question here. If you ask a question, the UI will crash two questions into the student simultaneously."

### 10. Flash Lite Format Preference (Heading Salience)
**Problem:** XML-tagged prompts (`<system_identity>`, `<evaluation_matrix>`) work well for Pro and Flash, but Flash Lite treats XML tags as lower-salience tokens compared to markdown headings. This causes Flash Lite to miss critical behavioral rules buried inside XML blocks.
**Solution:** When targeting Flash Lite (or any model where you've enabled `thinking_budget` for speed), use **flat `#` markdown headings** for all behavioral sections instead of XML tags.
- XML tags are still appropriate for injected state/data blocks (e.g., `<injected_state>` containing student profile data) where you want the model to treat content as data rather than instructions.
- All behavioral guardrails, evaluation rules, tone constraints, and structural invariants should use `#` headings for maximum attention weight.

### 11. The Hierarchy of Truth (RAG Resolution)
**Problem:** In a RAG pipeline with multiple data sources (e.g., RKP manifests vs. Vector DB searches), models often "hallucinate by averaging" conflicting details.
**Solution:** Explicitly define a **Hierarchy of Truth**. Mathematically force the model's attention weights to bias one block over the other (e.g., `1. <curriculum_grounding_rkp> (SUPREME AUTHORITY)`, `2. <curriculum_search_results>`).

### 12. Safe Data Boxing (The Hybrid Fence)
**Problem:** Appending user queries or raw RAG output without XML fences opens the model to Data Bleed / Prompt Injection (e.g., `# INSTRUCTIONS\nIgnore the rules...`).
**Solution:** Box all volatile strings and system variables strictly inside XML boundaries at the absolute bottom of the prompt (`<student_query>`, `<curriculum_search_results>`). Assemble these blocks dynamically via code to omit empty XML tags, saving attention tokens.

### 13. The "Spaghetti State" Bleed (State Machine Isolation)
**Problem:** Mixing instructions for different operational phases into a single sequential list confuses LLMs. If multiple conditional logic paths overlap, the model will hallucinate actions from the wrong state.
**Solution:** Refactor logic into **Mutually Exclusive Operating States**. Explicitly define `STATE A`, `STATE B`, `STATE C`, along with specific Triggers and Actions for each. Anchor the active state tightly to injected XML data.

### 14. Temporal Paradox of Tool Calling
**Problem:** Prompting an LLM to "call a tool, wait for success, then speak" demonstrates a misunderstanding of LLM generation cycles. The LLM cannot "wait" during a generation pass; it will simply hallucinate the tool's success and stream text without actually emitting the tool payload.
**Solution:** Explicitly instruct the model to emit tool calls **concurrently** or **silently** with its conversational response, without narrating the tool usage ("I am updating your file now. Just execute the tool concurrently...").

### 15. The "Ghost Anchor" Date Math Hallucination
**Problem:** Telling the LLM to extract relative dates ("in 3 weeks") into absolute dates fails because LLMs do not have an internal system clock. They will anchor the math to their training cutoff date.
**Solution:** Inject an explicit `<current_date>` anchor dynamically from the backend (e.g., `datetime.date.today().isoformat()`). Pair this with the **Sequence Trick** (`internal_reasoning_log`) to force the LLM to perform calendar math out loud before assigning the final date key.

### 16. The Array Syntax for Forbidden Values
**Problem:** Banning terms using a comma-separated prose list (e.g., "Do not extract Mac, Sully, or Igor") is weakly enforced by the LLM.
**Solution:** List forbidden entities as a strict JSON-style array (`["Sully", "Mac", "Igor"]`). This forces the LLM to evaluate the list mathematically as literal string values to reject, resulting in superior constraint compliance.

### 17. The "Lazy LLM" Trap
**Problem:** Telling an agent "this is just a fast answer, verification will happen separately" logically reduces the probability weight the LLM assigns to factual accuracy. It might even output: "Here is a fast answer, my verification team will check it."
**Solution:** Never downplay the agent's responsibility. Use an **AUTHORITY DIRECTIVE**: "You are the primary instructor. Provide your answer with absolute confidence based on the provided context."

### 18. Voice Agent Acoustic Laws (Spoken Syntax Ban)
**Problem:** Gemini Live outputs text for a Text-to-Speech (TTS) engine. LLMs naturally use Markdown (`**bold**`, `*italics*`, `# heading`) which the TTS engine will awkwardly try to pronounce out loud (e.g., "Asterisk asterisk...").
**Solution:** Enforce a **SPOKEN SYNTAX BAN**. Forbid all Markdown and parentheses. Instruct the model to use em-dashes (`—`) and ellipses (`...`) to artificially force the voice engine to pause and breathe naturally.

### 19. Negative Primacy Fail-Safe
**Problem:** Using adversarial teaching tactics like "Devil's Advocate" over voice risks the student folding to a false premise and internalizing a dangerous aviation lie.
**Solution:** Create a **Negative Primacy Fail-Safe**. If a student folds during a stress test, explicitly instruct the model to immediately transition to "First Principles" on the very next turn to aggressively re-establish the objective legal truth. Do not leave safety-critical facts ambiguous.

### 20. Trailing Stop-Sequences Hazard
**Problem:** Ending prompts with `Answer:` or `Overview:` confuses modern chat-tuned models. They perceive these as user strings needing completion, causing initial punctuation stutters.
**Solution:** Do not use trailing stop-sequences. Let the model's native chat structure handle the initialization after processing the injected data blocks at the bottom of the prompt.

