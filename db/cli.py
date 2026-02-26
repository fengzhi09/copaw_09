# -*- coding: utf-8 -*-
"""
Database CLI commands for Copaw
"""

import os
import sys
import click
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db import init_db, get_database_url, DatabaseCommands, session_scope, Agent


@click.group()
def db():
    """Database management commands."""
    pass


@db.command()
@click.option("--url", "-u", help="Database URL")
def init(url):
    """Initialize database tables."""
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
    click.echo(f"Backing up database to: {backup_file}")
    DatabaseCommands.backup(backup_file)
    click.echo("✅ Backup complete")


@db.command()
@click.argument("backup_file")
def restore(backup_file):
    """Restore database from file."""
    if not os.path.exists(backup_file):
        click.echo(f"❌ File not found: {backup_file}")
        return
    
    click.echo(f"Restoring database from: {backup_file}")
    DatabaseCommands.restore(backup_file)
    click.echo("✅ Restore complete")


@db.command()
def status():
    """Check database status."""
    result = DatabaseCommands.status()
    if result["status"] == "connected":
        click.echo("✅ Database: connected")
    else:
        click.echo(f"❌ Database: {result.get('message')}")


@db.command()
def list_agents():
    """List all agents."""
    with session_scope() as session:
        agents = session.query(Agent).all()
        for agent in agents:
            click.echo(f"{agent.id} | {agent.name} | {agent.role} | {agent.status}")


@db.command()
@click.option("--password", "-p", help="Database password")
@click.option("--port", "-o", default="5432", help="Database port")
def start_docker(password, port):
    """Start PostgreSQL with Docker."""
    password = password or os.environ.get("COPAW_DB_PASSWORD", "copaw_password")
    
    cmd = f"""docker run -d \\
  --name copaw-db \\
  --restart unless-stopped \\
  -e POSTGRES_DB=copaw \\
  -e POSTGRES_USER=copaw \\
  -e POSTGRES_PASSWORD={password} \\
  -p {port}:5432 \\
  -v ./data:/var/lib/postgresql/data \\
  postgres:16-alpine"""
    
    click.echo("Running:\n" + cmd)
    os.system(cmd)
    click.echo("✅ PostgreSQL started")


@db.command()
def stop_docker():
    """Stop PostgreSQL Docker container."""
    os.system("docker stop copaw-db")
    click.echo("✅ PostgreSQL stopped")


if __name__ == "__main__":
    db()
