# -*- coding: utf-8 -*-
"""
Database CLI commands for Copaw
"""

import os
import sys
import subprocess
from pathlib import Path

import click

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from db import (
        init_db,
        get_database_url,
        DatabaseCommands,
        session_scope,
        Agent,
    )
    DB_AVAILABLE = True
except ImportError as e:
    DB_AVAILABLE = False
    click.echo(f"Warning: Database module not available: {e}")


@click.group()
def db():
    """Database management commands."""
    pass


@db.command()
@click.option("--url", "-u", help="Database URL")
def init(url):
    """Initialize database tables."""
    if not DB_AVAILABLE:
        click.echo("❌ Database dependencies not installed")
        return
    
    click.echo(f"Initializing database...")
    
    if url is None:
        url = get_database_url()
    
    init_db(url)
    click.echo(f"Database initialized: {url}")
    
    # Verify connection
    status = DatabaseCommands.status()
    if status["status"] == "connected":
        click.echo("✅ Database connection OK")
    else:
        click.echo(f"❌ Database error: {status.get('message')}")


@db.command()
@click.argument("backup_file")
def backup(backup_file):
    """Backup database to file."""
    if not DB_AVAILABLE:
        click.echo("❌ Database dependencies not installed")
        return
    
    click.echo(f"Backing up database to: {backup_file}")
    DatabaseCommands.backup(backup_file)
    click.echo("✅ Backup complete")


@db.command()
@click.argument("backup_file")
def restore(backup_file):
    """Restore database from file."""
    if not DB_AVAILABLE:
        click.echo("❌ Database dependencies not installed")
        return
    
    if not os.path.exists(backup_file):
        click.echo(f"❌ File not found: {backup_file}")
        return
    
    click.echo(f"Restoring database from: {backup_file}")
    DatabaseCommands.restore(backup_file)
    click.echo("✅ Restore complete")


@db.command()
def status():
    """Check database status."""
    if not DB_AVAILABLE:
        click.echo("❌ Database dependencies not installed")
        return
    
    result = DatabaseCommands.status()
    if result["status"] == "connected":
        click.echo("✅ Database: connected")
    else:
        click.echo(f"❌ Database: {result.get('message')}")


@db.command()
def list_agents():
    """List all agents."""
    if not DB_AVAILABLE:
        click.echo("❌ Database dependencies not installed")
        return
    
    with session_scope() as session:
        agents = session.query(Agent).all()
        if not agents:
            click.echo("No agents found")
            return
        
        click.echo(f"{'ID':<5} {'Name':<20} {'Role':<15} {'Status':<10}")
        click.echo("-" * 55)
        for agent in agents:
            click.echo(f"{agent.id:<5} {agent.name:<20} {agent.role:<15} {agent.status:<10}")


@db.command()
@click.option("--password", "-p", help="Database password")
@click.option("--port", "-o", default="5432", help="Database port")
def start(password, port):
    """Start PostgreSQL with Docker (using docker-compose)."""
    password = password or os.environ.get("COPAW_DB_PASSWORD", "copaw_password")
    
    # Set environment variables
    env = os.environ.copy()
    env["COPAW_DB_PASSWORD"] = password
    env["COPAW_DB_PORT"] = port
    
    # Check if container already exists
    result = subprocess.run(
        ["docker", "ps", "-a", "--filter", "name=copaw-db", "--format", "{{.Names}}"],
        capture_output=True,
        text=True
    )
    
    if "copaw-db" in result.stdout:
        # Container exists, start it
        click.echo("Starting existing container...")
        subprocess.run(["docker", "start", "copaw-db"], check=True)
    else:
        # Run with docker-compose
        db_dir = Path(__file__).parent.parent / "db"
        click.echo(f"Starting PostgreSQL with pgvector...")
        
        result = subprocess.run(
            ["docker-compose", "up", "-d"],
            cwd=db_dir,
            env=env,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            click.echo(f"❌ Error: {result.stderr}")
            return
    
    click.echo(f"✅ PostgreSQL started on port {port}")
    click.echo(f"   Database: copaw")
    click.echo(f"   User: copaw")
    click.echo(f"   Password: {password}")
    click.echo(f"   pgvector: enabled")


@db.command()
def stop():
    """Stop PostgreSQL Docker container."""
    subprocess.run(["docker", "stop", "copaw-db"], capture_output=True)
    click.echo("✅ PostgreSQL stopped")


@db.command()
def restart():
    """Restart PostgreSQL Docker container."""
    subprocess.run(["docker", "restart", "copaw-db"], capture_output=True)
    click.echo("✅ PostgreSQL restarted")


@db.command()
def logs():
    """View PostgreSQL logs."""
    subprocess.run(["docker", "logs", "-f", "copaw-db"])


if __name__ == "__main__":
    db()
