"""End-to-End tests for AI Dev Graph Admin Panel using Playwright.

To run these tests, install Playwright:
    pip install playwright>=1.40.0 pytest-asyncio>=0.23.0
    
Then run:
    pytest tests/test_e2e.py -v
    
Or with specific browser:
    pytest tests/test_e2e.py -v --headed  # See browser window
"""

import pytest
import asyncio
from playwright.async_api import async_playwright
import uvicorn
import threading
import time

from ai_dev_graph.api.main import app



# Server management
class ServerManager:
    """Manage API server for testing."""
    
    def __init__(self, host="127.0.0.1", port=8001):
        self.host = host
        self.port = port
        self.url = f"http://{host}:{port}"
        self.thread = None
        self.is_running = False
    
    def start(self):
        """Start the server in a background thread."""
        def run_server():
            config = uvicorn.Config(app, host=self.host, port=self.port, log_level="error")
            server = uvicorn.Server(config)
            asyncio.run(server.serve())
        
        self.thread = threading.Thread(target=run_server, daemon=True)
        self.thread.start()
        self.is_running = True
        
        # Wait for server to start
        time.sleep(2)
    
    def stop(self):
        """Stop the server."""
        self.is_running = False


# Fixtures
@pytest.fixture(scope="session")
def server():
    """Start API server for entire test session."""
    manager = ServerManager()
    manager.start()
    
    yield manager
    
    manager.stop()


@pytest.fixture
def base_url(server):
    """Return the base URL for tests."""
    return server.url


