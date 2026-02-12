async function loadSummary() {
    const response = await fetch("/summary");
    const data = await response.json();

    document.getElementById("dayTotal").textContent = data.day;
    document.getElementById("weekTotal").textContent = data.week;
    document.getElementById("monthTotal").textContent = data.month;
    document.getElementById("yearTotal").textContent = data.year;

    const ctx = document.getElementById("categoryChart");
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.category.map(c => c.category),
            datasets: [{
                data: data.category.map(c => c.total)
            }]
        }
    });
}

loadSummary();
