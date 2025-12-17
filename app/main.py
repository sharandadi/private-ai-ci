import os
import threading
import logging
from flask import Flask, request, jsonify, abort

# --- IMPORTS ---
from security.hmac_check import verify_signature
from app.utils import clone_repository, cleanup_repository, get_repo_structure
from agents.orchestrator import CIOrchestrator
from app.config import Config
from app.models import db, Job, Log, Settings, Repository
import secrets

# --- CONFIGURATION ---
# Configure logging to see what's happening in the console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [Orchestrator] - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Serve static files from 'dist' folder (Frontend)
app = Flask(__name__, static_folder='../dist', static_url_path='/')
app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ci.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()
    
    # Migrate from .env if first time
    settings = Settings.query.first()
    if not settings:
        settings = Settings(id=1)
        # Try to load from .env
        if Config.GEMINI_API_KEY and Config.GEMINI_API_KEY != 'your_api_key_here':
            settings.gemini_api_key = Config.GEMINI_API_KEY
            settings.github_webhook_secret = Config.GITHUB_WEBHOOK_SECRET or secrets.token_urlsafe(32)
            settings.setup_completed = True
        db.session.add(settings)
        db.session.commit()

# Initialize Orchestrator
from agents.orchestrator import CIOrchestrator
orchestrator = CIOrchestrator()

def run_pipeline_task(repo_url, commit_sha, pusher_name, branch, job_id):
    """
    THE CORE WORKFLOW.
    This function runs in a background thread.
    It orchestrates the AutoGen Agents to test the code.
    """
    logger.info(f"[{job_id}] 🚀 Starting Private AI-CI Pipeline for {pusher_name} on {branch}")
    
    # Update Job Status to Running
    with app.app_context():
        job = Job.query.get(job_id)
        if job:
            job.status = "running"
            db.session.commit()

    local_path = None
    report_content = "Process Failed."

    try:
        # STEP 0: PREPARE
        local_path = clone_repository(repo_url, commit_sha)
        logger.info(f"[{job_id}] Repo cloned to temporary sandbox.")

        # STEP 1: GET STRUCTURE
        structure = get_repo_structure(local_path)
        logger.info(f"[{job_id}] File structure analyzed.")

        # STEP 2: RUN ORCHESTRATOR
        logger.info(f"[{job_id}] invoking AutoGen Orchestrator...")
        report_content = orchestrator.run(local_path, structure)
        
        logger.info(f"[{job_id}] Orchestrator finished.")
        logger.info(f"[{job_id}] Report content length: {len(report_content) if report_content else 0}")
        
        # Update Job Status to Success
        with app.app_context():
            job = Job.query.get(job_id)
            if job:
                job.status = "success"
                job.report_content = report_content if report_content else "Report generation failed or not found."
                db.session.commit()
        
    except Exception as e:
        logger.error(f"[{job_id}] ⚠️ Pipeline Critical Failure: {str(e)}")
        # Update Job Status to Failed
        with app.app_context():
            job = Job.query.get(job_id)
            if job:
                job.status = "failed"
                job.report_content = f"Critical Failure: {str(e)}"
                db.session.commit()
                
    finally:
        # Clean up disk space
        if local_path:
            cleanup_repository(local_path)
        logger.info(f"[{job_id}] Cleanup complete.")


@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """
    The Listener.
    Receives payloads from GitHub, verifies security, and triggers the pipeline.
    """
    # 1. Validate Signature
    signature_header = request.headers.get('X-Hub-Signature-256')
    settings = Settings.query.first()
    webhook_secret = settings.github_webhook_secret if settings else Config.GITHUB_WEBHOOK_SECRET

    if not verify_signature(request.data, signature_header, webhook_secret):
        return jsonify({"error": "Invalid signature"}), 403

    payload = request.json
    
    if not payload:
        abort(400, description="Invalid JSON payload")

    try:
        # Handle cases where payload might be different or partial
        repo_data = payload.get('repository', {})
        repo_url = repo_data.get('clone_url')
        commit_sha = payload.get('after') or payload.get('head_commit', {}).get('id')
        parsed_pusher = payload.get('pusher', {}).get('name', 'Unknown')
        ref = payload.get('ref', 'refs/heads/main')
        branch = ref.split('/')[-1]

        if not repo_url or not commit_sha:
             return jsonify({"error": "Missing repository url or commit sha"}), 400

    except KeyError as e:
        logger.error(f"Payload missing key: {e}")
        abort(400, description=f"Missing field: {e}")

    # Create Job Record
    job_id = commit_sha[:7]
    new_job = Job(
        id=job_id,
        repo_url=repo_url,
        commit_sha=commit_sha,
        pusher=parsed_pusher,
        branch=branch
    )
    db.session.add(new_job)
    db.session.commit()

    # 4. TRIGGER ASYNC PIPELINE
    thread = threading.Thread(
        target=run_pipeline_task, 
        args=(repo_url, commit_sha, parsed_pusher, branch, job_id)
    )
    thread.start()

    return jsonify({
        "status": "queued", 
        "job_id": job_id, 
        "msg": "Agents dispatched."
    }), 202

