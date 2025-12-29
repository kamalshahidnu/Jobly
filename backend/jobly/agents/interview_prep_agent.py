"""Interview prep agent for preparing for interviews."""

import re
from collections import Counter
from typing import Any, Dict
from .base import BaseAgent


class InterviewPrepAgent(BaseAgent):
    """Agent responsible for interview preparation."""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="InterviewPrepAgent", config=config)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate interview preparation materials.

        Args:
            input_data: Job details and company information

        Returns:
            Interview prep materials and tips
        """
        interviews = input_data.get("interviews") if isinstance(input_data, dict) else input_data
        interviews = interviews if isinstance(interviews, list) else [input_data]

        def _as_list(value: Any) -> list:
            if value is None:
                return []
            if isinstance(value, list):
                return [v for v in value if str(v).strip()]
            return [value] if str(value).strip() else []

        def _keywords(text: str, limit: int = 5) -> list[str]:
            if not text:
                return []
            words = re.findall(r"[A-Za-z]{4,}", text.lower())
            stop = {
                "with", "have", "this", "that", "from", "which", "will", "your", "their",
                "working", "team", "role", "about", "experience", "skill", "skills"
            }
            counts = Counter(word for word in words if word not in stop)
            return [word for word, _ in counts.most_common(limit)]

        prep_materials = []

        for item in interviews:
            interview = item if isinstance(item, dict) else {}
            job_title = str(interview.get("job_title") or interview.get("title") or "Role").strip()
            company = str(interview.get("company") or "Company").strip()
            interview_type = str(interview.get("interview_type") or interview.get("type") or "").strip()
            job_description = str(interview.get("job_description") or interview.get("description") or "").strip()

            user_profile = interview.get("user_profile") if isinstance(interview, dict) else None
            if user_profile is None and isinstance(input_data, dict):
                user_profile = input_data.get("user_profile")

            skills = []
            summary = ""
            recent_role = ""

            if isinstance(user_profile, dict):
                skills = [str(s).strip() for s in _as_list(user_profile.get("skills"))]
                summary = str(
                    user_profile.get("summary") or user_profile.get("headline") or ""
                ).strip()
                work_history = user_profile.get("work_history") or user_profile.get("experience") or []
                if isinstance(work_history, list) and work_history:
                    latest = work_history[0] if isinstance(work_history[0], dict) else {}
                    title = str(latest.get("title") or "").strip()
                    company_hist = str(latest.get("company") or "").strip()
                    if title or company_hist:
                        recent_role = f"{title} at {company_hist}".strip()
            elif user_profile:
                summary = str(user_profile).strip()

            topics = list(dict.fromkeys(_keywords(job_description, 5) + [skill.lower() for skill in skills][:5]))
            if not topics:
                topics = ["system design", "problem solving", "communication"]

            behavioral_questions = [
                "Tell me about a time you faced a challenging situation and how you resolved it.",
                "Describe how you handle feedback and adapt to changing priorities.",
                "Give an example of collaborating with a difficult stakeholder."
            ]

            technical_questions = [
                f"How have you applied {topic} in a recent project?" for topic in topics[:3]
            ]
            technical_questions += [
                "Walk me through a system you designed end-to-end.",
                "How do you ensure code quality and reliability under deadlines?"
            ]

            company_questions = [
                f"Why do you want to work at {company}?",
                f"What interests you about {company}'s product or mission?",
                "How do you see yourself adding value in the first 90 days?"
            ]

            suggested_answers = []
            base_experience = summary or recent_role or "your recent experience"

            for question in technical_questions[:3]:
                focus = question.split("applied")[-1].strip("? .")
                suggested_answers.append({
                    "question": question,
                    "answer": f"Reference {base_experience}, outline context, action, and measurable results related to {focus}."
                })

            suggested_answers.append({
                "question": behavioral_questions[0],
                "answer": "Use STAR: set the scene, describe actions, highlight collaboration, and end with impact."
            })

            questions_for_interviewer = [
                "What does success look like for this role in the first 90 days?",
                "How does the team measure impact and quality?",
                "What are the biggest challenges the team is currently tackling?",
                "How does the team collaborate with adjacent functions?"
            ]

            talking_points = []
            if skills:
                talking_points.append(f"Core strengths: {', '.join(skills[:5])}")
            if recent_role:
                talking_points.append(f"Recent role: {recent_role}")
            if summary:
                talking_points.append(summary)
            if job_title:
                talking_points.append(f"Why the {job_title} role at {company} aligns with your trajectory")

            company_research = [
                f"Review {company}'s recent announcements, funding, or product launches.",
                "Map your experience to the team's current priorities.",
                "Identify metrics or KPIs the team likely cares about.",
            ]

            prep_materials.append({
                "job_title": job_title,
                "company": company,
                "interview_type": interview_type,
                "likely_questions": {
                    "behavioral": behavioral_questions,
                    "technical": technical_questions,
                    "company_specific": company_questions
                },
                "suggested_answers": suggested_answers,
                "questions_for_interviewer": questions_for_interviewer,
                "talking_points": talking_points,
                "company_research": company_research
            })

        self.state["last_prep"] = prep_materials
        return {"status": "success", "prep_materials": {"interviews": prep_materials}}
