import uuid
from datetime import datetime
from openlineage.client import OpenLineageClient
from openlineage.client.run import RunEvent, RunState, Run, Job, Dataset
from openlineage.client.transport import HttpTransport
from src.config import MARQUEZ_URL, OPENLINEAGE_DISABLED

if OPENLINEAGE_DISABLED:
    client = None
else:
    transport = HttpTransport(url=MARQUEZ_URL, auth=None)
    client = OpenLineageClient(transport=transport)

def emit_lineage_event(event_type: str, job_name: str, inputs=None, outputs=None):
    """Emit an OpenLineage event."""
    if client is None:
        return
    run_id = str(uuid.uuid4())
    job = Job(namespace="governed-rag", name=job_name)
    run = Run(run_id=run_id)
    event = RunEvent(
        eventType=event_type,
        eventTime=datetime.now().isoformat(),
        run=run,
        job=job,
        inputs=inputs or [],
        outputs=outputs or [],
        producer="governed-rag-pipeline"
    )
    client.emit(event)