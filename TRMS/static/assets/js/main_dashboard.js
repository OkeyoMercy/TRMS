    document.addEventListener('DOMContentLoaded', function () {
        console.log('The js is accessed');
        const body = document.body;
        console.log('All data attributes:', body.dataset);
        const showProfileComponent = body.getAttribute('data-show-profile-component') === 'true';
        const profileComponentContainer = document.getElementById('profileComponentContainer');
        console.log('Show Profile Component:', showProfileComponent);
        const allowedPaths = ['/admin/', '/manager_dashboard/', '/driver_dashboard/'];
        const currentPath = window.location.pathname;

        if (profileComponentContainer && allowedPaths.includes(currentPath)) {
            profileComponentContainer.style.display = 'block';
        } else {
            profileComponentContainer.style.display = 'none';
        }

        // Attach a click event handler to links that toggle the profile component
        $(document).on('click', 'a[data-toggle-profile]', function() {
            $(profileComponentContainer).toggle(); // Toggle visibility based on current state
        });
    });
