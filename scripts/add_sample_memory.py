from app.rag.models import SaveAnswerRequest
from app.rag.memory import save_qa_to_disk, rebuild_memory_index

samples = [
    SaveAnswerRequest(
        question="What is your standard SLA commitment?",
        answer="Our standard SLA commitment is 99.9% service availability, subject to mutually agreed exclusions and maintenance windows.",
        tags=["SLA", "availability"],
        approved=True,
    ),
    SaveAnswerRequest(
        question="Do you support data encryption?",
        answer="Yes. We support encryption in transit using TLS and encryption at rest using industry-standard encryption controls, depending on the deployment environment.",
        tags=["security", "encryption"],
        approved=True,
    ),
]

for sample in samples:
    save_qa_to_disk(sample)

print(f"Indexed {rebuild_memory_index()} memory items.")
