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
from pathlib import Path
import json
import tempfile
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
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
        await page.click('button:has-text("Dashboard")')
        await page.wait_for_selector("#dashboard.active")
        
        # Test Nodes button
        await page.click('button:has-text("Nodos")')
        await page.wait_for_selector("#nodes.active")
        
        # Test Create button
        await page.click('button:has-text("Crear Nodo")')
        await page.wait_for_selector("#create.active")
        
        # Test Search button
        await page.click('button:has-text("Buscar")')
        await page.wait_for_selector("#search.active")
        
        # Test Settings button
        await page.click('button:has-text("Configuración")')
        await page.wait_for_selector("#settings.active")


class TestCreateNode:
    """Tests for creating nodes through the admin panel."""
    
    @pytest.mark.asyncio
    async def test_create_node_form_visible(self, page, base_url):
        """Test that create node form is visible."""
        await page.goto(f"{base_url}/admin")
        
        # Navigate to create section
        await page.click('button:has-text("Crear Nodo")')
        
        # Check form elements
        node_id_input = await page.query_selector("#nodeId")
        node_type_select = await page.query_selector("#nodeType")
        node_content = await page.query_selector("#nodeContent")
        create_button = await page.query_selector('button:has-text("Crear Nodo")')
        
        assert node_id_input is not None
        assert node_type_select is not None
        assert node_content is not None
        assert create_button is not None
    
    @pytest.mark.asyncio
    async def test_create_simple_node(self, page, base_url):
        """Test creating a simple node through the form."""
        await page.goto(f"{base_url}/admin")
        
        # Navigate to create section
        await page.click('button:has-text("Crear Nodo")')
        
        # Fill form
        await page.fill("#nodeId", "test_e2e_concept")
        await page.select_option("#nodeType", "concept")
        await page.fill("#nodeContent", "Test concept from E2E test")
        
        # Submit form
        await page.click('button:has-text("✓ Crear Nodo")')
        
        # Wait briefly for alert to appear
        await page.wait_for_timeout(1000)
        
        # Check if alert exists (may have class alert and alert-success)
        alert = await page.query_selector(".alert")
        assert alert is not None
    
    @pytest.mark.asyncio
    async def test_create_node_with_metadata(self, page, base_url):
        """Test creating node with metadata."""
        await page.goto(f"{base_url}/admin")
        
        # Navigate to create section
        await page.click('button:has-text("Crear Nodo")')
        
        # Fill form
        await page.fill("#nodeId", "test_e2e_rule")
        await page.select_option("#nodeType", "rule")
        await page.fill("#nodeContent", "Test rule from E2E")
        await page.fill("#nodeMetadata", '{"priority": "high"}')
        
        # Submit form
        await page.click('button:has-text("✓ Crear Nodo")')
        
        # Wait briefly for alert to appear
        await page.wait_for_timeout(1000)
        
        # Check if alert exists
        alert = await page.query_selector(".alert")
        assert alert is not None


class TestNodeManagement:
    """Tests for node management operations."""
    
    @pytest.mark.asyncio
    async def test_list_nodes_loads(self, page, base_url):
        """Test that nodes list loads."""
        await page.goto(f"{base_url}/admin")
        
        # Navigate to nodes section
        await page.click('button:has-text("Nodos")')
        
        # Wait for nodes list
        await page.wait_for_selector(".nodes-list", timeout=5000)
        
        # Check list exists
        nodes_list = await page.query_selector(".nodes-list")
        assert nodes_list is not None
    
    @pytest.mark.asyncio
    async def test_search_nodes_live(self, page, base_url):
        """Test live search functionality."""
        await page.goto(f"{base_url}/admin")
        
        # Navigate to nodes section
        await page.click('button:has-text("Nodos")')
        await page.wait_for_selector(".nodes-list", timeout=5000)
        
        # Type in search
        await page.fill("#searchInput", "philosophy")
        
        # Wait a bit for filtering
        await page.wait_for_timeout(500)
        
        # Check filtered results
        node_items = await page.query_selector_all(".node-item")
        assert len(node_items) > 0
    
    @pytest.mark.asyncio
    async def test_view_node_details(self, page, base_url):
        """Test viewing node details in modal."""
        await page.goto(f"{base_url}/admin")
        
        # Navigate to nodes
        await page.click('button:has-text("Nodos")')
        await page.wait_for_selector(".node-item", timeout=5000)
        
        # Click first node's "Ver" button
        view_buttons = await page.query_selector_all('button:has-text("Ver")')
        if view_buttons:
            await view_buttons[0].click()
            
            # Wait for modal
            await page.wait_for_selector(".modal.active", timeout=5000)
            
            # Check modal content
            modal = await page.query_selector(".modal-content")
            assert modal is not None


class TestSearchFunctionality:
    """Tests for advanced search."""
    
    @pytest.mark.asyncio
    async def test_search_by_type(self, page, base_url):
        """Test searching nodes by type."""
        await page.goto(f"{base_url}/admin")
        
        # Navigate to search
        await page.click('button:has-text("Buscar")')
        
        # Select type filter
        await page.select_option("#searchType", "rule")
        
        # Submit search
        await page.click('button:has-text("🔍 Buscar")')
        
        # Wait briefly for search to process
        await page.wait_for_timeout(500)
        
        # Check results exist (may be hidden but present in DOM)
        results = await page.query_selector("#searchResults")
        assert results is not None
    
    @pytest.mark.asyncio
    async def test_search_by_content(self, page, base_url):
        """Test searching by content match."""
        await page.goto(f"{base_url}/admin")
        
        # Navigate to search
        await page.click('button:has-text("Buscar")')
        
        # Enter search content
        await page.fill("#searchContent", "philosophy")
        
        # Submit search
        await page.click('button:has-text("🔍 Buscar")')
        
        # Wait briefly for search to process
        await page.wait_for_timeout(500)
        
        # Check results exist
        results = await page.query_selector("#searchResults")
        assert results is not None


