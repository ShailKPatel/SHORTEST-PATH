const canvas = document.getElementById('graphCanvas');
const ctx = canvas.getContext('2d');
const logArea = document.getElementById('logArea');

// State
let graph = null;
let startNode = null;
let endNode = null;
let animationSteps = [];
let isAnimating = false;
let animationSpeed = 100;

// Config
const NODE_RADIUS = 15;
const COLORS = {
    bg: '#000000',
    edge: '#333333',
    edgeHighlight: '#FFFF00',
    node: '#00FFFF', // Cyan border
    nodeFill: '#000000',
    start: '#FFFF00',
    end: '#FFB8FF',
    visited: '#2121DE',
    frontier: '#FFFFFF',
    path: '#FFFF00'
};

// Init
resizeCanvas();
window.addEventListener('resize', resizeCanvas);

// Interaction listeners for sliders
document.getElementById('numNodes').addEventListener('input', (e) => {
    document.getElementById('nodesValue').innerText = e.target.value;
});
document.getElementById('density').addEventListener('input', (e) => {
    document.getElementById('densityValue').innerText = e.target.value;
});

function resizeCanvas() {
    canvas.width = canvas.parentElement.clientWidth;
    canvas.height = canvas.parentElement.clientHeight;
    if (graph) {
        normalizeGraphCoords(); // Re-normalize on resize
        drawGraph();
    }
}

function log(msg) {
    console.log(`[SHORTEST-PATH]: ${msg}`);
}

const ALL_ALGOS = ["Dijkstra", "Bellman-Ford", "Floyd-Warshall", "Uniform Cost Search", "A*"];

// Sidebar Event Listeners
document.getElementById('btnGenerate').addEventListener('click', generateGraph);
document.getElementById('btnRun').addEventListener('click', runAlgorithm);
document.getElementById('btnViewCode').addEventListener('click', viewAlgorithmCode);

// New Selector Listeners
document.getElementById('startNodeSelect').addEventListener('change', (e) => {
    startNode = parseInt(e.target.value);
    drawGraph();
});
document.getElementById('endNodeSelect').addEventListener('change', (e) => {
    endNode = parseInt(e.target.value);
    drawGraph();
});

document.getElementById('btnReset').addEventListener('click', () => {
    isAnimating = false;
    currentStepIndex = 0;
    if (graph) drawGraph();
});
document.getElementById('speedSelect').addEventListener('change', (e) => {
    animationSpeed = parseInt(e.target.value);
});
document.getElementById('btnRunAll').addEventListener('click', runAllAlgorithms);
document.getElementById('closeModal').addEventListener('click', () => {
    document.getElementById('runAllModal').classList.add('hidden');
});


// Logic
async function generateGraph() {
    const numNodes = document.getElementById('numNodes').value;
    const density = document.getElementById('density').value;
    const directed = document.getElementById('directed').checked;

    // Clear graph before generating
    graph = null;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    log(`Generating graph... Nodes: ${numNodes}`);

    try {
        const res = await fetch('/api/generate-graph', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                num_nodes: parseInt(numNodes),
                density: parseFloat(density),
                directed: directed
            })
        });

        graph = await res.json();
        normalizeGraphCoords();

        // 1. Source to 1 Destination (0 -> Last)
        const nodes = graph.nodes;
        if (nodes.length > 0) {
            // Sort nodes by ID just in case, though usually 0..N
            nodes.sort((a, b) => a.id - b.id);

            populateSelectors(nodes);

            startNode = nodes[0].id; // 0
            endNode = nodes[nodes.length - 1].id; // Last

            // Set select values
            document.getElementById('startNodeSelect').value = startNode;
            document.getElementById('endNodeSelect').value = endNode;

            log(`Graph Generated. Start: ${startNode}, End: ${endNode}`);
            drawGraph();
            document.getElementById('nodeCount').innerText = nodes.length;
            document.getElementById('currentCost').innerText = "0";
            document.getElementById('visitedCount').innerText = "0";
            document.getElementById('statusText').innerText = "READY";
        }

    } catch (e) {
        log(`Error: ${e.message}`);
    }
}

function populateSelectors(nodes) {
    const startSel = document.getElementById('startNodeSelect');
    const endSel = document.getElementById('endNodeSelect');

    startSel.innerHTML = '';
    endSel.innerHTML = '';

    nodes.forEach(n => {
        const opt1 = document.createElement('option');
        opt1.value = n.id;
        opt1.innerText = n.id;
        startSel.appendChild(opt1);

        const opt2 = document.createElement('option');
        opt2.value = n.id;
        opt2.innerText = n.id;
        endSel.appendChild(opt2);
    });
}

