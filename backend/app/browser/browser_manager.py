from __future__ import annotations

import asyncio
import logging
import os
import socket
import subprocess
import tempfile
from typing import Dict, Optional, List
from collections import defaultdict

from app.browser.agent_browser_session import AgentBrowserSession
from app.browser.agent_browser_profile import AgentBrowserProfile
from browser_use.browser.session import BrowserSession

logger = logging.getLogger(__name__)

class BrowserManager:
    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(BrowserManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, main_browser_session: Optional[BrowserSession] = None):
        # Initialize only once
        if not hasattr(self, 'initialized'):
            self.browser_process = None
            self.cdp_url = None
            self._agent_sessions: Dict[str, AgentBrowserSession] = {}
            self.profiles: Dict[str, AgentBrowserProfile] = {}
            self.lock = asyncio.Lock()
            self.is_shutting_down = False
            self._agent_target_map: Dict[str, List[str]] = defaultdict(list)  # agent_id -> [target_ids]
            self._target_agent_map: Dict[str, str] = {}  # target_id -> agent_id
            self.initialized = True
            self.main_browser_session: Optional[BrowserSession] = main_browser_session

    def _find_free_port(self) -> int:
        """Finds a free port on localhost."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            return s.getsockname()[1]

    async def get_browser_profile(self, profile_id: str, **kwargs) -> AgentBrowserProfile:
        async with self._lock:
            if profile_id not in self.profiles:
                logger.info(f"Creating new browser profile: {profile_id}")
                self.profiles[profile_id] = AgentBrowserProfile(profile_id=profile_id, **kwargs)
            return self.profiles[profile_id]

    async def get_agent_session(
        self, 
        session_id: str, 
        profile_id: str,
        record_video_dir: Optional[str] = None,
        record_har_path: Optional[str] = None,
        traces_dir: Optional[str] = None,
        headless: bool = True,
        browser_executable_path: Optional[str] = None
    ) -> AgentBrowserSession:
        async with self.lock:
            if session_id in self._agent_sessions:
                return self._agent_sessions[session_id]

            if not self.browser_process or self.browser_process.poll() is not None:
                await self.launch_browser(headless=headless, executable_path=browser_executable_path)

            profile = self._get_or_create_profile(
                profile_id,
                record_video_dir=record_video_dir,
                record_har_path=record_har_path,
                traces_dir=traces_dir
            )
            
            session = AgentBrowserSession(
                id=session_id,
                cdp_url=self.cdp_url,
                browser_profile=profile,
                main_browser_session=self.main_browser_session
            )
            await session.start()
            self._agent_sessions[session_id] = session
            return session

    def _get_or_create_profile(
        self, 
        profile_id: str,
        record_video_dir: Optional[str] = None,
        record_har_path: Optional[str] = None,
        traces_dir: Optional[str] = None
    ) -> AgentBrowserProfile:
        if profile_id not in self.profiles:
            self.profiles[profile_id] = AgentBrowserProfile(
                profile_id=profile_id,
                record_video_dir=record_video_dir,
                record_har_path=record_har_path,
                traces_dir=traces_dir
            )
        return self.profiles[profile_id]

    async def launch_browser(self, headless: bool = True, executable_path: Optional[str] = None, 
                           browser_name: str = "chrome", vision_enabled: bool = True, 
                           cdp_port: int = None, 
                           custom_resolution: tuple = None):
        if self.browser_process and self.browser_process.poll() is not None:
            return  # Browser already running

        port = cdp_port or self._find_free_port()
        self.cdp_url = f"http://127.0.0.1:{port}"
        
        from app.services.browser_config_service import BrowserConfigService
        config_service = BrowserConfigService()

        effective_executable_path = executable_path or config_service.detect_installed_browsers().get(browser_name)
        
        if not effective_executable_path or not os.path.exists(effective_executable_path):
            raise FileNotFoundError(f"Browser executable not found at {effective_executable_path}")

        # Get all browser arguments based on configuration
        chrome_args = [effective_executable_path]
        browser_args = config_service.get_all_browser_args(
            browser_name=browser_name,
            vision_enabled=vision_enabled,
            cdp_port=port,
            custom_width=custom_resolution[0] if custom_resolution else None,
            custom_height=custom_resolution[1] if custom_resolution else None
        )
        chrome_args.extend(browser_args)
        
        # Add user data directory
        chrome_args.append(f"--user-data-dir={tempfile.mkdtemp(prefix='vibesurf_chrome_')}")
        
        if headless:
            chrome_args.extend(["--headless", "--disable-gpu"])

        logging.info(f"Launching browser with command: {' '.join(chrome_args)}")
        self.browser_process = subprocess.Popen(
            chrome_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a moment for the process to start
        await asyncio.sleep(1)
        
        # Check if the process is still running
        if self.browser_process.poll() is not None:
            # Process has exited, get the error output
            stdout, stderr = self.browser_process.communicate()
            logging.error(f"Browser process exited with code {self.browser_process.returncode}")
            logging.error(f"Browser stdout: {stdout.decode()}")
            logging.error(f"Browser stderr: {stderr.decode()}")
            raise RuntimeError(f"Browser process exited with code {self.browser_process.returncode}")
        
        # Wait for browser to start and CDP endpoint to be available
        await self._wait_for_cdp_endpoint(self.cdp_url, max_attempts=30, delay=1)
        logging.info(f"Browser launched with CDP URL: {self.cdp_url}")
        
        # Initialize the main browser session
        if not self.main_browser_session:
            self.main_browser_session = BrowserSession(cdp_url=self.cdp_url)
            await self._safe_connect_session(self.main_browser_session)

    async def _wait_for_cdp_endpoint(self, cdp_url: str, max_attempts: int = 30, delay: float = 1.0):
        """Wait for the CDP endpoint to become available."""
        import httpx
        
        version_url = f"{cdp_url.rstrip('/')}/json/version"
        
        for attempt in range(max_attempts):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(version_url, timeout=5.0)
                    if response.status_code == 200:
                        logging.debug(f"CDP endpoint is available after {attempt + 1} attempts")
                        logging.debug(f"Version info: {response.text}")
                        return
            except Exception as e:
                logging.debug(f"CDP endpoint not ready (attempt {attempt + 1}/{max_attempts}): {e}")
                
            if attempt < max_attempts - 1:  # Don't sleep on the last attempt
                await asyncio.sleep(delay)
        
        raise RuntimeError(f"CDP endpoint at {cdp_url} did not become available after {max_attempts} attempts")

    async def _safe_connect_session(self, session: BrowserSession, max_attempts: int = 5):
        """Safely connect a browser session with retry logic."""
        last_exception = None
        
        for attempt in range(max_attempts):
            try:
                # Ensure the session has the correct CDP URL before connecting
                if hasattr(session, 'browser_profile') and session.browser_profile:
                    session.browser_profile.cdp_url = self.cdp_url
                
                await session.connect()
                logging.debug(f"Successfully connected session on attempt {attempt + 1}")
                return
            except Exception as e:
                last_exception = e
                logging.warning(f"Failed to connect session (attempt {attempt + 1}/{max_attempts}): {e}")
                if attempt < max_attempts - 1:  # Don't sleep on the last attempt
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        raise RuntimeError(f"Failed to connect session after {max_attempts} attempts: {last_exception}")

    async def register_agent(self, agent_id: str, target_id: Optional[str] = None) -> AgentBrowserSession:
        """
        Register an agent and return its primary isolated browser session.
        An agent can only be registered once.
        """
        if agent_id in self._agent_sessions:
            logger.info(f"Agent {agent_id} is already registered.")
            agent_session = self._agent_sessions[agent_id]
        else:
            # Create agent session with proper configuration
            agent_session = AgentBrowserSession(
                id=agent_id,
                cdp_url=self.main_browser_session.cdp_url,
                browser_profile=self.main_browser_session.browser_profile,
                main_browser_session=self.main_browser_session,
            )
            logger.info(f"🚀 Starting agent session for {agent_id} to initialize watchdogs...")
            try:
                await agent_session.start()
                self._agent_sessions[agent_id] = agent_session
            except Exception as e:
                logger.error(f"Failed to start agent session {agent_id}: {e}")
                # Try to reconnect the main session and retry
                try:
                    await self._safe_connect_session(self.main_browser_session)
                    await agent_session.start()
                    self._agent_sessions[agent_id] = agent_session
                except Exception as retry_e:
                    logger.error(f"Retry failed for agent session {agent_id}: {retry_e}")
                    raise RuntimeError(f"Failed to register agent {agent_id} after retry: {retry_e}") from retry_e
            
        # Assign a target to the agent
        await self.assign_target_to_agent(agent_id, target_id)
        return agent_session

    async def assign_target_to_agent(self, agent_id: str, target_id: Optional[str] = None) -> bool:
        """Assign a target to an agent with security validation."""
        # Validate agent exists
        if agent_id not in self._agent_sessions:
            logger.warning(f"Agent '{agent_id}' is not registered.")
            return False

        agent_session = self._agent_sessions[agent_id]

        # Validate target assignment
        if target_id:
            try:
                target_id = await self.main_browser_session.get_target_id_from_tab_id(target_id)
            except Exception:
                logger.warning(f"Target ID '{target_id}' not found.")
                target_id = None
            if target_id:
                target_id_owner = self.get_target_owner(target_id)
                if target_id_owner and target_id_owner != agent_id:
                    logger.warning(
                        f"Target id: {target_id} belongs to {target_id_owner}. You cannot assign it to {agent_id}.")
                    return False

        # Get or create available target
        if target_id is None:
            new_target = await self.main_browser_session.cdp_client.send.Target.createTarget(
                params={'url': 'about:blank'})
            target_id = new_target["targetId"]

        # Connect agent to the target
        await agent_session.connect_agent(target_id=target_id)
        return True

    async def unassign_target(self, target_id: str) -> bool:
        """Unassign a target from its agent."""
        if not target_id:
            logger.warning(f"Please provide valid target id: {target_id}")
            return False
        target_id_owner = self.get_target_owner(target_id)
        if target_id_owner is None:
            logger.warning(f"Target id: {target_id} does not belong to any agent.")
            return False
        agent_session = self._agent_sessions[target_id_owner]
        target_cdp_session = agent_session.get_cdp_session_pool().pop(target_id, None)
        if target_cdp_session is not None:
            await target_cdp_session.disconnect()
        return True

    async def unregister_agent(self, agent_id: str, close_tabs: bool = False):
        """Clean up all resources for an agent with enhanced security cleanup."""
        if agent_id not in self._agent_sessions:
            logger.warning(f"Agent '{agent_id}' is not registered.")
            return

        agent_session = self._agent_sessions.pop(agent_id, None)
        
        try:
            # Close tabs if requested
            if close_tabs and agent_session:
                try:
                    root_client = self.main_browser_session.cdp_client if self.main_browser_session else None
                    if root_client:
                        for target_id in agent_session.get_cdp_session_pool():
                            try:
                                logger.info(f"Close target id: {target_id}")
                                await root_client.send.Target.closeTarget(params={'targetId': target_id})
                            except Exception as e:
                                # Log error if closing tab fails, but continue cleanup
                                logger.warning(f"Error closing target {target_id}: {e}")
                except Exception as e:
                    logger.warning(f"Error closing tabs for agent {agent_id}: {e}")

            # Disconnect the agent's CDP session regardless
            if agent_session:
                try:
                    await agent_session.disconnect_agent()
                except Exception as e:
                    logger.warning(f"Error disconnecting agent {agent_id}: {e}")
                
                try:
                    await agent_session.stop()
                except Exception as e:
                    logger.warning(f"Error stopping agent session {agent_id}: {e}")
        except Exception as e:
            logger.error(f"Error during agent {agent_id} cleanup: {e}")

    def get_agent_sessions(self, agent_id: str) -> Optional[AgentBrowserSession]:
        """Get all sessions (pages) for an agent."""
        return self._agent_sessions.get(agent_id, None)

    def get_active_agents(self) -> List[str]:
        """List all active agent IDs."""
        return list(self._agent_sessions.keys())

    def get_agent_target_ids(self, agent_id: str) -> List[str]:
        """Get all target IDs assigned to a specific agent."""
        agent_session = self.get_agent_sessions(agent_id)
        if agent_session is None:
            return []
        else:
            return list(agent_session.get_cdp_session_pool().keys())

    def get_target_owner(self, target_id: str) -> Optional[str]:
        """Get the agent ID that owns a specific target."""
        for agent_id in self._agent_sessions:
            agent_target_ids = self.get_agent_target_ids(agent_id)
            if target_id in agent_target_ids:
                return agent_id
        return None

    async def close_session(self, session_id: str):
        if session_id in self._agent_sessions:
            logger.info(f"Closing agent session: {session_id}")
            session = self._agent_sessions.pop(session_id)
            await session.stop()
            
            # If no more sessions, consider closing the browser
            if not self._agent_sessions:
                await self.shutdown_browser()

    async def shutdown_browser(self):
        """Shutdown the browser and clean up all resources."""
        try:
            # Unregister all agents first
            agent_ids = list(self._agent_sessions.keys())
            logger.info(f"Shutting down browser, unregistering {len(agent_ids)} agents")
            
            for agent_id in agent_ids:
                try:
                    await self.unregister_agent(agent_id, True)
                    await asyncio.sleep(0.1)  # Small delay between cleanup operations
                except Exception as e:
                    logger.warning(f"Error during agent {agent_id} cleanup: {e}")

            # Terminate browser process if it exists
            if self.browser_process:
                try:
                    logger.info("Terminating browser process")
                    self.browser_process.terminate()
                    # Wait for process to terminate gracefully
                    try:
                        self.browser_process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        # Force kill if it doesn't terminate gracefully
                        self.browser_process.kill()
                        self.browser_process.wait()
                    logger.info("Browser process terminated successfully")
                except Exception as e:
                    logger.warning(f"Error terminating browser process: {e}")
            
            # Clean up CDP connections
            if self.main_browser_session:
                try:
                    await self.main_browser_session.stop()
                    logger.info("Main browser session stopped")
                except Exception as e:
                    logger.warning(f"Error stopping main browser session: {e}")
            
            # Reset state
            self.browser_process = None
            self.cdp_url = None
            self._agent_sessions.clear()
            self._agent_target_map.clear()
            self._target_agent_map.clear()
            self.main_browser_session = None
            
            logger.info("Browser shutdown completed successfully")
        except Exception as e:
            logger.error(f"Error during browser shutdown: {e}")
            raise

    @classmethod
    async def get_instance(cls) -> "BrowserManager":
        if not cls._instance:
            async with cls._lock:
                if not cls._instance:
                    cls._instance = cls()
        return cls._instance

    async def get_or_create_agent_session(self, session_id: str, profile_id: str, **kwargs) -> AgentBrowserSession:
        return await self.get_agent_session(session_id, profile_id, **kwargs)

    async def cleanup_agent(self, session_id: str):
        await self.close_session(session_id)
        logger.info(f"Cleaned up agent resources for session: {session_id}")

    async def get_all_sessions(self) -> Dict[str, AgentBrowserSession]:
        return self._agent_sessions

    async def get_all_profiles(self) -> Dict[str, AgentBrowserProfile]:
        return self.profiles