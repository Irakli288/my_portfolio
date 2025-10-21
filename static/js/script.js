
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('project-modal');
    const closeModal = document.querySelector('.close-modal');
    const viewDetailsBtns = document.querySelectorAll('.view-details-btn');

    // Admin modal elements
    const adminModal = document.getElementById('admin-modal');
    const adminBtn = document.getElementById('admin-btn');
    const closeAdminModal = document.getElementById('close-admin-modal');
    const requestAccessBtn = document.getElementById('request-access-btn');
    const cancelAdminBtn = document.getElementById('cancel-admin-btn');

    // Modal elements
    const modalTitle = document.getElementById('modal-title');
    const modalDescription = document.getElementById('modal-description');
    const modalLink = document.getElementById('modal-link');
    const modalImage = document.getElementById('modal-image');
    const modalImageContainer = document.getElementById('modal-image-container');

    // Open modal when clicking on "Подробнее" button
    viewDetailsBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const projectId = this.getAttribute('data-project-id');
            openModal(projectId);
        });
    });

    // Open modal when clicking on card (but not on buttons)
    const portfolioCards = document.querySelectorAll('.portfolio-card');
    portfolioCards.forEach(card => {
        card.addEventListener('click', function(e) {
            // Don't open modal if clicking on buttons or links
            if (e.target.tagName === 'BUTTON' || e.target.tagName === 'A' || e.target.closest('button') || e.target.closest('a')) {
                return;
            }
            const projectId = this.getAttribute('data-project-id');
            openModal(projectId);
        });
    });

    // Close modal events
    closeModal.addEventListener('click', function() {
        modal.style.display = 'none';
    });

    window.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });

    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.style.display === 'block') {
            modal.style.display = 'none';
        }
    });

    // Function to open modal and fetch project data
    function openModal(projectId) {
        fetch(`/project/${projectId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Project not found');
                }
                return response.json();
            })
            .then(data => {
                // Use translations if available
                if (window.translations && window.translations.projects && window.translations.projects[projectId]) {
                    const translatedProject = window.translations.projects[projectId];
                    modalTitle.textContent = translatedProject.title;
                    modalDescription.textContent = translatedProject.full_description;
                } else {
                    modalTitle.textContent = data.title;
                    modalDescription.textContent = data.full_description;
                }

                // Set image if available
                if (data.preview_image) {
                    modalImage.src = data.preview_image;
                    modalImage.alt = data.title;
                    modalImageContainer.style.display = 'block';
                } else {
                    modalImageContainer.style.display = 'none';
                }

                // Set up project link
                if (data.live_url && data.live_url.trim() !== '') {
                    modalLink.href = data.live_url;
                    modalLink.style.display = 'inline-block';
                    modalLink.target = '_blank';
                } else {
                    modalLink.style.display = 'none';
                }
                modal.style.display = 'block';

                // Add fade-in animation
                modal.style.opacity = '0';
                setTimeout(() => {
                    modal.style.opacity = '1';
                }, 10);
            })
            .catch(error => {
                console.error('Error fetching project data:', error);
                const errorMessage = window.currentLang === 'ru' ? 'Ошибка загрузки данных проекта' : 'Error loading project data';
                alert(errorMessage);
            });
    }

    // Admin modal functionality
    if (adminBtn) {
        adminBtn.addEventListener('click', function() {
            adminModal.style.display = 'block';
            adminModal.style.opacity = '0';
            setTimeout(() => {
                adminModal.style.opacity = '1';
            }, 10);
        });
    }

    if (closeAdminModal) {
        closeAdminModal.addEventListener('click', function() {
            adminModal.style.display = 'none';
            resetAdminModal();
        });
    }

    if (cancelAdminBtn) {
        cancelAdminBtn.addEventListener('click', function() {
            adminModal.style.display = 'none';
            resetAdminModal();
        });
    }

    // Close admin modal when clicking outside
    window.addEventListener('click', function(e) {
        if (e.target === adminModal) {
            adminModal.style.display = 'none';
            resetAdminModal();
        }
    });

    let authCheckInterval = null;

    if (requestAccessBtn) {
        requestAccessBtn.addEventListener('click', function() {
            // Send request to backend
            fetch('/api/request_access', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.token) {
                    // Hide buttons, show waiting spinner
                    document.querySelector('.admin-modal-actions').style.display = 'none';
                    document.getElementById('waiting-approval').style.display = 'block';

                    // Start checking status
                    startAuthCheck(data.token);
                }
            })
            .catch(error => {
                console.error('Error requesting access:', error);
                alert('Ошибка при отправке запроса');
            });
        });
    }

    function startAuthCheck(token) {
        // Check status every 2 seconds
        authCheckInterval = setInterval(() => {
            fetch(`/api/check_auth/${token}`)
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'approved') {
                        // Success! Redirect to admin panel
                        clearInterval(authCheckInterval);
                        window.location.href = `/admin/login?token=${token}&auto=1`;
                    } else if (data.status === 'rejected') {
                        // Rejected by admin
                        clearInterval(authCheckInterval);
                        adminModal.style.display = 'none';
                        resetAdminModalToInitial();

                        const currentLang = window.currentLang || 'en';
                        const message = currentLang === 'ru'
                            ? 'Администратор отклонил запрос на доступ'
                            : 'Admin rejected the access request';
                        showNotification(message, 'error');
                    } else if (data.status === 'invalid') {
                        // Invalid token
                        clearInterval(authCheckInterval);
                        resetAdminModalToInitial();

                        const currentLang = window.currentLang || 'en';
                        const message = currentLang === 'ru'
                            ? 'Сессия истекла'
                            : 'Session expired';
                        showNotification(message, 'error');
                    }
                    // else status is 'pending', keep waiting
                })
                .catch(error => {
                    console.error('Error checking auth status:', error);
                });
        }, 2000);
    }

    function resetAdminModal() {
        if (authCheckInterval) {
            clearInterval(authCheckInterval);
            authCheckInterval = null;
        }
        resetAdminModalToInitial();
    }

    function resetAdminModalToInitial() {
        const waitingApproval = document.getElementById('waiting-approval');
        if (waitingApproval) waitingApproval.style.display = 'none';

        const modalActions = document.querySelector('.admin-modal-actions');
        if (modalActions) modalActions.style.display = 'flex';

        // Reset description text
        const modalDesc = document.getElementById('admin-modal-description');
        if (!modalDesc) return;

        const currentLang = window.currentLang || 'en';

        if (currentLang === 'ru') {
            modalDesc.innerHTML = `
                Для доступа к админ-панели требуется подтверждение администратора.<br>
                Нажмите "Запросить доступ" - администратор получит уведомление в Telegram и сможет одобрить ваш запрос.
            `;
        } else {
            modalDesc.innerHTML = `
                Admin panel access requires administrator approval.<br>
                Click "Request Access" - admin will receive a Telegram notification and can approve your request.
            `;
        }
    }

    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;

        document.body.appendChild(notification);

        // Trigger animation
        setTimeout(() => notification.classList.add('show'), 10);

        // Remove after 5 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }

    // Smooth scroll for page
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add loading animation for images
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        img.addEventListener('load', function() {
            this.style.opacity = '1';
        });

        // Handle broken images
        img.addEventListener('error', function() {
            this.style.background = '#2a2a2a';
            this.style.border = '2px dashed #555';
            this.alt = 'Изображение недоступно';
        });
    });

    // Add parallax effect to hero section
    window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        const heroImage = document.querySelector('.hero-image img');
        if (heroImage) {
            heroImage.style.transform = `translateY(${scrolled * 0.5}px)`;
        }
    });

    // Add fade-in animation for portfolio cards
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Initially hide cards and observe them
    portfolioCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = `all 0.6s ease ${index * 0.1}s`;
        observer.observe(card);
    });

    // Create tag copies for continuous scrolling
    function createTagCopies() {
        const cardTags = document.querySelectorAll('.card-tags');
        cardTags.forEach(tagsContainer => {
            const tags = tagsContainer.querySelectorAll('.tag-badge');
            if (tags.length > 0) {
                // Clear any existing copies
                const existingCopies = tagsContainer.querySelectorAll('.tag-badge-copy');
                existingCopies.forEach(copy => copy.remove());
                
                // Create copies of all tags
                tags.forEach(tag => {
                    const copy = tag.cloneNode(true);
                    copy.classList.add('tag-badge-copy');
                    tagsContainer.appendChild(copy);
                });
            }
        });
    }

    // Create copies on page load and resize
    createTagCopies();
    window.addEventListener('resize', createTagCopies);
});