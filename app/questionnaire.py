from typing import List, Dict, Tuple
from dataclasses import dataclass
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt
from rich.progress import track

@dataclass
class Question:
    text: str
    options: List[str]

class QuestionnaireApp:
    def __init__(self, questions: Dict[str, List[str]]):
        self.questions = [Question(q, opts) for q, opts in questions.items()]
        self.responses = []
        self.console = Console()

    def run(self) -> Tuple[Dict, str]:
        for question in track(self.questions, description="Processing..."):
            answer = self.ask_question(question)
            self.responses.append((question.text, answer))
        return self.generate_context()

    def ask_question(self, question: Question) -> str:
        self.console.clear()
        self.console.print(Panel.fit(f"[bold yellow]{question.text}[/]", title="Question"))
        options = "\n".join(f"[bold cyan]{i}. {option}[/]" for i, option in enumerate(question.options, 1))
        self.console.print(Panel.fit(options, title="Options"))
        choice = IntPrompt.ask("Choose an option", choices=[str(i) for i in range(1, len(question.options)+1)])
        return question.options[int(choice) - 1]

    def generate_context(self) -> Tuple[Dict, str]:
        json_context = {
            "metadata": {"total_questions": len(self.questions), "answered": len(self.responses)},
            "answers": [{"question": q, "selected_answer": a} for q, a in self.responses]
        }
        text_context = "\n".join([f"Q: {q}\nA: {a}" for q, a in self.responses])
        return json_context, text_context
