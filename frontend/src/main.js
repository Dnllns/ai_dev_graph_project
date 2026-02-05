import './style.css';
import * as d3 from 'd3';

// Constants: Neon Cyberpunk Palette
const NODE_COLORS = {
  "project": "#ff2e63",    // Neon Pink
  "concept": "#08d9d6",    // Cyan
  "rule": "#ff9a00",       // Orange
  "guideline": "#00ff9d",  // Matrix Green
  "instruction": "#d500f9", // Vivid Purple
  "resource": "#256eff",   // Electric Blue
  "test": "#ffd300",       // Cyber Yellow
  "default": "#475569"
};

// Global State
let simulation;
let zoom;
let svg;
let g;
let graphData = { nodes: [], links: [] };
let linkedByIndex = {};
let activeFilters = new Set(Object.keys(NODE_COLORS));

// DOM Initialization
document.addEventListener('DOMContentLoaded', () => {
  initLegend();
  initFilters();
  loadGraphVisualization();

  // Make settings panel open by default or logic? Let's start closed for cleaner view
  // No, standard is usually open or minimal. Let's toggle it open initially to show features
  // document.getElementById('settings-content').style.maxHeight = '500px'; 
  // Actually user asked for collapsed improvement, let's keep it closed or minimal.
  // Let's rely on user click.
});

window.addEventListener('resize', () => {
  if (document.getElementById('dashboard').classList.contains('active')) {
    resizeGraph();
  }
});

// --- UI Logic ---

window.toggleSettingsPanel = function () {
  const content = document.getElementById('settings-content');
  const chevron = document.getElementById('settings-chevron');

  if (content.style.maxHeight === '0px' || !content.style.maxHeight) {
    content.style.maxHeight = '500px'; // Approx max height
    content.style.opacity = '1';
    chevron.style.transform = 'rotate(180deg)';
  } else {
    content.style.maxHeight = '0px';
    content.style.opacity = '0';
    chevron.style.transform = 'rotate(0deg)';
  }
}

window.initLegend = function () {
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

    item.innerHTML = `<div style="width:8px; height:8px; border-radius:50%; background:${color}; box-shadow: 0 0 6px ${color}"></div><span>${type.toUpperCase()}</span>`;
    legendContainer.appendChild(item);
  });
}

window.initFilters = function () {
  const container = document.getElementById('filter-controls');
  if (!container) return;

  container.innerHTML = '';
  Object.keys(NODE_COLORS).forEach(type => {
    if (type === 'default') return;
    const toggle = document.createElement('label');
    toggle.className = 'filter-toggle';
    toggle.innerHTML = `
            <input type="checkbox" class="filter-checkbox" value="${type}" checked onchange="toggleFilter('${type}')">
            <span>${type.charAt(0).toUpperCase() + type.slice(1)}</span>
        `;
    container.appendChild(toggle);
  });
}

// --- Main View Logic ---

window.showSection = function (id) {
  document.querySelectorAll('.section').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));

  document.getElementById(id).classList.add('active');

  // Update Sidebar state
  const navItems = document.querySelectorAll('.nav-item');
  if (id === 'dashboard') navItems[0].classList.add('active');
  if (id === 'nodes') navItems[1].classList.add('active');
  if (id === 'create') navItems[2].classList.add('active');
  if (id === 'logs') navItems[3].classList.add('active');

  if (id === 'nodes') loadNodesList();
  if (id === 'logs') loadLogs();
  if (id === 'dashboard') {
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
    .on("click", resetHighlight);

  g = svg.append("g");

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
    .force("collide", d3.forceCollide().radius(35));

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
    .attr("stroke", "var(--border)") // Add explicit stroke for export compatibility
    .attr("stroke-opacity", 0.3)
    .attr("marker-end", "url(#arrow)");

  // Nodes
  const tooltip = d3.select("#graph-tooltip");

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
    .on("dblclick", focusNode) // New Feature
    .on("mouseover", function (event, d) {
      const type = d.type || d.data?.type || 'default';
      const color = NODE_COLORS[type] || NODE_COLORS.default;
      tooltip.transition().duration(200).style("opacity", 1);
      tooltip.html(`
                <strong style="color:${color}">${d.id}</strong><br/>
                <span style="color:#94a3b8; font-size:0.75rem">${type.toUpperCase()}</span><br/>
                <div style="margin-top:4px; font-size:0.75rem; color:#cbd5e1; max-height:60px; overflow:hidden;">
                    ${(d.content || d.data?.content || '').slice(0, 80)}
                </div>
            `)
        .style("left", (event.pageX + 15) + "px")
        .style("top", (event.pageY - 28) + "px");
    })
    .on("mouseout", function () {
      tooltip.transition().duration(500).style("opacity", 0);
    });

  node.append("circle")
    .attr("r", d => {
      const type = d.type || d.data?.type || 'default';
      return (type === 'project' || d.id.startsWith("role_")) ? 16 : 10;
    })
    .attr("fill", d => {
      const type = d.type || d.data?.type || 'default';
      return NODE_COLORS[type] || NODE_COLORS.default;
    })
    .attr("stroke", "rgba(255,255,255,0.4)")
    .attr("stroke-width", 2)
    .style("filter", d => {
      const type = d.type || d.data?.type || 'default';
      const color = NODE_COLORS[type] || NODE_COLORS.default;
      return `drop-shadow(0 0 6px ${color})`;
    });

  node.append("text")
    .attr("dx", 16)
    .attr("dy", 4)
    .text(d => d.id)
    .style("fill", "#94a3b8") // Explicit fill for export
    .style("font-size", "10px")
    .style("font-family", "sans-serif");

  // Simulation Tick
  simulation.on("tick", () => {
    link
      .attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y);

    node.attr("transform", d => `translate(${d.x},${d.y})`);
  });

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

