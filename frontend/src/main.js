import './style.css';
import * as d3 from 'd3';

// Constants
const NODE_COLORS = {
  "project": "#f43f5e",
  "concept": "#3b82f6",
  "rule": "#f59e0b",
  "guideline": "#10b981",
  "instruction": "#8b5cf6",
  "resource": "#64748b",
  "test": "#eab308",
  "default": "#475569"
};

// Global State
let simulation;
let zoom;
let svg;
let g;
let graphData = { nodes: [], links: [] };
let linkedByIndex = {};

// DOM Initialization
document.addEventListener('DOMContentLoaded', () => {
  initLegend();
  loadGraphVisualization();

  // Global Search Handler
  window.handleGlobalSearch = function (query) {
    query = query.toLowerCase();

    // Filter in Graph View
    if (query.length > 0) {
      d3.selectAll(".node").each(function (d) {
        const match = d.id.toLowerCase().includes(query) || (d.data.content && d.data.content.toLowerCase().includes(query));
        d3.select(this).classed("dimmed", !match).classed("highlighted", match);
      });
      d3.selectAll(".link").classed("dimmed", true);
    } else {
      resetHighlight();
    }

    // Filter in Library View
    if (document.getElementById('nodes').classList.contains('active')) {
      window.filterNodesLib(query);
    }
  };
});

window.addEventListener('resize', () => {
  if (document.getElementById('dashboard').classList.contains('active')) {
    resizeGraph();
  }
});

// --- Initialization Helpers ---

function initLegend() {
  const legendContainer = document.getElementById('legend');
  if (!legendContainer) return;

  legendContainer.innerHTML = '<h4 style="margin-bottom:8px; font-weight:600; font-size:0.8rem;">LEGEND</h4>';

  Object.entries(NODE_COLORS).forEach(([type, color]) => {
    if (type === 'default') return;
    const item = document.createElement('div');
    item.style.display = 'flex';
    item.style.alignItems = 'center';
    item.style.gap = '8px';
    item.style.marginBottom = '4px';
    item.style.fontSize = '0.75rem';
    item.style.color = 'var(--text-muted)';

    item.innerHTML = `<div style="width:8px; height:8px; border-radius:50%; background:${color}"></div><span>${type.toUpperCase()}</span>`;
    legendContainer.appendChild(item);
  });
}

// --- Main View Logic ---

window.showSection = function (id) {
  document.querySelectorAll('.section').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));

  document.getElementById(id).classList.add('active');

  // Find nav item (hacky but works)
  const navItems = document.querySelectorAll('.nav-item');
  if (id === 'dashboard') navItems[0].classList.add('active');
  if (id === 'nodes') navItems[1].classList.add('active');
  if (id === 'create') navItems[2].classList.add('active');
  if (id === 'logs') navItems[3].classList.add('active');

  if (id === 'nodes') loadNodesList();
  if (id === 'logs') loadLogs();
  if (id === 'dashboard') {
    // Give time for layout to happen
    setTimeout(resizeGraph, 100);
  }
};

window.resizeGraph = function () {
  if (!svg) return;
  const container = document.getElementById('graph-container');
  const width = container.clientWidth;
  const height = container.clientHeight;
  svg.attr("width", width).attr("height", height);
  if (simulation) {
    simulation.force("center", d3.forceCenter(width / 2, height / 2));
    simulation.alpha(0.3).restart();
  }
}

// --- Graph Visualization Core ---

window.loadGraphVisualization = async function () {
  try {
    const response = await fetch('/graph');
    if (!response.ok) throw new Error('Failed to fetch graph');

    const rawData = await response.json();
    const links = rawData.links || rawData.edges || [];
    // Deep copy to allow D3 mutation without affecting raw data logic if reloaded
    graphData = {
      nodes: rawData.nodes.map(d => ({ ...d })),
      links: links.map(d => ({ ...d }))
    };

    // Update Stats
    document.getElementById('totalNodes').textContent = graphData.nodes.length;
    document.getElementById('totalEdges').textContent = graphData.links.length;
    document.getElementById('density').textContent = (rawData.density || 0).toFixed(4);

    // Prep Connectivity Index
    linkedByIndex = {};
    graphData.links.forEach(d => {
      linkedByIndex[`${d.source},${d.target}`] = 1;
    });

    renderGraph();

  } catch (error) {
    console.error("Error loading graph:", error);
  }
};

