document.addEventListener("DOMContentLoaded", () => {
    const steps = document.querySelectorAll(".progress-step");
    const track = document.getElementById("progress-track");

    if (!steps.length) return;

    const current = window.currentStep || 1;

    steps.forEach(step => {
        const num = parseInt(step.dataset.step);

        if (num < current) {
            step.classList.add("completed");
        } else if (num === current) {
            step.classList.add("active");
        }
    });
});

function updateProgress(stepNumber) {
    const steps = document.querySelectorAll(".progress-step");

    if (!steps.length) return;

    steps.forEach(step => {
        const num = parseInt(step.dataset.step);

        step.classList.remove("active", "completed");

        if (num < stepNumber) {
            step.classList.add("completed");
        } else if (num === stepNumber) {
            step.classList.add("active");
        }
    });
}

window.updateProgress = updateProgress;