function nodeClicked(event, d) {
  event.stopPropagation();
  d3.select("#graph-tooltip").style("opacity", 0);

  // Highlight L1 Neighbors
  const neighbors = new Set();
  d3.selectAll(".link").each(function (l) {
    if (l.source.id === d.id) neighbors.add(l.target.id);
    if (l.target.id === d.id) neighbors.add(l.source.id);
  });

  d3.selectAll(".node").classed("dimmed", true).classed("highlighted", false).attr("opacity", 0.1);

  d3.selectAll(".node")
    .filter(n => n.id === d.id || neighbors.has(n.id))
    .classed("dimmed", false)
    .classed("highlighted", true)
    .attr("opacity", 1);

  d3.selectAll(".link").classed("dimmed", true).attr("opacity", 0.05);
  d3.selectAll(".link")
    .filter(l => (l.source.id === d.id || l.target.id === d.id))
    .classed("dimmed", false)
    .attr("opacity", 1);

  window.showDetails(d);
}

function focusNode(event, d) {
  event.stopPropagation();
  const width = document.getElementById('graph-container').clientWidth;
  const height = document.getElementById('graph-container').clientHeight;

  svg.transition().duration(1000).call(
    zoom.transform,
    d3.zoomIdentity.translate(width / 2, height / 2).scale(2).translate(-d.x, -d.y)
  );
}

function resetHighlight() {
  d3.selectAll(".node").classed("dimmed", false).classed("highlighted", false).attr("opacity", 1).style("display", d => activeFilters.has(d.data.type) ? "block" : "none");
  d3.selectAll(".link").classed("dimmed", false).classed("highlighted", false).attr("opacity", 1).style("display", l => (activeFilters.has(l.source.data.type) && activeFilters.has(l.target.data.type)) ? "block" : "none");
  window.closeModal();
}

window.toggleFilter = function (type) {
  if (activeFilters.has(type)) {
    activeFilters.delete(type);
  } else {
    activeFilters.add(type);
  }

  // Update graph visibility
  d3.selectAll(".node").style("display", d => activeFilters.has(d.data.type || 'default') ? "block" : "none");
  d3.selectAll(".link").style("display", d => (activeFilters.has(d.source.data.type) && activeFilters.has(d.target.data.type)) ? "block" : "none");
}

window.zoomIn = function () { svg.transition().call(zoom.scaleBy, 1.2); }
window.zoomOut = function () { svg.transition().call(zoom.scaleBy, 0.8); }
window.resetZoom = function () {
  const width = document.getElementById('graph-container').clientWidth;
  const height = document.getElementById('graph-container').clientHeight;
  svg.transition().duration(750).call(
    zoom.transform,
    d3.zoomIdentity.translate(width / 2, height / 2).scale(0.6).translate(-width / 2, -height / 2)
  );
}

window.updateForce = function (type, value) {
  document.getElementById(`val-${type}`).textContent = value;
  if (!simulation) return;
  if (type === 'charge') simulation.force("charge").strength(+value);
  else if (type === 'link') simulation.force("link").distance(+value);
  simulation.alpha(0.3).restart();
}

window.exportGraphPng = function () {
  const svgNode = document.querySelector("#graph-container svg");
  if (!svgNode) return;

  const serializer = new XMLSerializer();
  let source = serializer.serializeToString(svgNode);

  // Add specific namespaces if missing
  if (!source.match(/^<svg[^>]+xmlns="http\:\/\/www\.w3\.org\/2000\/svg"/)) {
    source = source.replace(/^<svg/, '<svg xmlns="http://www.w3.org/2000/svg"');
  }

  const canvas = document.createElement("canvas");
  canvas.width = svgNode.clientWidth * 2; // High res
  canvas.height = svgNode.clientHeight * 2;
  const ctx = canvas.getContext("2d");

  const img = new Image();
  img.src = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(source);

  img.onload = () => {
    ctx.fillStyle = "#0f172a"; // Background color
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

    const a = document.createElement("a");
    a.download = "nexus_graph.png";
    a.href = canvas.toDataURL("image/png");
    a.click();
  };
}

// --- Details & Modals ---

window.showDetails = function (d) {
  const nodeData = d.data || d;
  const content = nodeData.content || "No content available.";
  const type = d.type || nodeData.type || "unknown";

  const panel = document.getElementById('details-panel');
  const typeTag = document.getElementById('details-type');

  typeTag.textContent = type;
  typeTag.style.borderColor = NODE_COLORS[type] || NODE_COLORS.default;
  typeTag.style.color = NODE_COLORS[type] || NODE_COLORS.default;

  document.getElementById('details-title').textContent = d.id;
  document.getElementById('details-text').textContent = content;
  document.getElementById('details-meta').textContent = JSON.stringify(nodeData.metadata || nodeData, null, 2);

  panel.classList.add('active');
};

window.closeModal = function () {
  document.getElementById('details-panel').classList.remove('active');
};

// --- Library ---

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
  // Basic impl
  const id = document.getElementById('nodeId').value;
  const type = document.getElementById('nodeType').value;
  const content = document.getElementById('nodeContent').value;

  if (!id || !content) return alert("Required fields missing");

  try {
    await fetch('/nodes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id, type, content, metadata: {} })
    });
    alert("Success");
    document.getElementById('nodeId').value = "";
  } catch (e) {
    alert("Error");
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