function renderGraph() {
  const container = document.getElementById('graph-container');
  const width = container.clientWidth;
  const height = container.clientHeight;

  d3.select("#graph-container svg").remove();

  svg = d3.select("#graph-container")
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .on("click", resetHighlight); // Background click resets

  g = svg.append("g");

  // Zoom setup
  zoom = d3.zoom()
    .scaleExtent([0.1, 8])
    .on("zoom", (event) => g.attr("transform", event.transform));

  svg.call(zoom);

  // Forces
  const chargeVal = parseInt(document.querySelector('input[oninput*="charge"]').value);
  const linkDistVal = parseInt(document.querySelector('input[oninput*="link"]').value);

  simulation = d3.forceSimulation(graphData.nodes)
    .force("link", d3.forceLink(graphData.links).id(d => d.id).distance(linkDistVal))
    .force("charge", d3.forceManyBody().strength(chargeVal))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collide", d3.forceCollide().radius(30));

  // Arrow Marker
  svg.append("defs").selectAll("marker")
    .data(["end"])
    .enter().append("marker")
    .attr("id", "arrow")
    .attr("viewBox", "0 -5 10 10")
    .attr("refX", 25)
    .attr("refY", 0)
    .attr("markerWidth", 4)
    .attr("markerHeight", 4)
    .attr("orient", "auto")
    .append("path")
    .attr("d", "M0,-5L10,0L0,5")
    .attr("fill", "var(--border-light)");

  // Links
  const link = g.append("g")
    .selectAll(".link")
    .data(graphData.links)
    .enter().append("line")
    .attr("class", "link")
    .attr("marker-end", "url(#arrow)");

  // Nodes
  const node = g.append("g")
    .selectAll(".node")
    .data(graphData.nodes)
    .enter().append("g")
    .attr("class", "node")
    .call(d3.drag()
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended))
    .on("click", nodeClicked)
    .on("mouseover", nodeHovered)
    .on("mouseout", nodeUnhovered);

  node.append("circle")
    .attr("r", d => d.id.startsWith("role_") ? 16 : 10) // Larger for roles
    .attr("fill", d => NODE_COLORS[d.data?.type] || NODE_COLORS.default);

  node.append("text")
    .attr("dx", 16)
    .attr("dy", 4)
    .text(d => d.id);

  // Simulation Tick
  simulation.on("tick", () => {
    link
      .attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y);

    node.attr("transform", d => `translate(${d.x},${d.y})`);
  });

  // Initial Fit
  setTimeout(window.resetZoom, 500);
}

// --- Interactions ---

function dragstarted(event, d) {
  if (!event.active) simulation.alphaTarget(0.3).restart();
  d.fx = d.x;
  d.fy = d.y;
}

function dragged(event, d) {
  d.fx = event.x;
  d.fy = event.y;
}

function dragended(event, d) {
  if (!event.active) simulation.alphaTarget(0);
  d.fx = null;
  d.fy = null;
}

function isConnected(a, b) {
  return linkedByIndex[`${a.id},${b.id}`] || linkedByIndex[`${b.id},${a.id}`] || a.id === b.id;
}

function nodeHovered(event, d) {
  // Optional: Hover effect (lightweight)
  // We prefer click for heavy filtering, but hover can imply
}

function nodeUnhovered(event, d) {
}

function nodeClicked(event, d) {
  event.stopPropagation(); // Prevent background click

  // Highlight Neighbors
  d3.selectAll(".node").classed("dimmed", o => !isConnected(d, o));
  d3.selectAll(".node").classed("highlighted", o => isConnected(d, o));

  d3.selectAll(".link").classed("dimmed", l => l.source.id !== d.id && l.target.id !== d.id);
  d3.selectAll(".link").classed("highlighted", l => l.source.id === d.id || l.target.id === d.id);

  // Show details
  window.showDetails(d);
}

function resetHighlight() {
  d3.selectAll(".node").classed("dimmed", false).classed("highlighted", false);
  d3.selectAll(".link").classed("dimmed", false).classed("highlighted", false);
  window.closeModal();
}

// --- Controls ---

window.zoomIn = function () {
  svg.transition().call(zoom.scaleBy, 1.2);
}

window.zoomOut = function () {
  svg.transition().call(zoom.scaleBy, 0.8);
}

