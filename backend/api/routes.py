from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import Dict, Any
import uuid
import os
import asyncio
import tempfile
from datetime import datetime

from ..agents.agent_orchestrator import AgentOrchestrator
from ..utils.report_generator import ReportGenerator
from ..utils.logger import get_logger
from ..utils import memory_storage
from .data_import_routes import router as data_import_router
from .llm_routes import router as llm_router

# Import types directly since shared folder is outside backend package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.types.models import ProjectInput, ProjectAnalysis

router = APIRouter()
logger = get_logger(__name__)

# Include sub-routers
router.include_router(data_import_router, prefix="/data", tags=["data-import"])
router.include_router(llm_router, prefix="/config", tags=["configuration"])

orchestrator = AgentOrchestrator()
report_generator = ReportGenerator()

@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_project(
    project_input: ProjectInput,
    background_tasks: BackgroundTasks
):
    """
    Analyze a project description using AI agents.
    """
    try:
        analysis_id = str(uuid.uuid4())

        # Save to memory storage
        memory_storage.save_analysis(analysis_id, {
            "input_description": project_input.description,
            "status": "processing",
            "created_at": datetime.utcnow().isoformat()
        })

        # Start background analysis
        background_tasks.add_task(
            run_analysis,
            analysis_id,
            project_input.description,
            project_input.dict()
        )

        return {
            "analysis_id": analysis_id,
            "status": "processing",
            "message": "Analysis started. Use the analysis_id to check status."
        }

    except Exception as e:
        logger.error(f"Error starting analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """
    Get the status and results of an analysis.
    """
    try:
        analysis = memory_storage.get_analysis(analysis_id)

        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")

        return analysis

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis/{analysis_id}/report/{format}")
async def download_report(
    analysis_id: str,
    format: str
):
    """
    Download the analysis report in PDF or Markdown format.
    """
    if format not in ["pdf", "markdown"]:
        raise HTTPException(status_code=400, detail="Format must be 'pdf' or 'markdown'")

    try:
        analysis = memory_storage.get_analysis(analysis_id)

        if not analysis or analysis.get("status") != "completed":
            raise HTTPException(status_code=404, detail="Analysis not found or not completed")

        # Prepare analysis data
        summary_data = analysis.get('summary_analysis', {})
        technical_data = analysis.get('technical_analysis', {})
        estimation_data = analysis.get('estimation_analysis', {})

        analysis_data = {
            "input_description": analysis.get("input_description", ""),
            "summary": summary_data if summary_data else {
                "executive_summary": {"project_overview": analysis.get('executive_summary', '')},
                "project_highlights": {},
                "major_risks": analysis.get('risks_and_dependencies', []),
                "key_recommendations": [],
                "next_steps": []
            },
            "technical_analysis": technical_data if technical_data else {
                "recommended_tech_stack": analysis.get('tech_stack', {})
            },
            "estimation_analysis": estimation_data if estimation_data else {
                "team_composition": analysis.get('team_composition', []),
                "cost_breakdown": analysis.get('cost_estimate', {}),
                "timeline_breakdown": analysis.get('timeline_breakdown', {})
            }
        }

        if format == "pdf":
            # Create temporary file with .pdf extension
            fd, output_path = tempfile.mkstemp(suffix='.pdf', prefix=f'report_{analysis_id}_')
            os.close(fd)  # Close file descriptor, we'll write to it later

            report_generator.generate_pdf_report(analysis_data, output_path)
            return FileResponse(
                output_path,
                media_type="application/pdf",
                filename=f"project_report_{analysis_id}.pdf"
            )
        else:  # markdown
            markdown_content = report_generator.generate_markdown_report(analysis_data)

            # Create temporary file with .md extension
            fd, output_path = tempfile.mkstemp(suffix='.md', prefix=f'report_{analysis_id}_')
            os.close(fd)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            return FileResponse(
                output_path,
                media_type="text/markdown",
                filename=f"project_report_{analysis_id}.md"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

async def run_analysis(analysis_id: str, project_description: str, context: Dict[str, Any]):
    """
    Background task to run the AI analysis.
    """
    try:
        logger.info(f"Starting analysis for {analysis_id}")

        # Run the analysis
        analysis_result = await orchestrator.analyze_project(project_description, context)

        # Extract data for storage
        summary_data = analysis_result.get('summary', {})
        technical_data = analysis_result.get('technical_analysis', {})
        estimation_data = analysis_result.get('estimation_analysis', {})

        # Update memory storage with results
        memory_storage.update_analysis_status(
            analysis_id,
            status="completed",
            completed_at=datetime.utcnow().isoformat(),
            # Full agent outputs
            intake_analysis=analysis_result.get('intake_analysis', {}),
            technical_analysis=technical_data,
            estimation_analysis=estimation_data,
            summary_analysis=summary_data,
            # Legacy flat fields for backward compatibility
            executive_summary=summary_data.get('executive_summary', {}).get('project_overview', ''),
            tech_stack=technical_data.get('recommended_tech_stack', {}),
            team_composition=estimation_data.get('team_composition', []),
            timeline_breakdown=estimation_data.get('timeline_breakdown', {}),
            cost_estimate=estimation_data.get('cost_breakdown', {}),
            risks_and_dependencies=summary_data.get('major_risks', [])
        )

        logger.info(f"Analysis {analysis_id} completed successfully")

    except Exception as e:
        error_message = str(e)
        logger.error(f"Error in analysis {analysis_id}: {error_message}")

        # Check if it's a user-friendly error message (from quota limit)
        if "power nap" in error_message or "recharge" in error_message:
            friendly_message = error_message
        else:
            friendly_message = f"Analysis failed: {error_message}"

        # Update status to failed with user-friendly message
        memory_storage.update_analysis_status(
            analysis_id,
            status="failed",
            error=friendly_message
        )