document.addEventListener('DOMContentLoaded', () => {
    const licenseKeyInput = document.getElementById('licenseKey');
    const saveKeyBtn = document.getElementById('saveKeyBtn');
    const keyStatus = document.getElementById('keyStatus');
    const toneSelect = document.getElementById('toneSelect');
    const lengthSelect = document.getElementById('lengthSelect');

    // 1. Browser storage se purani saved values load karna
    chrome.storage.local.get(['bcreatiq_key', 'bcreatiq_tone', 'bcreatiq_length'], (data) => {
        if (data.bcreatiq_key) {
            licenseKeyInput.value = data.bcreatiq_key;
            keyStatus.textContent = "🟢 Key Saved Locally";
            keyStatus.style.color = "#06b6d4";
        }
        if (data.bcreatiq_tone) toneSelect.value = data.bcreatiq_tone;
        if (data.bcreatiq_length) lengthSelect.value = data.bcreatiq_length;
    });

    // 2. Key Save Button Ka Logic
    saveKeyBtn.addEventListener('click', () => {
        const keyVal = licenseKeyInput.value.trim();
        if (keyVal) {
            chrome.storage.local.set({ 'bcreatiq_key': keyVal }, () => {
                keyStatus.textContent = "✅ Key Saved Successfully!";
                keyStatus.style.color = "#d946ef";
            });
        } else {
            keyStatus.textContent = "❌ Key cannot be empty";
            keyStatus.style.color = "#ef4444";
        }
    });

    // 3. Tone aur Length badalte hi automatic save hona
    toneSelect.addEventListener('change', () => {
        chrome.storage.local.set({ 'bcreatiq_tone': toneSelect.value });
    });

    lengthSelect.addEventListener('change', () => {
        chrome.storage.local.set({ 'bcreatiq_length': lengthSelect.value });
    });
});