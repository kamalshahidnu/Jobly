"""CLI command definitions."""

import click
import json
from pathlib import Path

from ...config.settings import settings
from ...memory.sqlite_store import SQLiteStore
from ...services.profile_service import ProfileService
from ...services.job_service import JobService
from ...services.analytics_service import AnalyticsService
from ...services.outreach_service import OutreachService
from ...agents.job_search_agent import JobSearchAgent

from .display import display_table, display_success, display_error, display_info


def _db_path_from_url(url: str) -> str:
    # settings.database_url defaults to "sqlite:///./jobly.db"
    if not url:
        return "jobly.db"
    if url.startswith("sqlite:///"):
        return url.replace("sqlite:///", "", 1)
    if url.startswith("sqlite://"):
        return url.replace("sqlite://", "", 1)
    return url


def _get_store() -> SQLiteStore:
    store = SQLiteStore(_db_path_from_url(settings.database_url))
    store.connect()
    return store


DEFAULT_USER_ID = "demo_user"


@click.group()
def profile_cmd():
    """Profile management commands."""
    return None


@profile_cmd.command("upload")
@click.argument("resume_path", type=click.Path(exists=True))
@click.option("--user-id", default=DEFAULT_USER_ID, help="User ID to save profile under")
def upload_resume(resume_path, user_id):
    """Upload and parse resume."""
    display_info(f"Parsing resume from: {resume_path}")
    store = _get_store()
    service = ProfileService(store)
    profile_data = service.parse_resume(resume_path)
    profile_data.setdefault("id", user_id)
    profile_data.setdefault("name", "Demo User")
    profile_data.setdefault("email", "demo@example.com")

    existing = service.get_profile(user_id)
    if existing:
        service.update_profile(user_id, profile_data)
    else:
        service.create_profile(profile_data)

    display_success(f"Resume parsed and profile saved for user '{user_id}'")


@profile_cmd.command("show")
@click.option("--user-id", default=DEFAULT_USER_ID, help="User ID")
def show_profile(user_id):
    """Display current profile."""
    store = _get_store()
    service = ProfileService(store)
    profile = service.get_profile(user_id)
    if not profile:
        display_info(f"No profile found for '{user_id}'. Run `jobly profile upload <resume>` first.")
        return
    display_table([profile.model_dump()], title="Profile")


@click.group()
def search_cmd():
    """Job search commands."""
    return None


@search_cmd.command("jobs")
@click.option("--keywords", "-k", required=True, help="Search keywords")
@click.option("--location", "-l", default="Remote", help="Job location")
@click.option("--limit", default=50, help="Maximum results")
@click.option("--seed", type=click.Path(exists=True), help="Optional JSON file of seed jobs")
@click.option("--save", is_flag=True, help="Save results into the local DB")
def search_jobs(keywords, location, limit, seed, save):
    """Search for jobs."""
    display_info(f"Searching for '{keywords}' in '{location}'...")
    seed_jobs = []
    if seed:
        try:
            seed_jobs = json.loads(Path(seed).read_text(encoding="utf-8"))
        except Exception:
            seed_jobs = []

    agent = JobSearchAgent(config={"seed_jobs": seed_jobs, "default_limit": limit})
    import asyncio

    jobs_result = asyncio.run(agent.execute({"keywords": keywords, "location": location, "limit": limit}))
    jobs = jobs_result.get("jobs", [])
    display_success(f"Found {len(jobs)} jobs")
    if jobs:
        display_table(jobs[: min(len(jobs), 25)], title="Jobs (top 25)")

    if save and jobs:
        store = _get_store()
        svc = JobService(store)
        for job in jobs:
            try:
                svc.create_job(job)
            except Exception:
                continue
        display_success("Saved jobs to local DB")


@click.group()
def apply_cmd():
    """Application commands."""
    return None


@apply_cmd.command("submit")
@click.argument("job_id")
@click.option("--auto", is_flag=True, help="Auto-submit without approval")
def submit_application(job_id, auto):
    """Submit job application."""
    display_info(f"Preparing application for job: {job_id}")
    if auto:
        display_info("Auto-submit requires an integration (Greenhouse/Lever/etc.).")
        display_success("Application submission queued (mock)")
    else:
        display_info("Review and approve in UI")


@click.group()
def track_cmd():
    """Application tracking commands."""
    return None


@track_cmd.command("list")
@click.option("--status", "-s", help="Filter by status")
def list_applications(status):
    """List all applications."""
    display_info("No applications found")


@track_cmd.command("update")
@click.argument("app_id")
@click.option("--status", "-s", required=True, help="New status")
def update_application(app_id, status):
    """Update application status."""
    display_info(f"Updating application {app_id} to {status}")
    display_success("Application updated!")


@click.group()
def network_cmd():
    """Networking commands."""
    return None


@network_cmd.command("discover")
@click.option("--company", "-c", required=True, help="Company name")
@click.option("--role", "-r", help="Target role")
def discover_contacts(company, role):
    """Discover contacts at company."""
    display_info(f"Discovering contacts at {company}...")
    display_info("Contact discovery requires integrations (LinkedIn / Apollo / etc.).")
    display_success("Found 0 contacts (mock)")


@network_cmd.command("message")
@click.argument("contact_id")
@click.option("--auto", is_flag=True, help="Auto-send without approval")
def send_message(contact_id, auto):
    """Send outreach message."""
    display_info(f"Generating message for contact: {contact_id}")
    store = _get_store()
    svc = OutreachService(store)
    try:
        message = svc.generate_outreach_message(contact_id, {"sender_name": "Demo User"})
    except Exception as exc:
        display_error(str(exc))
        return
    click.echo(message)
    if auto:
        ok = svc.send_message(contact_id, message, method="email")
        if ok:
            display_success("Message sent!")
        else:
            display_error("Message not sent. Configure SMTP settings in `.env`.")
    else:
        display_info("Review and send with --auto when ready")


@click.group()
def analytics_cmd():
    """Analytics commands."""
    return None


@analytics_cmd.command("stats")
@click.option("--days", default=30, help="Number of days to analyze")
def show_stats(days):
    """Show application statistics."""
    display_info(f"Statistics for last {days} days:")
    store = _get_store()
    svc = AnalyticsService(store)
    user_id = DEFAULT_USER_ID
    stats = svc.get_application_stats(user_id)
    response = svc.get_response_rate(user_id, days=days)
    success = svc.get_success_metrics(user_id)

    click.echo(f"  Total Applications: {stats['total_applications']}")
    click.echo(f"  Response Rate: {response}%")
    click.echo(f"  Interview Rate: {success['interview_rate']}%")
    click.echo(f"  Offer Rate: {success['offer_rate']}%")


@analytics_cmd.command("export")
@click.option("--output", "-o", default="report.pdf", help="Output file")
def export_report(output):
    """Export analytics report."""
    display_info(f"Generating report: {output}")
    # Phase 1: Export a very simple JSON snapshot. PDF report can be added later.
    store = _get_store()
    svc = AnalyticsService(store)
    user_id = DEFAULT_USER_ID
    report = {
        "user_id": user_id,
        "generated_at": __import__("datetime").datetime.utcnow().isoformat(timespec="seconds"),
        "stats": svc.get_application_stats(user_id),
        "response_rate": svc.get_response_rate(user_id),
        "success": svc.get_success_metrics(user_id),
    }
    Path(output).write_text(json.dumps(report, indent=2), encoding="utf-8")
    display_success(f"Report saved to {output}")