function normalizeGraphCoords() {
    // Basic Normalization to fit canvas with padding
    if (!graph || graph.nodes.length === 0) return;

    const padding = 50;
    const width = canvas.width - padding * 2;
    const height = canvas.height - padding * 2;

    // 1. Find Min/Max X and Y from original data
    let minX = Infinity, maxX = -Infinity;
    let minY = Infinity, maxY = -Infinity;

    graph.nodes.forEach(n => {
        if (n.x < minX) minX = n.x;
        if (n.x > maxX) maxX = n.x;
        if (n.y < minY) minY = n.y;
        if (n.y > maxY) maxY = n.y;
    });

    const rangeX = maxX - minX || 1; // Avoid divide by zero
    const rangeY = maxY - minY || 1;

    // 2. Map to canvas
    graph.nodes.forEach(n => {
        // Normalize 0..1 then Scale to Width/Height
        const normX = (n.x - minX) / rangeX;
        const normY = (n.y - minY) / rangeY;

        n.canvasX = normX * width + padding;
        n.canvasY = normY * height + padding;
    });
}

function drawGraph(stepState = null) {
    ctx.fillStyle = COLORS.bg;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    if (!graph) return;

    // Draw Edges
    graph.edges.forEach(edge => {
        const u = graph.nodes.find(n => n.id === edge.source);
        const v = graph.nodes.find(n => n.id === edge.target);

        if (!u || !v) return;

        ctx.beginPath();
        ctx.moveTo(u.canvasX, u.canvasY);
        ctx.lineTo(v.canvasX, v.canvasY);

        if (graph.directed) {
            // Draw arrow (simplified)
        }

        ctx.strokeStyle = COLORS.edge;
        ctx.lineWidth = 1;

        // Highlight edges in the shortest path
        // Highlight edges in the shortest path
        let isInPath = false;
        if (stepState && stepState.parents) {
            // Strict Path Highlighting: Backtrack from EndNode to StartNode
            // Only highlight if this edge matches the parent relationship

            // Check if endNode is reached or we are visualizing a path
            // For general stepState, we might want to show the tree.
            // But user requested "wrong path" fixed.
            // So we usually want to highlight the path found SO FAR to current_node or to end_node if done.

            // Let's assume we want to highlight path to endNode if it has a parent,
            // or maybe path to current_node? 
            // Typically in these viz, we want final path yellow.
            // Let's backtrack from endNode.

            let curr = endNode;
            while (curr !== startNode && curr !== null && stepState.parents[curr] !== undefined) {
                const p = stepState.parents[curr];
                if (p === null) break;

                // Check if this edge is (p -> curr)
                if (edge.source === p && edge.target === curr) {
                    isInPath = true;
                }
                // Undirected check
                if (!graph.directed && edge.source === curr && edge.target === p) {
                    isInPath = true;
                }

                curr = p;

                // Safety break
                if (curr === startNode) break;
            }
        }

        if (isInPath) {
            ctx.strokeStyle = '#FFFF00'; // Yellow for path
            ctx.lineWidth = 4;
        }

        ctx.stroke();

        // Draw Weight (Enhanced Readability)
        const midX = (u.canvasX + v.canvasX) / 2;
        const midY = (u.canvasY + v.canvasY) / 2;

        ctx.fillStyle = '#000'; // Black background
        ctx.fillRect(midX - 6, midY - 6, 12, 12); // Square Box

        ctx.strokeStyle = '#333';
        ctx.strokeRect(midX - 6, midY - 6, 12, 12); // Border

        ctx.fillStyle = '#00FFFF'; // Paccyan text
        ctx.font = 'bold 10px Roboto Mono';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(edge.weight, midX, midY);
    });

    // Draw Nodes
    graph.nodes.forEach(node => {
        let color = COLORS.nodeFill;
        let borderColor = COLORS.node;
        let textColor = '#fff'; // Default white text

        // Dynamic Status
        if (stepState) {
            if (stepState.current_node === node.id) {
                borderColor = '#FFFFFF';
                color = '#FFFF00'; // Active
                textColor = '#000';
            } else if (stepState.frontier.includes(node.id)) {
                borderColor = '#FFFFFF'; // Blink?
            } else if (stepState.visited.includes(node.id)) {
                color = COLORS.visited;
            }
        }

        const isStart = (node.id === startNode);
        const isEnd = (node.id === endNode);



        // Shape
        ctx.beginPath();
        if (isStart) {
            ctx.fillStyle = COLORS.start;
            ctx.arc(node.canvasX, node.canvasY, NODE_RADIUS * 1.2, 0, 2 * Math.PI);
            borderColor = '#fff';
        } else if (isEnd) {
            ctx.fillStyle = COLORS.end;
            ctx.arc(node.canvasX, node.canvasY, NODE_RADIUS * 1.2, 0, 2 * Math.PI);
            borderColor = '#fff';
        } else {
            ctx.arc(node.canvasX, node.canvasY, NODE_RADIUS, 0, 2 * Math.PI);
            ctx.fillStyle = color;
        }
        ctx.fill();
        ctx.strokeStyle = borderColor;
        ctx.stroke();

        if (isStart || isEnd) textColor = '#000';

        // ID
        ctx.fillStyle = textColor;
        ctx.font = 'bold 12px Roboto Mono'; // Slightly bigger
        ctx.textAlign = 'center';
        // Center text in node
        ctx.fillText(node.id, node.canvasX, node.canvasY + 4);

        // Distance Label (d=?)
        let distText = "d=?";
        if (stepState && stepState.distances[node.id] !== undefined) {
            let d = stepState.distances[node.id];
            if (d === "Infinity" || d === Infinity) {
                distText = "d=∞";
            } else {
                distText = `d=${Number(d).toFixed(0)}`;
            }
        } else if (node.id === startNode) {
            distText = "d=0";
        }

        // Draw distance tag above node
        ctx.fillStyle = '#0f0';
        ctx.font = '9px Roboto Mono';
        ctx.fillText(distText, node.canvasX, node.canvasY - 18);
    });

    if (stepState) {
        document.getElementById('visitedCount').innerText = stepState.visited.length;
        document.getElementById('statusText').innerText = "RUNNING";
        if (stepState.distances[endNode] !== undefined) {
            let d = stepState.distances[endNode];
            if (d === "Infinity" || d === Infinity) {
                document.getElementById('currentCost').innerText = "∞";
            } else {
                document.getElementById('currentCost').innerText = Number(d).toFixed(1);
            }
        }
    }
}

