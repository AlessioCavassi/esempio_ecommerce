// Custom JavaScript for ShoeStore

document.addEventListener('DOMContentLoaded', function() {
    console.log('ShoeStore JS Loaded');

    // Example: Add confirmation for delete buttons in admin
    const deleteForms = document.querySelectorAll('form.delete-form');
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!confirm('Are you sure you want to delete this item?')) {
                event.preventDefault();
            }
        });
    });

    // Add more interactive JS as needed
    // e.g., handling dynamic updates in cart, form validations, etc.

});
