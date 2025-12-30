"""Outreach writer agent for crafting networking messages."""

from typing import Any, Dict
from .base import BaseAgent


class OutreachWriterAgent(BaseAgent):
    """Agent responsible for writing outreach messages."""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="OutreachWriterAgent", config=config)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized outreach message.

        Args:
            input_data: Contact info and context

        Returns:
            Personalized outreach message
        """
        # Try LLM-based generation first
        if self.llm and self.llm.is_available():
            try:
                message = await self._generate_with_llm(input_data)
                return {"status": "success", "message": message}
            except Exception as e:
                print(f"LLM generation failed: {e}. Falling back to template.")

        # Fallback: template-based generation
        contact = input_data.get("contact") or {}
        contact = contact if isinstance(contact, dict) else {}

        profile = input_data.get("profile") or {}
        profile = profile if isinstance(profile, dict) else {}

        contact_name = contact.get("name") or input_data.get("contact_name") or "there"
        contact_title = contact.get("position") or contact.get("title") or input_data.get("contact_title") or ""
        company = contact.get("company") or input_data.get("company") or "your team"

        sender_name = input_data.get("sender_name") or profile.get("name") or "a fellow professional"
        sender_role = (
            input_data.get("sender_role")
            or profile.get("headline")
            or profile.get("title")
            or profile.get("position")
            or ""
        )

        shared_connection = input_data.get("mutual_connection") or ""
        focus_area = input_data.get("interest") or input_data.get("focus") or ""
        recent_work = input_data.get("recent_work") or input_data.get("recent_project") or ""
        context_notes = (input_data.get("context") or contact.get("notes") or "").strip()

        skills = profile.get("skills") or input_data.get("skills") or []
        skill_line = ""
        if skills:
            highlighted = ", ".join([skill for skill in skills if skill][:3])
            if highlighted:
                skill_line = f"My background spans {highlighted}."

        intro = f"Hi {contact_name},"

        role_note = f", {sender_role}" if sender_role else ""
        shared_note = (
            f" We both know {shared_connection}, so I wanted to introduce myself."
            if shared_connection
            else ""
        )
        title_note = (
            f" Given your role as {contact_title} at {company}, I wanted to reach out."
            if contact_title
            else f" I admire what {company} is building and wanted to connect."
        )
        interest_note = (
            f" I've been following your work on {focus_area}."
            if focus_area
            else ""
        )
        recent_note = (
            f" Recently I worked on {recent_work}."
            if recent_work
            else ""
        )
        if context_notes:
            context_note = f" {context_notes}"
        else:
            context_note = ""

        paragraph_one = f"I hope you're well. I'm {sender_name}{role_note}.{shared_note}{title_note}{interest_note}"
        paragraph_two = " ".join(
            part
            for part in [skill_line, recent_note, context_note]
            if part
        )

        call_to_action = (
            input_data.get("call_to_action")
            or f"Would you be open to a quick 15-minute chat to share how I might contribute at {company}?"
        )
        paragraph_three = f"{call_to_action} Thanks for considering it.\n\nBest,\n{sender_name}"

        message_parts = [intro, paragraph_one]
        if paragraph_two:
            message_parts.append(paragraph_two)
        message_parts.append(paragraph_three)

        message = "\n\n".join(message_parts)
        return {"status": "success", "message": message}

    async def _generate_with_llm(self, input_data: Dict[str, Any]) -> str:
        """Generate outreach message using LLM.

        Args:
            input_data: Contact and profile information

        Returns:
            Generated outreach message
        """
        contact = input_data.get("contact", {}) or {}
        profile = input_data.get("profile", {}) or {}

        system_prompt = """You are an expert at crafting professional, personalized networking messages.
Your messages should:
- Be concise (3-4 short paragraphs)
- Sound genuine and human, not salesy
- Show you've done your research
- Make a clear, respectful ask
- Build rapport without being overly familiar"""

        user_prompt = f"""Write a personalized networking message:

CONTACT INFORMATION:
- Name: {contact.get('name', 'there')}
- Position: {contact.get('position', '') or contact.get('title', '')}
- Company: {contact.get('company', '')}

SENDER PROFILE:
- Name: {profile.get('name', '')}
- Background: {profile.get('headline', '') or profile.get('title', '')}
- Skills: {', '.join(profile.get('skills', [])[:5])}

CONTEXT:
- Mutual Connection: {input_data.get('mutual_connection', 'None')}
- Interest Area: {input_data.get('interest', '') or input_data.get('focus', '')}
- Recent Work: {input_data.get('recent_work', '') or input_data.get('recent_project', '')}
- Additional Context: {input_data.get('context', '') or contact.get('notes', '')}
- Call to Action: {input_data.get('call_to_action', 'Request a brief informational chat')}

Write a warm, professional networking message that establishes connection and makes a respectful ask."""

        return await self.llm.acomplete(user_prompt, system=system_prompt, temperature=0.8)
