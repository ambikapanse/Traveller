document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".like-icon").forEach(function (icon) {
        icon.addEventListener("click", function () {
            const postId = this.getAttribute("data-post-id");
            const likeCountElement = document.getElementById(`like-count-${postId}`);
            const iconElement = this; // Current clicked icon

            fetch(`/like/${postId}/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": window.csrfToken
                },
                credentials: "same-origin"
            })
                .then(response => response.json())
                .then(data => {
                    // Update like count
                    likeCountElement.textContent = data.likes;

                    // Toggle icon classes
                    if (iconElement.classList.contains("far")) {
                        iconElement.classList.remove("far");
                        iconElement.classList.add("fas");
                    } else {
                        iconElement.classList.remove("fas");
                        iconElement.classList.add("far");
                    }
                })
                .catch(error => console.error('Error:', error));
        });
    });
});
