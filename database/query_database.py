#!/usr/bin/env python3
"""
Interactive query interface for the medical cases database
"""

import sqlite3
import sys

class MedicalCasesQuery:
    def __init__(self, db_path="medical_cases.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        
    def get_all_categories(self):
        """Get all categories"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM categories ORDER BY name")
        return [row[0] for row in cursor.fetchall()]
    
    def get_cases_by_category(self, category_name):
        """Get all cases for a specific category"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT c.case_id, c.category_id
            FROM cases c
            JOIN categories cat ON c.category_id = cat.id
            WHERE cat.name = ?
            ORDER BY c.case_id
        """, (category_name,))
        return cursor.fetchall()
    
    def get_case_details(self, case_id):
        """Get all sections and subsections for a specific case"""
        cursor = self.conn.cursor()
        
        # Get sections
        cursor.execute("""
            SELECT s.id, s.section_type, s.content
            FROM sections s
            WHERE s.case_id = ?
            ORDER BY s.id
        """, (case_id,))
        sections = cursor.fetchall()
        
        result = []
        for section in sections:
            section_id, section_type, content = section
            
            # Get subsections for this section
            cursor.execute("""
                SELECT subsection_type, content
                FROM subsections
                WHERE section_id = ?
                ORDER BY id
            """, (section_id,))
            subsections = cursor.fetchall()
            
            result.append({
                'section_type': section_type,
                'content': content,
                'subsections': [dict(row) for row in subsections]
            })
        
        return result
    
    def search_content(self, search_term, section_type=None):
        """Search for content containing a specific term"""
        cursor = self.conn.cursor()
        
        if section_type:
            cursor.execute("""
                SELECT s.case_id, s.section_type, s.content
                FROM sections s
                WHERE s.content LIKE ? AND s.section_type = ?
                ORDER BY s.case_id
            """, (f'%{search_term}%', section_type))
        else:
            cursor.execute("""
                SELECT s.case_id, s.section_type, s.content
                FROM sections s
                WHERE s.content LIKE ?
                ORDER BY s.case_id
            """, (f'%{search_term}%',))
        
        return cursor.fetchall()
    
    def get_statistics(self):
        """Get database statistics"""
        cursor = self.conn.cursor()
        
        stats = {}
        
        # Total counts
        cursor.execute("SELECT COUNT(*) FROM categories")
        stats['categories'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM cases")
        stats['cases'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM sections")
        stats['sections'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM subsections")
        stats['subsections'] = cursor.fetchone()[0]
        
        # Cases per category
        cursor.execute("""
            SELECT cat.name, COUNT(c.case_id) as case_count
            FROM categories cat
            LEFT JOIN cases c ON cat.id = c.category_id
            GROUP BY cat.id, cat.name
            ORDER BY case_count DESC
        """)
        stats['cases_per_category'] = cursor.fetchall()
        
        return stats
    
    def close(self):
        """Close database connection"""
        self.conn.close()

def main():
    """Interactive query interface"""
    if len(sys.argv) < 2:
        print("Usage: python query_database.py <command> [args]")
        print("\nCommands:")
        print("  categories                    - List all categories")
        print("  cases <category>             - List cases in a category")
        print("  case <case_id>               - Show details for a specific case")
        print("  search <term> [section_type] - Search for content")
        print("  stats                        - Show database statistics")
        return
    
    query = MedicalCasesQuery()
    command = sys.argv[1].lower()
    
    try:
        if command == "categories":
            categories = query.get_all_categories()
            print("Categories:")
            for i, cat in enumerate(categories, 1):
                print(f"  {i:2d}. {cat}")
        
        elif command == "cases":
            if len(sys.argv) < 3:
                print("Please specify a category name")
                return
            category = sys.argv[2]
            cases = query.get_cases_by_category(category)
            print(f"Cases in {category}:")
            for case in cases:
                print(f"  - {case[0]}")
        
        elif command == "case":
            if len(sys.argv) < 3:
                print("Please specify a case ID")
                return
            case_id = sys.argv[2]
            details = query.get_case_details(case_id)
            print(f"Case: {case_id}")
            print("=" * 50)
            for section in details:
                print(f"\nSection: {section['section_type']}")
                print("-" * 30)
                print(section['content'][:200] + "..." if len(section['content']) > 200 else section['content'])
                
                if section['subsections']:
                    print("\nSubsections:")
                    for sub in section['subsections']:
                        print(f"  {sub['subsection_type']}: {sub['content'][:100]}...")
        
        elif command == "search":
            if len(sys.argv) < 3:
                print("Please specify a search term")
                return
            search_term = sys.argv[2]
            section_type = sys.argv[3] if len(sys.argv) > 3 else None
            
            results = query.search_content(search_term, section_type)
            print(f"Search results for '{search_term}':")
            for result in results:
                print(f"  {result[0]} - {result[1]}")
        
        elif command == "stats":
            stats = query.get_statistics()
            print("Database Statistics:")
            print(f"  Categories: {stats['categories']}")
            print(f"  Cases: {stats['cases']}")
            print(f"  Sections: {stats['sections']}")
            print(f"  Subsections: {stats['subsections']}")
            print("\nCases per Category:")
            for category, count in stats['cases_per_category']:
                print(f"  {category}: {count}")
        
        else:
            print(f"Unknown command: {command}")
    
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        query.close()

if __name__ == "__main__":
    main()
