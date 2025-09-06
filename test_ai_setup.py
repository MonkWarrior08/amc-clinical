#!/usr/bin/env python3
"""
Test script to verify AI system setup

This script tests the basic functionality of the AI system
without requiring a full Django environment.
"""

import os
import sys
import json
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        # Test Django imports
        import django
        from django.conf import settings
        print("✓ Django imports successful")
    except ImportError as e:
        print(f"✗ Django import failed: {e}")
        return False
    
    try:
        # Test LangChain imports
        from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        from langchain_pinecone import PineconeVectorStore
        from pinecone import Pinecone
        print("✓ LangChain imports successful")
    except ImportError as e:
        print(f"✗ LangChain import failed: {e}")
        return False
    
    try:
        # Test dotenv
        from dotenv import load_dotenv
        print("✓ dotenv import successful")
    except ImportError as e:
        print(f"✗ dotenv import failed: {e}")
        return False
    
    return True

def test_environment():
    """Test environment variable setup"""
    print("\nTesting environment variables...")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        'OPENAI_API_KEY',
        'PINECONE_API_KEY',
        'PINECONE_INDEX_NAME'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"✗ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file")
        return False
    else:
        print("✓ All required environment variables are set")
        return True

def test_ai_config():
    """Test AI configuration"""
    print("\nTesting AI configuration...")
    
    try:
        # Set up Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
        django.setup()
        
        from simulation.ai_core.config import AIConfig
        
        config = AIConfig()
        print("✓ AI configuration created successfully")
        
        # Test LLM creation
        llm = config.get_llm()
        print("✓ LLM created successfully")
        
        # Test embeddings
        embeddings = config.get_embeddings()
        print("✓ Embeddings created successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ AI configuration failed: {e}")
        return False

def test_models():
    """Test Django models"""
    print("\nTesting Django models...")
    
    try:
        from simulation.models import Case, Session, Feedback, AIAgentState
        print("✓ All models imported successfully")
        
        # Test model creation
        case = Case(
            case_id='test_case',
            category='test_category',
            scenario='Test scenario',
            instructions_for_patient='Test instructions'
        )
        print("✓ Case model created successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Model test failed: {e}")
        return False

def test_ai_agents():
    """Test AI agents"""
    print("\nTesting AI agents...")
    
    try:
        from simulation.ai_core.patient_agent import PatientAgent
        from simulation.ai_core.examiner_workflow import ExaminerWorkflow
        from simulation.ai_core.feedback_agent import FeedbackAgent
        
        # Test patient agent
        patient_agent = PatientAgent("Test patient instructions", "test_session")
        print("✓ Patient agent created successfully")
        
        # Test examiner workflow
        case_data = {
            'examination_details': 'Test examination details',
            'info_for_facilitator_exam_findings': 'Test facilitator findings'
        }
        examiner_workflow = ExaminerWorkflow(case_data)
        print("✓ Examiner workflow created successfully")
        
        # Test feedback agent
        feedback_agent = FeedbackAgent(case_data)
        print("✓ Feedback agent created successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ AI agents test failed: {e}")
        return False

def main():
    """Main test function"""
    print("Clinical AI ExamPro - AI System Setup Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_environment,
        test_ai_config,
        test_models,
        test_ai_agents
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! AI system is ready to use.")
        return True
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
