"""AI prompts and templates for various agents."""

# Profile parsing prompts
PROFILE_PARSE_PROMPT = """
Extract structured information from the following resume:

{resume_text}

Return a JSON object with the following fields:
- name
- email
- phone
- location
- skills (array)
- experience_years
- work_history (array of objects with: company, title, duration, description)
- education (array of objects with: school, degree, field, year)
- summary
"""

# Job ranking prompts
JOB_RANK_PROMPT = """
Given the user profile and job posting below, provide a match score from 0-100.

User Profile:
{profile}

Job Posting:
{job}

Consider:
1. Skills match
2. Experience level
3. Location preferences
4. Industry alignment
5. Job type (full-time, contract, etc.)

Return JSON with: score, reasoning, matched_skills, missing_skills
"""

# Resume tailoring prompts
RESUME_TAILOR_PROMPT = """
Tailor the resume for the specific job posting.

Original Resume:
{resume}

Target Job:
{job}

Instructions:
1. Emphasize relevant skills and experiences
2. Use keywords from the job description
3. Quantify achievements where possible
4. Keep it concise and ATS-friendly
5. Maintain truthfulness - don't add fake experience

Return the tailored resume text.
"""

# Cover letter generation prompts
COVER_LETTER_PROMPT = """
Write a compelling cover letter for the job application.

User Profile:
{profile}

Job Details:
{job}

Company Research:
{company_info}

Guidelines:
1. Show enthusiasm for the role
2. Highlight relevant achievements
3. Explain why you're a good fit
4. Keep it to 3-4 paragraphs
5. Professional but personable tone

Return the cover letter text.
"""

# Outreach message prompts
OUTREACH_MESSAGE_PROMPT = """
Write a personalized networking message to connect with this person.

Contact Info:
{contact}

Context:
{context}

Guidelines:
1. Be genuine and specific
2. Mention a shared connection or interest
3. Keep it brief (2-3 short paragraphs)
4. Clear call-to-action
5. Professional but warm tone

Return the outreach message text.
"""

# Contact discovery prompts
CONTACT_DISCOVERY_PROMPT = """
Based on the company and role, suggest relevant people to contact:

Company: {company}
Role: {role}

Return JSON array of suggested contacts with:
- likely_title (e.g., "Hiring Manager", "Engineering Manager")
- department
- search_keywords
- priority (high, medium, low)
"""

# Interview prep prompts
INTERVIEW_PREP_PROMPT = """
Generate interview preparation materials for:

Job: {job_title} at {company}
Job Description: {job_description}
User Background: {user_profile}

Provide:
1. Likely interview questions (behavioral, technical, company-specific)
2. Suggested answers based on user's background
3. Questions to ask the interviewer
4. Key talking points about the user's experience
5. Company research highlights

Return structured JSON.
"""
