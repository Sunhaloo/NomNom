document.addEventListener('DOMContentLoaded', function () {
    const reviewsData = {};

    let currentProductName = '';
    let selectedRating = 0;
    let isSubmittingReview = false; // Flag to prevent multiple submissions

    // Quantity control functions
    window.incrementQuantity = function (event) {
        event.preventDefault();
        event.stopPropagation();
        const input = event.target.parentElement.querySelector('.qty-input');
        const currentValue = parseInt(input.value);
        if (currentValue < 99) {
            input.value = currentValue + 1;
        }
    };

    window.decrementQuantity = function (event) {
        event.preventDefault();
        event.stopPropagation();
        const input = event.target.parentElement.querySelector('.qty-input');
        const currentValue = parseInt(input.value);
        if (currentValue > 1) {
            input.value = currentValue - 1;
        }
    };

    // Add to cart function with quantity
    window.addToCartWithQuantity = function (event, productName, productPrice, productImage, productCategory) {
        event.preventDefault();

        // Get the quantity from the card
        const card = event.target.closest('.product-card');
        const quantityInput = card.querySelector('.qty-input');
        const quantity = parseInt(quantityInput.value);

        // Get the button that was clicked
        const clickedButton = event.target.closest('.btn-add-cart');

        // Get CSRF token
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

        // Send AJAX request to add to cart
        fetch('/cart/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken || ''
            },
            body: JSON.stringify({
                name: productName,
                price: productPrice,
                image: productImage,
                quantity: quantity,
                category: productCategory
            })
        })
            .then(response => {
                if (response.status === 403 || response.status === 401) {
                    // If user not logged in, show login prompt
                    // Don't show animation for unauthenticated users
                    showLoginPrompt();
                    return Promise.reject('Not authenticated');
                }

                // Only show animation if logged in and request was successful
                if (clickedButton) {
                    createFlyingAnimation(clickedButton);
                }

                return response.json();
            })
            .then(data => {
                if (data.success) {
                    showNotification(data.message, 'success');
                    // Update cart counter
                    updateCartCount(data.cart_count);
                    // Reset quantity to 1
                    quantityInput.value = 1;
                } else {
                    showNotification(data.message || 'Failed to add to cart', 'error');
                }
            })
            .catch(error => {
                if (error !== 'Not authenticated') {
                    showNotification('Failed to add to cart', 'error');
                }
            });
    };


    window.addToCart = function (productName, productPrice, productImage) {
        // Get CSRF token
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

        // Send AJAX request to add to cart
        fetch('/cart/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken || ''
            },
            body: JSON.stringify({
                name: productName,
                price: productPrice,
                image: productImage,
                quantity: 1
            })
        })
            .then(response => {
                if (response.status === 403 || response.status === 401) {
                    // If user not logged in, show login prompt
                    // Don't show animation for unauthenticated users
                    showLoginPrompt();
                    return Promise.reject('Not authenticated');
                }

                // Note: We can't show animation here since we don't have an event context
                // Animation is typically shown when called from an event handler

                return response.json();
            })
            .then(data => {
                if (data.success) {
                    showNotification(data.message, 'success');
                    // Update cart counter
                    updateCartCount(data.cart_count);
                } else {
                    showNotification(data.message || 'Failed to add to cart', 'error');
                }
            })
            .catch(error => {
                if (error !== 'Not authenticated') {
                    showNotification('Failed to add to cart', 'error');
                }
            });
    };

    // Function to create flying cart animation (made it global for reuse)
    window.createFlyingAnimation = function (sourceElement) {
        const cartIcon = document.querySelector('.cart-icon-container');
        if (!cartIcon || !sourceElement) return;

        // Get positions
        const sourceRect = sourceElement.getBoundingClientRect();
        const cartRect = cartIcon.getBoundingClientRect();

        // Calculate translation
        const deltaX = cartRect.left - sourceRect.left;
        const deltaY = cartRect.top - sourceRect.top;

        // Create flying element
        const flyingElement = document.createElement('div');
        flyingElement.className = 'flying-item';
        flyingElement.innerHTML = '<i class="fas fa-shopping-cart"></i>';
        flyingElement.style.left = sourceRect.left + 'px';
        flyingElement.style.top = sourceRect.top + 'px';
        flyingElement.style.setProperty('--tx', deltaX + 'px');
        flyingElement.style.setProperty('--ty', deltaY + 'px');
        flyingElement.style.fontSize = '24px';
        flyingElement.style.color = '#8D6E63';

        document.body.appendChild(flyingElement);

        // Remove after animation
        setTimeout(() => {
            flyingElement.remove();
        }, 800);
    }


    // Open review modal
    window.openReviewModal = function (productName) {
        currentProductName = productName;

        const modal = document.getElementById('reviewModal');
        const modalTitle = document.getElementById('modalTitle');

        modalTitle.textContent = `${productName} Reviews`;

        // Load product reviews
        loadProductReviews(productName);

        // Reset form
        document.getElementById('reviewForm').reset();
        selectedRating = 0;
        updateRatingStars(0);

        // Show modal
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    };

    // Close review modal
    window.closeReviewModal = function () {
        const modal = document.getElementById('reviewModal');
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    };

    // Load product reviews from server
    function loadProductReviews(productName) {
        // Find the pastry ID for this product name
        const productCard = document.querySelector(`.product-card[data-product="${productName}"]`);
        if (!productCard) {
            console.error('Could not find product card for', productName);
            return;
        }

        const pastryId = productCard.getAttribute('data-pastry-id');
        if (!pastryId) {
            console.error('Could not find pastry ID for', productName);
            return;
        }

        // Fetch reviews from the server
        fetch(`/review/get/${pastryId}/`)
            .then(response => response.json())
            .then(data => {
                if (data.reviews) {
                    // Calculate average rating
                    let totalRating = 0;
                    if (data.reviews.length > 0) {
                        totalRating = data.reviews.reduce((sum, review) => sum + review.rating, 0);
                    }
                    const averageRating = data.reviews.length > 0 ? (totalRating / data.reviews.length) : 0;

                    // Update summary
                    document.getElementById('summaryRating').textContent = averageRating.toFixed(1);
                    document.getElementById('summaryCount').textContent = `Based on ${data.reviews.length} reviews`;

                    // Update summary stars
                    const summaryStars = document.getElementById('summaryStars');
                    summaryStars.innerHTML = generateStars(averageRating);

                    // Load review list
                    const reviewList = document.getElementById('reviewList');
                    reviewList.innerHTML = '';

                    if (data.reviews.length === 0) {
                        reviewList.innerHTML = '<div class="review-item">No reviews yet. Be the first reviewer!</div>';
                    } else {
                        data.reviews.forEach(review => {
                            const reviewItem = document.createElement('div');
                            reviewItem.className = 'review-item';
                            reviewItem.innerHTML = `
                        <div class="review-header">
                          <div class="reviewer-name">${review.user}</div>
                          <div class="review-date">${review.date}</div>
                        </div>
                        <div class="review-rating">${generateStars(review.rating)}</div>
                        <div class="review-text">${review.comment}</div>
                      `;
                            reviewList.appendChild(reviewItem);
                        });
                    }

                    // Update the local cache with server data
                    reviewsData[productName] = {
                        rating: averageRating,
                        count: data.reviews.length,
                        reviews: data.reviews.map(r => ({
                            name: r.user,
                            rating: r.rating,
                            date: r.date,
                            text: r.comment
                        }))
                    };
                }
            })
            .catch(error => {
                console.error('Error loading reviews:', error);
                // Fallback to cached data if there's an error
                const productReviews = reviewsData[productName] || { rating: 0, count: 0, reviews: [] };

                // Update summary
                document.getElementById('summaryRating').textContent = productReviews.rating.toFixed(1);
                document.getElementById('summaryCount').textContent = `Based on ${productReviews.count} reviews`;

                // Update summary stars
                const summaryStars = document.getElementById('summaryStars');
                summaryStars.innerHTML = generateStars(productReviews.rating);

                // Load review list
                const reviewList = document.getElementById('reviewList');
                reviewList.innerHTML = '';

                if (productReviews.reviews.length === 0) {
                    reviewList.innerHTML = '<div class="review-item">No reviews yet. Be the first reviewer!</div>';
                } else {
                    productReviews.reviews.forEach(review => {
                        const reviewItem = document.createElement('div');
                        reviewItem.className = 'review-item';
                        reviewItem.innerHTML = `
                    <div class="review-header">
                      <div class="reviewer-name">${review.name}</div>
                      <div class="review-date">${review.date}</div>
                    </div>
                    <div class="review-rating">${generateStars(review.rating)}</div>
                    <div class="review-text">${review.text}</div>
                  `;
                        reviewList.appendChild(reviewItem);
                    });
                }
            });
    }

    // Generate star rating HTML
    function generateStars(rating) {
        let starsHTML = '';
        const fullStars = Math.floor(rating);
        const hasHalfStar = rating % 1 !== 0;

        for (let i = 0; i < fullStars; i++) {
            starsHTML += '<i class="fas fa-star"></i>';
        }

        if (hasHalfStar) {
            starsHTML += '<i class="fas fa-star-half-alt"></i>';
        }

        const emptyStars = 5 - Math.ceil(rating);
        for (let i = 0; i < emptyStars; i++) {
            starsHTML += '<i class="far fa-star"></i>';
        }

        return starsHTML;
    }

    // Update product card rating
    function updateProductCardRating(productName) {
        const productReviews = reviewsData[productName];
        if (!productReviews) return;

        const productCard = document.querySelector(`.product-card[data-product="${productName}"]`);

        if (productCard) {
            // Update stars
            const starsElement = productCard.querySelector('.stars');
            if (starsElement) {
                starsElement.innerHTML = generateStars(productReviews.rating);
            }

            // Update rating text
            const ratingElement = productCard.querySelector('.rating-count');
            if (ratingElement) {
                ratingElement.textContent = `${productReviews.rating.toFixed(1)} (${productReviews.count} reviews)`;
            }
        }
    }

    // Handle rating input
    const stars = document.querySelectorAll('.rating-input .star');

    stars.forEach(star => {
        star.addEventListener('click', function () {
            selectedRating = parseInt(this.getAttribute('data-rating'));
            updateRatingStars(selectedRating);
        });

        star.addEventListener('mouseenter', function () {
            const hoverRating = parseInt(this.getAttribute('data-rating'));
            updateRatingStars(hoverRating);
        });
    });

    const ratingInput = document.getElementById('ratingInput');
    if (ratingInput) {
        ratingInput.addEventListener('mouseleave', function () {
            updateRatingStars(selectedRating);
        });
    }

    // Handle form submission
    const reviewForm = document.getElementById('reviewForm');
    if (reviewForm) {
        reviewForm.addEventListener('submit', function (e) {
            e.preventDefault();

            // Prevent multiple submissions
            if (isSubmittingReview) {
                return; // Already submitting, ignore additional clicks
            }

            isSubmittingReview = true; // Set flag to prevent multiple submissions

            // Check if user is logged in
            const isAuthenticated = this.dataset.userAuthenticated === 'true';
            if (!isAuthenticated) {
                showLoginPrompt('You must login and purchase this item to submit a review.');
                isSubmittingReview = false; // Reset flag
                return;
            }

            if (selectedRating === 0) {
                showNotification('Please select a rating', 'error');
                isSubmittingReview = false; // Reset flag
                return;
            }

            const text = document.getElementById('reviewText').value;
            const pastryName = currentProductName; // Use the current product name

            // Get the pastry ID by searching the page for it
            const productCard = document.querySelector(`.product-card[data-product="${pastryName}"]`);
            if (!productCard) {
                showNotification('Error: Could not find pastry information', 'error');
                isSubmittingReview = false; // Reset flag
                return;
            }

            const pastryId = productCard.getAttribute('data-pastry-id');
            if (!pastryId) {
                showNotification('Error: Could not find pastry ID', 'error');
                isSubmittingReview = false; // Reset flag
                return;
            }

            // Get CSRF token
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

            // Make AJAX request to backend
            fetch(`/review/add/${pastryId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken || ''
                },
                body: JSON.stringify({
                    rating: selectedRating,
                    comment: text
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification(data.message, 'success');

                    // Reset form
                    reviewForm.reset();
                    selectedRating = 0;
                    updateRatingStars(0);

                    // Reload reviews to show the new one
                    setTimeout(() => {
                        loadProductReviews(currentProductName);
                    }, 1000);

                    // Close the modal after successful submission
                    setTimeout(() => {
                        closeReviewModal();
                    }, 1500); // Close after 1.5 seconds to allow user to see the success message
                } else {
                    showNotification(data.error || 'Failed to submit review', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Error submitting review', 'error');
            })
            .finally(() => {
                isSubmittingReview = false; // Always reset the flag
            });
        });
    }

    // Close modal when clicking outside
    window.addEventListener('click', function (event) {
        const modal = document.getElementById('reviewModal');
        if (event.target === modal) {
            closeReviewModal();
        }
    });

    // Update rating stars display
    function updateRatingStars(rating) {
        const stars = document.querySelectorAll('.rating-input .star');

        stars.forEach((star, index) => {
            if (index < rating) {
                star.classList.add('active');
            } else {
                star.classList.remove('active');
            }
        });
    }

    // Show notification
    function showNotification(message, type = 'success') {
        const notification = document.getElementById('notification');
        const notificationText = document.getElementById('notificationText');

        if (notificationText) {
            notificationText.textContent = message;
        } else {
            notification.textContent = message;
        }

        if (type === 'error') {
            notification.style.backgroundColor = '#dc3545';
        } else {
            notification.style.backgroundColor = '#5D4037'; // Primary brown
        }

        notification.classList.add('show');

        setTimeout(() => {
            notification.classList.remove('show');
        }, 3000);
    }
});