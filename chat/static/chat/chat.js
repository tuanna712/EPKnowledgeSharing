
var preview = document.getElementById("preview");

const randomString = generateRandomString(32); // You can change the length to any desired value
// console.log("Random String: ", randomString);

setCookie('csrftoken', randomString, 1);

// console.log("Document Cookie: ", document.cookie);

var refNum = 3;
var searchNum = 1;
var userOpenAiKey = null;

const settings = {
    numRef: 10,
    searchCoef: 0.5,
    sortDescending: true,
    userOpenAiKey: userOpenAiKey,
    verifyUserOpenaiKey: false,
    verifySystemOpenaiKey: false,
    openaiKeyMode: "system",
};

function openPreview(embedLink) {
    document.getElementById("preview").src = embedLink;
}

function handleKeyDown(event) {
    if (event.key === 'Enter') {
        // Prevent the default behavior of Enter key (e.g., new line)
        event.preventDefault();

        // Call sendMessage function when Enter key is pressed
            sendMessage();
    }
}

function createSummary(file) {
    var imageHtml = "";
    for (var i = 0; i < file.images.length; i++) {
        imageHtml += '<a style="height: 100%;" href=\'' + file.images[i] + '\' target="_blank"><img height="100%" width="auto" src=\'' + file.images[i] + '\' alt=""></a>'
    }
    const div = document.createElement('div');

    if (imageHtml.length == 0) {
        div.innerHTML = '<div class="p-2 d-flex justify-content-between" style="background-color: #DFF5FF;">' +
                                '<a target="_blank" href=\'' + file.file_redirect_url + '\' class="text-decoration-none fw-bold text-truncate" style="max-width: 80%;">' + file.file_name + '</a>' +
                                '<span class="text-secondary fst-italic">'+'Year: '+ file.year +' Page: ' + file.page_num + '</span>' +
                        '</div> '+
                        '<div class="p-2">' +
                            '<div class="fst-italic">Relevant information:</div>'+
                            '<div>\'' + file.text + '\'</div>' +
                            '<div class="fst-italic">No relevant images.</div>' +
                        '</div>';
    } else {
        div.innerHTML = '<div class="p-2 d-flex justify-content-between" style="background-color: #DFF5FF;">' +
        '<a target="_blank" href=\'' + file.file_redirect_url + '\' class="text-decoration-none fw-bold text-truncate" style="max-width: 80%;">' + file.file_name + '</a>' +
        '<span class="text-secondary fst-italic">'+'Year: '+ file.year +' Page: ' + file.page_num + '</span>' +
        '</div> '+
        '<div class="p-2">' +
        '<div class="fst-italic">Relevant information:</div>'+
        '<div>\'' + file.text + '\'</div>' +
        '<div class="fst-italic">Relevant images:</div>' +
        '<div class="hstack gap-1 overflow-x-auto" style="height: 30vh;">' +
        imageHtml
        '</div>' +
        '</div>';
    }

    return div;
}