window.resetZoom = function () {
  const width = document.getElementById('graph-container').clientWidth;
  const height = document.getElementById('graph-container').clientHeight;
  svg.transition().duration(750).call(
    zoom.transform,
    d3.zoomIdentity.translate(width / 2, height / 2).scale(0.8).translate(-width / 2, -height / 2) // Centering logic approx
  );
}

window.updateForce = function (type, value) {
  document.getElementById(`val-${type}`).textContent = value;
  if (!simulation) return;

  if (type === 'charge') {
    simulation.force("charge").strength(+value);
  } else if (type === 'link') {
    simulation.force("link").distance(+value);
  }
  simulation.alpha(0.3).restart();
}

// --- Details & Modals ---

window.showDetails = function (d) {
  const nodeData = d.data || d;

  // If d came from search list, it might not have 'data' wrapper if struct differs, 
  // but graph d has d.data. Check structure.
  const content = nodeData.content || (d.data ? d.data.content : "No content");
  const type = nodeData.type || (d.data ? d.data.type : "Unknown");
  const id = d.id;

  document.getElementById('details-type').textContent = type;
  document.getElementById('details-type').style.color = NODE_COLORS[type] || NODE_COLORS.default;
  document.getElementById('details-title').textContent = id;
  document.getElementById('details-text').textContent = content;
  document.getElementById('details-meta').textContent = JSON.stringify(nodeData.metadata || {}, null, 2);

  document.getElementById('details-panel').style.display = 'flex';
};

window.closeModal = function () {
  document.getElementById('details-panel').style.display = 'none';
};

// --- Library & Other Sections ---

window.loadNodesList = async function () {
  const res = await fetch('/nodes');
  const nodes = await res.json();
  const container = document.getElementById('nodesList');
  container.innerHTML = nodes.map(n => `
        <div class="card-item" onclick="fetchNodeDetails('${n.id}')" style="cursor:pointer; border-left:4px solid ${NODE_COLORS[n.data.type] || '#ccc'}">
            <span style="font-size:0.7rem; font-weight:700; text-transform:uppercase; color:${NODE_COLORS[n.data.type]}">${n.data.type}</span>
            <h3 style="margin:8px 0; font-size:1.1rem;">${n.id}</h3>
            <p style="font-size:0.9rem; color:var(--text-muted); display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden;">
                ${n.data.content}
            </p>
        </div>
    `).join('');
};

window.filterNodesLib = function (term) {
  const cards = document.querySelectorAll('.card-item');
  cards.forEach(card => {
    const text = card.innerText.toLowerCase();
    card.style.display = text.includes(term) ? 'block' : 'none';
  });
};

window.fetchNodeDetails = async function (id) {
  const res = await fetch(`/nodes/${id}`);
  const data = await res.json();
  window.showDetails({ id: data.id, data: data.data });
};

window.createNode = async function () {
  // Re-implemented quickly
  const id = document.getElementById('nodeId').value;
  const type = document.getElementById('nodeType').value;
  const content = document.getElementById('nodeContent').value;

  if (!id || !content) return alert("ID and Content required");

  try {
    await fetch('/nodes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id, type, content, metadata: {} })
    });
    alert("Created!");
    document.getElementById('nodeId').value = "";
    document.getElementById('nodeContent').value = "";
  } catch (e) {
    alert("Error creating node");
  }
};

window.loadLogs = async function () {
  const res = await fetch('/logs');
  const logs = await res.json();
  const tbody = document.getElementById('logsBody');
  tbody.innerHTML = logs.map(log => `
        <tr style="border-bottom:1px solid var(--border);">
            <td style="padding:12px; font-size:0.85rem; color:var(--text-muted);">${new Date(log.timestamp).toLocaleTimeString()}</td>
            <td style="padding:12px; font-weight:700; color:var(--primary);">${log.method}</td>
            <td style="padding:12px; font-family:monospace;">${log.path}</td>
            <td style="padding:12px;"><span style="padding:4px 8px; border-radius:4px; background:${log.status_code < 300 ? 'rgba(16,185,129,0.2)' : 'rgba(239,68,68,0.2)'}; color:${log.status_code < 300 ? '#10b981' : '#ef4444'}; font-size:0.75rem; font-weight:700;">${log.status_code}</span></td>
            <td style="padding:12px;">${log.duration_ms}ms</td>
        </tr>
    `).join('');
};

window.downloadJson = function () {
  window.open('/graph', '_blank');
};
