from google import genai
from loguru import logger

from app.config.settings import settings
from app.models.chat import MoodAnalysisResult, ConversationMessage
from app.models.session import SessionModel


class SessionAnalyzer:
    """
    This class provides methods to analyze a session's mood data
    and summarize the main mood and counts.
    """

    PROMPT_TEMPLATE = """
    # SYSTEM INSTRUCTIONS:
    ## 1. Core Persona & Role
    You are an expert AI Session Analysis and Summarization Engine. Your task is to analyze a conversation by cross-referencing two parallel data sources: the conversation transcript and a corresponding mood analysis log. You are an objective observer.

    ## 2. Primary Task
    Analyze the user's session by correlating the `conversation_history` and `mood_history` JSON strings provided below. The entry at `conversation_history[i]` corresponds directly to the entry at `mood_history[i]`.
    - **Determine the Overall Mood:** Identify the single, primary emotional theme of the session. This is the root emotion the user was expressing or the main problem they were trying to solve.
    - **Analyze the Emotional Journey:** Use the sequence of `mood` values from the `mood_history` to understand the emotional arc of the conversation.
    - **Generate a Concise Summary:** Write a brief, third-person summary of the conversation. It must capture the main topic, the emotional journey, and the outcome.

    ## 3. Output Requirements
    - Your output **must** be a single, valid JSON object and nothing else.
    - The JSON object must contain exactly two keys: `mood` (string, from the list: 'joy', 'sadness', 'anger', 'fear', 'surprise', 'disgust', 'neutral') and `summary` (string).

    --- EXAMPLES FOR GUIDANCE ---

    **-- Example 1: Emotional Arc from Fear to Neutrality --**
    *Conversation History (JSON format):*
    [
    {{
        "message": "I have that huge presentation with the leadership team tomorrow.",
        "reply": "That's a big deal! You've prepared so much for this. How are you feeling about it?",
        "timestamp": "2025-09-11T14:20:00.099Z"
    }},
    {{
        "message": "They just added the CEO to the invite. I don't think I can do this.",
        "reply": "Wow, it's completely understandable why that would feel intimidating. But the CEO's attendance shows how important your work is. You know this material inside and out.",
        "timestamp": "2025-09-11T14:21:15.123Z"
    }}
    ]
    *Mood History (JSON format):*
    [
    {{ "mood": "neutral", "confidence": 85 }},
    {{ "mood": "fear", "confidence": 96 }}
    ]
    ```json
    {{
    "mood": "fear",
    "summary": "The user's initial neutrality turned to fear and anxiety upon learning the CEO would attend their presentation. The AI provided reassurance to help manage their stress and reframe the situation positively."
    }}
    ```

    **-- Example 2: Sustained Joyful Arc --**
    *Conversation History (JSON format):*
    [
    {{
        "message": "I've been studying for this certification for six months. The final exam was today.",
        "reply": "Wow, that's serious dedication! I've got my fingers crossed for you. Let me know how it goes!",
        "timestamp": "2025-09-12T10:04:00.000Z"
    }},
    {{
        "message": "I PASSED!!! I can't believe it!",
        "reply": "YES! That is fantastic news! All of that hard work completely paid off. Congratulations!",
        "timestamp": "2025-09-12T10:05:30.000Z"
    }}
    ]
    *Mood History (JSON format):*
    [
    {{ "mood": "neutral", "confidence": 90 }},
    {{ "mood": "joy", "confidence": 99 }}
    ]
    ```json
    {{
    "mood": "joy",
    "summary": "The user shared the joyful news of passing a difficult exam after a long period of study. The session was celebratory and focused on acknowledging the user's success."
    }}
    --- END OF EXAMPLES ---

    Analyze the following:

    Conversation History (JSON format):
    {conversation_history}

    Mood History (JSON format):
    {mood_history}
    """

    def __init__(self):
        self._model = "gemini-2.5-flash"
        self._client = genai.Client(api_key=settings.GEMINI_API_KEY)

    def summarize(
        self,
        conversation_history: list[ConversationMessage],
        mood_history: list[MoodAnalysisResult],
    ) -> SessionModel:
        prompt = self.PROMPT_TEMPLATE.format(
            conversation_history=[h.model_dump_json() for h in conversation_history],
            mood_history=[m.model_dump_json() for m in mood_history],
        )
        response = self._client.models.generate_content(
            model=self._model, contents=prompt
        )
        return SessionModel.parse_json_markdown(str(response.text))