async function sendMessage() {
    // Clear existing "Answer More" buttons
    document.querySelectorAll('.answer-more-btn').forEach(btn => btn.remove());

    if (settings.verifySystemOpenaiKey == true || settings.verifyUserOpenaiKey == true){
    
    const inputBox = document.getElementById('inputBox');
    const message = inputBox.value;

    if (message.trim() !== '') {
        const chatbox = document.getElementById('chatbox');
        const newDiv = document.createElement('div');

        // Create user div
        const youTitle = document.createElement('div');
        youTitle.classList.add('fw-bold');
        youTitle.textContent = "You";
        newDiv.appendChild(youTitle);

        const newMessage = document.createElement('div');
        newMessage.textContent = message;
        newDiv.appendChild(newMessage);
        chatbox.appendChild(newDiv);


        // Clear the input box after sending a message
        inputBox.value = '';

        // Create chatbot div
        const chatbotDiv = document.createElement('div');

        const botTitle = document.createElement('div');
        botTitle.classList.add('fw-bold', 'text-info');
        botTitle.textContent = "AI Assistant";
        chatbotDiv.appendChild(botTitle);

        const replyStatus = document.createElement('div');
        replyStatus.classList.add('text-secondary', 'fst-italic', 'ms-3');
        const replyWait = document.createElement('div');
        const spinner = document.createElement('span');
        spinner.classList.add('spinner-border', 'spinner-border-sm', 'me-2');
        replyWait.appendChild(spinner);
        const replyWaitText = document.createElement('span');
        replyWaitText.textContent = "Generating response ..."
        replyWait.appendChild(replyWaitText);
        replyStatus.appendChild(replyWait);
        chatbotDiv.appendChild(replyStatus);
        chatbox.appendChild(chatbotDiv);
        chatbox.scrollTop = chatbox.scrollHeight;

        var summaryTab = document.getElementById('summary-tab');
        summaryTab.classList.add('d-flex', 'justify-content-center', 'align-items-center');
        summaryTab.innerHTML = 
        '<div><center><div class="spinner-grow spinner-grow-sm" role="status"></div></center><div class = "text-secondary">Fetching your results ...</div></div>'

        try {
            // Use `await` directly on the fetch call
            const data = await deliver(message);
            const reply = document.createElement('div');
            reply.textContent = data.reply;

            replyWait.removeChild(spinner);
            replyWait.removeChild(replyWaitText);
            chatbotDiv.appendChild(reply);

            // Create "Answer More" button
            if (data.intent == "technical"){
                const answerMoreBtn = document.createElement('answer-more-btn');
                answerMoreBtn.style.background = 'none';
                answerMoreBtn.style.border = 'none';
                answerMoreBtn.style.fontStyle = 'italic';
                answerMoreBtn.style.color = 'blue';
                answerMoreBtn.style.cursor = 'pointer';
                answerMoreBtn.style.float = 'right';
                // answerMoreBtn.textContent = "Answer More";
                answerMoreBtn.onclick = function() {
                    // Logic for "Answer More" button click
                    inputBox.focus();
                };
                chatbotDiv.appendChild(answerMoreBtn);
            };
            // Scroll to the bottom of the chatbox to show the latest message
            chatbox.scrollTop = chatbox.scrollHeight;
        } catch (error) {
            console.error('Error delivering message:', error.message);
        }
    }

    }else{
        assistInform('text-warning', 'Import your OPENAI KEY first!')
    };
}

async function getReferences(message) {
    var jsonSettings = {};
    jsonSettings['numRef'] = settings.numRef;
    jsonSettings['searchCoef'] = settings.searchCoef;
    jsonSettings['sortDescending'] = settings.sortDescending;
    jsonSettings['message'] = message;
    jsonSettings['list_files'] = getFileList();
    jsonSettings['userOpenAiKey'] = settings.userOpenAiKey;
    jsonSettings['verifyUserOpenaiKey'] = settings.verifyUserOpenaiKey;
    jsonSettings['verifySystemOpenaiKey'] = settings.verifySystemOpenaiKey;
    jsonSettings['openaiKeyMode'] = settings.openaiKeyMode;

    const csrftoken = getCookie('csrftoken');

    const refs = await fetch("refs/", {
        method: "POST",
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json',
        },
        mode: 'same-origin',
        body: JSON.stringify(jsonSettings),  // Wrap the message in an object
    });

    if (!refs.ok) {
        throw new Error('Network response was not ok');
    }

    const data = await refs.json();

    return data;  // Return the parsed JSON response
}

async function deliver(message) {
    const csrftoken = getCookie('csrftoken');

    const refs_data = await getReferences(message);
    if (refs_data.status == "success") {
        console.log("deliver() - API Refs: ", refs_data);

        var summaryTab = document.getElementById('summary-tab');
        summaryTab.classList.remove('d-flex', 'justify-content-center', 'align-items-center');
        summaryTab.innerHTML = "";

        //Check if refs.files is empty array
        const refNum = document.getElementById('refs-num').value;
        console.log("deliver() - User Refs: ", refNum);
        var dispRefNum = 0;
        if (refs_data.refNum > 0 && refNum < refs_data.refNum) {
            dispRefNum = refNum;
        } else {
            dispRefNum = refs_data.refNum;
        };
        
        if (dispRefNum > 0) {
            console.log("deliver() - Displayed References: ", dispRefNum);
            for (var i = 0; i < dispRefNum; i++) { //refs.files.length <<== ERROR with .length function
                summaryTab.appendChild(createSummary(refs_data.files[i]));
            };
        } else {
            console.log("deliver() - No References Found");
        };

        // Update list of filter files
        const unique_refs = Array.from(new Set(
            refs_data.files
                .filter(({ file_id, file_name }) => file_id && file_name)
                .map(({ file_id, file_name }) => JSON.stringify({ file_id, file_name }))
        )).map(JSON.parse);

        const fileListContainer = document.getElementById('files-filter');
        const files_ul = document.getElementById('file-list-ul');
        fileListContainer.removeChild(files_ul);
        showFileFilter(unique_refs);

        // Get final Chat response
        jsonInput = {
            'intent':refs_data.intent,
            'message': message,
            'refs': refs_data,
            'userOpenAiKey': settings.userOpenAiKey,
            'verifyUserOpenaiKey': settings.verifyUserOpenaiKey,
            'verifySystemOpenaiKey': settings.verifySystemOpenaiKey,
            'openaiKeyMode': settings.openaiKeyMode,
        }

        // Get Chat Response
        const chat_response = await fetch("reply/", {
            method: "POST",
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json',
            },
            mode: 'same-origin',
            body: JSON.stringify(jsonInput),  // Wrap the message in an object
        });

        if (!chat_response.ok) {
            throw new Error('Network chat_response was not ok');
        }

        const chat_data = await chat_response.json();
        return chat_data;  // Return the parsed JSON chat_response
    } else {
        refs_data.reply = "Error: " + refs_data.error;
        refs_data.intent = 'basic';
        return refs_data;
    };

}

