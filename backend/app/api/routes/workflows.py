from fastapi import APIRouter, Depends, HTTPException

from app.agents.workflows import WorkflowOrchestrator
from app.api.dependencies import get_workflow_orchestrator
from app.core.models import WorkflowRequest, WorkflowResponse
from app.utils.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/workflows/execute", response_model=WorkflowResponse)
async def execute_workflow(
    request: WorkflowRequest,
    orchestrator: WorkflowOrchestrator = Depends(get_workflow_orchestrator),
) -> WorkflowResponse:
    try:
        logger.info("workflow_request_received", workflow_type=request.workflow_type.value)

        response = await orchestrator.execute_workflow(request)

        return response

    except Exception as e:
        logger.error("workflow_execution_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")