// No images used
function drawPacman(x, y) { } // Deprecated
function drawGhost(x, y) { } // Deprecated

function drawArrow(ctx, x1, y1, x2, y2) {
    const headLength = 10;
    const dx = x2 - x1;
    const dy = y2 - y1;
    const angle = Math.atan2(dy, dx);

    // Shorten line to stop at node boundary
    const endX = x2 - NODE_RADIUS * Math.cos(angle);
    const endY = y2 - NODE_RADIUS * Math.sin(angle);
    const startX = x1 + NODE_RADIUS * Math.cos(angle);
    const startY = y1 + NODE_RADIUS * Math.sin(angle);

    ctx.beginPath();
    ctx.moveTo(startX, startY);
    ctx.lineTo(endX, endY);

    // Arrow head
    ctx.lineTo(endX - headLength * Math.cos(angle - Math.PI / 6), endY - headLength * Math.sin(angle - Math.PI / 6));
    ctx.moveTo(endX, endY);
    ctx.lineTo(endX - headLength * Math.cos(angle + Math.PI / 6), endY - headLength * Math.sin(angle + Math.PI / 6));

    ctx.strokeStyle = COLORS.edge;
    ctx.stroke();
}

function drawPacman(x, y) {
    // Draw Image if loaded, else fallback
    if (pacmanImg.complete && pacmanImg.naturalWidth !== 0) {
        const size = NODE_RADIUS * 2.5; // Slightly larger than node
        ctx.drawImage(pacmanImg, x - size / 2, y - size / 2, size, size);
    } else {
        ctx.beginPath();
        ctx.arc(x, y, NODE_RADIUS, 0, 2 * Math.PI); // Full circle fallback
        ctx.fillStyle = COLORS.start;
        ctx.fill();
        ctx.strokeStyle = '#fff';
        ctx.stroke();
    }
}

function drawGhost(x, y) {
    // unused right now as both prefer pacman
    if (ghostImg.complete && ghostImg.naturalWidth !== 0) {
        const size = NODE_RADIUS * 2.5;
        ctx.drawImage(ghostImg, x - size / 2, y - size / 2, size, size);
    } else {
        ctx.beginPath();
        ctx.arc(x, y - 2, NODE_RADIUS - 2, Math.PI, 0, false);
        ctx.lineTo(x + NODE_RADIUS - 2, y + NODE_RADIUS - 2);
        // ctx.lineTo(x - NODE_RADIUS + 2, y + NODE_RADIUS - 2);
        ctx.fillStyle = COLORS.end;
        ctx.fill();
        // Eyes
        ctx.fillStyle = '#fff';
        ctx.fillRect(x - 5, y - 5, 4, 4);
        ctx.fillRect(x + 2, y - 5, 4, 4);
    }
}

