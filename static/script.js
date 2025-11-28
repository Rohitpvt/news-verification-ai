const tabButtons = document.querySelectorAll('.tab-button');
tabButtons.forEach(b => b.addEventListener('click', function() {
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    tabButtons.forEach(btn => btn.classList.remove('active'));
    document.getElementById(this.getAttribute('data-tab')).classList.add('active');
    this.classList.add('active');
}));
