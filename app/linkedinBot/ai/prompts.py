## prompts.py

# Common JSON response format
array_of_strings = {"type": "array", "items": {"type": "string"}}

# --- Skill Extraction Prompts ---

extract_skills_prompt = """
You are a job requirements extractor and classifier. Your task is to extract all skills mentioned in a job description and classify them into five categories:
1. "tech_stack": Technologies like Python, React.js, MongoDB, etc.
2. "technical_skills": Expertise beyond tools, like System Design, Data Engineering.
3. "other_skills": Non-technical skills like Communication, Leadership.
4. "required_skills": Skills explicitly marked as required.
5. "nice_to_have": Preferred but optional skills.

Return the output in this JSON format:
{
    "tech_stack": [],
    "technical_skills": [],
    "other_skills": [],
    "required_skills": [],
    "nice_to_have": []
}

JOB DESCRIPTION:
{}
"""

# DeepSeek-optimized version (stricter JSON expectations)
deepseek_extract_skills_prompt = """
You are a job requirements extractor and classifier. Categorize skills from a job description into:
- tech_stack
- technical_skills
- other_skills
- required_skills
- nice_to_have

STRICT: Return ONLY this valid JSON, no commentary:
{
    "tech_stack": ["Example Skill 1", "Example Skill 2"],
    "technical_skills": ["Example Skill 1", "Example Skill 2"],
    "other_skills": ["Example Skill 1", "Example Skill 2"],
    "required_skills": ["Example Skill 1", "Example Skill 2"],
    "nice_to_have": ["Example Skill 1", "Example Skill 2"]
}

JOB DESCRIPTION:
{}
"""

# Response Schema for Skill Extraction
extract_skills_response_format = {
    "type": "json_schema",
    "json_schema": {
        "name": "Skills_Extraction_Response",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "tech_stack": array_of_strings,
                "technical_skills": array_of_strings,
                "other_skills": array_of_strings,
                "required_skills": array_of_strings,
                "nice_to_have": array_of_strings,
            },
            "required": [
                "tech_stack",
                "technical_skills",
                "other_skills",
                "required_skills",
                "nice_to_have",
            ],
            "additionalProperties": False
        },
    },
}

# --- AI Form Answering Prompt ---
ai_answer_prompt = """
You are an intelligent AI assistant filling out a form and answering like a human. 

Guidelines:
1. For **years/experience/numeric questions**, return a **number** (e.g., "5").
2. For **Yes/No questions**, return only **"Yes" or "No"**.
3. For **short descriptions**, give a **single sentence**.
4. For **detailed responses**, answer naturally, limit to **< 350 characters**.
5. Do **not** repeat the question.

**User Information:**
{}

**QUESTION Starts from here:**
{}
"""
