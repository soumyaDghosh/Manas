from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request, Depends
from app.utils.auth import verify_firebase_token
from app.models.chat import ChatInput, ConversationMessage, MoodAnalysisResult
from app.models.session import SessionModel, SessionsResponse
from app.utils.chat import MoodAnalyzer, SessionAnalyzer
from app.utils.redis import RedisService
from datetime import datetime

router = APIRouter()


@router.post("/process", status_code=202, response_model=MoodAnalysisResult)
async def process_text(
    request: Request,
    bg_tasks: BackgroundTasks,
    data: ChatInput = Query(..., min_length=10),
    uid: str = Depends(verify_firebase_token),
    redis_service: RedisService = Depends(RedisService.get_service),
    mood_analyzer: MoodAnalyzer = Depends(MoodAnalyzer),
):
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
    input_text: str = data.text
    if not input_text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")

    history = await redis_service.get_chat_history(uid)
    mood = mood_analyzer.analyze(text=input_text, history=history)

    chat = ConversationMessage(
        message=input_text, reply=mood.reply, timestamp=data.timestamp
    )
    bg_tasks.add_task(redis_service.add_chat_history, uid, chat)
    bg_tasks.add_task(redis_service.add_session_moods, uid, mood)
    return mood


@router.post("/end-session", response_model=SessionModel)
async def end_session(
    request: Request,
    uid: str = Depends(verify_firebase_token),
    redis_service: RedisService = Depends(RedisService.get_service),
    session_analyzer: SessionAnalyzer = Depends(SessionAnalyzer),
):
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

    session_moods: list[MoodAnalysisResult] = await redis_service.get_session_moods(uid)
    chat_history: list[ConversationMessage] = await redis_service.get_chat_history(uid)

    if not session_moods or not chat_history:
        redis_service.clear_db(uid)
        raise HTTPException(
            status_code=424,
            detail="No data in the current session to process. Please call /api/v1/process first.",
        )

    summary: SessionModel = session_analyzer.summarize(chat_history, session_moods)
    redis_service.clear_db(uid)

    firestore_db = request.app.state.firestore_db
    user_sessions = (
        firestore_db.collection("users").document(uid).collection("sessions")
    )
    user_sessions.add(
        {
            "mood": summary.mood.value,
            "summary": summary.summary,
            "created_at": summary.created_at or datetime.now(),
        }
    )
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
    user_sessions = (
        firestore_db.collection("users").document(uid).collection("sessions")
    )

    sessions = user_sessions.stream()
    session_list: list[SessionModel] = []

    for session in sessions:
        session_data = SessionModel(
            mood=session.to_dict().get("mood", ""),
            summary=session.to_dict().get("summary", ""),
            created_at=session.to_dict().get("created_at", datetime.now()),
        )
        session_list.append(session_data)

    return SessionsResponse(sessions=session_list)
