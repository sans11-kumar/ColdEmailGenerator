$(document).ready(function() {
    // DOM elements
    const messagesContainer = $('#messages');
    const userInput = $('#user-input');
    const sendButton = $('#send-btn');
    const emailDisplay = $('#email-display');
    const emailContent = $('#email-content');
    const copyButton = $('#copy-btn');
    const downloadButton = $('#download-btn');
    const verifyApiBtn = $('#verify-api-btn');
    const apiStatusContainer = $('#api-status-container');
    const apiVerificationModal = new bootstrap.Modal(document.getElementById('apiVerificationModal'));
    const verifyApiSubmitBtn = $('#verifyApiBtn');
    const apiVerificationResult = $('#apiVerificationResult');
    
    // Variables
    let isFirstMessage = true;
    let apiStatus = {
        deepseek: { status: 'unknown' },
        groq: { status: 'unknown' }
    };
    
    // Check API status
    checkApiStatus();
    
    // Start the conversation
    setTimeout(() => {
        appendBotMessage("Hi there! I'm your AI Cold Email Generator. I'll help you create a personalized cold outreach email. Let me ask you a few questions to get started.");
        setTimeout(() => {
            sendRequest('');
        }, 1000);
    }, 500);
    
    // Handle user input - on click and on enter key
    sendButton.on('click', handleUserInput);
    userInput.on('keypress', function(e) {
        if (e.which === 13) {
            handleUserInput();
        }
    });
    
    // Open API verification modal
    verifyApiBtn.on('click', function() {
        apiVerificationResult.empty();
        apiVerificationModal.show();
    });
    
    // Handle API verification
    verifyApiSubmitBtn.on('click', function() {
        const deepseekApiKey = $('#deepseekApiKey').val().trim();
        const deepseekApiBase = $('#deepseekApiBase').val().trim();
        const groqApiKey = $('#groqApiKey').val().trim();
        
        if (!deepseekApiKey && !groqApiKey) {
            apiVerificationResult.html('<div class="alert alert-warning">Please enter at least one API key to verify.</div>');
            return;
        }
        
        // Show loading indicator
        apiVerificationResult.html('<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div><p>Verifying API keys...</p></div>');
        
        // Disable verify button
        verifyApiSubmitBtn.prop('disabled', true);
        
        // Send verification request
        $.ajax({
            url: '/verify-api',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                deepseek_api_key: deepseekApiKey,
                deepseek_api_base: deepseekApiBase,
                groq_api_key: groqApiKey
            }),
            success: function(response) {
                // Enable verify button
                verifyApiSubmitBtn.prop('disabled', false);
                
                // Update API status
                apiStatus = response.apis || {
                    deepseek: response.deepseek,
                    groq: response.groq
                };
                
                // Display verification results
                let resultHtml = '<div class="mt-3">';
                
                // DeepSeek result
                if (deepseekApiKey) {
                    if (response.deepseek.status === 'success') {
                        resultHtml += '<div class="alert alert-success">✅ DeepSeek API: Connection successful</div>';
                    } else {
                        resultHtml += `<div class="alert alert-danger">❌ DeepSeek API: ${response.deepseek.message}</div>`;
                    }
                }
                
                // Groq result
                if (groqApiKey) {
                    if (response.groq.status === 'success') {
                        resultHtml += '<div class="alert alert-success">✅ Groq API: Connection successful</div>';
                    } else {
                        resultHtml += `<div class="alert alert-danger">❌ Groq API: ${response.groq.message}</div>`;
                    }
                }
                
                // Overall result
                if (response.overall.status === 'success') {
                    resultHtml += '<div class="alert alert-success mt-2">✅ At least one API is working. You can use the application.</div>';
                } else {
                    resultHtml += '<div class="alert alert-warning mt-2">⚠️ All APIs failed to connect. The application will use a basic template generator.</div>';
                }
                
                resultHtml += '</div>';
                apiVerificationResult.html(resultHtml);
                
                // Update API status display
                updateApiStatusDisplay();
            },
            error: function() {
                // Enable verify button
                verifyApiSubmitBtn.prop('disabled', false);
                
                apiVerificationResult.html('<div class="alert alert-danger">Error connecting to the server. Please try again.</div>');
            }
        });
    });
    
    // Copy email to clipboard
    copyButton.on('click', function() {
        const text = emailContent.text();
        navigator.clipboard.writeText(text)
            .then(() => {
                const originalText = copyButton.text();
                copyButton.text('Copied!');
                setTimeout(() => {
                    copyButton.text(originalText);
                }, 2000);
            })
            .catch(err => {
                console.error('Failed to copy text: ', err);
            });
    });
    
    // Download email as text file
    downloadButton.on('click', function() {
        $.ajax({
            url: '/download',
            method: 'GET',
            success: function(response) {
                const blob = new Blob([response.email], { type: 'text/plain' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = 'cold_email.txt';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
            },
            error: function(xhr) {
                console.error('Error downloading email:', xhr.responseText);
            }
        });
    });
    
    // Check API status
    function checkApiStatus() {
        $.ajax({
            url: '/check-api',
            method: 'GET',
            success: function(response) {
                apiStatus = response.apis;
                updateApiStatusDisplay();
                
                if (response.status === 'error') {
                    appendBotMessage(`⚠️ API Connection Warning: All APIs failed to connect. The application will use a basic template generator.`);
                } else {
                    // Check individual APIs
                    const apis = response.apis;
                    let workingApis = [];
                    
                    if (apis.deepseek.status === 'success') {
                        workingApis.push('DeepSeek');
                    }
                    
                    if (apis.groq.status === 'success') {
                        workingApis.push('Groq');
                    }
                    
                    if (workingApis.length > 0) {
                        appendBotMessage(`✅ Connected to ${workingApis.join(' and ')} API${workingApis.length > 1 ? 's' : ''}.`);
                    }
                }
            },
            error: function() {
                appendBotMessage("⚠️ Warning: Could not check API status. The application will use a basic template if the APIs are unavailable.");
            }
        });
    }
    
    // Update API status display
    function updateApiStatusDisplay() {
        let statusHtml = '<div class="d-flex justify-content-between align-items-center mb-2">';
        statusHtml += '<div>';
        
        // DeepSeek status
        if (apiStatus.deepseek.status === 'success') {
            statusHtml += '<span class="badge bg-success me-2">DeepSeek: Connected</span>';
        } else if (apiStatus.deepseek.status === 'error') {
            statusHtml += '<span class="badge bg-danger me-2" title="' + (apiStatus.deepseek.message || 'Connection failed') + '">DeepSeek: Failed</span>';
        } else {
            statusHtml += '<span class="badge bg-secondary me-2">DeepSeek: Not Configured</span>';
        }
        
        // Groq status
        if (apiStatus.groq.status === 'success') {
            statusHtml += '<span class="badge bg-success me-2">Groq: Connected</span>';
        } else if (apiStatus.groq.status === 'error') {
            statusHtml += '<span class="badge bg-danger me-2" title="' + (apiStatus.groq.message || 'Connection failed') + '">Groq: Failed</span>';
        } else {
            statusHtml += '<span class="badge bg-secondary me-2">Groq: Not Configured</span>';
        }
        
        statusHtml += '</div>';
        statusHtml += '<button id="verify-api-btn" class="btn btn-sm btn-outline-secondary">Verify API Keys</button>';
        statusHtml += '</div>';
        
        apiStatusContainer.html(statusHtml);
        
        // Reattach event listener
        $('#verify-api-btn').on('click', function() {
            apiVerificationResult.empty();
            apiVerificationModal.show();
        });
    }
    
    // Handle user input
    function handleUserInput() {
        const message = userInput.val().trim();
        if (message) {
            appendUserMessage(message);
            userInput.val('');
            showTypingIndicator();
            sendRequest(message);
        }
    }
    
    // Send request to server
    function sendRequest(message) {
        $.ajax({
            url: '/chat',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ message: message }),
            success: function(response) {
                hideTypingIndicator();
                appendBotMessage(response.message);
                
                // If an email was generated, display it
                if (response.email) {
                    // Clean up the email if it contains error messages
                    let emailText = response.email;
                    if (emailText.startsWith("⚠️ Error:") || emailText.startsWith("⚠️ Authentication Error:")) {
                        const templateStart = emailText.indexOf("Here's a basic email template instead:");
                        if (templateStart !== -1) {
                            emailText = emailText.substring(templateStart + "Here's a basic email template instead:".length).trim();
                        }
                    }
                    
                    emailContent.text(emailText);
                    emailDisplay.removeClass('d-none');
                    // Scroll to the email display
                    $('html, body').animate({
                        scrollTop: emailDisplay.offset().top - 100
                    }, 500);
                }
            },
            error: function(xhr) {
                hideTypingIndicator();
                appendBotMessage("Sorry, there was an error processing your request. Please try again.");
                console.error('Error:', xhr.responseText);
            }
        });
    }
    
    // Append user message to chat
    function appendUserMessage(message) {
        const messageElement = $('<div class="message-container user"><div class="message user-message"></div></div>');
        messageElement.find('.message').text(message);
        messagesContainer.append(messageElement);
        scrollToBottom();
    }
    
    // Append bot message to chat
    function appendBotMessage(message) {
        const messageElement = $('<div class="message-container bot"><div class="message bot-message"></div></div>');
        messageElement.find('.message').text(message);
        messagesContainer.append(messageElement);
        scrollToBottom();
    }
    
    // Show typing indicator
    function showTypingIndicator() {
        const typingIndicator = $('<div class="message-container bot"><div class="typing-indicator">Typing<span></span><span></span><span></span></div></div>');
        messagesContainer.append(typingIndicator);
        scrollToBottom();
    }
    
    // Hide typing indicator
    function hideTypingIndicator() {
        messagesContainer.find('.typing-indicator').parent().remove();
    }
    
    // Scroll chat to bottom
    function scrollToBottom() {
        messagesContainer.scrollTop(messagesContainer[0].scrollHeight);
    }

    // Add save button to modal footer
    const modalFooter = $('#apiVerificationModal .modal-footer');
    if (!$('#saveApiKeysBtn').length) {
        modalFooter.prepend('<button type="button" class="btn btn-success" id="saveApiKeysBtn" disabled>Save Keys</button>');
    }
    
    // Handle save button click
    $('#saveApiKeysBtn').on('click', function() {
        const deepseekApiKey = $('#deepseekApiKey').val().trim();
        const deepseekApiBase = $('#deepseekApiBase').val().trim();
        const groqApiKey = $('#groqApiKey').val().trim();
        
        // Show loading indicator
        apiVerificationResult.html('<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div><p>Saving API keys...</p></div>');
        
        // Disable buttons
        $('#saveApiKeysBtn').prop('disabled', true);
        verifyApiSubmitBtn.prop('disabled', true);
        
        // Send update request
        $.ajax({
            url: '/update-api-keys',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                deepseek_api_key: deepseekApiKey,
                deepseek_api_base: deepseekApiBase,
                groq_api_key: groqApiKey
            }),
            success: function(response) {
                // Enable buttons
                $('#saveApiKeysBtn').prop('disabled', false);
                verifyApiSubmitBtn.prop('disabled', false);
                
                if (response.status === 'success') {
                    apiVerificationResult.html('<div class="alert alert-success">✅ API keys saved successfully! The application will now use these keys.</div>');
                    
                    // Update API status
                    apiStatus = response.verification.apis || {
                        deepseek: response.verification.deepseek,
                        groq: response.verification.groq
                    };
                    
                    // Update API status display
                    updateApiStatusDisplay();
                    
                    // Reload the page after 2 seconds to apply the new keys
                    setTimeout(function() {
                        location.reload();
                    }, 2000);
                } else {
                    apiVerificationResult.html(`<div class="alert alert-danger">❌ Failed to save API keys: ${response.message}</div>`);
                }
            },
            error: function() {
                // Enable buttons
                $('#saveApiKeysBtn').prop('disabled', false);
                verifyApiSubmitBtn.prop('disabled', false);
                
                apiVerificationResult.html('<div class="alert alert-danger">❌ Error connecting to the server. Please try again.</div>');
            }
        });
    });
    
    // Enable save button when verification is successful
    verifyApiSubmitBtn.on('click', function() {
        // This will be called after the verification is complete
        setTimeout(function() {
            const deepseekSuccess = apiStatus.deepseek && apiStatus.deepseek.status === 'success';
            const groqSuccess = apiStatus.groq && apiStatus.groq.status === 'success';
            
            // Enable save button if at least one API is working
            $('#saveApiKeysBtn').prop('disabled', !(deepseekSuccess || groqSuccess));
        }, 1000);
    });
}); 