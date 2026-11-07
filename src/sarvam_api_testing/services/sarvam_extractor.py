
import os
import json
import time

from dotenv import load_dotenv
from sarvamai import SarvamAI
from src.sarvam_api_testing.schema.esic import WORKER_SCHEMA

load_dotenv()

API_KEY = os.getenv("SARVAM_API_KEY")

if not API_KEY:
    raise RuntimeError("SARVAM_API_KEY is missing from .env")

client = SarvamAI(
    api_subscription_key=API_KEY
)

# WORKER_SCHEMA = {
#     "type": "object",
#     "properties": {
#         "document_type": {"type": "string"},
#         "name": {"type": "string"},
#         "father_name": {"type": "string"},
#         "date_of_birth": {"type": "string"},
#         "uan": {"type": "string"},
#         "esic_number": {"type": "string"},
#         "bank_account_number": {"type": "string"},
#         "ifsc": {"type": "string"},
#         "identity_number_last4": {"type": "string"},
#         "driving_licence_number": {"type": "string"}
#     }
# }


def extract_worker_document(file_path: str):

    with open(file_path, "rb") as pdf:

        job = client.doc_ai.extract(
            file=[
                (
                    os.path.basename(file_path),
                    pdf,
                    "application/pdf"
                )
            ],
            schema=json.dumps(WORKER_SCHEMA),
            output_format="json"
        )

    print("Sarvam Job ID:", job.job_id)

    terminal_states = {
        "completed",
        "partially_completed",
        "failed",
        "rejected"
    }

    for attempt in range(60):

        status = client.doc_ai.get_status(
            job_id=job.job_id
        )

        current_status = status.status.lower()

        print("Sarvam Status:", current_status)

        if current_status in terminal_states:
            break

        time.sleep(5)

    else:
        raise TimeoutError("Sarvam extraction timed out")

    if current_status not in {"completed", "partially_completed"}:
        raise RuntimeError(
            f"Sarvam extraction failed: {current_status}"
        )

    result = client.doc_ai.get_results(
        job_id=job.job_id
    )

    return result.result
