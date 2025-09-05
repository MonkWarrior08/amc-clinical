"""
Database utilities for the simulation app
"""

import sqlite3
import os
from typing import List, Dict, Optional

class MedicalCasesQuery:
    def __init__(self, db_path=None):
        if db_path is None:
            # Get the database path relative to the project root
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            db_path = os.path.join(project_root, 'database', 'medical_cases.db')
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        
    def get_all_categories(self) -> List[str]:
        """Get all categories"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM categories ORDER BY name")
        return [row[0] for row in cursor.fetchall()]
    
    def get_cases_by_category(self, category_name: str) -> List[Dict]:
        """Get all cases for a specific category with basic info"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT c.case_id, c.category_id, cat.name as category_name
            FROM cases c
            JOIN categories cat ON c.category_id = cat.id
            WHERE cat.name = ?
            ORDER BY c.case_id
        """, (category_name,))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_case_with_content(self, case_id: str) -> Optional[Dict]:
        """Get case details including SCENARIO and Instruction_for_doc content"""
        cursor = self.conn.cursor()
        
        # Get case basic info
        cursor.execute("""
            SELECT c.case_id, cat.name as category_name
            FROM cases c
            LEFT JOIN categories cat ON c.category_id = cat.id
            WHERE c.case_id = ?
        """, (case_id,))
        case_info = cursor.fetchone()
        
        if not case_info:
            return None
        
        # Get Instruction_for_doc section
        cursor.execute("""
            SELECT s.content
            FROM sections s
            WHERE s.case_id = ? AND s.section_type = 'Instruction_for_doc'
            LIMIT 1
        """, (case_id,))
        instruction_section = cursor.fetchone()
        
        # Get SCENARIO subsection from Instruction_for_doc
        scenario_content = ""
        if instruction_section:
            instruction_content = instruction_section[0]
            # Extract SCENARIO content
            import re
            scenario_match = re.search(r'\[SCENARIO\](.*?)(?=\[|$)', instruction_content, re.DOTALL)
            if scenario_match:
                scenario_content = scenario_match.group(1).strip()
        
        return {
            'case_id': case_info[0],
            'category_name': case_info[1],
            'scenario': scenario_content,
            'instruction_for_doc': instruction_section[0] if instruction_section else ""
        }
    
    def get_cases_with_content_by_category(self, category_name: str) -> List[Dict]:
        """Get all cases for a category with their content"""
        cases = self.get_cases_by_category(category_name)
        cases_with_content = []
        
        for case in cases:
            case_id = case['case_id']
            case_content = self.get_case_with_content(case_id)
            if case_content:
                cases_with_content.append(case_content)
        
        return cases_with_content
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