function getCookie(name) {
	let cookieValue = null;
	if (document.cookie && document.cookie !== '') {
		const cookies = document.cookie.split(';');
		for (let i = 0; i < cookies.length; i++) {
			const cookie = cookies[i].trim();
			// Does this cookie string begin with the name we want?
			if (cookie.substring(0, name.length + 1) === (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}

function showNotification(message, id) {
    const notification = document.getElementById(id);
    notification.textContent = message;
    notification.classList.add('show');
    // Hide the notification after a few seconds
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000); // Adjust the time as needed
}

async function changeSettings() {
    const refNum = document.getElementById('refs-num').value;
    const searchCoefs = document.getElementById('search-coefs').value;
    const sortRefs = document.getElementById('sort-refs');
    let userOpenAiKey = document.getElementById('inputOpenAIKey').value;

    if (refNum > 20) {
        alert("Maximum number of references is 20.")
        return;
    }
    if (searchNum < 0 || searchNum > 1) {
        alert("Must be in range 0 - 1.")
        return;
    }
    settings.numRef = refNum;
    settings.searchCoef = searchCoefs;
    settings.userOpenAiKey = userOpenAiKey;
    if (sortRefs.checked) {
        settings.sortDescending = true;
    } else {
        settings.sortDescending = false;
    }
    console.log("changeSettings() - Settings: ",settings);
    
    // Close the modal
    $('#setting-modal').modal('hide');
    // Ensure the backdrop is removed completely after the modal is hidden
    $('#setting-modal').on('hidden.bs.modal', function () {
        $('.modal-backdrop').remove();
    });

    textSettings = "Setting saved! <br> Number of references: " + settings.numRef + "<br> Search Coefficients: " + settings.searchCoef + "<br> Sort Descending: " + settings.sortDescending + "<br> OpenAI Key: " + settings.userOpenAiKey + "<br>";
    assistInform('text-success', textSettings);
    await checkLLMKey();
}

async function checkLLMKey(){
    const userOpenAiKey = document.getElementById('inputOpenAIKey').value;
    const csrftoken = getCookie('csrftoken');
    const refs = await fetch("checkllm/", {
        method: "POST",
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json',
        },
        mode: 'same-origin',
        body: JSON.stringify({'userOpenAiKey': userOpenAiKey}),  // Wrap the message in an object
    });
    if (!refs.ok) {
        throw new Error('Network response was not ok');
    }
    const data = await refs.json();
    if (data.status == true) {
        assistInform('text-success', "OpenAI Key is valid! Ready to use!");
        // showNotification("OpenAI Key is valid! Ready to use!", "noti-success-key");
        settings.verifyUserOpenaiKey = true;
        settings.openaiKeyMode = "user";
    } else {
        assistInform('text-warning', "OpenAI Key is invalid! Please change to another OpenAI Key");
        // showNotification("OpenAI Key is invalid! Please change to another OpenAI Key", "noti-failed-key");
        settings.verifyUserOpenaiKey = false;
    };
}

function getFileList() {
    var file_ids = [];
    var checkboxes = document.querySelectorAll('input[type=checkbox]:checked');
    checkboxes.forEach(function (checkbox) {
        file_ids.push(checkbox.value);
    });
    console.log("getFileList() - List of files for Filtering: ", file_ids);
    return file_ids;
}


async function getFileFilter() {
    checkDatabasesIsAlive()
    const csrftoken = getCookie('csrftoken');
    const files = await fetch("files/", {
        method: "GET",
        mode: 'same-origin',
    });

    if (!files.ok) {
        throw new Error('Network response was not ok');
    }
    const data = await files.json();
    console.log("getFileFilter() - File ID sample: ",data.files[0].file_id);
    
    await showFileFilter(data.files);

    console.log("getFileFilter() - OPENAI_KEY .env status: ", data.openai_key_status);
    if (data.openai_key_status == false) {
        textContent = "<i>OPENAI_KEY không còn hiệu lực, liên hệ nhà quản trị hoặc tự thêm key của bạn trong mục cài đặt cạnh nút gửi phía dưới! <br>(OPENAI_KEY is no longer valid, please contact the administrator or add your key in the settings next to the send button below!)</i>";
        assistInform("text-warning", textContent)
        //update openai key status
        settings.verifySystemOpenaiKey = false;
        console.log("getFileFilter() - OPENAI_KEY verifySystemOpenaiKey status: ", settings.verifySystemOpenaiKey);
    }else{
        settings.verifySystemOpenaiKey = true;
        console.log("getFileFilter() - OPENAI_KEY verifySystemOpenaiKey status: ", settings.verifySystemOpenaiKey);
    };

    return data.files;  // Return the parsed JSON response
}

async function showFileFilter(files) {
    const fileListContainer = document.getElementById('files-filter');

    const fileListUl = document.createElement('ul');
    fileListUl.setAttribute('id', 'file-list-ul');
    fileListUl.classList.add('list-group', 'overflow-x-hidden');
    fileListUl.style.overflowY = 'auto';
    fileListUl.style.height = 'calc(100vh - 120px)';
    fileListContainer.appendChild(fileListUl);

    files.forEach(file => {
        const fileListLi = document.createElement('li');
        fileListLi.classList.add('list-group-item', 'd-flex', 'list-group-hover');

        const fileCheckbox = document.createElement('input');
        fileCheckbox.classList.add('form-check-input', 'me-2');
        fileCheckbox.type = 'checkbox';
        fileCheckbox.value = file.file_id;
        fileCheckbox.id = 'tick-' + file.file_id;
        fileCheckbox.addEventListener('change', getFileList);
        fileListLi.appendChild(fileCheckbox);

        const fileLabel = document.createElement('label');
        fileLabel.classList.add('form-check-label', 'fw-light');
        fileLabel.setAttribute('for', 'tick-' + file.file_id);
        fileLabel.style.fontSize = 'small';
        fileLabel.textContent = file.file_name;
        fileListLi.appendChild(fileLabel);

        fileListUl.appendChild(fileListLi);
    });
}

function setCookie(name, value, hours) {
    const now = new Date();
    now.setTime(now.getTime() + (hours * 60 * 60 * 1000));
    const expires = "expires=" + now.toUTCString();
    document.cookie = name + "=" + value + ";" + expires + ";path=/";
}

function generateRandomString(length) {
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    const charactersLength = characters.length;
    
    for (let i = 0; i < length; i++) {
        const randomIndex = Math.floor(Math.random() * charactersLength);
        result += characters[randomIndex];
    }

    return result;
}

function assistInform(textClass, textContent) {
    const chatbox = document.getElementById('chatbox');
    const errorDiv = document.createElement('div');

    const botTitle = document.createElement('div');
    botTitle.classList.add('fw-bold', 'text-info');
    botTitle.textContent = "AI Assistant";
    errorDiv.appendChild(botTitle);

    const errorMessage = document.createElement('div');
    errorMessage.classList.add(textClass);
    errorMessage.innerHTML = textContent;
    
    errorDiv.appendChild(errorMessage);
    chatbox.appendChild(errorDiv);
    chatbox.scrollTop = chatbox.scrollHeight;
    }

async function checkDatabasesIsAlive() {
    const csrftoken = getCookie('csrftoken');
    const files = await fetch("checkdbs/", {
        method: "GET",
        mode: 'same-origin',
    });

    if (!files.ok) {
        throw new Error('Network response was not ok');
    }
    const data = await files.json();
    console.log("checkDatabasesIsAlive() - MongoDB:", data.mongo_status, " MySQL:", data.mysql_status, " Weaviate:", data.weaviate_status);
    
    if (data.mongo_status == false || data.mysql_status == false || data.weaviate_status == false){
        alert("Can not connect to Database! Please contact website Admin!");
    }

}