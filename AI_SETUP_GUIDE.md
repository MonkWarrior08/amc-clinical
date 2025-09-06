# Clinical AI ExamPro - AI System Setup Guide

This guide will help you set up and test the AI system for Clinical AI ExamPro.

## Prerequisites

- Python 3.8 or higher
- Django 5.2.5
- OpenAI API key
- Pinecone API key and index

## Installation Steps

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install additional Pinecone dependencies
pip install -r scripts/requirements_pinecone.txt
```

### 2. Environment Configuration

Create a `.env` file in the project root:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=amc-tutor

# Django Configuration
SECRET_KEY=your_django_secret_key_here
```

### 3. Database Setup

```bash
# Run Django migrations
python manage.py makemigrations
python manage.py migrate

# Populate Case model with existing data
python manage.py migrate simulation 0002
```

### 4. Test the Setup

```bash
# Run the setup test
python test_ai_setup.py

# Run the AI system test
python manage.py test_ai_system

# Run interactive test
python manage.py test_ai_system --interactive
```

## API Usage Examples

### Start a Session

```bash
curl -X POST http://localhost:8000/api/start-session/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token" \
  -d '{"case_id": "case_001"}'
```

### Interact with Patient

```bash
curl -X POST http://localhost:8000/api/interact/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token" \
  -d '{"session_id": "session_id", "user_input": "Hello, how are you feeling?"}'
```

### Request Examiner Findings

```bash
curl -X POST http://localhost:8000/api/interact/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token" \
  -d '{"session_id": "session_id", "user_input": "Examiner: I would like to examine the patient"}'
```

### End Session and Get Feedback

```bash
curl -X POST http://localhost:8000/api/end-session/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token" \
  -d '{"session_id": "session_id"}'
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are installed
2. **API Key Errors**: Verify environment variables are set correctly
3. **Database Errors**: Run migrations and check database connection
4. **Pinecone Errors**: Verify Pinecone index exists and is accessible

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Individual Components

```python
# Test patient agent
from simulation.ai_core.patient_agent import PatientAgent
agent = PatientAgent("Test instructions", "test_session")
is_examiner, response = agent.process_user_input("Hello")

# Test examiner workflow
from simulation.ai_core.examiner_workflow import ExaminerWorkflow
workflow = ExaminerWorkflow({"examination_details": "Test details"})
response = workflow.process_examiner_request("Examiner: Show me vital signs")

# Test feedback agent
from simulation.ai_core.feedback_agent import FeedbackAgent
agent = FeedbackAgent({"case_id": "test"}, vector_store)
feedback = agent.generate_feedback("Test transcript", "test_case")
```

## Next Steps

1. **Customize Patient Personas**: Modify case instructions for different patient types
2. **Enhance Feedback**: Add more sophisticated evaluation criteria
3. **Integrate Voice**: Connect with speech-to-text and text-to-speech services
4. **Add Analytics**: Track user performance and session metrics
5. **Scale Up**: Deploy to production with proper security measures

## Support

For technical support or questions about the AI system, please refer to:
- Code documentation in the `simulation/ai_core/` directory
- API documentation in `simulation/api_views.py`
- Test examples in `simulation/management/commands/test_ai_system.py`
