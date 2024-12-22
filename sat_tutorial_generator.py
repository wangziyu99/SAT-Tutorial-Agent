# sat_tutorial_generator.py
"""
SAT Reading Tutorial Generator

This module automates the generation of comprehensive SAT Reading tutorials using the Claude API.
It processes example questions, generates explanations, and compiles both individual tutorials
and a complete study guide.

Features:
- Processes question examples from markdown files
- Generates tutorials using Claude API
- Creates visual diagrams for strategies
- Compiles individual and comprehensive guides
- Handles error logging and recovery

Dependencies:
    - anthropic: For API calls to Claude
    - tqdm: Progress tracking
    - pathlib: Cross-platform file operations
    - logging: Error tracking and debugging

Author: [Original Author Name]
Last Modified: December 2024
"""

import anthropic
import json
import re
import os
from pathlib import Path
from typing import Dict, List, Optional
import logging
from datetime import datetime
import time
from tqdm import tqdm

# Import configuration settings
from sat_config import (
    QUESTION_TYPES,
    TUTORIAL_PROMPTS,
    TIME_GUIDELINES
)

class SATTutorialGenerator:
    """
    Generates SAT Reading tutorials using the Claude API.

    This class handles the entire tutorial generation pipeline:
    1. Loading and processing example questions
    2. Generating tutorial content via Claude API
    3. Creating and formatting tutorials
    4. Compiling comprehensive study guides

    Attributes:
        client (anthropic.Client): Claude API client instance
        questions_dir (Path): Directory containing question files
        output_dir (Path): Directory for saving generated tutorials
        labels (Dict): Mapping of file IDs to question metadata
    """

    def __init__(self, api_key: str, questions_dir: str = "questions-1218", labels_file: str = "question_labels.json"):
        """
        Initialize the tutorial generator with API access and file paths.

        Args:
            api_key (str): Claude API authentication key
            questions_dir (str): Path to directory containing question files
            labels_file (str): Path to JSON file containing question metadata

        Raises:
            Exception: If output directory creation fails
        """
        # Initialize API client and paths
        self.client = anthropic.Client(api_key=api_key)
        self.questions_dir = Path(questions_dir)
        self.output_dir = Path("tutorials_by_question_type")
        
        # Create output directory with error handling
        try:
            self.output_dir.mkdir(exist_ok=True)
            logging.info(f"Output directory created/verified at: {self.output_dir.absolute()}")
            logging.info(f"Output directory exists: {self.output_dir.exists()}")
            logging.info(f"Output directory is writable: {os.access(self.output_dir, os.W_OK)}")
        except Exception as e:
            logging.error(f"Error creating output directory: {str(e)}")
            raise
            
        # Load question labels and setup logging
        self.labels = self.load_labels(labels_file)
        self.setup_logging()

    def setup_logging(self):
        """
        Configure logging system with timestamps and output handlers.
        
        Creates a new timestamped log file for each run and sets up both file
        and console logging with appropriate formatting.
        """
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Create timestamped log file
        log_file = log_dir / f'tutorial_gen_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

    def load_labels(self, labels_file: str) -> Dict:
        """
        Load and validate question labels from JSON file.

        Args:
            labels_file (str): Path to JSON file containing question metadata

        Returns:
            Dict: Mapping of file IDs to question metadata
            Empty dict if file loading fails

        Logs question type distribution for verification.
        """
        try:
            # Check file existence
            if not Path(labels_file).exists():
                logging.error(f"Labels file not found: {labels_file}")
                return {}
                
            # Load and validate JSON content
            with open(labels_file, 'r', encoding='utf-8') as f:
                labels = json.load(f)
            
            if not labels:
                logging.error("Labels file is empty")
                return {}
                
            # Analyze and log question type distribution
            question_type_counts = {}
            for label in labels:
                q_type_id = label.get('question_type', 'UNKNOWN')
                question_type_counts[q_type_id] = question_type_counts.get(q_type_id, 0) + 1

            logging.info("Question Type (ID) Distribution:")
            for q_type_id, count in question_type_counts.items():
                q_type_name = QUESTION_TYPES.get(q_type_id, "UNKNOWN")
                logging.info(f"  ID={q_type_id} => '{q_type_name}': {count} questions")
                
            return {item['file_id']: item for item in labels}
            
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding labels file: {str(e)}")
            return {}
        except Exception as e:
            logging.error(f"Error loading labels file: {str(e)}")
            return {}

    def extract_sections(self, content: str) -> Dict:
        """
        Parse markdown content into sections based on ## headers.

        Args:
            content (str): Raw markdown content

        Returns:
            Dict: Mapping of section names to their content
            
        Example sections: Passage, Question, Choices, Answer, Skill
        """
        sections = {}
        current_section = None
        current_content = []
        
        for line in content.split('\n'):
            if line.startswith('##'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line.replace('#', '').strip()
                current_content = []
            else:
                current_content.append(line)
                
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
            
        return sections

    def get_examples_by_question_type_name(self, question_type_name: str) -> List[Dict]:
        """
        Collect example questions for a specific question type.

        Args:
            question_type_name (str): Name of the question type to find examples for

        Returns:
            List[Dict]: List of example questions with metadata and content
            Limited to 3 examples per question type.

        Each example contains:
            - id: File identifier
            - passage_category: Category of the passage
            - passage_subcategory: Subcategory if applicable
            - passage: The reading passage text
            - question: The actual question
            - choices: Answer choices
            - answer: Correct answer
            - skill: Tested skill
            - question_type_name: Type of question
        """
        examples = []
        matching_labels = [
            label_info for label_info in self.labels.values()
            if label_info.get('question_type', '') == question_type_name
        ]

        logging.info(f"Found {len(matching_labels)} matching files for question_type={question_type_name}")
        
        for label_info in matching_labels:
            try:
                # Process each matching file
                file_id = label_info['file_id']
                file_path = self.questions_dir / f"{file_id}.md"
                
                if not file_path.exists():
                    logging.warning(f"File not found: {file_path}")
                    continue

                # Extract content sections
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                sections = self.extract_sections(content)
                if not sections.get('Passage'):
                    logging.warning(f"No passage found in file: {file_path}")
                    continue

                # Compile example data
                examples.append({
                    'id': file_id,
                    'passage_category': label_info.get('passage_category', 'General'),
                    'passage_subcategory': label_info.get('passage_subcategory', ''),
                    'passage': sections.get('Passage', ''),
                    'question': sections.get('Question', ''),
                    'choices': sections.get('Choices', ''),
                    'answer': sections.get('Answer', ''),
                    'skill': sections.get('Skill', ''),
                    'question_type_name': question_type_name
                })
                logging.info(f"Successfully processed example {file_id}")
            except Exception as e:
                logging.error(f"Error processing file {label_info.get('file_id')} => {str(e)}")
                continue

        examples.sort(key=lambda x: x['id'])
        return examples[:3]

    def generate_tutorial_for_question_type(self, question_type_id: str) -> Optional[str]:
        """
        Generate a comprehensive tutorial for a specific question type.

        Args:
            question_type_id (str): ID of the question type to generate tutorial for

        Returns:
            Optional[str]: Generated tutorial content or None if generation fails

        The tutorial includes:
            - Introduction
            - Approach diagram
            - Practice section
            - Passage analysis
            - Visual analysis
            - Solution walkthrough
            - Key strategies
            - Conclusion
        """
        try:
            question_type_name = QUESTION_TYPES.get(question_type_id, "UNKNOWN")
            examples = self.get_examples_by_question_type_name(question_type_name)
            
            if not examples:
                logging.warning(f"No examples found for question type: {question_type_id}")
                return None

            example = examples[0]
            logging.info(f"Using example {example['id']} for tutorial generation")

            # Prepare format dictionary for prompts
            format_dict = {
                'question_type_name': question_type_name,
                'category': example.get('passage_category', 'General'),
                'subcategory': example.get('passage_subcategory', ''),
                'passage': example.get('passage', ''),
                'question': example.get('question', ''),
                'choices': example.get('choices', '')
            }

            # Generate each section using Claude API
            sections = []
            
            # Introduction
            intro_content = self.invoke(TUTORIAL_PROMPTS["introduction"].format(**format_dict))
            if intro_content:
                sections.append(("Introduction", intro_content))
            
            # Strategy diagram
            approach_diagram = self.invoke(TUTORIAL_PROMPTS["approach_diagram"].format(**format_dict))
            if approach_diagram:
                sections.append(("General Strategy", approach_diagram))
            
            # Practice section
            practice_section = f"""## Let's Practice

Here's a typical SAT Reading {format_dict['category']} passage that tests {question_type_name} skills:

{format_dict['passage']}

Now, try this question:

{format_dict['question']}

Consider these options:
{format_dict['choices']}

Take a moment to think about your approach before reading the solution."""
            sections.append(("Practice", practice_section))
            
            # Analysis sections
            passage_analysis = self.invoke(TUTORIAL_PROMPTS["passage_analysis"].format(**format_dict))
            if passage_analysis:
                sections.append(("Understanding the Passage", passage_analysis))
            
            passage_diagram = self.invoke(TUTORIAL_PROMPTS["passage_analysis_diagram"].format(**format_dict))
            if passage_diagram:
                sections.append(("Visual Analysis", passage_diagram))
            
            # Solution and strategies
            solution = self.invoke(TUTORIAL_PROMPTS["question_solution"].format(**format_dict))
            if solution:
                sections.append(("Step-by-Step Solution", solution))
            
            strategies = self.invoke(TUTORIAL_PROMPTS["strategies"].format(**format_dict))
            if strategies:
                sections.append(("Key Strategies", strategies))
            
            conclusion = self.invoke(TUTORIAL_PROMPTS["conclusion"].format(**format_dict))
            if conclusion:
                sections.append(("Moving Forward", conclusion))

            # Verify all sections are present
            missing_sections = [title for title, content in sections if not content]
            if missing_sections:
                logging.error(f"Missing content for sections: {', '.join(missing_sections)}")
                return None

            # Combine sections with proper formatting
            tutorial_content = []
            for title, content in sections:
                if content and content.strip():
                    tutorial_content.append(f"# {title}\n\n{content.strip()}")

            return "\n\n".join(tutorial_content)

        except Exception as e:
            logging.error(f"Error generating tutorial for {question_type_id}: {str(e)}")
            return None

    def invoke(self, prompt: str, max_retries: int = 3, max_tokens: int = 4096) -> Optional[str]:
        """
        Make API calls to Claude with retry logic.

        Args:
            prompt (str): Prompt to send to Claude
            max_retries (int): Maximum number of retry attempts
            max_tokens (int): Maximum tokens in response

        Returns:
            Optional[str]: Generated content or None if all retries fail

        Uses exponential backoff for retries.
        """
        for attempt in range(max_retries):
            try:
                response = self.client.messages.create(
                    model="claude-3-5-haiku-latest",
                    max_tokens=max_tokens,
                    temperature=0.5,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            except Exception as e:
                logging.error(f"API attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        return None

    def save_tutorial_by_question_type(self, question_type_id: str, content: str):
        """
        Save a generated tutorial with proper formatting.

        Args:
            question_type_id (str): ID of the question type
            content (str): Tutorial content to save

        The saved tutorial includes:
            - Title
            - Main content
            - Time management guidelines
            - Expert tips
        """
        try:
            question_type_name = QUESTION_TYPES.get(question_type_id, "Unknown")
            safe_qtype = question_type_name.replace(" ", "_").lower()
            filename = f"{question_type_id}_{safe_qtype}_tutorial.md"
            filepath = self.output_dir / filename

            logging.info(f"Attempting to save file: {filepath}")
            
            # Clean and format content
            cleaned_content = self.clean_content(content)
            
            # Format final content
            final_content = f"""# SAT Reading Tutorial: {question_type_name}

{cleaned_content}

## Time Management Guidelines
- Reading Time: {TIME_GUIDELINES.get(question_type_name, {}).get('reading', 2)} minutes
- Solving Time: {TIME_GUIDELINES.get(question_type_name, {}).get('solving', 2)} minutes

## Expert Tip 
{self._get_expert_tip(question_type_name)}"""
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(final_content)
                
            logging.info(f"Successfully saved tutorial at: {filepath}")
                    
        except Exception as e:
            logging.error(f"Error saving tutorial for {question_type_id}: {str(e)}")
            raise

    def clean_content(self, content: str) -> str:
        """
        Clean and standardize markdown formatting.

        Args:
            content (str): Raw content to clean

        Returns:
            str: Cleaned and formatted content with standardized spacing,
                 proper header formatting, and consistent list indentation
        """
        if not content:
            return ""
        
        # Process line by line
        lines = []
        for line in content.split('\n'):
            # Remove trailing whitespace
            line = line.rstrip()
            
            # Fix header formatting
            if line.lstrip().startswith('#'):
                # Remove all leading whitespace for headers
                line = line.lstrip()
            
            # Fix list item formatting
            elif line.lstrip().startswith(('-', '*')):
                indent_level = len(line) - len(line.lstrip())
                if indent_level > 0:
                    # Preserve one level of indentation for nested lists
                    line = "  " * (indent_level // 2) + line.lstrip()
                else:
                    line = line.lstrip()
            
            lines.append(line)
        
        # Join lines and fix multiple consecutive blank lines
        content = '\n'.join(lines)
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content.strip()

    def compile_complete_guide(self):
        """
        Compile all tutorials into a comprehensive study guide.
        
        This method:
        1. Creates a master guide with table of contents
        2. Combines all individual tutorials
        3. Adds general SAT reading tips and strategies
        4. Ensures consistent formatting throughout
        
        The final guide includes:
        - Table of contents with links
        - Individual tutorials for each question type
        - Appendix with general tips
        - Time management guidelines
        """
        try:
            combined_path = self.output_dir / "sat_reading_complete_guide.md"
            
            with open(combined_path, "w", encoding="utf-8") as combined:
                # Write main title and introduction
                combined.write("""# SAT Reading Mastery Guide

This comprehensive guide covers all question types you'll encounter on the SAT Reading section, with detailed strategies and examples for each type.

## Table of Contents\n""")
                
                # Add table of contents with links
                for question_type_id, question_type_name in sorted(QUESTION_TYPES.items()):
                    combined.write(f"- [{question_type_name}](#{question_type_name.lower().replace(' ', '-')})\n")
                
                combined.write("\n---\n\n")
                
                # Combine all tutorial files
                for question_type_id in sorted(QUESTION_TYPES.keys()):
                    filename = f"{question_type_id}_{QUESTION_TYPES[question_type_id].replace(' ', '_').lower()}_tutorial.md"
                    filepath = self.output_dir / filename
                    
                    if filepath.exists():
                        with open(filepath, "r", encoding="utf-8") as f:
                            content = f.read()
                            
                            # Clean up the content
                            cleaned_content = self.clean_content(content)
                            
                            # Add to guide
                            combined.write(f"{cleaned_content}\n\n---\n\n")
                    else:
                        logging.warning(f"Tutorial file not found: {filepath}")
                
                # Add appendix with general tips
                combined.write("""# Appendix: General SAT Reading Tips

## Time Management
- Total time for Reading section: 65 minutes
- Recommended time per passage: 13 minutes
- Leave 2-3 minutes for review

## Key Strategies
1. Always read the passage first
2. Refer back to the passage for every question
3. Use process of elimination
4. Pay attention to line references
5. Watch out for extreme answer choices

## Practice Tips
- Take full-length practice tests
- Review all mistakes thoroughly
- Focus on understanding why correct answers are right
- Practice active reading daily
""")
            
            logging.info(f"Successfully created complete guide at: {combined_path}")
            
        except Exception as e:
            logging.error(f"Error creating complete guide: {str(e)}")
            raise

    def _get_expert_tip(self, question_type_name: str) -> str:
        """
        Provide a tailored expert tip for each question type.

        Args:
            question_type_name (str): Name of the question type

        Returns:
            str: Expert tip specific to the question type
            Returns a default tip if question type is not recognized

        Each tip focuses on key strategies and common pitfalls specific
        to the question type.
        """
        tips = {
            "Words in Context": 
                "Notice how the text defines or contrasts a word, and double-check that the meaning fits the broader context.",
            "Text Structure and Purpose": 
                "Identify how paragraphs and transitions lead to the author's main argument and shape the overall structure.",
            "Cross-Text Connections": 
                "Compare points of agreement or tension between passages, looking for shared or differing evidence.",
            "Central Ideas and Details": 
                "Focus on the main argument and how key details clarify or reinforce it.",
            "Command of Evidence": 
                "Locate explicit textual or quantitative evidence that validates your chosen answer.",
            "Inferences": 
                "Draw logical conclusions from what's stated or strongly implied; avoid external assumptions.",
            "Boundaries": 
                "Observe where one argument ends and another begins, noting shift words or phrases.",
            "Form, Structure, and Sense": 
                "See how the format—paragraphing, sectioning, headings—contributes to meaning.",
            "Rhetorical Synthesis": 
                "Check how rhetorical devices and style work together to persuade or inform.",
            "Transitions": 
                "Look for signaling words or phrases that indicate logical shifts or additions."
        }
        return tips.get(question_type_name, "Always confirm your final selection by re-reading the relevant lines in the passage.")