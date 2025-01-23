# SAT Reading Tutor: LLM-Powered Agent

A cutting-edge system leveraging large language models (LLMs) to automatically generate comprehensive Scholastic Assessment Test (SAT) Reading tutorials. This agent processes example questions, crafts detailed explanations, and compiles both modular tutorials and an all-encompassing study guide. By harnessing the Claude API and advanced prompt engineering techniques, this tool empowers students to master SAT Reading through dynamic, explainable, and personalized content generation.

## Quick Start

```bash
# Install dependencies
pip install anthropic tqdm

# Run the demo notebook
jupyter notebook sat_tutorial_generator_demo.ipynb
```

## Project Structure

```
project_root/
├── sat_tutorial_generator.py    # Main generator class
├── sat_config.py               # Configuration settings
├── sat_tutorial_generator_demo.ipynb  # Demo notebook
├── questions-1218/             # Input question files
│   ├── question_1_0_0_easy.md
│   ├── question_1_0_0_hard.md
│   └── ...
├── question_labels.json        # Question metadata
├── tutorials_by_question_type/ # Generated tutorials
│   ├── 1_words_in_context_tutorial.md
│   └── ...
└── logs/                      # Log files
```

## Input File Formats

### Question Files (questions-1218/*.md)
```markdown
## Abstract
[Optional citation information]

## Passage
[Reading passage text]

## Question
[Question text]

## Skill
[Question type name]

## Choices
- A) [choice text]
- B) [choice text]
- C) [choice text]
- D) [choice text]

## Answer
- A) Correct: [explanation]
- B) Incorrect: [explanation]
- C) Incorrect: [explanation]
- D) Incorrect: [explanation]
```

### Question Labels (question_labels.json)
```json
{
  "file_id": "question_9_0_88_hard",
    "question_type": "Words in Context",
    "difficulty": "easy/hard",
    "passage_category": "Natural Sciences",
    "passage_subcategory": "Life sciences"
}
```

## Generated Tutorial Format

Each tutorial follows this exact structure:

### 1. Title Section
```markdown
# SAT Reading Tutorial: [Question Type]
```

### 2. Introduction
```markdown
# Introduction

[200-250 words of introduction content]
```

### 3. Strategy Section
```markdown
# General Strategy

```mermaid
[strategy diagram]
```
```

### 4. Practice Section
```markdown
# Practice

Here's a typical SAT Reading passage that tests [skill] skills:

[Passage text]

Now, try this question:

[Question text]

Consider these options:
A) [choice]
B) [choice]
C) [choice]
D) [choice]
```

### 5. Analysis Section
```markdown
# Understanding the Passage

When approaching this passage, students should:
- [Key point 1]
- [Key point 2]

This passage demonstrates classic characteristics:
- [Feature 1]
- [Feature 2]
```

### 6. Visual Analysis
```markdown
# Visual Analysis

```mermaid
[passage structure diagram]
```
```

### 7. Solution Section
```markdown
# Step-by-Step Solution

1. [Step 1 explanation]
2. [Step 2 explanation]

Key evidence:
- [Evidence point 1]
- [Evidence point 2]
```

### 8. Strategy Section
```markdown
# Key Strategies

[Strategy content with bullet points]
```

### 9. Conclusion Section
```markdown
# Moving Forward

[Conclusion content]

## Time Management Guidelines
- Reading Time: X minutes
- Solving Time: Y minutes

## Expert Tip
[Single-paragraph expert tip]
```

## Critical Formatting Rules

1. Headers
   - Main sections use single #
   - Time Management and Expert Tip use ##
   - No other header levels
   - No trailing punctuation in headers

2. Lists
   - Use - for unordered lists
   - Use 1. for ordered lists
   - Single space after markers
   - No blank lines between items

3. Mermaid Diagrams
   - Use ```mermaid fence
   - No blank lines in diagram code
   - Single blank line before/after

4. Spacing
   - Single blank line after headers
   - Single blank line between sections
   - No double blank lines
   - No trailing whitespace

5. Special Elements
   - Use A) B) C) D) for choices
   - Time guidelines use hyphens
   - Expert tip is single paragraph

## Complete Guide Structure

The compiled guide (sat_reading_complete_guide.md) follows:

```markdown
# SAT Reading Mastery Guide

## Table of Contents
- [Question Type 1](#link)
- [Question Type 2](#link)

---

[Individual tutorials content]

---

# Appendix: General SAT Reading Tips

## Time Management
[time management tips]

## Key Strategies
[strategies]

## Practice Tips
[practice tips]
```

## Usage

1. Configure your API key:
```python
API_KEY = 'your-api-key-here'
```

2. Initialize generator:
```python
generator = SATTutorialGenerator(
    api_key=API_KEY,
    questions_dir="questions-1218",
    labels_file="question_labels.json"
)
```

3. Generate tutorials:
```python
# Single tutorial
result = generator.generate_tutorial_for_question_type("1")
if result:
    generator.save_tutorial_by_question_type("1", result)

# All tutorials
for question_type_id, name in QUESTION_TYPES.items():
    result = generator.generate_tutorial_for_question_type(question_type_id)
    if result:
        generator.save_tutorial_by_question_type(question_type_id, result)
```

4. Compile guide:
```python
generator.compile_complete_guide()
```

## Error Handling

- Logs are written to `logs/tutorial_gen_[timestamp].log`
- Failed API calls retry with exponential backoff
- Invalid files are skipped with warnings
- Missing sections trigger error logs

## Frontend Implementation Notes

1. Mermaid Diagrams
   - Use Mermaid.js for rendering
   - Maintain default styling
   - Use responsive width

2. Navigation
   - Generate anchors for # headers
   - Use kebab-case for links

3. Time Guidelines
   - Consider special styling
   - Two-column layout recommended

4. Lists
   - Maintain consistent indentation
   - Use standard bullet/number styling

## Contact
Neil Wang
ziyuloveu@gmail.com

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

Copyright 2024

Licensed under the Apache License, Version 2.0 (the "License");
you may not use these files except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
