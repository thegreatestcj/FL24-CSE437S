let longitude;
let latitude;
let timeZone;
let dailyArtKnowledge;

$(document).ready( function() {
    disableTabsButton();
    $('#title-line-1').css({ visibility: 'visible' }).animate({ opacity: 1 }, 1000, function() {
        $('#title-line-2').css({ visibility: 'visible' }).animate({ opacity: 1 }, 1000, function() {
            $('#button-container').css({ visibility: 'visible' }).animate({ opacity: 1 }, 1000);
        });
    });
    timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    // Initialize Swiper for carousel
    const swiper = new Swiper('.swiper-container', {
        direction: 'vertical',
        loop: true,
        pagination: {
            el: '.swiper-pagination',
        },
        autoplay: {
            delay: 4000,
        },
        speed: 1200,
    });
    // Handle button click
    $('.tab-button').click(function() {
        // Remove active-button styling from all buttons
        $('#tab-container').removeClass('hidden')
        $('.tab-button').removeClass('bg-sky-800 text-white hover:bg-sky-950 active-button').addClass('bg-gray-300 text-gray-800 hover:bg-gray-400');

        let buttonContainerWidth = $('#button-container').outerWidth();
        $('#tab-container').css('width', buttonContainerWidth + 'px');
        
        // Add active-button styling to the clicked button
        $(this).removeClass('bg-gray-300 text-gray-800 hover:bg-gray-400').addClass('bg-sky-800 text-white hover:bg-sky-950 active-button');
        
        // Toggle content display based on which button is clicked
        if ($(this).attr('id') === 'tab-daily') {
            // Show place list content
            $('#content-daily').removeClass('hidden');
            $('#content-discover').addClass('hidden'); 
            $('#content-chat').addClass('hidden');
        } else if ($(this).attr('id') === 'tab-discover') {
            $('#content-daily').addClass('hidden');
            $('#content-discover').removeClass('hidden'); 
            $('#content-chat').addClass('hidden');
        } else if ($(this).attr('id') === 'tab-chat') {
            $('#content-daily').addClass('hidden');
            $('#content-discover').addClass('hidden'); 
            $('#content-chat').removeClass('hidden');
        }
    });

    // AI Chat AJAX Request
    let conversationHistory = [];  // To store the chat context

    function sendMessage() {
        const message = $('#chat-input').val().trim();
        if (message) {
            // Display user message
            $('#chat-messages').append(`<div class="user-message text-right mb-2">${message}</div>`);
            $('#chat-input').val('');

            // Add user message to the conversation history
            conversationHistory.push({ role: "user", content: message });
            // Append a "Typing..." indicator
            const typingIndicator = $('<div class="ai-reply text-left mb-2 text-gray-500 italic">Thinking...</div>');
            $('#chat-messages').append(typingIndicator);
            $('#chat-messages').scrollTop($('#chat-messages')[0].scrollHeight); // Scroll to bottom

            $.ajax({
                url: '/api/v1/chat/',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ 
                    message: message, 
                    history: conversationHistory 
                }),
                success: function(response) {
                    typingIndicator.remove();

                    // Append a blank div for the AI response
                    const aiReplyDiv = $('<div class="ai-reply text-left mb-2"></div>');
                    $('#chat-messages').append(aiReplyDiv);
                    const parsedMarkdown = marked.parse(response.reply);
                    typeText(aiReplyDiv, parsedMarkdown);

                    // Update conversation history with AI reply
                    conversationHistory = response.updated_history;
                },
                error: function(error) {
                    console.error('Chat error:', error);
                    $('#chat-messages').append(`<div class="error-message text-left text-red-500">Error: Could not retrieve response.</div>`);
                }
            });

            $('#chat-messages').scrollTop($('#chat-messages')[0].scrollHeight);
        }
    }

    $('#send-button').click(sendMessage);

    // Allow sending message with Enter key
    $('#chat-input').on('keydown', function(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();  // Prevent new line in textarea
            sendMessage();
        }
    });
})

