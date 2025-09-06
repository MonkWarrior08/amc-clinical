# Clinical AI ExamPro - AI System Implementation

This document describes the comprehensive AI system implementation for Clinical AI ExamPro, including three main AI personas/workflows: the interactive "Patient" agent, the "Examiner" findings retriever, and the "Feedback" generation agent.

## System Architecture

The AI system is built using LangChain and integrates with:
- **OpenAI GPT-4** for patient and feedback generation
- **Pinecone** vector database for RAG (Retrieval-Augmented Generation)
- **Django ORM** for data persistence
- **SQLite** for case data storage

## Core Components

### 1. Shared LangChain Setup (`simulation/ai_core/config.py`)

- **LLM Integration**: Configured to use OpenAI GPT-4 with appropriate temperature settings
- **Memory Management**: ConversationBufferWindowMemory for maintaining context
- **Pinecone Integration**: Vector store setup for RAG functionality
- **Environment Configuration**: Secure API key management

### 2. AI Patient Agent (`simulation/ai_core/patient_agent.py`)

**Purpose**: Role-plays as the patient during medical simulations

**Key Features**:
- **Persona Loading**: Retrieves `instructions_for_patient` from Case model to establish patient character
- **Conversation Flow**: Maintains conversation context using LangChain memory
- **Examiner Detection**: Detects "Examiner" keyword to pause patient role-play
- **Response Generation**: Generates empathetic, realistic patient responses
- **Memory Management**: Tracks conversation history and patient state

**Usage**:
```python
from simulation.ai_core.patient_agent import PatientAgent

agent = PatientAgent(case_instructions, session_id)
is_examiner_request, response = agent.process_user_input(user_input)
```

### 3. Examiner Findings Workflow (`simulation/ai_core/examiner_workflow.py`)

**Purpose**: Handles examination findings retrieval when user addresses "Examiner"

**Key Features**:
- **Intent Parsing**: Classifies examiner requests (physical exam, lab results, imaging, etc.)
- **Data Retrieval**: Accesses examination details from Case model
- **Priority System**: Uses `info_for_facilitator_exam_findings` when available
- **Response Formatting**: Returns structured examination findings

**Usage**:
```python
from simulation.ai_core.examiner_workflow import ExaminerWorkflow

workflow = ExaminerWorkflow(case_data)
response = workflow.process_examiner_request("Examiner: I would like to examine the face")
```

### 4. Feedback Generation Agent (`simulation/ai_core/feedback_agent.py`)

**Purpose**: Generates comprehensive feedback reports using RAG

**Key Features**:
- **Session Analysis**: Compares session transcript against suggested approach
- **RAG Integration**: Queries Pinecone for relevant medical guidance
- **Score Calculation**: Implements pass/fail logic based on coverage and compliance
- **Structured Feedback**: Generates detailed reports with specific recommendations

**Usage**:
```python
from simulation.ai_core.feedback_agent import FeedbackAgent

agent = FeedbackAgent(case_data, vector_store)
feedback = agent.generate_feedback(transcript, case_id)
```

### 5. Main AI Service (`simulation/ai_core/ai_service.py`)

**Purpose**: Coordinates all AI agents and provides main interface

**Key Features**:
- **Session Management**: Creates and manages AI sessions
- **Agent Coordination**: Routes requests to appropriate agents
- **State Management**: Tracks session state and agent status
- **Memory Persistence**: Saves conversation data to database

## Database Models

### Case Model
- Stores medical case information including patient instructions and examination details
- Contains suggested approach for evaluation (specific questions, management plan, pitfalls)
- Links to categories and maintains case metadata

### Session Model
- Tracks user sessions with conversation history and transcript
- Manages session state (active/inactive, patient paused)
- Stores session metadata and duration

### Feedback Model
- Stores generated feedback reports with scores and analysis
- Contains RAG sources used for feedback generation
- Links to sessions and includes generation metadata

### AIAgentState Model
- Tracks AI agent state for each session
- Stores patient persona and memory data
- Manages examiner and feedback agent states

## API Endpoints

### Session Management
- `POST /api/start-session/` - Start a new AI session
- `POST /api/end-session/` - End session and generate feedback
- `GET /api/session-state/<session_id>/` - Get current session state

### Interactions
- `POST /api/interact/` - Process user input during session
- `POST /api/resume-patient/` - Resume patient agent after examiner interaction

### Feedback
- `GET /api/feedback/<session_id>/` - Get feedback for completed session
- `GET /api/session-history/` - Get user's session history

## Usage Examples

### Starting a Session
```python
# Start a new session
response = requests.post('/api/start-session/', json={
    'case_id': 'case_001'
})
session_id = response.json()['session_id']
```

### Patient Interaction
```python
# Interact with patient
response = requests.post('/api/interact/', json={
    'session_id': session_id,
    'user_input': "Hello, how are you feeling today?"
})
patient_response = response.json()['response']
```

### Examiner Interaction
```python
# Request examination findings
response = requests.post('/api/interact/', json={
    'session_id': session_id,
    'user_input': "Examiner: I would like to examine the patient's vital signs"
})
examiner_response = response.json()['response']
```

### Ending Session and Getting Feedback
```python
# End session and get feedback
response = requests.post('/api/end-session/', json={
    'session_id': session_id
})
feedback = response.json()['feedback']
```

## Configuration

### Environment Variables
```bash
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=amc-tutor
```

### Dependencies
```bash
pip install -r requirements.txt
```

## Testing

### Automated Test
```bash
python manage.py test_ai_system
```

### Interactive Test
```bash
python manage.py test_ai_system --interactive
```

### Test with Specific Case
```bash
python manage.py test_ai_system --case-id case_001
```

## Key Features

### 1. Real-time Patient Simulation
- Dynamic patient responses based on case instructions
- Context-aware conversation flow
- Emotional state consistency

### 2. Intelligent Examiner Workflow
- Automatic detection of examiner requests
- Contextual examination findings retrieval
- Structured response formatting

### 3. Comprehensive Feedback Generation
- RAG-enhanced feedback using medical literature
- Detailed analysis of session performance
- Actionable recommendations for improvement

### 4. Scalable Architecture
- Modular design for easy extension
- Memory-efficient session management
- Database persistence for data integrity

## Future Enhancements

1. **Multi-language Support**: Extend to support multiple languages
2. **Advanced Analytics**: Add detailed performance metrics
3. **Custom Personas**: Allow custom patient persona creation
4. **Real-time Collaboration**: Support multiple users in same session
5. **Integration APIs**: Connect with external medical systems

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure all required environment variables are set
2. **Pinecone Connection**: Verify Pinecone index exists and is accessible
3. **Memory Issues**: Check session cleanup and memory management
4. **Response Quality**: Adjust temperature settings for different agents

### Debug Mode

Enable debug logging by setting:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Support

For technical support or questions about the AI system implementation, please refer to the code documentation or contact the development team.
