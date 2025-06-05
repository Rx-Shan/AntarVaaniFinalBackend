from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.sample_questions import SAMPLE_QUESTIONS
from app.utils import load_therapists
from app.llm_setup import initialize_llm, create_or_load_vector_db
from app.qa_chain import setup_qa_chain
import os
import uvicorn

# File paths
CSV_PATH = "app/updated_mental_health_professionals.csv"
PDF_PATH = "app/data/mental_health_Document.pdf"
DB_PATH = "app/chroma_db"

# Load model, vector DB, chain, and therapists
llm = initialize_llm()
vector_db = create_or_load_vector_db(PDF_PATH, DB_PATH)
qa_chain = setup_qa_chain(vector_db, llm)
therapists = load_therapists(CSV_PATH)

# Combine therapist info
therapist_info = "\n".join([
    f"Name: {t['Name']}, Specialization: {t['Specialization']}, Experience: {t['Experience']} years\nContact: {t['Contact']}\nApproach: {t['Approach']}"
    for t in therapists
])

app = FastAPI()

# Allow frontend calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace with frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class QuestionnaireRequest(BaseModel):
    answers: list[str]

class ChatRequest(BaseModel):
    user_input: str
    history: list[list[str]]
    initial_msg: str

# Questionnaire GET
@app.get("/questions")
def get_questions():
    return SAMPLE_QUESTIONS

# Questionnaire POST
@app.post("/submit")
def submit_questionnaire(data: QuestionnaireRequest):
    questions = list(SAMPLE_QUESTIONS.keys())
    responses = list(zip(questions, data.answers))

    context_str = "\n".join([f"Q: {q}\nA: {a}" for q, a in responses])
    initial_msg = llm.invoke(f"""
1. Greet the user.
2. Analyze their questionnaire responses.
3. Recommend the most suitable therapist.
4. Provide contact information.

User Responses:
{context_str}

Available Therapists:
{therapist_info}
""").content

    return {
        "initial_message": initial_msg,
        "chat_history": [["AntarVaani", initial_msg]]
    }

# Chat POST
@app.post("/chat")
def chat_with_bot(data: ChatRequest):
    history = data.history or []
    history.append(["User", data.user_input])
    response = qa_chain.run(data.user_input)
    history.append(["AntarVaani", response])
    return {"chat_history": history}

# if __name__ == "__main__":
#     port = int(os.getenv("PORT", 8000))  # use env PORT or default 8000
#     uvicorn.run("app.main:app", host="0.0.0.0", port=port)  # <-- use the variable here!