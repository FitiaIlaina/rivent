// document.addEventListener('DOMContentLoaded', function() {
//   // Countdown timer functionality
//   const countdownDate = new Date('May 17, 2025 18:00:00').getTime();
  
//   function updateCountdown() {
//     const now = new Date().getTime();
//     const distance = countdownDate - now;
    
//     // Calculate days, hours, minutes, seconds
//     const days = Math.floor(distance / (1000 * 60 * 60 * 24));
//     const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
//     const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
//     const seconds = Math.floor((distance % (1000 * 60)) / 1000);
    
//     // Update the countdown display
//     document.getElementById('days').textContent = days;
//     document.getElementById('hours').textContent = hours;
//     document.getElementById('minutes').textContent = minutes;
//     document.getElementById('seconds').textContent = seconds;
    
//     // If countdown is finished
//     if (distance < 0) {
//       clearInterval(countdownInterval);
//       document.getElementById('days').textContent = '0';
//       document.getElementById('hours').textContent = '0';
//       document.getElementById('minutes').textContent = '0';
//       document.getElementById('seconds').textContent = '0';
//     }
//   }
  
//   // Update countdown every second
//   updateCountdown();
//   const countdownInterval = setInterval(updateCountdown, 1000);





// Old
document.addEventListener('DOMContentLoaded', function () {
  // Récupère la date depuis l'attribut data-date
  const countdownEl = document.querySelector('.countdown');
  const countdownDate = new Date(countdownEl.dataset.date).getTime();

  function updateCountdown() {
    const now = new Date().getTime();
    const distance = countdownDate - now;

    const days = Math.floor(distance / (1000 * 60 * 60 * 24));
    const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((distance % (1000 * 60)) / 1000);

    document.getElementById('days').textContent = days;
    document.getElementById('hours').textContent = hours;
    document.getElementById('minutes').textContent = minutes;
    document.getElementById('seconds').textContent = seconds;

    if (distance < 0) {
      clearInterval(countdownInterval);
      document.getElementById('days').textContent = '0';
      document.getElementById('hours').textContent = '0';
      document.getElementById('minutes').textContent = '0';
      document.getElementById('seconds').textContent = '0';
    }
  }

  updateCountdown();
  const countdownInterval = setInterval(updateCountdown, 1000);

  
  // Ticket selection functionality
  const selectButtons = document.querySelectorAll('.select-btn');
  
  selectButtons.forEach(button => {
    button.addEventListener('click', function() {
      // Toggle selected state
      const isSelected = this.classList.contains('selected');
      
      if (isSelected) {
        this.classList.remove('selected');
        this.innerHTML = '<i class="bi bi-plus"></i>';
      } else {
        this.classList.add('selected');
        this.innerHTML = '<i class="bi bi-check"></i>';
      }
    });
  });
  
  // Info icon tooltip functionality
  const infoIcons = document.querySelectorAll('.info-icon');
  
  infoIcons.forEach(icon => {
    icon.addEventListener('mouseenter', function() {
      const tooltip = this.nextElementSibling;
      tooltip.style.display = 'block';
    });
    
    icon.addEventListener('mouseleave', function() {
      const tooltip = this.nextElementSibling;
      tooltip.style.display = 'none';
    });
  });
  
  // Reserve button functionality
  const reserveBtn = document.querySelector('.reserve-btn');
  
  reserveBtn.addEventListener('click', function() {
    // Check if any ticket is selected
    const selectedTickets = document.querySelectorAll('.select-btn.selected');
    
    if (selectedTickets.length > 0) {
      alert('Merci pour votre réservation!');
    } else {
      alert('Veuillez sélectionner au moins un billet.');
    }
  });
  
  // Mobile menu toggle
  const menuToggle = document.querySelector('.menu-toggle');
  const mobileMenu = document.querySelector('.mobile-menu');
  
  if (menuToggle) {
    menuToggle.addEventListener('click', function() {
      mobileMenu.classList.toggle('active');
    });
  }
  
  // Close mobile menu when clicking outside
  document.addEventListener('click', function(event) {
    if (!event.target.closest('.menu-toggle') && !event.target.closest('.mobile-menu')) {
      if (mobileMenu.classList.contains('active')) {
        mobileMenu.classList.remove('active');
      }
    }
  });
  
  // // Voir plus functionality
  // const voirPlus = document.querySelector('.voir-plus');
  // const eventDescription = document.querySelector('.event-description p');
  
  // if (voirPlus && eventDescription) {
  //   const fullText = eventDescription.textContent;
  //   const shortText = fullText.substring(0, 150) + '...';
  //   let isExpanded = false;
    
  //   eventDescription.textContent = shortText;
    
  //   voirPlus.addEventListener('click', function(e) {
  //     e.preventDefault();
      
  //     if (isExpanded) {
  //       eventDescription.textContent = shortText;
  //       voirPlus.textContent = 'Voir plus';
  //     } else {
  //       eventDescription.textContent = fullText;
  //       voirPlus.textContent = 'Voir moins';
  //     }
      
  //     isExpanded = !isExpanded;
  //   });
  // }
});