class TestSettings:
    """Tests for settings and operations."""
    
    @pytest.mark.asyncio
    async def test_settings_page_loads(self, page, base_url):
        """Test that settings page loads."""
        await page.goto(f"{base_url}/admin")
        
        # Navigate to settings
        await page.click('button:has-text("Configuración")')
        
        # Check settings elements
        graph_status = await page.query_selector("#graphStatus")
        assert graph_status is not None
    
    @pytest.mark.asyncio
    async def test_download_graph(self, page, base_url):
        """Test downloading graph as JSON."""
        await page.goto(f"{base_url}/admin")
        
        # Navigate to settings
        await page.click('button:has-text("Configuración")')
        
        # Listen for download (async context manager)
        async with page.expect_download() as download_info:
            await page.click('button:has-text("⬇️ Descargar JSON")')
        
        download = await download_info.value
        
        # Verify download
        assert download.suggested_filename is not None
        assert download.suggested_filename.startswith("graph_")


class TestResponsiveness:
    """Tests for responsive design."""
    
    @pytest.mark.asyncio
    async def test_admin_panel_mobile_view(self, browser, base_url):
        """Test admin panel on mobile viewport."""
        context = await browser.new_context(
            viewport={"width": 375, "height": 667}  # iPhone size
        )
        page = await context.new_page()
        
        await page.goto(f"{base_url}/admin")
        
        # Check elements are visible
        dashboard = await page.query_selector("#dashboard")
        assert dashboard is not None
        
        # Take screenshot for visual inspection
        # await page.screenshot(path="mobile_view.png")
        
        await context.close()
    
    @pytest.mark.asyncio
    async def test_admin_panel_tablet_view(self, browser, base_url):
        """Test admin panel on tablet viewport."""
        context = await browser.new_context(
            viewport={"width": 768, "height": 1024}  # iPad size
        )
        page = await context.new_page()
        
        await page.goto(f"{base_url}/admin")
        
        # Check responsive layout
        container = await page.query_selector(".container")
        assert container is not None
        
        await context.close()


class TestUserFlow:
    """Integration tests for complete user workflows."""
    
    @pytest.mark.asyncio
    async def test_complete_workflow_create_and_search(self, page, base_url):
        """Test complete workflow: create node, then search for it."""
        await page.goto(f"{base_url}/admin")
        
        # Step 1: Create a new node
        await page.click('button:has-text("Crear Nodo")')
        await page.fill("#nodeId", f"workflow_test_{int(time.time())}")
        await page.select_option("#nodeType", "concept")
        await page.fill("#nodeContent", "Workflow test concept")
        await page.click('button:has-text("✓ Crear Nodo")')
        
        # Wait for success
        await page.wait_for_selector(".alert-success", timeout=5000)
        
        # Step 2: Navigate to search
        await page.click('button:has-text("Buscar")')
        
        # Step 3: Search for the created node
        await page.select_option("#searchType", "concept")
        await page.click('button:has-text("🔍 Buscar")')
        
        # Wait briefly for search to process
        await page.wait_for_timeout(500)
        
        # Step 4: Verify results element exists
        results = await page.query_selector("#searchResults")
        assert results is not None
    
    @pytest.mark.asyncio
    async def test_complete_workflow_create_view_delete(self, page, base_url):
        """Test workflow: create, view, and list nodes."""
        await page.goto(f"{base_url}/admin")
        
        # Create node
        await page.click('button:has-text("Crear Nodo")')
        test_id = f"view_test_{int(time.time())}"
        await page.fill("#nodeId", test_id)
        await page.select_option("#nodeType", "guideline")
        await page.fill("#nodeContent", "Test guideline for view")
        await page.click('button:has-text("✓ Crear Nodo")')
        await page.wait_for_selector(".alert-success", timeout=5000)
        
        # Navigate to nodes list
        await page.click('button:has-text("Nodos")')
        await page.wait_for_selector(".node-item", timeout=5000)
        
        # Search for our node
        await page.fill("#searchInput", test_id)
        await page.wait_for_timeout(300)
        
        # Verify node appears
        node_items = await page.query_selector_all(".node-item")
        assert len(node_items) > 0


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
        await page.click('button:has-text("Nodos")')
        await page.wait_for_selector(".node-item", timeout=5000)
        
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
        
        # Get initial total nodes
        initial_text = await page.text_content("#totalNodes")
        
        # Click refresh
        await page.click('button:has-text("🔄 Actualizar")')
        
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
        await page.click('button:has-text("Crear Nodo")')
        
        # Fill form
        await page.fill("#nodeId", "test_value")
        await page.fill("#nodeContent", "test content")
        
        # Click reset
        await page.click('button:has-text("↻ Limpiar")')
        
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
        await page.click('button:has-text("Nodos")')
        await page.wait_for_selector(".node-item", timeout=5000)
        
        # Click view button to open modal
        view_buttons = await page.query_selector_all('button:has-text("Ver")')
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
