import re
import json
from pathlib import Path
import logging
from datetime import datetime
import anthropic
from typing import Dict, Optional, List, Tuple
from textbook_own.sat_config_backup import SAT_PASSAGE_CATEGORIES, QUESTION_TYPES

class SATLabeler:
    def __init__(self, api_key: str, questions_dir: str = "questions-1218"):
        """Initialize the SAT labeler with API access and directories."""
        self.client = anthropic.Client(api_key=api_key)
        self.questions_dir = Path(questions_dir)
        self.setup_logging()

    def setup_logging(self):
        """Configure logging with timestamps."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f'labeling_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

    def parse_filename(self, filename: str) -> Dict:
        """Extract question number and difficulty from filename."""
        pattern = r'question_(\d+)_(\d+)_(\d+)_(\w+)\.md'
        match = re.match(pattern, filename)
        if match:
            return {
                'question_type': match.group(1),
                'book': match.group(2),
                'paragraph': match.group(3),
                'difficulty': match.group(4)
            }
        return None

    def extract_sections(self, content: str) -> Dict:
        """Extract different sections from markdown content."""
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

    def get_passage_labels(self, passage: str) -> Dict:
        """Get passage category and subcategory using Claude."""
        prompt = f"""Analyze this SAT Reading passage and classify it into exactly one category and subcategory from the following list:

{json.dumps(SAT_PASSAGE_CATEGORIES, indent=2)}

Passage:
{passage}

Return only the category and subcategory in this format:
CATEGORY: [main category]
SUBCATEGORY: [specific subcategory]"""

        try:
            response = self.client.messages.create(
                model="claude-3-5-haiku-latest",
                max_tokens=4096,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            text = response.content[0].text
            category_match = re.search(r'CATEGORY:\s*(.*?)(?:\n|$)', text)
            subcategory_match = re.search(r'SUBCATEGORY:\s*(.*?)(?:\n|$)', text)
            
            if category_match and subcategory_match:
                return {
                    'category': category_match.group(1).strip(),
                    'subcategory': subcategory_match.group(1).strip()
                }
            
        except Exception as e:
            logging.error(f"Error getting passage labels: {str(e)}")
        
        return None

    def process_question_file(self, file_path: Path) -> Optional[Dict]:
        """Process a single question file."""
        try:
            # Parse filename for metadata
            filename_info = self.parse_filename(file_path.name)
            if not filename_info:
                logging.error(f"Could not parse filename: {file_path.name}")
                return None

            # Read and parse file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            sections = self.extract_sections(content)
            if not sections.get('Passage'):
                logging.error(f"No passage found in {file_path.name}")
                return None

            # Get passage labels
            passage_labels = self.get_passage_labels(sections['Passage'])
            if not passage_labels:
                logging.error(f"Could not get passage labels for {file_path.name}")
                return None

            # Combine all information
            result = {
                'file_id': file_path.stem,
                'question_type': QUESTION_TYPES.get(filename_info['question_type'], 'Unknown'),
                'difficulty': filename_info['difficulty'],
                'passage_category': passage_labels['category'],
                'passage_subcategory': passage_labels['subcategory']
            }

            return result

        except Exception as e:
            logging.error(f"Error processing {file_path}: {str(e)}")
            return None

    def process_all_questions(self, output_file: str = "question_labels.json"):
        """Process all question files and save results."""
        results = []
        
        for file_path in sorted(self.questions_dir.glob("*.md")):
            logging.info(f"Processing {file_path.name}")
            result = self.process_question_file(file_path)
            if result:
                results.append(result)
                
            # Save progress every 10 files
            if len(results) % 10 == 0:
                self.save_results(results, output_file)
                
        self.save_results(results, output_file)
        logging.info(f"Processed {len(results)} files. Results saved to {output_file}")

    def save_results(self, results: List[Dict], output_file: str):
        """Save results to JSON file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)

def main():
    api_key = "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"  # Replace with your API key
    labeler = SATLabeler(api_key=api_key)
    labeler.process_all_questions()

if __name__ == "__main__":
    main()