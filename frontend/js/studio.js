document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('designForm');
    const logsArea = document.getElementById('logsArea');
    const submitBtn = document.getElementById('submitBtn');
    const imageInput = document.getElementById('imageInput');

    // Image Preview
    imageInput.addEventListener('change', function (e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                document.getElementById('imagePreview').src = e.target.result;
                document.getElementById('previewContainer').classList.remove('hidden');
            }
            reader.readAsDataURL(file);
        }
    });

    function addLog(text, type = 'info') {
        const line = document.createElement('div');
        line.className = `console-line ${type}`;

        // Timestamp
        const time = new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
        const timeSpan = document.createElement('span');
        timeSpan.className = 'console-timestamp';
        timeSpan.textContent = `[${time}]`;

        // Content Container
        const contentSpan = document.createElement('div');
        contentSpan.className = 'console-content';

        // Agent Detection
        let processedText = text;
        const agentMatch = text.match(/^(\w+):\s(.+)/);

        if (agentMatch) {
            const agentName = agentMatch[1];
            const message = agentMatch[2];

            const agentBadge = document.createElement('span');
            agentBadge.className = `log-agent-name agent-${agentName.toLowerCase()}`;
            agentBadge.textContent = agentName;
            contentSpan.appendChild(agentBadge);

            processedText = message;
        }

        // Message Text (Wrapped in span for flexbox handling)
        const textSpan = document.createElement('span');
        textSpan.textContent = processedText;
        contentSpan.appendChild(textSpan);

        // Status Bagdes (REJECTED / APPROVED)
        if (text.includes("REJECTED")) {
            const badge = document.createElement('div');
            badge.className = 'status-badge status-rejected';
            badge.innerHTML = '<i class="fa-solid fa-circle-xmark"></i> REJECTED';
            contentSpan.appendChild(badge);
            line.classList.add('error');
        } else if (text.includes("APPROVED") || text.includes("SUCCESS")) {
            const badge = document.createElement('div');
            badge.className = 'status-badge status-approved';
            badge.innerHTML = '<i class="fa-solid fa-circle-check"></i> APPROVED';
            contentSpan.appendChild(badge);
            line.classList.add('success');
        }

        line.appendChild(timeSpan);
        line.appendChild(contentSpan);

        logsArea.appendChild(line);
        logsArea.scrollTop = logsArea.scrollHeight;
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Show Overlay
        document.getElementById('analysisOverlay').classList.remove('hidden');
        document.getElementById('analysisOverlay').classList.add('flex');

        addLog("Initializing Agent Swarm...");

        const level = document.querySelector('input[name="limbConfig"]:checked')?.value || "Not specified";

        // Collect all checked activities
        const activityCheckboxes = document.querySelectorAll('input[name="activity"]:checked');
        const activities = Array.from(activityCheckboxes).map(cb => cb.value);

        const notes = document.getElementById('detailsInput').value;
        const imageFile = document.getElementById('imageInput').files[0];

        addLog(`Configuration captured: ${activities.join(", ") || "None"} / ${level}`);

        const formData = new FormData();
        if (imageFile) {
            formData.append('image', imageFile);
            addLog("Image attached for analysis.");
        } else {
            addLog("Warning: No image provided (using test mode).", 'red');
        }

        // Send structured data
        formData.append('limbConfig', level);
        // Append each activity separately so FastAPI receives a list
        activities.forEach(act => formData.append('activity', act));
        formData.append('notes', notes);

        try {
            addLog("Sending data to Google Cloud (Backend)...");
            const response = await fetch('/api/process-design', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                addLog("SUCCESS: Design Generated. Redirecting...", 'green');

                // Save Result Data and Original Image (Preview) to move to the next page
                localStorage.setItem('auraDesignData', JSON.stringify(data));

                // We also need the original image. Since we can't easily pass the File object,
                // we rely on the DataURI we generated for the preview.
                const previewSrc = document.getElementById('imagePreview').src;
                localStorage.setItem('auraOriginalImage', previewSrc);

                // Simulation Delay to let user read "SUCCESS"
                setTimeout(() => {
                    window.location.href = 'editor.html';
                }, 1500);

            } else {
                addLog("Error: " + JSON.stringify(data), 'error');
            }
        } catch (err) {
            addLog("Network Error: " + err.message, 'error');
        }
    });
});
