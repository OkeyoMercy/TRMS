    document.addEventListener('DOMContentLoaded', function () {
        console.log('The js is accessed');
        var body = document.body;
        console.log('All data attributes:', body.dataset);
        var showProfileComponent = body.getAttribute('data-show-profile-component') === 'true';
        var profileComponentContainer = document.getElementById('profileComponentContainer');
        console.log('Show Profile Component:', showProfileComponent);

        if (showProfileComponent) {
            profileComponentContainer.style.display = 'block';
        } else {
            profileComponentContainer.style.display = 'none';
        }
    });
