function validateNumber(input){
    const value = input.value ;

    if(value.length < 3 || value.length > 6){
        input.setCustomValidity("Le prix doit être 500 ar minimum ")
        prixSimple += 500
    }
    else{
        input.setCustomValidity("")
    }
}



// deconnexion 
document.getElementById('logout-btn').addEventListener('click', function(event) {
    event.preventDefault(); 
    event.stopPropagation();
    document.getElementById('logout-modal').style.display = 'block';
  });

  document.getElementById('confirm-logout').addEventListener('click', function() {
    window.location.href = "/deconnexion";
  });

  document.getElementById('cancel-logout').addEventListener('click', function() {
    document.getElementById('logout-modal').style.display = 'none'; 
  });


  

  const items = [
    { title: "Item 1", description: "This is a description for item 1", color: "#3498db" },
    { title: "Item 2", description: "This is a description for item 2", color: "#e74c3c" },
    { title: "Item 3", description: "This is a description for item 3", color: "#2ecc71" },
    { title: "Item 4", description: "This is a description for item 4", color: "#f39c12" },
    { title: "Item 5", description: "This is a description for item 5", color: "#9b59b6" },
    { title: "Item 6", description: "This is a description for item 6", color: "#1abc9c" },
    { title: "Item 7", description: "This is a description for item 7", color: "#d35400" },
    { title: "Item 8", description: "This is a description for item 8", color: "#34495e" },
    { title: "Item 9", description: "This is a description for item 9", color: "#7f8c8d" },
    { title: "Item 10", description: "This is a description for item 10", color: "#16a085" },
    { title: "Item 11", description: "This is a description for item 11", color: "#c0392b" },
    { title: "Item 12", description: "This is a description for item 12", color: "#27ae60" },
    { title: "Item 13", description: "This is a description for item 13", color: "#f1c40f" },
    { title: "Item 14", description: "This is a description for item 14", color: "#8e44ad" },
    { title: "Item 15", description: "This is a description for item 15", color: "#2980b9" },
    { title: "Item 16", description: "This is a description for item 16", color: "#e67e22" },
    { title: "Item 17", description: "This is a description for item 17", color: "#95a5a6" },
    { title: "Item 18", description: "This is a description for item 18", color: "#2c3e50" }
];

// Pagination variables
const itemsPerPage = 5;
let currentPage = 1;
const totalPages = Math.ceil(items.length / itemsPerPage);

// DOM elements
const itemGrid = document.getElementById('itemGrid');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const pageInfo = document.getElementById('pageInfo');

// Function to render items for current page
function renderItems() {
    // Add animation class
    itemGrid.style.opacity = '0';
    itemGrid.style.transform = 'translateX(20px)';
    
    setTimeout(() => {
        // Clear the grid
        itemGrid.innerHTML = '';
        
        // Calculate starting and ending indices
        const startIndex = (currentPage - 1) * itemsPerPage;
        const endIndex = Math.min(startIndex + itemsPerPage, items.length);
        
        // Render items for current page
        for (let i = startIndex; i < endIndex; i++) {
            const item = items[i];
            const itemElement = document.createElement('div');
            itemElement.className = 'grid-item';
            
            itemElement.innerHTML = `
                <div class="item-image" style="background-color: ${item.color}">
                    ${item.title}
                </div>
                <div class="item-content">
                    <h3 class="item-title">${item.title}</h3>
                    <p class="item-description">${item.description}</p>
                </div>
            `;
            
            itemGrid.appendChild(itemElement);
        }
        
        // Update pagination info
        pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
        
        // Enable/disable buttons
        prevBtn.disabled = currentPage === 1;
        nextBtn.disabled = currentPage === totalPages;

        // Remove animation class with a smooth transition
        itemGrid.style.opacity = '1';
        itemGrid.style.transform = 'translateX(0)';
    }, 300);
}

// Event listeners for pagination buttons
prevBtn.addEventListener('click', () => {
    if (currentPage > 1) {
        currentPage--;
        renderItems();
        // Smooth scroll to top of grid
        itemGrid.scrollIntoView({ behavior: 'smooth' });
    }
});

nextBtn.addEventListener('click', () => {
    if (currentPage < totalPages) {
        currentPage++;
        renderItems();
        // Smooth scroll to top of grid
        itemGrid.scrollIntoView({ behavior: 'smooth' });
    }
});

// Initial render
renderItems();

