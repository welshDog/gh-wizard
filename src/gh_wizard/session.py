"""Session management for hyperfocus mode."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
import uuid

from gh_wizard.utils.logger import setup_logger

logger = setup_logger(__name__)


class SessionManager:
    """Manage hyperfocus sessions and context preservation."""

    def __init__(self, config_dir: Optional[str] = None):
        """Initialize session manager.
        
        Args:
            config_dir: Directory for session storage. Defaults to ~/.ghwizard
        """
        if config_dir is None:
            config_dir = os.path.expanduser("~/.ghwizard")
        
        self.config_dir = Path(config_dir)
        self.sessions_dir = self.config_dir / "sessions"
        self.current_session_file = self.config_dir / "current_session.json"
        
        # Create directories if they don't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def start(self, name: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Start a new hyperfocus session.
        
        Args:
            name: Session name
            metadata: Optional metadata (repo, branch, etc.)
            
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())[:8]
        
        session = {
            "session_id": session_id,
            "name": name,
            "created_at": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat(),
            "status": "active",
            "metadata": metadata or {},
            "context": {},
            "breadcrumbs": [],
        }
        
        # Save session
        session_file = self.sessions_dir / f"{session_id}.json"
        with open(session_file, "w") as f:
            json.dump(session, f, indent=2)
        
        # Set as current
        self._set_current_session(session_id)
        logger.info(f"Session started: {session_id} - {name}")
        
        return session_id

    def pause(self, session_id: Optional[str] = None) -> None:
        """Pause current or specified session.
        
        Args:
            session_id: Optional session ID. Uses current if not provided.
        """
        if session_id is None:
            session_id = self._get_current_session_id()
        
        if not session_id:
            raise ValueError("No active session")
        
        session = self._load_session(session_id)
        session["status"] = "paused"
        session["last_active"] = datetime.now().isoformat()
        self._save_session(session_id, session)
        logger.info(f"Session paused: {session_id}")

    def resume(self, session_id: str) -> None:
        """Resume a paused session.
        
        Args:
            session_id: Session ID to resume
        """
        session = self._load_session(session_id)
        session["status"] = "active"
        session["last_active"] = datetime.now().isoformat()
        self._save_session(session_id, session)
        self._set_current_session(session_id)
        logger.info(f"Session resumed: {session_id}")

    def get_current_session(self) -> Optional[Dict[str, Any]]:
        """Get current active session."""
        session_id = self._get_current_session_id()
        if session_id:
            return self._load_session(session_id)
        return None

    def get_last_session(self) -> Optional[Dict[str, Any]]:
        """Get the most recently modified session."""
        sessions: List[Dict[str, Any]] = []
        for session_file in self.sessions_dir.glob("*.json"):
            try:
                with open(session_file) as f:
                    session = json.load(f)
                    sessions.append(session)
            except Exception as e:
                logger.warning(f"Failed to load session {session_file}: {e}")
        
        if sessions:
            # Sort by last_active
            sessions.sort(key=lambda x: x.get("last_active", ""), reverse=True)
            return sessions[0]
        return None

    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all sessions."""
        sessions = []
        for session_file in self.sessions_dir.glob("*.json"):
            try:
                with open(session_file) as f:
                    session = json.load(f)
                    sessions.append(session)
            except Exception as e:
                logger.warning(f"Failed to load session {session_file}: {e}")
        
        # Sort by last_active
        sessions.sort(key=lambda x: x.get("last_active", ""), reverse=True)
        return sessions

    def update_context(self, session_id: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> None:
        """Update session context.
        
        Args:
            session_id: Optional session ID. Uses current if not provided.
            context: Context data to merge
        """
        if session_id is None:
            session_id = self._get_current_session_id()
        
        if not session_id:
            raise ValueError("No active session")
        
        session = self._load_session(session_id)
        if context:
            session["context"].update(context)
        session["last_active"] = datetime.now().isoformat()
        self._save_session(session_id, session)

    def add_breadcrumb(self, message: str, session_id: Optional[str] = None) -> None:
        """Add a breadcrumb (navigation trace) to session.
        
        Args:
            message: Breadcrumb message
            session_id: Optional session ID. Uses current if not provided.
        """
        if session_id is None:
            session_id = self._get_current_session_id()
        
        if not session_id:
            raise ValueError("No active session")
        
        session = self._load_session(session_id)
        session["breadcrumbs"].append({
            "timestamp": datetime.now().isoformat(),
            "message": message,
        })
        self._save_session(session_id, session)

    # Private methods
    def _load_session(self, session_id: str) -> Dict[str, Any]:
        """Load session from disk."""
        session_file = self.sessions_dir / f"{session_id}.json"
        with open(session_file) as f:
            result: Dict[str, Any] = json.load(f)
            return result

    def _save_session(self, session_id: str, session: Dict[str, Any]) -> None:
        """Save session to disk."""
        session_file = self.sessions_dir / f"{session_id}.json"
        with open(session_file, "w") as f:
            json.dump(session, f, indent=2)

    def _set_current_session(self, session_id: str) -> None:
        """Set current session ID."""
        with open(self.current_session_file, "w") as f:
            json.dump({"session_id": session_id}, f)

    def _get_current_session_id(self) -> Optional[str]:
        """Get current session ID."""
        try:
            if self.current_session_file.exists():
                with open(self.current_session_file) as f:
                    data: Dict[str, Any] = json.load(f)
                    return data.get("session_id")
        except Exception as e:
            logger.warning(f"Failed to get current session: {e}")
        return None