# --- API ENDPOINTS ---

@app.route('/api/setup', methods=['GET', 'POST'])
def setup():
    """Initial setup endpoint"""
    settings = Settings.query.first()
    if not settings:
        settings = Settings(id=1)
        db.session.add(settings)
    
    if request.method == 'GET':
        return jsonify(settings.to_dict())
    
    # POST: Auto-complete setup (user doesn't configure API key)
    data = request.json
    if not settings.setup_completed:
        settings.github_webhook_secret = settings.github_webhook_secret or secrets.token_urlsafe(32)
        settings.setup_completed = True
        db.session.commit()
    
    return jsonify({"success": True, "message": "Setup completed"})

@app.route('/api/settings', methods=['GET', 'PUT'])
def settings_endpoint():
    """Get/update settings"""
    settings = Settings.query.first()
    if not settings:
        return jsonify({"error": "Setup not completed"}), 400
    
    if request.method == 'GET':
        return jsonify(settings.to_dict())
    
    # PUT: Update settings
    data = request.json
    if 'gemini_api_key' in data:
        settings.gemini_api_key = data['gemini_api_key']
    if 'github_webhook_secret' in data:
        settings.github_webhook_secret = data['github_webhook_secret']
    db.session.commit()
    
    return jsonify({"success": True})

@app.route('/api/repositories', methods=['GET', 'POST'])
def repositories():
    """List or add repositories"""
    if request.method == 'GET':
        repos = Repository.query.filter_by(active=True).all()
        return jsonify([r.to_dict() for r in repos])
    
    # POST: Add repository
    data = request.json
    repo = Repository(
        name=data['name'],
        github_url=data['github_url'],
        webhook_id=data.get('webhook_id')
    )
    db.session.add(repo)
    db.session.commit()
    
    return jsonify(repo.to_dict()), 201

@app.route('/api/repositories/<int:repo_id>', methods=['DELETE'])
def delete_repository(repo_id):
    """Remove repository"""
    repo = Repository.query.get_or_404(repo_id)
    repo.active = False
    db.session.commit()
    return jsonify({"success": True})

@app.route('/api/webhook-url', methods=['GET'])
def webhook_url():
    """Get the webhook URL for GitHub configuration"""
    # Try to detect ngrok URL from request
    base_url = request.host_url.rstrip('/')
    webhook_endpoint = f"{base_url}/webhook"
    
    settings = Settings.query.first()
    
    return jsonify({
        "webhook_url": webhook_endpoint,
        "webhook_secret": settings.github_webhook_secret if settings else "Not configured",
        "setup_completed": settings.setup_completed if settings else False
    })

# --- EXISTING ENDPOINTS ---

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    jobs = Job.query.order_by(Job.created_at.desc()).limit(50).all()
    return jsonify([j.to_dict() for j in jobs])

@app.route('/api/jobs/<job_id>', methods=['GET'])
def get_job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    return jsonify(job.to_dict())

@app.route('/api/jobs/<job_id>/logs', methods=['GET'])
def get_job_logs(job_id):
    logs = Log.query.filter_by(job_id=job_id).order_by(Log.timestamp).all()
    return jsonify([l.to_dict() for l in logs])

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path and os.path.exists(app.static_folder + '/' + path):
        return app.send_static_file(path)
    return app.send_static_file('index.html')


@app.route('/health', methods=['GET'])
def health_check():
    """Simple endpoint to check if the Orchestrator is alive."""
    return jsonify({
        "status": "healthy", 
        "service": "Private AI-CI Orchestrator",
        "mode": "Zero-Config"
    }), 200

if __name__ == '__main__':
    # Listen on all interfaces (0.0.0.0) so Docker/External tools can reach it
    app.run(host='0.0.0.0', port=8080)