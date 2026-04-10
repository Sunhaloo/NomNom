$(function () {
    const reviewsData = {};

    let currentProductName = '';
    let selectedRating = 0;
    let isSubmittingReview = false; // Flag to prevent multiple submissions

    // Quantity control functions
    window.incrementQuantity = function (event) {
        event.preventDefault();
        event.stopPropagation();
        const $input = $(event.target).parent().find('.qty-input');
        const currentValue = parseInt($input.val(), 10);
        if (currentValue < 99) {
            $input.val(currentValue + 1);
        }
    };

    window.decrementQuantity = function (event) {
        event.preventDefault();
        event.stopPropagation();
        const $input = $(event.target).parent().find('.qty-input');
        const currentValue = parseInt($input.val(), 10);
        if (currentValue > 1) {
            $input.val(currentValue - 1);
        }
    };

    // Add to cart function with quantity
    window.addToCartWithQuantity = function (event, productName, productPrice, productImage, productCategory) {
        event.preventDefault();

        // Get the quantity from the card
        const $card = $(event.target).closest('.product-card');
        const $quantityInput = $card.find('.qty-input');
        const quantity = parseInt($quantityInput.val(), 10);

        // Get the button that was clicked
        const clickedButton = $(event.target).closest('.btn-add-cart')[0];

        // Get CSRF token
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

        // Send AJAX request to add to cart
        $.ajax({
            url: '/cart/add/',
            method: 'POST',
            contentType: 'application/json',
            dataType: 'json',
            headers: {
                'X-CSRFToken': csrftoken || ''
            },
            data: JSON.stringify({
                name: productName,
                price: productPrice,
                image: productImage,
                quantity: quantity,
                category: productCategory
            }),
            success: function (data, textStatus, jqXHR) {
                // Only show animation if logged in and request was successful
                if (jqXHR.status !== 401 && jqXHR.status !== 403 && clickedButton) {
                    createFlyingAnimation(clickedButton);
                }

                if (data.success) {
                    showNotification(data.message, 'success');
                    // Update cart counter
                    updateCartCount(data.cart_count);
                    // Reset quantity to 1
                    $quantityInput.val(1);
                } else {
                    showNotification(data.message || 'Failed to add to cart', 'error');
                }
            },
            error: function (jqXHR) {
                if (jqXHR.status === 401 || jqXHR.status === 403) {
                    // If user not logged in, show login prompt
                    // Don't show animation for unauthenticated users
                    showLoginPrompt();
                } else {
                    showNotification('Failed to add to cart', 'error');
                }
            }
        });
    };


    window.addToCart = function (productName, productPrice, productImage) {
        // Get CSRF token
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

        // Send AJAX request to add to cart
        $.ajax({
            url: '/cart/add/',
            method: 'POST',
            contentType: 'application/json',
            dataType: 'json',
            headers: {
                'X-CSRFToken': csrftoken || ''
            },
            data: JSON.stringify({
                name: productName,
                price: productPrice,
                image: productImage,
                quantity: 1
            }),
            success: function (data, textStatus, jqXHR) {
                if (jqXHR.status === 401 || jqXHR.status === 403) {
                    // If user not logged in, show login prompt
                    showLoginPrompt();
                    return;
                }

                if (data.success) {
                    showNotification(data.message, 'success');
                    // Update cart counter
                    updateCartCount(data.cart_count);
                } else {
                    showNotification(data.message || 'Failed to add to cart', 'error');
                }
            },
            error: function (jqXHR) {
                if (jqXHR.status === 401 || jqXHR.status === 403) {
                    showLoginPrompt();
                } else {
                    showNotification('Failed to add to cart', 'error');
                }
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

        const $modal = $('#reviewModal');
        const $modalTitle = $('#modalTitle');

        $modalTitle.text(`${productName} Reviews`);

        // Load product reviews
        loadProductReviews(productName);

        // Reset form
        document.getElementById('reviewForm').reset();
        selectedRating = 0;
        updateRatingStars(0);

        // Show modal
        $modal.show();
        $('body').css('overflow', 'hidden');
    };

    // Close review modal
    window.closeReviewModal = function () {
        const $modal = $('#reviewModal');
        $modal.hide();
        $('body').css('overflow', 'auto');
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
        $.getJSON(`/review/get/${pastryId}/`)
            .done(function (data) {
                if (data.reviews) {
                    // Calculate average rating
                    let totalRating = 0;
                    if (data.reviews.length > 0) {
                        totalRating = data.reviews.reduce((sum, review) => sum + review.rating, 0);
                    }
                    const averageRating = data.reviews.length > 0 ? (totalRating / data.reviews.length) : 0;

                    // Update summary in modal
                    $('#summaryRating').text(averageRating.toFixed(1));
                    $('#summaryCount').text(`Based on ${data.reviews.length} reviews`);

                    // Update summary stars in modal
                    const $summaryStars = $('#summaryStars');
                    $summaryStars.html(generateStars(averageRating));

                    // Load review list in modal
                    const $reviewList = $('#reviewList');
                    $reviewList.empty();

                    if (data.reviews.length === 0) {
                        $reviewList.html('<div class="review-item">No reviews yet. Be the first reviewer!</div>');
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
                         $reviewList.append(reviewItem);
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

                    // Also update the underlying product card on the page
                     updateProductCardRating(productName);
                }
            })
            .fail(function (error) {
                console.error('Error loading reviews:', error);
                // Fallback to cached data if there's an error
                const productReviews = reviewsData[productName] || { rating: 0, count: 0, reviews: [] };

                // Update summary in modal
                $('#summaryRating').text(productReviews.rating.toFixed(1));
                $('#summaryCount').text(`Based on ${productReviews.count} reviews`);

                // Update summary stars in modal
                const $summaryStars = $('#summaryStars');
                $summaryStars.html(generateStars(productReviews.rating));

                // Load review list in modal
                const $reviewList = $('#reviewList');
                $reviewList.empty();

                if (productReviews.reviews.length === 0) {
                    $reviewList.html('<div class="review-item">No reviews yet. Be the first reviewer!</div>');
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
                        $reviewList.append(reviewItem);
                    });
                }

                // Keep the product card in sync with whatever data we have
                updateProductCardRating(productName);
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
    const $stars = $('.rating-input .star');

    $stars.on('click', function () {
        selectedRating = parseInt($(this).data('rating'), 10);
        updateRatingStars(selectedRating);
    });

    $stars.on('mouseenter', function () {
        const hoverRating = parseInt($(this).data('rating'), 10);
        updateRatingStars(hoverRating);
    });

    const $ratingInput = $('#ratingInput');
    if ($ratingInput.length) {
        $ratingInput.on('mouseleave', function () {
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
            $.ajax({
                url: `/review/add/${pastryId}/`,
                method: 'POST',
                contentType: 'application/json',
                dataType: 'json',
                headers: {
                    'X-CSRFToken': csrftoken || ''
                },
                data: JSON.stringify({
                    rating: selectedRating,
                    comment: text
                }),
                success: function (data) {
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
                },
                error: function (error) {
                    console.error('Error:', error);
                    showNotification('Error submitting review', 'error');
                },
                complete: function () {
                    isSubmittingReview = false; // Always reset the flag
                }
            });
        });
    }

    // Close modal when clicking outside
    $(window).on('click', function (event) {
        const modal = document.getElementById('reviewModal');
        if (event.target === modal) {
            closeReviewModal();
        }
    });

    // Update rating stars display
    function updateRatingStars(rating) {
        const $starsLocal = $('.rating-input .star');

        $starsLocal.each(function (index) {
            if (index < rating) {
                $(this).addClass('active');
            } else {
                $(this).removeClass('active');
            }
        });
    }

    // Show notification
    function showNotification(message, type = 'success') {
        const $notification = $('#notification');
        const $notificationText = $('#notificationText');

        if ($notificationText.length) {
            $notificationText.text(message);
        } else {
            $notification.text(message);
        }

        if (type === 'error') {
            $notification.css('background-color', '#dc3545');
        } else {
            $notification.css('background-color', '#5D4037'); // Primary brown
        }

        $notification.addClass('show');

        setTimeout(() => {
            $notification.removeClass('show');
        }, 3000);
    }
});