$(document).ready( async function() {

    try {
        const position = await getCurrentPosition();
        const { latitude, longitude } = position.coords;
        enableTabsButton();
    } catch (error) {
        console.warn('Location access denied or error occurred:', error);
        enableTabsButton();
    }

    $('#tab-daily').click(async function() {
        console.log("Fetching daily knowledge...")
        if (typeof myObject !== 'undefined') {
            console.log(dailyArtKnowledge);
            displayDailyArtKnowledge(dailyArtKnowledge);
        } else {
            const response = await fetchDailyArtKnowledge(latitude, longitude, timeZone);
            console.log(response);
            dailyArtKnowledge = response.fact;
            console.log(dailyArtKnowledge);
            displayDailyArtKnowledge(dailyArtKnowledge);
        }
    });
})

function getCurrentPosition() {
    const deferred = $.Deferred();

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => deferred.resolve(position),
            (error) => deferred.reject(error)
        );
    } else {
        deferred.reject(new Error('Geolocation is not supported by this browser.'));
    }

    return deferred.promise();
}

async function fetchDailyArtKnowledge(latitude, longitude, timeZone) {
    return sendLocationBasedRequest('/api/v1/daily-art-knowledge/', latitude, longitude, timeZone, user);
}

function displayDailyArtKnowledge(fact) {
    $('#content-daily').html(`<p id="content-daily-text" class="text-md"></p>`);
    const dailyText = $('#content-daily-text');
    typeText(dailyText, fact);
}

function disableTabsButton() {
    const $loadingCaption = $('#loading-caption');
    $loadingCaption.removeClass('hidden');
    const $tabsButton = $('.tab-button');
    $tabsButton.prop('disabled', true);
    $tabsButton.addClass('bg-stone-300 dark:bg-stone-400 text-gray-950 cursor-not-allowed'); // Gray out for disabled effect
    $tabsButton.removeClass('bg-gray-300 text-gray-800 hover:bg-gray-400');
}

function enableTabsButton() {
    const $tabsButton = $('.tab-button');
    $tabsButton.prop('disabled', false);
    $tabsButton.removeClass('bg-stone-300 dark:bg-stone-400 text-gray-950 cursor-not-allowed');
    $tabsButton.addClass('bg-gray-300 text-gray-800 hover:bg-gray-400');
    const $loadingCaption = $('#loading-caption');
    $loadingCaption.addClass('hidden');
}

async function sendLocationBasedRequest(url, latitude, longitude, timeZone, user = null) {
    try {
        const requestData = {
            latitude: latitude,
            longitude: longitude,
            timeZone: timeZone,
        };

        if (user) {
            requestData.user = user;  // Add user info if available
        }

        const response = await $.ajax({
            url: url,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(requestData),
        });

        return response;
    } catch (error) {
        console.error(`Error sending request to ${url}:`, error);
        throw error;
    }
}


// Function for typing effect
function typeText(element, html, speed = 500, charSpeed = 10) {
    let charIndex = 0; 
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html'); 
    const childNodes = Array.from(doc.body.childNodes); 
    let currentNode = null; 
    let isTextNode = false; 

    function typeNextCharFromNode() {
        if (charIndex < currentNode.nodeValue.length) {
            element.append(currentNode.nodeValue[charIndex++]);
            setTimeout(typeNextCharFromNode, charSpeed);
        } else {
            charIndex = 0; 
            typeNextNode();
        }
    }

    function typeNextNode() {
        if (childNodes.length) {
            currentNode = childNodes.shift();

            if (currentNode.nodeType === Node.TEXT_NODE) {
                isTextNode = true; 
                typeNextCharFromNode(); 
            } else if (currentNode.nodeType === Node.ELEMENT_NODE) {
                element.append(currentNode.cloneNode(true));
                setTimeout(typeNextNode, speed);
            } else {
                typeNextNode();
            }
        }
    }

    typeNextNode();
}

function typeRawText(element, text, speed = 10) {
    let charIndex = 0;

    function typeNextChar() {
        if (charIndex < text.length) {
            element.append(text[charIndex++]);
            setTimeout(typeNextChar, speed);
        }
    }

    typeNextChar();
}