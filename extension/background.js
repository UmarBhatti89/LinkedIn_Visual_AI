console.log("[AI_EXT_BG] Standard Messaging Service with Access Keys Active!");

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "generateComment") {
        
        // Browser Storage se key, tone aur length aik sath read karna
        chrome.storage.local.get(['bcreatiq_key', 'bcreatiq_tone', 'bcreatiq_length'], async (settings) => {
            const currentKey = settings.bcreatiq_key || "";
            const currentTone = settings.bcreatiq_tone || "Insightful";
            const currentLength = settings.bcreatiq_length || "Medium";

            try {
                const response = await fetch("http://127.0.0.1:8000/generate-comment", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        post_text: request.postText,
                        author_name: request.authorName,
                        tone: currentTone,
                        length: currentLength,
                        image_url: request.imageUrl || "",
                        license_key: currentKey // <--- AUTOMATIC KEY PASS
                    })
                });

                // Status 403 handling check for Access Denied
                if (response.status === 403) {
                    const errorData = await response.json();
                    sendResponse({ success: false, error: errorData.detail, status: 403 });
                    return;
                }

                const data = await response.json();
                
                if (data && data.suggested_comment) {
                    sendResponse({ success: true, comment: data.suggested_comment });
                } else {
                    sendResponse({ success: false, error: "No comment received from bCreatiq server" });
                }

            } catch (error) {
                console.error("[AI_EXT_BG] Fetch Error:", error);
                sendResponse({ success: false, error: error.message });
            }
        });

        return true; 
    }
});