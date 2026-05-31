document.body.style.borderTop = "5px solid #00f2fe"; 
console.log("[AI_EXT] Absolute Event-Isolated Script Active!");

function addAiButton() {
    const buttons = document.querySelectorAll('button');
    
    buttons.forEach(btn => {
        const btnText = btn.innerText.trim();
        const isMainCommentBtn = btnText === 'Comment' || btnText === 'Reply';
        
        const isSubmitBtn = btn.closest('.comments-comment-box__form-container') || 
                            btn.classList.contains('comments-comment-box__submit-button') || 
                            btn.classList.contains('artdeco-button--primary');

        if (isMainCommentBtn && !isSubmitBtn) {
            const buttonContainer = btn.parentNode;
            const actionRow = buttonContainer ? buttonContainer.parentNode : null; 
            
            if (actionRow && !actionRow.querySelector('.ai-reply-btn')) {
                const aiBtn = document.createElement('button');
                aiBtn.className = 'ai-reply-btn';
                aiBtn.innerText = '✨ AI Reply';
                aiBtn.style.cssText = "background-color: #0a66c2; color: white; border: none; border-radius: 16px; padding: 0 15px; font-size: 13px; font-weight: bold; cursor: pointer; margin-left: 5px; height: 35px; display: inline-flex; align-items: center;";
                
                aiBtn.addEventListener('click', async (e) => {
                    e.preventDefault();
                    e.stopPropagation(); // Event ko page par mazeed leak hone se rokna
                    
                    const clickedButton = e.currentTarget;
                    const originalText = clickedButton.innerText;
                    
                    clickedButton.innerText = '⏳ Generating...';
                    clickedButton.disabled = true;

                    try {
                        // --- DYNAMIC SCOPE ISOLATION ---
                        // Button ke event se strictly parent card dhoondna (Anti-Leakage)
                        let currentPostCard = clickedButton.closest('.feed-shared-update-v2') || 
                                              clickedButton.closest('.occludable-update') || 
                                              clickedButton.closest('[data-urn]') || 
                                              clickedButton.closest('.artdeco-modal') ||
                                              clickedButton.closest('article');

                        // Safe backup agar direct closest click par slow ho
                        if (!currentPostCard) {
                            currentPostCard = clickedButton.parentElement.parentElement.parentElement.parentElement;
                        }

                        let postText = window.getSelection().toString().trim();
                        let authorName = "LinkedIn Connection";

                        // --- UNIVERSAL TEXT EXTRACTOR ---
                        if (!postText && currentPostCard && typeof currentPostCard.querySelector === 'function') {
                            
                            // 1. Pehle LinkedIn ke standard known text containers check karo
                            const textSelectors = [
                                '.feed-shared-update-v2__commentary',
                                '.feed-shared-update-v2__description',
                                '.update-components-text',
                                '.feed-shared-inline-show-more-text',
                                'span[dir="ltr"]'
                            ];

                            for (let selector of textSelectors) {
                                const elements = currentPostCard.querySelectorAll(selector);
                                for (let el of elements) {
                                    // Filter out comments, replies, and empty spans
                                    if (el && !el.closest('.comments-comment-item') && !el.closest('.comment') && el.innerText.trim().length > 20) {
                                        postText = el.innerText.trim();
                                        break;
                                    }
                                }
                                if (postText) break;
                            }

                            // 2. DEEP FALLBACK: Agar dynamic tags ki wajah se abhi bhi text khali hai
                            if (!postText || postText.length < 15) {
                                // Post card ke top area (jahan text hota hai) ko target karo, comments section se pehle
                                const topContentArea = currentPostCard.querySelector('.feed-shared-update-v2__text-area, .feed-shared-update-v2__header, .update-components-actor');
                                if (topContentArea) {
                                    postText = topContentArea.innerText.trim();
                                } else {
                                    // Pura card text uthao aur comments saaf kar do
                                    let fullCardText = currentPostCard.innerText;
                                    const commentIndex = fullCardText.indexOf('Comment');
                                    if (commentIndex > 0) {
                                        postText = fullCardText.substring(0, commentIndex).trim();
                                    } else {
                                        postText = fullCardText.trim();
                                    }
                                }
                            }

                            // Clean "...see more" and messy line breaks
                            if (postText) {
                                postText = postText.replace(/[\r\n]+/g, ' ')
                                                   .replace('...see more', '')
                                                   .replace('... See more', '')
                                                   .trim();
                            }

                            // Author Name Extraction
                            const authorElement = currentPostCard.querySelector('.update-components-actor__name, .feed-shared-actor__title, .comments-post-meta__profile-link, h3, h1');
                            if (authorElement) {
                                authorName = authorElement.innerText.trim().split('\n')[0];
                            }
                        }

                        // Agar ALL METHODS fail ho jayein tabhi sirf ye neutral sentence bhejain
                        if (!postText || postText.length < 15) {
                            postText = "A wonderful professional update sharing progress, success, or an interesting update.";
                        }

                        console.log("[AI_EXT] Extracted Scope Text Successfully:", postText.substring(0, 60));
						
						// --- MULTIMODAL IMAGE EXTRACTOR (DIRECT PASS) ---
                        let postImageUrl = "";
                        if (currentPostCard && typeof currentPostCard.querySelector === 'function') {
                            const imgEl = currentPostCard.querySelector('.update-components-article__image img, .update-components-image__image-link img, .feed-shared-image__container img, img[class*="image"]');
                            if (imgEl && imgEl.src && !imgEl.src.startsWith('data:')) {
                                postImageUrl = imgEl.src;
                                console.log("[AI_EXT] Sent raw secure image link to background pipeline.");
                            }
                        }

                        // Neutral context statement
                        if (!postText || postText.length < 15) {
                            postText = "An elegant visual update, quote, image, or message shared by the author.";
                        }

                        // --- BACKGROUND MESSAGE PIPELINE (SINGLE & ALIGNED) ---
						chrome.runtime.sendMessage(
							{ 
								action: "generateComment", 
								postText: postText, 
								authorName: authorName,
								imageUrl: postImageUrl 
							},
							(response) => {
								// Anti-Stuck Reset
								clickedButton.innerText = originalText;
								clickedButton.disabled = false;

								if (chrome.runtime.lastError) {
									console.error("[AI_EXT] Runtime Error:", chrome.runtime.lastError);
									return;
								}

								if (response && response.success) {
									const actualCommentText = response.comment || response.suggested_comment || (typeof response === 'string' ? response : "");
									
									// Check if 403 Access Denied error returned from API
									if (response.error && response.status === 403) {
										alert(response.error);
										return;
									}

									let localCommentBox = null;
									if (currentPostCard && typeof currentPostCard.querySelector === 'function') {
										localCommentBox = currentPostCard.querySelector('div.ql-editor, div[role="textbox"]');
									}

									if (!localCommentBox && currentPostCard && typeof currentPostCard.querySelector === 'function') {
										const nativeBtn = currentPostCard.querySelector('.comment-button, button[aria-label*="Comment"], button[aria-label*="Reply"]');
										if (nativeBtn) nativeBtn.click();
									}

									setTimeout(() => {
										if (currentPostCard && typeof currentPostCard.querySelector === 'function' && !localCommentBox) {
											localCommentBox = currentPostCard.querySelector('div.ql-editor, div[role="textbox"]');
										}

										if (localCommentBox) {
											localCommentBox.focus();
											if (localCommentBox.isContentEditable) {
												localCommentBox.innerHTML = '';
												const inputEvent = new InputEvent('input', { bubbles: true, cancelable: true });
												localCommentBox.dispatchEvent(inputEvent);
												document.execCommand('insertText', false, String(actualCommentText));
											} else {
												localCommentBox.value = String(actualCommentText);
												localCommentBox.dispatchEvent(new Event('input', { bubbles: true }));
											}
											console.log("[AI_EXT] Flawless Isolated Injection Completed.");
										} else {
											navigator.clipboard.writeText(String(actualCommentText));
											alert("Box direct access nahi hua. Copied to Clipboard! Press Ctrl+V.");
										}
									}, 450);

								} else {
									alert(response.error || "API Error! Python server check karen.");
								}
							}
						);
                    } catch (err) {
                        console.error("[AI_EXT] Fatal Click Error:", err);
                        clickedButton.innerText = originalText;
                        clickedButton.disabled = false;
                    }
                });

                buttonContainer.after(aiBtn);
            }
        }
    });
}

// Dynamic Feed Syncing
setInterval(addAiButton, 1500);