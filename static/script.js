// Function to update word count
function updateWordCount(text) {
    const wordCountDisplay = document.getElementById("wordCount");
    const wordCount = text ? text.trim().split(/\s+/).length : 0;
    wordCountDisplay.textContent = `Total Word Count: ${wordCount}`;
}
function handleTextInput(event) {
    const textInput = document.getElementById("textInput");
    const text = event.target.value.trim();
    updateWordCount(text);
}
// Function to handle TXT files
function handleTxtFile(file) {
    const reader = new FileReader();
    reader.onload = function (e) {
        const text = e.target.result;
        const textInput = document.getElementById("textInput");
        textInput.value = text; // Display content in the textarea
        updateWordCount(text); // Update word count
    };
    reader.readAsText(file);
}

// Function to handle DOC/DOCX files
function handleDocFile(file) {
    const reader = new FileReader();
    reader.onload = function (e) {
        const arrayBuffer = e.target.result;
        mammoth.extractRawText({ arrayBuffer: arrayBuffer })
            .then(function (result) {
                const text = result.value;
                const textInput = document.getElementById("textInput");
                textInput.value = text; // Display content in the textarea
                updateWordCount(text); // Update word count
            });

    };
    reader.readAsArrayBuffer(file);
}
// Function to handle PDF files using pdf.js
async function handlePdfFile(file) {
    const reader = new FileReader();
    reader.onload = async function (e) {
        const typedArray = new Uint8Array(e.target.result);
        const pdf = await pdfjsLib.getDocument(typedArray).promise;
        let text = "";

        for (let i = 1; i <= pdf.numPages; i++) {
            const page = await pdf.getPage(i);
            const content = await page.getTextContent();
            text += content.items.map((item) => item.str).join(" ");
        }

        const textInput = document.getElementById("textInput");
        textInput.value = text; // Display content in the textarea
        updateWordCount(text); // Update word count
    };
    reader.readAsArrayBuffer(file);
}

// Function to handle file upload and determine file type
function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) {
        alert("No file uploaded. Please select a file.");
        return;
    }

    const fileType = file.type;
    const fileName = file.name.toLowerCase();

    if (fileType === "text/plain") {
        handleTxtFile(file);
    } else if (fileType === "application/pdf") {
            handlePdfFile(file); // Handles PDF files 
    }else if (
        fileType === "application/vnd.openxmlformats-officedocument.wordprocessingml.document" ||
        fileType === "application/msword" ||
        fileName.endsWith(".docx") ||
        fileName.endsWith(".doc")
    ) {
        handleDocFile(file);
    } else {
        alert("Unsupported file type. Please upload a TXT,PDF,or DOC/DOCX file.");
    }
}

// Initialize event listeners
document.addEventListener("DOMContentLoaded", () => {
    const fileUpload = document.getElementById("fileUpload");
    const textInput = document.getElementById("textInput");

    // Attach file upload event listener
    fileUpload.addEventListener("change", handleFileUpload);

    // Update word count when text is manually typed
    textInput.addEventListener("input", () => {
        const text = textInput.value.trim();
        updateWordCount(text);
    });
});
//for loading messages 
document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    const submitBtn = form.querySelector("button");
    const loadingOverlay = document.getElementById("loadingOverlay");
    const textInput = document.getElementById("textInput");
    const wordCountDisplay = document.getElementById("wordCount");

    // Word count feature
    textInput.addEventListener("input", function () {
        const words = textInput.value.trim().split(/\s+/).filter(word => word.length > 0);
        wordCountDisplay.textContent = `Total Word Count: ${words.length}`;
    });

    form.addEventListener("submit", function (event) {
        event.preventDefault(); // Prevent default form submission

        // Show loading animation
        loadingOverlay.style.display = "flex";
        form.classList.add("disabled"); // Disable form elements

        // Disable submit button to prevent multiple clicks
        submitBtn.disabled = true;

        // Simulate a delay before actual submission (you can replace this with real form submission)
        setTimeout(() => {
            form.submit();
        }, 2500); // Delay of 2.5 seconds
    });
});
// JavaScript to handle collapsible FAQ functionality
function toggleAnswer(questionElement) {
    const answerElement = questionElement.nextElementSibling;
    if (answerElement.style.display === "none" || answerElement.style.display === "") {
        answerElement.style.display = "block"; // Show the answer
    } else {
        answerElement.style.display = "none"; // Hide the answer
    }
}
// JavaScript functionality for RESULT Page
document.addEventListener("DOMContentLoaded", function () {
    // Simulating file content loading
    // Fetch file content from backend
    fetch('http://localhost:3000/getFileContent')
        .then(response => response.text())
        .then(data => {
            document.getElementById("file-content").textContent = data;
        })
        .catch(error => console.error('Error fetching file content:', error));

    // Download button functionality
    //const downloadButton = document.getElementById("download-button");
    const downloadMessage = document.getElementById("download-message");

    downloadButton.addEventListener("click", function () {
        // fetch('/downloadFile')
        //     .then(response => response.blob())
        //     .then(blob => {
        //         const url = window.URL.createObjectURL(blob);
        //         const a = document.createElement("a");
        //         a.href = url;
        //         a.download = "plagiarized_file.pdf";
        //         document.body.appendChild(a);
        //         a.click();
        //         document.body.removeChild(a);

                downloadMessage.style.display = "block";
                setTimeout(() => {
                    downloadMessage.style.display = "none";
                }, 2000);
            })
            .catch(error => console.error('Error downloading file:', error));
});
/*document.addEventListener("DOMContentLoaded", async function () {
    // Example plagiarism score (replace this with actual data from backend)
   try{
    // Fetch plagiarism score from backend
    let response = await fetch("http://localhost:3000/getPlagiarismScore");
    let data = await response.json();
    
    let plagiarismScore = data.plagiarismScore || 0;
    let uniqueContent = 100 - plagiarismScore;

    let canvas = document.getElementById("piechart")
    if (!canvas) {
        console.error("Canvas element not found!");
        return;
    }

    let ctx = canvas.getContext("2d");

    // Create the pie chart
    new Chart(ctx, {
        type: "pie",
        data: {
            labels: ["Plagiarized", "Unique"],
            datasets: [{
                data: [plagiarismScore, uniqueContent],
                backgroundColor: ["#ff4d4d", "#4caf50"],
                hoverBackgroundColor: ["#ff1a1a", "#388e3c"]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: "bottom"
                }
            }
        }
    });
    console.log("Pie chart successfully loaded with data:",data);
}
catch (error) {
    console.error("Error fetching plagiarism score:", error);
}
});
*/