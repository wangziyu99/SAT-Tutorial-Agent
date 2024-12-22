# sat_config.py

# Passage topics
SAT_PASSAGE_CATEGORIES = {
    "Literature": [
        "Classical novels",
        "Modern literature", 
        "Poetry",
        "Drama"
    ],
    "History and Social Studies": [
        "Major historical events",
        "Social issues",
        "Cultural phenomena"
    ],
    "Natural Sciences": [
        "Life sciences",
        "Physical sciences", 
        "Earth and space sciences"
    ],
    "Social Commentary": [
        "Political and policy analysis",
        "Cultural and art criticism",
        "Technology and society development"
    ]
}

# Time management guidelines
TIME_GUIDELINES = {
    "Words in Context": {"reading": 1, "solving": 1},
    "Text Structure and Purpose": {"reading": 2, "solving": 1.5},
    "Central Ideas and Details": {"reading": 2, "solving": 2},
    "Command of Evidence": {"reading": 1.5, "solving": 1.5},
    "Inferences": {"reading": 2, "solving": 2},
    "Boundaries": {"reading": 1, "solving": 1},
    "Form, Structure, and Sense": {"reading": 1.5, "solving": 1.5},
    "Rhetorical Synthesis": {"reading": 2, "solving": 2},
    "Transitions": {"reading": 1, "solving": 1}
}

# sat_config.py

QUESTION_TYPES = {
    "1": "Words in Context",
    "2": "Text Structure and Purpose",
    "3": "Cross-Text Connections",
    "4": "Central Ideas and Details",
    "5": "Command of Evidence (Textual, Quantitative)",
    "6": "Inferences",
    "7": "Boundaries",
    "8": "Form, Structure, and Sense",
    "9": "Rhetorical Synthesis",
    "10": "Transitions"
}

TUTORIAL_PROMPTS = {
    "introduction": """Write a clear, engaging introduction (200-250 words) for {question_type_name} questions in the SAT Reading section, focusing on how they appear in {category} passages ({subcategory} if applicable). Address:
1. Typical question stems and wording for {question_type_name}.
2. Why this question type is key to scoring well in the Reading section.
3. How {category} passages commonly test this skill (mention any unique features of {subcategory} texts).
4. A short real-life or exam-day scenario illustrating how to spot and handle these questions quickly.
5. One immediate “quick tip” students can use when facing {question_type_name} questions in {category} passages.

Stay practical and motivational—students should finish this introduction feeling ready to dive deeper.""",

    "passage_analysis": """Analyze this SAT Reading {category} passage ({subcategory}, the text is {passage} ~200-350 words provided). In 250-300 words, show students how to dissect and comprehend it effectively:
1. Demonstrate an active reading approach (e.g., annotating main ideas, looking for shifts in tone or perspective).
2. Point out key textual features typical of {category} or {subcategory} passages (e.g., historical context, scientific data, literary style).
3. Give at least two specific examples from the passage that highlight common SAT-tested concepts (line references or quotes).
4. Explain how identifying the passage’s main idea and the author’s purpose sets the stage for tackling any {question_type_name} question.

Keep the explanation concise but detailed enough that students can directly apply these reading tactics.""",

    "question_solution": """Craft a step-by-step solution (200-300 words) for the following {question_type_name} question in a {category} passage ({subcategory} included):

Passage:
{passage}

Question:
{question}

Choices:
{choices}

Show:
1. How to rephrase the question to clarify what is being asked.
2. Where and how to look for evidence in {category} texts (include at least one direct quote or line number).
3. How to eliminate common trap choices (e.g., partial truths, extreme language, out-of-scope answers).
4. Why the correct choice matches both the passage details and the SAT’s reading standards.
5. A brief reflection on how students can replicate this reasoning under time pressure.

Aim to model the thought process an expert reader follows when solving {question_type_name} questions.""",

    "strategies": """In 250-300 words, outline essential SAT Reading strategies for {question_type_name} questions, specifically in {category} passages (with {subcategory} features if relevant). Include:
1. Reading techniques that work well for {category} texts (e.g., identifying argument shifts in Historical passages or focusing on data interpretation in Scientific ones).
2. Practical tips for spotting correct evidence quickly (like keywords, referencing line numbers, or summarizing paragraphs).
3. The most common “traps” or pitfalls the SAT uses for {question_type_name} in {category} contexts.
4. Time-saving tips: how to budget your ~65 minutes across 5 Reading passages, focusing on {question_type_name} question efficiency.
5. Realistic study or practice steps that directly boost performance on {question_type_name} in {category} passages.

Emphasize real SAT scenarios so students can readily use these strategies.""",

    "conclusion": """Write a concise conclusion (120-150 words) wrapping up {question_type_name} questions in {category} passages:
1. Recap the core skill or mindset needed for success (like focusing on evidence or understanding tone).
2. Give one final piece of advice for studying or practicing {question_type_name} in {category}/{subcategory} texts.
3. Note a common mistake that often leads to incorrect answers (e.g., picking an answer that “sounds right” but lacks textual support).
4. End with an encouraging call to action, reminding students how mastering {question_type_name} can improve both their test score and overall reading skills.

Keep it direct, optimistic, and oriented toward self-improvement.""",

    "approach_diagram": """Create a Mermaid diagram that shows a genuinely helpful strategy for solving SAT Reading {question_type_name} questions. Limit to 6-8 nodes maximum. Focus on:
- Key decision points that actually matter
- Common pitfalls and how to avoid them
- Critical thinking paths
- Verification checkpoints

Make the diagram practical and specific to this question type's challenges. Show what experienced SAT tutors actually teach their students.

Use graph TD format with clear node labels relevant to {question_type_name} questions.""",

    "passage_analysis_diagram": """After analyzing this specific SAT Reading passage and question:

PASSAGE:
{passage}

QUESTION:
{question}

Create a Mermaid diagram that reveals the passage's key elements. Limit to 8 nodes maximum. Show:
- The logical structure of the author's argument
- Key relationships between concepts
- Important shifts in ideas
- Critical evidence connections

Focus on what will actually help students understand the passage's construction and how it connects and helps to the question.

IMPORTANT: Return ONLY the Mermaid diagram code without any introductory text, explanations, or commentary.

Use graph TD format with node labels that reflect this specific passage's structure."""
}
