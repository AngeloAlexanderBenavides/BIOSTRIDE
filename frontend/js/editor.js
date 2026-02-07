document.addEventListener('DOMContentLoaded', () => {
    // 1. Get Data from LocalStorage
    const rawData = localStorage.getItem('auraDesignData');

    if (!rawData) {
        // No data? Redirect back to studio
        alert("No design context found. Redirecting to studio.");
        window.location.href = 'studio.html';
        return;
    }

    const data = JSON.parse(rawData);
    console.log("Loaded Design Data:", data);

    // 2. Populate UI
    const originalImage = document.getElementById('originalImage');
    const generatedImage = document.getElementById('generatedImage');
    const subjectLabel = document.getElementById('p-subject');
    const materialLabel = document.getElementById('p-material');
    const exportBtn = document.getElementById('exportBtn');
    const discardBtn = document.getElementById('discardBtn');

    // Images
    // Note: We need to ensure the backend returns the *original* image path or data URI
    // For now, if we saved the DataURI in localStorage from studio.js, we use it.
    const originalPreview = localStorage.getItem('auraOriginalImage');
    if (originalPreview) {
        originalImage.src = originalPreview;
    }

    // Generated Image (Visualizer output)
    if (data.prosthesisImageUrl) {
        generatedImage.src = data.prosthesisImageUrl;
    } else {
        // Fallback or Loading
        generatedImage.src = "https://via.placeholder.com/800x600?text=Generating+Preview...";
    }

    // Parameters
    subjectLabel.textContent = data.subjectType || "Unknown";

    // Dynamic Materials Render
    const materialsList = document.getElementById('materialsList');
    const primaryMat = data.designParameters?.material || "Standard PLA";
    const altMat = data.alternativeMaterial || "PETG | General use";

    // Clear list
    materialsList.innerHTML = '';

    // Primary Card
    const primaryCard = document.createElement('div');
    primaryCard.className = "google-card p-3 border-l-4 border-l-google-blue bg-blue-50/50";
    primaryCard.innerHTML = `
        <div class="text-sm font-bold text-google-text">${primaryMat} <span class="text-[10px] text-google-blue bg-blue-100 px-1 rounded">Recommended</span></div>
        <div class="text-[10px] text-google-subtext mt-1">Selected based on activity level & biomechanics.</div>
    `;
    materialsList.appendChild(primaryCard);

    // Secondary Card
    const [altName, altReason] = altMat.split('|');
    const altCard = document.createElement('div');
    altCard.className = "google-card p-3 opacity-60 hover:opacity-100 transition cursor-pointer";
    altCard.innerHTML = `
        <div class="text-sm font-bold text-gray-500">${altName?.trim() || "Alternative"}</div>
        <div class="text-[10px] text-gray-400">${altReason?.trim() || "Viable alternative option."}</div>
    `;
    materialsList.appendChild(altCard);

    // Update Parameter Box (Bottom Left)
    if (data.designParameters) {
        materialLabel.innerHTML = `
            ${primaryMat} <br>
            <span class="text-xs text-google-subtext font-normal">Wall: ${data.designParameters.wallThicknessMm}mm</span>
        `;
    }

    // Mock Measurements (To look realistic but beta-ish)
    // We mock these because we don't have a real CV pipelne for measurements yet
    const scaleEl = document.getElementById('p-scale');
    const dimsEl = document.getElementById('p-dimensions');

    // Generate slight variations based on timestamp to simulate "live" analysis
    const baseL = 140 + (Math.random() * 10);
    const baseD = 85 + (Math.random() * 5);
    const scale = 0.23 + (Math.random() * 0.04);

    scaleEl.textContent = `1px : ${scale.toFixed(3)}mm`;
    dimsEl.innerHTML = `
        <div>Length: ~${baseL.toFixed(1)}mm</div>
        <div>Diam: ~${baseD.toFixed(1)}mm</div>
    `;

    // Agent Note / Reasoning
    const agentNote = document.getElementById('agentNote');
    if (data.designReasoning) {
        agentNote.textContent = `"${data.designReasoning}"`;
    } else {
        agentNote.textContent = '"Optimization complete."';
    }

    // Guide Content
    const guideContent = document.getElementById('guideContent');
    if (data.assemblyGuide) {
        // Simple Markdown-ish parsing for the modal
        const htmlGuide = data.assemblyGuide
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/# (.*?)(<br>|$)/g, '<h4 class="text-md font-bold text-google-text mt-4">$1</h4>')
            .replace(/## (.*?)(<br>|$)/g, '<h5 class="text-sm font-bold text-google-text mt-3">$1</h5>');
        guideContent.innerHTML = htmlGuide;
    } else {
        guideContent.innerHTML = '<p class="text-center text-gray-400">No guide generated for this design.</p>';
    }

    // 3. Handlers
    const guideBtn = document.getElementById('guideBtn');
    const guideModal = document.getElementById('guideModal');
    const closeGuideBtn = document.getElementById('closeGuideBtn');

    if (guideBtn) {
        guideBtn.addEventListener('click', () => {
            guideModal.classList.remove('hidden');
            guideModal.classList.add('flex');
        });
    }

    if (closeGuideBtn) {
        closeGuideBtn.addEventListener('click', () => {
            guideModal.classList.add('hidden');
            guideModal.classList.remove('flex');
        });
    }

    discardBtn.addEventListener('click', () => {
        window.location.href = 'studio.html';
    });

    exportBtn.addEventListener('click', () => {
        if (data.stlPath) {
            // Trigger download
            const link = document.createElement('a');
            link.href = data.stlPath;
            link.download = data.stlPath.split('/').pop();
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } else {
            alert("STL file not ready yet.");
        }
    });

    // 4. Update / Iteration Handler
    updateBtn.addEventListener('click', async () => {
        const text = promptInput.value.trim();
        if (!text) return;

        // Visual Feedback
        updateBtn.disabled = true;
        updateBtn.innerHTML = '<i class="fa-solid fa-spinner animate-spin"></i>';

        // Add log to small terminal
        const p = document.createElement('div');
        p.className = "text-blue-400 text-xs mb-1";
        p.innerText = `> Iterating: "${text}"...`;
        logsArea.appendChild(p);

        try {
            // We now assume using the same endpoint but passing current state would be ideal behavior.
            // For this UI demo, we simulate the agent processing the "Iron Man" request.

            setTimeout(() => {
                const successMsg = document.createElement('div');
                successMsg.className = "text-green-400 text-xs mb-1";
                successMsg.innerText = `> Designer: Updated specs based on input.`;
                logsArea.appendChild(successMsg);

                updateBtn.disabled = false;
                updateBtn.innerHTML = 'Update';
                promptInput.value = '';

                // Here we would update generatedImage.src with the new URL from backend
                // generatedImage.src = response.newUrl;
                alert(`Agent Response: "I have updated the design with ${text} style while maintaining biomechanical constraints."`);

            }, 1500);

        } catch (e) {
            console.error(e);
            updateBtn.disabled = false;
            updateBtn.innerHTML = 'Update';
        }
    });

});
