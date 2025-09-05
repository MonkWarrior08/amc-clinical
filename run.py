#!/usr/bin/env python3
"""
AMC Clinical - Main Launcher Script

This script provides easy access to all the main functionality of the system.
"""

import sys
import os
from pathlib import Path

def show_menu():
    """Display the main menu"""
    print("🏥 AMC Clinical - Medical Cases Management System")
    print("=" * 50)
    print()
    print("1. Database Management (SQLite)")
    print("2. PDF Processing & Pinecone Upload")
    print("3. Semantic Search (Pinecone)")
    print("4. Test PDF Processing")
    print("5. Setup & Configuration")
    print("6. Show Project Structure")
    print("0. Exit")
    print()

def run_database_management():
    """Run database management tools"""
    print("\n📊 Database Management")
    print("-" * 30)
    print("Available commands:")
    print("  python database/create_medical_cases_db.py")
    print("  python database/test_database.py")
    print("  python database/query_database.py <command>")
    print()
    print("Example queries:")
    print("  python database/query_database.py categories")
    print("  python database/query_database.py cases Cardiovascular_system")
    print("  python database/query_database.py case Erin_Campbell")
    print()

def run_pdf_processing():
    """Run PDF processing and Pinecone upload"""
    print("\n📄 PDF Processing & Pinecone Upload")
    print("-" * 40)
    print("1. Test PDF processing (no API keys needed):")
    print("   python pdf_processing/test_pdf_processing.py")
    print()
    print("2. Upload to Pinecone (requires API keys):")
    print("   python pdf_processing/pdf_to_pinecone.py")
    print()

def run_semantic_search():
    """Run semantic search tools"""
    print("\n🔍 Semantic Search (Pinecone)")
    print("-" * 35)
    print("1. Test setup:")
    print("   python pinecone_search/setup_pinecone.py")
    print()
    print("2. Search the database:")
    print("   python pinecone_search/search_pinecone.py 'your query'")
    print("   python pinecone_search/search_pinecone.py 'medical diagnosis' 10")
    print()

def run_test_pdf():
    """Run PDF processing test"""
    print("\n🧪 Testing PDF Processing...")
    os.chdir("pdf_processing")
    os.system("python test_pdf_processing.py")
    os.chdir("..")

def run_setup():
    """Run setup and configuration"""
    print("\n⚙️ Setup & Configuration...")
    os.chdir("pinecone_search")
    os.system("python setup_pinecone.py")
    os.chdir("..")

def show_structure():
    """Show project structure"""
    print("\n📁 Project Structure")
    print("-" * 20)
    print("""
amc-clinical/
├── database/                    # SQLite database management
│   ├── create_medical_cases_db.py
│   ├── test_database.py
│   ├── query_database.py
│   └── medical_cases.db
├── pdf_processing/              # PDF text extraction and processing
│   ├── pdf_to_pinecone.py
│   └── test_pdf_processing.py
├── pinecone_search/            # Pinecone vector search
│   ├── search_pinecone.py
│   └── setup_pinecone.py
├── scripts/                    # Utility scripts
│   └── requirements_pinecone.txt
├── docs/                       # Documentation
│   └── README_PINECONE.md
├── source_pdf/                 # Source PDF files
│   ├── management_print.pdf
│   ├── chapter 3 and 4_print.pdf
│   ├── Master medcine 2_print.pdf
│   └── medicine 1_print.pdf
├── core/                       # Django core
├── simulation/                 # Django simulation app
├── cases.txt                   # Medical cases data
├── cases2.txt                  # Additional medical cases data
└── .env                        # Environment variables
    """)

def main():
    """Main function"""
    while True:
        show_menu()
        choice = input("Enter your choice (0-6): ").strip()
        
        if choice == "0":
            print("👋 Goodbye!")
            break
        elif choice == "1":
            run_database_management()
        elif choice == "2":
            run_pdf_processing()
        elif choice == "3":
            run_semantic_search()
        elif choice == "4":
            run_test_pdf()
        elif choice == "5":
            run_setup()
        elif choice == "6":
            show_structure()
        else:
            print("❌ Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()
