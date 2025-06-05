from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

def setup_qa_chain(vector_db, llm):
    prompt_template = """
    Context: {context}
    User: {question}
    AntarVaani:"""

    PROMPT = PromptTemplate(template=prompt_template.strip(), input_variables=['context', 'question'])

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_db.as_retriever(),
        chain_type_kwargs={"prompt": PROMPT}
    )
    return qa_chain