class MoodAnalyzer:
    """
    This class provides sentiment analysis and empathetic response generation
    using Google's Gemini AI with comprehensive error handling and logging.
    """

    PROMPT_TEMPLATE = """
      # SYSTEM INSTRUCTIONS:

      ## 1. Core Persona & Role
      You are an advanced conversational AI. Your primary role is to act as an empathetic, supportive, and intelligent companion in a one-on-one conversation with a user. Your persona is that of a compassionate and thoughtful friend: you are curious, non-judgmental, and your main goal is to make the user feel heard and understood.

      ## 2. Primary Task
      For each new user message, you must perform two tasks and return them in a single JSON object:
      - **Analyze Mood:** Classify the user's mood into one of: 'joy', 'sadness', 'anger', 'fear', 'surprise', 'disgust', 'neutral'.
      - **Generate Reply:** Craft a natural, human-like reply that is context-aware, empathetic, and logically follows the conversation history.

      ## 3. Output Requirements
      - Your output MUST be a single, valid JSON object and nothing else.
      - The JSON object must contain exactly three keys: `mood` (string), `confidence` (number 0-100), and `reply` (string).

      ## 4. Critical Boundaries & Safety Rules
      - **You are NOT a therapist or a professional.** Do not provide medical, legal, or financial advice. If a user seems to be in serious distress or mentions self-harm, gently guide them towards professional help in your reply.
      - **Maintain Neutrality:** On sensitive or complex personal topics (relationships, beliefs, etc.), remain a supportive listener. Do not take sides, give strong advice, or pass judgment.
      - **Use Context:** The `Conversation History` is provided as a JSON string. Use it to understand the full context, including your own past replies, to avoid repeating yourself and maintain conversational flow. You can use the `timestamp` to understand the conversation's pacing.

      # USER TASK:

      Below is the conversation history and the user's latest message. Perform your analysis and generate the JSON response according to the System Instructions.

      --- EXAMPLES FOR GUIDANCE ---

      **-- Example 1: Handling Despair with Care --**
      *Conversation History (JSON format):*
      No previous messages.
      *User's Latest Message:*
      "I am doomed! I think I'm going to do something stupid."
      ```json
      {{
        "mood": "fear",
        "confidence": 98,
        "reply": "It sounds like you are in a tremendous amount of pain right now, and I'm really concerned. Please know that your feelings are valid, but you don't have to go through this alone. There are people who want to help, and talking to a professional can make a real difference."
      }}
      ````

      **-- Example 2: Navigating User Anxiety and Offering Support --**
      *Conversation History (JSON format):*

      ```json
      [
        {{
          "message": "I have that huge presentation with the leadership team tomorrow.",
          "reply": "That's a big deal! You've prepared so much for this. I'm sure you'll do great. How are you feeling about it?",
          "timestamp": "2025-09-11T14:20:00.099000Z"
        }}
      ]
      ```

      *User's Latest Message:*
      "They just added the CEO to the invite. I don't think I can do this."

      ```json
      {{
        "mood": "fear",
        "confidence": 96,
        "reply": "Wow, it's completely understandable why that would feel intimidating, and it's okay to feel that pressure. But take a deep breath. The fact that the CEO is attending shows how important and visible your work is. You've already done the hard preparation. You know this material inside and out."
      }}
      ```

      --- END OF EXAMPLES ---

      **Analyze the following:**

      **Conversation History (JSON format):**
      {conversation_history}

      **User's Latest Message:**
      {final_sentence}
    """

    def __init__(self):
        """
        Initialize the MoodAnalyzer with a Gemini AI client.
        """
        self._model = "gemini-2.5-flash"
        self._client = genai.Client(api_key=settings.GEMINI_API_KEY)

    def analyze(
        self, text: str, history: list[ConversationMessage]
    ) -> MoodAnalysisResult:
        """
        Analyze the mood of the given text and generate an empathetic reply.

        Args:
            text (str): The latest user message.
            history (list): List of prior conversation messages in JSON string format.
        Returns:
            MoodAnalysisResult: A dictionary with keys 'mood', 'confidence', and 'reply'.
        """
        prompt = self.PROMPT_TEMPLATE.format(
            conversation_history=[h.model_dump_json() for h in history],
            final_sentence=text,
        )
        logger.info("analyzing with prompt")

        try:
            response = self._client.models.generate_content(
                model=self._model, contents=prompt
            )
        except Exception as e:
            logger.error(f"Error during Gemini API call: {str(e)}")
            raise
        return MoodAnalysisResult.parse_json_markdown(str(response.text))
