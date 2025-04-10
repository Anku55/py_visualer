document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('uploadForm');
    const statusDiv = document.getElementById('status');
    const errorDiv = document.getElementById('error');
    const graphContainer = document.getElementById('graph-container');
    const cacheStatus = document.getElementById('cache-status');
    const cacheStatusText = cacheStatus.querySelector('.status-text');

    function showCacheStatus(message, duration = 3000) {
        cacheStatusText.textContent = message;
        cacheStatus.classList.remove('d-none');
        setTimeout(() => {
            cacheStatus.classList.add('d-none');
        }, duration);
    }

    // Node type colors with increased saturation
    const nodeColors = {
        file: '#2196f3',     // Bright blue
        class: '#4caf50',    // Green
        function: '#ffc107',  // Yellow
        method: '#ff9800',    // Orange
        import: '#9e9e9e',    // Gray
        error: '#f44336'      // Red
    };

    // Node sizes by type
    const nodeSizes = {
        file: 25,
        class: 20,
        function: 15,
        method: 15,
        import: 10,
        error: 15
    };

    // Link types
    const linkTypes = {
        defines: { color: '#4CAF50', width: 2 },    // Green
        calls: { color: '#FFC107', width: 1.5 },    // Yellow
        imports: { color: '#9E9E9E', width: 1 },    // Gray
        contains: { color: '#2196F3', width: 2 }     // Blue
    };

    // Keep track of current visualization elements
    let currentSvg = null;
    let currentTooltip = null;
    let currentSimulation = null;

    // Clear any existing visualizations on page load
    clearVisualization();

    function clearVisualization() {
        console.log('Clearing visualization...');
        showCacheStatus('Clearing previous visualization...');
        
        // Stop the current simulation if it exists
        if (currentSimulation) {
            currentSimulation.stop();
            currentSimulation = null;
        }

        // Remove all D3 event listeners and elements
        if (currentSvg) {
            // Remove all event listeners
            currentSvg.selectAll('*').on('.', null);
            currentSvg.on('.', null);
            // Remove the SVG element
            currentSvg.remove();
            currentSvg = null;
        }

        // Remove tooltip
        if (currentTooltip) {
            currentTooltip.remove();
            currentTooltip = null;
        }

        // Clear the graph container completely
        while (graphContainer.firstChild) {
            graphContainer.removeChild(graphContainer.firstChild);
        }

        // Reset D3 zoom behavior
        d3.select('#graph-container').on('.zoom', null);

        // Force garbage collection hint
        if (window.gc) window.gc();
        
        showCacheStatus('Visualization cleared, ready for new data...', 2000);
    }

    // Handle form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const fileInput = document.getElementById('fileInput');
        const file = fileInput.files[0];
        
        if (!file) {
            showError('Please select a file');
            return;
        }

        // Clear previous visualization BEFORE anything else
        clearVisualization();

        // Create fresh FormData
        const formData = new FormData();
        formData.append('file', file);

        // Show loading status
        statusDiv.classList.remove('d-none');
        errorDiv.classList.add('d-none');
        showCacheStatus('Processing new file...', 5000);

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData,
                cache: 'no-store' // Prevent browser caching
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.error) {
                showError(data.error);
                showCacheStatus('Error processing file', 3000);
            } else {
                showCacheStatus('Creating new visualization...', 2000);
                visualizeGraph(data.graph_data);
            }
        } catch (error) {
            showError('An error occurred while processing the file');
            showCacheStatus('Error processing file', 3000);
            console.error('Error:', error);
        } finally {
            statusDiv.classList.add('d-none');
            // Reset file input
            fileInput.value = '';
        }
    });

    function showError(message) {
        errorDiv.textContent = message;
        errorDiv.classList.remove('d-none');
    }

    function visualizeGraph(graphData) {
        const width = graphContainer.clientWidth;
        const height = graphContainer.clientHeight;

        // Create SVG container
        currentSvg = d3.select('#graph-container')
            .append('svg')
            .attr('width', width)
            .attr('height', height)
            .style('background-color', 'var(--bg-secondary)');

        // Create a group for the zoom transform
        const g = currentSvg.append('g');

        // Create tooltip
        currentTooltip = d3.select('body')
            .append('div')
            .attr('class', 'tooltip')
            .style('opacity', 0);

        // Enhanced force simulation
        currentSimulation = d3.forceSimulation(graphData.nodes)
            .force('link', d3.forceLink(graphData.links)
                .id(d => d.id)
                .distance(d => {
                    // Adjust link distance based on node types
                    const sourceType = d.source.type;
                    const targetType = d.target.type;
                    if (sourceType === 'file' || targetType === 'file') return 200;
                    if (sourceType === 'class' || targetType === 'class') return 150;
                    if (d.type === 'calls') return 100;
                    return 80;
                }))
            .force('charge', d3.forceManyBody()
                .strength(d => {
                    // Adjust repulsion force based on node type
                    if (d.type === 'file') return -2000;
                    if (d.type === 'class') return -1000;
                    if (d.type === 'function' || d.type === 'method') return -500;
                    return -300;
                }))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(d => nodeSizes[d.type] * 2));

        // Create arrow markers for different link types
        const defs = currentSvg.append('defs');
        Object.entries(linkTypes).forEach(([type, style]) => {
            defs.append('marker')
                .attr('id', `arrow-${type}`)
                .attr('viewBox', '0 -5 10 10')
                .attr('refX', 20)
                .attr('refY', 0)
                .attr('markerWidth', 6)
                .attr('markerHeight', 6)
                .attr('orient', 'auto')
                .append('path')
                .attr('d', 'M0,-5L10,0L0,5')
                .attr('fill', style.color);
        });

        // Add glow effect
        const glowFilter = defs.append('filter')
            .attr('id', 'glow');
        
        glowFilter.append('feGaussianBlur')
            .attr('stdDeviation', '2')
            .attr('result', 'coloredBlur');
        
        const feMerge = glowFilter.append('feMerge');
        feMerge.append('feMergeNode')
            .attr('in', 'coloredBlur');
        feMerge.append('feMergeNode')
            .attr('in', 'SourceGraphic');

        // Create links
        const link = g.append('g')
            .selectAll('line')
            .data(graphData.links)
            .enter()
            .append('line')
            .attr('stroke', d => linkTypes[d.type]?.color || '#666')
            .attr('stroke-width', d => linkTypes[d.type]?.width || 1)
            .attr('stroke-opacity', 0.6)
            .attr('marker-end', d => `url(#arrow-${d.type})`);

        // Create nodes
        const node = g.append('g')
            .selectAll('g')
            .data(graphData.nodes)
            .enter()
            .append('g')
            .call(d3.drag()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended));

        // Add circles to nodes
        node.append('circle')
            .attr('r', d => nodeSizes[d.type])
            .style('fill', d => nodeColors[d.type])
            .style('stroke', '#fff')
            .style('stroke-width', 2)
            .style('filter', 'url(#glow)');

        // Add labels to nodes
        node.append('text')
            .text(d => d.name)
            .attr('x', d => nodeSizes[d.type] + 5)
            .attr('y', 4)
            .style('fill', 'var(--text-primary)')
            .style('font-size', d => {
                if (d.type === 'file') return '14px';
                if (d.type === 'class') return '13px';
                return '12px';
            })
            .style('font-weight', d => d.type === 'file' ? '600' : '500')
            .style('text-shadow', '1px 1px 2px rgba(0,0,0,0.8)');

        // Add hover effects and tooltip
        node.on('mouseover', function(event, d) {
                // Highlight connected nodes and links
                const connectedNodeIds = new Set();
                link.each(l => {
                    if (l.source.id === d.id) connectedNodeIds.add(l.target.id);
                    if (l.target.id === d.id) connectedNodeIds.add(l.source.id);
                });

                node.style('opacity', n => 
                    n.id === d.id || connectedNodeIds.has(n.id) ? 1 : 0.3
                );
                link.style('opacity', l => 
                    l.source.id === d.id || l.target.id === d.id ? 1 : 0.1
                );

                d3.select(this).select('circle')
                    .style('stroke', '#fff')
                    .style('stroke-width', 3);

                currentTooltip.transition()
                    .duration(200)
                    .style('opacity', .9);
                
                const content = `
                    <strong>${d.name}</strong><br/>
                    Type: ${d.type}<br/>
                    ${d.complexity ? `Complexity: ${d.complexity}<br/>` : ''}
                    ${d.maintainability ? `Maintainability: ${d.maintainability.toFixed(2)}<br/>` : ''}
                    ${d.documentation ? `Documentation: ${d.documentation}<br/>` : ''}
                `;
                
                currentTooltip.html(content)
                    .style('left', (event.pageX + 10) + 'px')
                    .style('top', (event.pageY - 28) + 'px');
            })
            .on('mouseout', function() {
                // Reset highlighting
                node.style('opacity', 1);
                link.style('opacity', 0.6);

                d3.select(this).select('circle')
                    .style('stroke', '#fff')
                    .style('stroke-width', 2);

                currentTooltip.transition()
                    .duration(500)
                    .style('opacity', 0);
            });

        // Update positions on each tick
        currentSimulation.on('tick', () => {
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);

            node
                .attr('transform', d => `translate(${d.x},${d.y})`);
        });

        // Add zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on('zoom', (event) => {
                g.attr('transform', event.transform);
            });

        currentSvg.call(zoom);

        // Drag functions
        function dragstarted(event, d) {
            if (!event.active) currentSimulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }

        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }

        function dragended(event, d) {
            if (!event.active) currentSimulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }
    }
}); 