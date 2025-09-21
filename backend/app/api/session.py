from fastapi import APIRouter, HTTPException, Request, Depends
from app.utils.auth import verify_firebase_token
from app.models.chat import ChatInput, ConversationMessage, MoodAnalysisResult
from app.models.session import SessionModel, SessionsResponse
from app.utils.chat import MoodAnalyzer, SessionAnalyzer
from redis import Redis
from datetime import datetime
import json

router = APIRouter()

@router.post("/process", status_code=202, response_model=MoodAnalysisResult)
def process_text(request: Request, data: ChatInput, uid: str = Depends(verify_firebase_token)):
    """
    Process user input text to analyze mood and generate empathetic reply.

    Args:
        request: FastAPI request object to access app state.
        data: ChatInput containing the text and timestamp.
        uid: User ID extracted from Firebase token.

    Returns:
        MoodAnalysisResult: Detected mood, confidence score, and generated reply.

    Raises:
        HTTPException: 400 for bad input, 500 for processing errors.
    """
    redis_db: Redis = request.app.state.redis_db
    input_text = data.text
    if not input_text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")

    chat_history = redis_db.lrange(f"user:{uid}:chat_history", 0, -1)
    mood_analyzer = MoodAnalyzer(
        gemini_api_key=request.app.state.gemini_api_key
    )
    mood = mood_analyzer.analyze(
        text=input_text,
        history=[h for h in chat_history]
    )
    chat = ConversationMessage(
        message=input_text,
        reply=mood.reply,
        timestamp=data.timestamp
    )
    redis_db.rpush(f"user:{uid}:session_moods", mood.model_dump_json())
    redis_db.rpush(f"user:{uid}:chat_history", chat.model_dump_json())
    return mood


@router.post("/end-session", response_model=SessionModel)
def end_session(request: Request, uid: str = Depends(verify_firebase_token)):
    """
    End the current session, summarize the mood, and store the session in Firestore.

    Args:
        request: FastAPI request object to access app state.
        uid: User ID extracted from Firebase token.

    Returns:
        SessionSummary: Summary of the session including main mood and counts.

    Raises:
        HTTPException: 404 if no session data, 500 for processing errors.
    """
    redis_db: Redis = request.app.state.redis_db
    session_moods_raw = redis_db.lrange(f"user:{uid}:session_moods", 0, -1)
    chat_history_raw = redis_db.lrange(f"user:{uid}:chat_history", 0, -1)


    if not session_moods_raw:
        redis_db.delete(f"user:{uid}:session_moods")
        redis_db.delete(f"user:{uid}:chat_history")
        raise HTTPException(status_code=404, detail="No data in the current session to process. Please call /api/v1/process first.")

    session_moods = list(map(MoodAnalysisResult.model_validate_json, session_moods_raw))
    chat_history = list(map(ConversationMessage.model_validate_json, chat_history_raw))


    session_analyzer = SessionAnalyzer(
        gemini_api_key=request.app.state.gemini_api_key
    )
    summary: SessionModel = session_analyzer.summarize(chat_history, session_moods)
    redis_db.delete(f"user:{uid}:chat_history")
    redis_db.delete(f"user:{uid}:session_moods")

    firestore_db = request.app.state.firestore_db
    user_sessions = firestore_db.collection("users").document(uid).collection("sessions")
    user_sessions.add({
        "mood": summary.mood.value,
        "summary": summary.summary,
        "created_at": summary.created_at or datetime.now()
    })
    return summary


@router.get("/sessions", response_model=SessionsResponse)
def get_sessions(request: Request, uid: str = Depends(verify_firebase_token)):
    """
    Retrieve all past sessions for the authenticated user.
    Args:
        request: FastAPI request object to access app state.
        uid: User ID extracted from Firebase token.

    Returns:
        SessionsResponse: List of past sessions.
    """
    firestore_db = request.app.state.firestore_db
    user_sessions = firestore_db.collection("users").document(uid).collection("sessions")

    sessions = user_sessions.stream()
    session_list: list[SessionModel] = []

    for session in sessions:
        session_data = SessionModel(
            id=session.id,
            mood=session.to_dict().get("mood", ""),
            summary=session.to_dict().get("summary", ""),
            created_at=session.to_dict().get("created_at", datetime.now())
        )
        session_list.append(session_data)

    return SessionsResponse(sessions=session_list)
