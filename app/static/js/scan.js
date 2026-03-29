document.addEventListener("DOMContentLoaded", () => {
    const startBtn = document.getElementById("startScan");
    const stopBtn = document.getElementById("stopScan");
    const interactive = document.getElementById("interactive");
    const cameraSelect = document.getElementById("camera");
    const snackbar = document.getElementById("feedback");
    var selectedDeviceId = null;

    function startScan() {
        interactive.replaceChildren();
        stopBtn.disabled = false;
        startBtn.disabled = true;

        const config = {
            inputStream: {
                name: "Live",
                type: "LiveStream",
                target: document.querySelector("#interactive"),
                constraints: {
                    deviceId: selectedDeviceId,
                },
            },
            decoder: {
                readers: ["ean_reader"],
            },
            locate: true,
            numOfWorkers: navigator.hardwareConcurrency || 4,
            frequency: 10,
        };

        Quagga.init(config, function (err) {
            if (err) {
                console.error(err);
                stopScan();
                return;
            }
            Quagga.start();
        });

        Quagga.onDetected(function (result) {
            const code = result.codeResult.code;
            alert(code + " (" + code.length + ")");
            if (code.length === 13 || code.length === 10) {
                queryISBN(code);
                console.log("Found code: " + code);
            }
        });
    }

    function stopScan() {
        Quagga.stop();
        interactive.replaceChildren("Click Start to start scanning.");
        stopBtn.disabled = true;
        startBtn.disabled = false;
    }

    cameraSelect.addEventListener("change", async function () {
        selectedDeviceId = this.value;

        stopScan();
        setTimeout(() => startScan(), 300);
    });

    startBtn.addEventListener("click", function () {
        populateCameraList();
    });

    stopBtn.addEventListener("click", function () {
        stopScan();
    });

    async function populateCameraList() {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: true,
        });

        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoDevices = devices.filter(
            (device) => device.kind === "videoinput",
        );

        cameraSelect.innerHTML = '<option value="">Select a camera...</option>';
        videoDevices.forEach((device, index) => {
            const option = document.createElement("option");
            option.value = device.deviceId;
            option.text = device.label;
            cameraSelect.appendChild(option);

            if (
                device.facingMode == "environment" ||
                device.label.indexOf("facing back") >= 0
            )
                selectedDeviceId = device.deviceId;
            cameraSelect.value = device.deviceId;
        });

        if (!selectedDeviceId === null && videoDevices.length > 0) {
            cameraSelect.value = videoDevices[0].deviceId;
            selectedDeviceId = videoDevices[0].deviceId;
        }

        startScan();
    }

    function addFeedback(content, className) {
        feedback = document.getElementById("feedback");
        feedback.classList = [];
        feedback.classList.add("snackbar", className);
        feedback.innerHTML = content;

        feedback.showPopover();
    }

    function removeFeedback() {
        feedback = document.getElementById("feedback");
        feedback.hidePopover();
    }

    async function queryISBN(isbn) {
        addFeedback(
            `<progress class="primary circle small"></progress> Scanned ${isbn}, looking it up.`,
            "primary",
        );

        try {
            const form = new FormData();
            form.append("isbn", isbn);

            const response = await fetch("/isbn/", {
                method: "POST",
                body: form,
            });

            if (response.status === 400) {
                const data = await response.json();
                const message = Object.values(data)[0][0];

                addFeedback(`<i>error</i> ${message} (ISBN: ${isbn})`, "error");
                setTimeout(removeFeedback, 3000);
            } else if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            } else {
                const data = await response.json();
                addFeedback(
                    `<i>check</i>Successfully added ${data.title}`,
                    "primary",
                );
                setTimeout(removeFeedback, 3000);
            }
        } catch (error) {
            addFeedback(
                "<i>dangerous</i> An unexpected error has happened!",
                "error",
            );
            setTimeout(removeFeedback, 3000);
        }
    }
});