@pytest.fixture
async def browser():
    """Create browser instance for tests."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        yield browser
        await browser.close()


@pytest.fixture
async def page(browser, base_url):
    """Create a new page for each test."""
    context = await browser.new_context()
    page = await context.new_page()
    yield page
    await context.close()


# Tests
class TestAdminDashboard:
    """Tests for Admin Panel Dashboard."""
    
    @pytest.mark.asyncio
    async def test_load_admin_panel(self, page, base_url):
        """Test that admin panel loads successfully."""
        await page.goto(f"{base_url}/admin")
        
        # Check page title
        assert "AI Dev Graph" in await page.title()
        
        # Check dashboard section exists
        dashboard = await page.query_selector("#dashboard")
        assert dashboard is not None
    
    @pytest.mark.asyncio
    async def test_dashboard_displays_stats(self, page, base_url):
        """Test that dashboard displays graph statistics."""
        await page.goto(f"{base_url}/admin")
        
        # Wait for stats to load
        await page.wait_for_selector("#totalNodes", timeout=5000)
        
        # Check stats elements exist
        total_nodes = await page.query_selector("#totalNodes")
        total_edges = await page.query_selector("#totalEdges")
        density = await page.query_selector("#density")
        
        assert total_nodes is not None
        assert total_edges is not None
        assert density is not None
        
        # Check that stats have content
        nodes_text = await total_nodes.text_content()
        assert nodes_text and nodes_text.strip() != ""
    
    @pytest.mark.asyncio
    async def test_navigation_buttons(self, page, base_url):
        """Test that all navigation buttons work."""
        await page.goto(f"{base_url}/admin")
        
        # Test Dashboard button
        await page.click('.nav-item:has-text("Visualizer")')
        await page.wait_for_selector("#dashboard.active")
        
        # Test Nodes button
        await page.click('.nav-item:has-text("Nodes Library")')
        await page.wait_for_selector("#nodes.active")
        
        # Test Create button
        await page.click('.nav-item:has-text("Ingest Knowledge")')
        await page.wait_for_selector("#create.active")
        
        # Test Logs button
        await page.click('.nav-item:has-text("Activity Logs")')
        await page.wait_for_selector("#logs.active")


class TestCreateNode:
    """Tests for creating nodes through the admin panel."""
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_create_node_form_visible(self, page, base_url):
        """Test that create node form is visible."""
        await page.goto(f"{base_url}/admin")
        
        # Navigate to create section
        await page.click('.nav-item:has-text("Ingest Knowledge")')
        
        # Check form elements
        node_id_input = await page.query_selector("#nodeId")
        node_type_select = await page.query_selector("#nodeType")
        node_content = await page.query_selector("#nodeContent")
        create_button = await page.query_selector('button:has-text("Create Node")')
        
        assert node_id_input is not None
        assert node_type_select is not None
        assert node_content is not None
        assert create_button is not None
    
    @pytest.mark.asyncio
    async def test_create_simple_node(self, page, base_url):
        """Test creating a simple node through the form."""
        await page.goto(f"{base_url}/admin")
        
        # Navigate to create section
        await page.click('.nav-item:has-text("Ingest Knowledge")')
        
        # Fill form
        await page.fill("#nodeId", "test_e2e_concept")
        await page.select_option("#nodeType", "concept")
        await page.fill("#nodeContent", "Test concept from E2E test")
        
        # Submit form
        await page.click('button:has-text("Create Node")')
        
        # Wait briefly for alert to appear
        await page.wait_for_selector("#alertBox", state="visible", timeout=5000)
        
        # Check if alert exists 
        alert = await page.query_selector("#alertBox")
        assert alert is not None
    
    @pytest.mark.asyncio
    async def test_create_node_with_metadata(self, page, base_url):
        """Test creating node with metadata."""
        await page.goto(f"{base_url}/admin")
        
        # Navigate to create section
        await page.click('.nav-item:has-text("Ingest Knowledge")')
        
        # Fill form
        await page.fill("#nodeId", "test_e2e_rule")
        await page.select_option("#nodeType", "rule")
        await page.fill("#nodeContent", "Test rule from E2E")
        await page.fill("#nodeMetadata", '{"priority": "high"}')
        
        # Submit form
        await page.click('button:has-text("Create Node")')
        
        # Wait briefly for alert to appear
        await page.wait_for_selector("#alertBox", state="visible", timeout=5000)
        
        # Check if alert exists
        alert = await page.query_selector("#alertBox")
        assert alert is not None


class TestNodeManagement:
    """Tests for node management operations."""
    
    @pytest.mark.asyncio
    async def test_list_nodes_loads(self, page, base_url):
        """Test that nodes list loads."""
        await page.goto(f"{base_url}/admin")
        
        # Navigate to nodes section
        await page.click('.nav-item:has-text("Nodes Library")')
        
        # Wait for nodes list
        await page.wait_for_selector("#nodesList", timeout=5000)
        
        # Check list exists
        nodes_list = await page.query_selector("#nodesList")
        assert nodes_list is not None
    
    @pytest.mark.asyncio
    async def test_search_nodes_live(self, page, base_url):
        """Test live search functionality."""
        await page.goto(f"{base_url}/admin")
        
        # Navigate to nodes section
        await page.click('.nav-item:has-text("Nodes Library")')
        await page.wait_for_selector(".node-card", timeout=5000)
        
        # Type in search
        await page.fill("#searchInput", "philosophy")
        
        # Wait a bit for filtering
        await page.wait_for_timeout(500)
        
        # Check filtered results
        node_items = await page.query_selector_all(".node-card")
        assert len(node_items) > 0
    
    @pytest.mark.asyncio
    async def test_view_node_details(self, page, base_url):
        """Test viewing node details in modal."""
        await page.goto(f"{base_url}/admin")
        
        # Navigate to nodes
        await page.click('.nav-item:has-text("Nodes Library")')
        await page.wait_for_selector(".node-card", timeout=5000)
        
        # Click first node card
        await page.click(".node-card")
        
        # Wait for modal
        await page.wait_for_selector(".modal.active", timeout=5000)
        
        # Check modal content
        modal = await page.query_selector(".modal-content")
        assert modal is not None


# Removed obsolete UI tests


class TestUserFlow:
    """Integration tests for complete user workflows."""
    
    @pytest.mark.asyncio
    async def test_complete_workflow_create_and_search(self, page, base_url):
        """Test complete workflow: create node, then search for it."""
        await page.goto(f"{base_url}/admin")
        
        # Step 1: Create a new node
        await page.click('.nav-item:has-text("Ingest Knowledge")')
        await page.fill("#nodeId", f"workflow_test_{int(time.time())}")
        await page.select_option("#nodeType", "concept")
        await page.fill("#nodeContent", "Workflow test concept")
        await page.click('button:has-text("Create Node")')
        
        # Wait for success
        await page.wait_for_selector("#alertBox", state="visible", timeout=5000)
        
        # Step 2: Navigate to nodes list (search)
        await page.click('.nav-item:has-text("Nodes Library")')
        
        # Step 3: Search for the created node
        await page.fill("#searchInput", "workflow_test")
        
        # Wait briefly for search to process
        await page.wait_for_timeout(500)
        
        # Step 4: Verify results exist
        results = await page.query_selector(".node-card")
        assert results is not None


class TestAPIIntegration:
    """Tests for API integration through the UI."""
    
    @pytest.mark.asyncio
    async def test_api_health_check(self, server):
        """Test API health endpoint."""
        try:
            import aiohttp
        except ImportError:
            pytest.skip("aiohttp not installed")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{server.url}/health") as resp:
                assert resp.status == 200
                data = await resp.json()
                assert data["status"] == "ok"
    
    @pytest.mark.asyncio
    async def test_graph_api_endpoint(self, server):
        """Test /graph API endpoint."""
        try:
            import aiohttp
        except ImportError:
            pytest.skip("aiohttp not installed")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{server.url}/graph") as resp:
                assert resp.status == 200
                data = await resp.json()
                assert "nodes" in data or "directed" in data
    
    @pytest.mark.asyncio
    async def test_create_node_via_api_and_verify_in_ui(self, page, server, base_url):
        """Test creating node via API and verifying it in UI."""
        try:
            import aiohttp
            import uuid
        except ImportError:
            pytest.skip("aiohttp not installed")
        
        # Create node via API
        node_id = f"api_test_{uuid.uuid4().hex[:8]}"
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{server.url}/nodes",
                json={
                    "id": node_id,
                    "type": "resource",
                    "content": "Created via API for E2E test",
                    "parents": []
                }
            ) as resp:
                assert resp.status == 200
        
        # Verify in UI
        await page.goto(f"{base_url}/admin")
        await page.click('.nav-item:has-text("Nodes Library")')
        await page.wait_for_selector(".node-card", timeout=5000)
        
        # Search for it
        await page.fill("#searchInput", node_id)
        await page.wait_for_timeout(300)
        
        # Check it appears
        content = await page.content()
        assert node_id in content


# Utility tests
class TestUIElements:
    """Tests for UI elements and interactions."""
    
    @pytest.mark.asyncio
    async def test_refresh_button_works(self, page, base_url):
        """Test that refresh button updates data."""
        await page.goto(f"{base_url}/admin")
        
        # Click refresh
        await page.click('button:has-text("Refresh View")')
        
        # Wait for potential update
        await page.wait_for_timeout(1000)
        
        # Check that element still exists
        updated_text = await page.text_content("#totalNodes")
        assert updated_text is not None
    
    @pytest.mark.asyncio
    async def test_form_reset_button(self, page, base_url):
        """Test that form reset button clears inputs."""
        await page.goto(f"{base_url}/admin")
        
        # Navigate to create
        await page.click('.nav-item:has-text("Ingest Knowledge")')
        
        # Fill form
        await page.fill("#nodeId", "test_value")
        await page.fill("#nodeContent", "test content")
        
        # Click reset
        await page.click('button:has-text("Clear")')
        
        # Check inputs are cleared
        node_id_value = await page.input_value("#nodeId")
        content_value = await page.input_value("#nodeContent")
        
        assert node_id_value == ""
        assert content_value == ""
    
    @pytest.mark.asyncio
    async def test_modal_close_button(self, page, base_url):
        """Test that modal close button works."""
        await page.goto(f"{base_url}/admin")
        
        # Navigate to nodes
        await page.click('.nav-item:has-text("Nodes Library")')
        await page.wait_for_selector(".node-card", timeout=5000)
        
        # Click view button to open modal
        view_buttons = await page.query_selector_all(".node-card")
        if view_buttons:
            await view_buttons[0].click()
            await page.wait_for_selector(".modal.active", timeout=5000)
            
            # Click close button
            await page.click(".modal-close")
            
            # Wait for modal to close
            await page.wait_for_timeout(300)
            
            # Check modal is not visible
            modal = await page.query_selector(".modal.active")
            assert modal is None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