async function runAlgorithm() {
    if (!graph) {
        log("No graph generated!");
        return;
    }

    const algo = document.getElementById('algorithmSelect').value;
    log(`Running ${algo}...`);
    isAnimating = false; // Stop current

    const payload = {
        algorithm: algo,
        start_node: startNode,
        end_node: endNode,
        graph: graph
    };

    try {
        const res = await fetch('/api/run-algorithm', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await res.json();

        if (data.steps) {
            animationSteps = data.steps;
            startAnimation();
        } else {
            console.error("No steps returned", data);
            log("No steps returned from algorithm.");
        }
    } catch (e) {
        console.error(e);
        log(`Error: ${e.message}`);
    }
}

async function runAllAlgorithms() {
    if (!graph) {
        log("No graph to run!");
        return;
    }

    console.log("Running all algorithms...");
    const modal = document.getElementById('runAllModal');
    const container = document.getElementById('modalContent');
    const loading = document.getElementById('modalLoading');

    modal.classList.remove('hidden');
    container.innerHTML = '';
    loading.classList.remove('hidden');

    // Sequential execution
    for (const algo of ALL_ALGOS) {
        try {
            const payload = {
                algorithm: algo,
                start_node: startNode,
                end_node: endNode,
                graph: graph
            };

            const start = performance.now();
            const res = await fetch('/api/run-algorithm', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            const end = performance.now();

            if (data.steps) {
                // Find last step
                const lastStep = data.steps[data.steps.length - 1];
                const cost = lastStep.distances[endNode];
                const expanded = lastStep.visited.length;
                const time = (end - start).toFixed(0);

                const finalCost = (cost === "Infinity" || cost === Infinity) ? "∞" : Number(cost).toFixed(1);

                // Append Card
                const card = document.createElement('div');
                card.className = "bg-gray-900 border-2 border-pacblue p-4 text-xs font-mono";
                card.innerHTML = `
                    <div class="text-pacyellow font-bold text-sm mb-2 border-b border-gray-700 pb-1">${algo}</div>
                    <div class="flex justify-between"><span>COST:</span> <span class="text-white">${finalCost}</span></div>
                    <div class="flex justify-between"><span>NODES:</span> <span class="text-white">${expanded}</span></div>
                    <div class="flex justify-between"><span>TIME:</span> <span class="text-white">~${time}ms</span></div>
                 `;
                container.appendChild(card);
            }

        } catch (e) {
            console.error(e);
            const errCard = document.createElement('div');
            errCard.className = "bg-red-900/50 border-2 border-red-500 p-4 text-xs font-mono";
            errCard.innerText = `Error running ${algo}: ${e.message}`;
            container.appendChild(errCard);
        }
    }

    loading.classList.add('hidden');
}

function startAnimation() {
    isAnimating = true;
    let index = 0;

    function loop() {
        if (!isAnimating || index >= animationSteps.length) {
            isAnimating = false;

            // Show final state with path highlighted
            if (animationSteps.length > 0) {
                const finalStep = animationSteps[animationSteps.length - 1];
                drawGraph(finalStep);
                document.getElementById('statusText').innerText = "COMPLETE";

                // Log final path cost
                if (finalStep.distances[endNode] !== undefined) {
                    const finalCost = finalStep.distances[endNode];
                    if (finalCost === Infinity || finalCost === "Infinity") {
                        log("No path found!");
                    } else {
                        log(`Path found! Total cost: ${Number(finalCost).toFixed(2)}`);
                    }
                }
            }

            log("Finished.");
            return;
        }

        const step = animationSteps[index];
        drawGraph(step);
        log(step.description);

        index++;
        setTimeout(loop, animationSpeed);
    }

    loop();
}

// Initial Graph - Generate and Run Algorithm on Load
generateGraph().then(() => {
    // Wait a bit for graph to render, then auto-run the selected algorithm
    setTimeout(() => {
        runAlgorithm();
    }, 500);
});

// View Code feature
document.getElementById('closeCodeModal').addEventListener('click', () => {
    document.getElementById('codeModal').classList.add('hidden');
});

// ESC key to close modal
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const modal = document.getElementById('codeModal');
        if (!modal.classList.contains('hidden')) {
            modal.classList.add('hidden');
        }
    }
});

async function viewAlgorithmCode() {
    const algo = document.getElementById('algorithmSelect').value;
    const modal = document.getElementById('codeModal');
    const content = document.getElementById('codeContent');
    const title = document.getElementById('codeModalTitle');

    title.innerText = `${algo.toUpperCase()} - PYTHON CODE`;
    modal.classList.remove('hidden');
    content.innerText = "Loading source code...";

    try {
        // Encode algo name for URL
        const res = await fetch(`/api/algorithm-code/${encodeURIComponent(algo)}`);
        const data = await res.json();

        if (res.ok) {
            content.innerText = data.code;
        } else {
            content.innerText = `Error: ${data.detail || 'Failed to load code'}`;
        }
    } catch (e) {
        content.innerText = `Failed to fetch code: ${e.message}`;
    }
}
