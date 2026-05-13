document.addEventListener("DOMContentLoaded", () => {

    const canvas = document.getElementById("orderPieChart");
    if (!canvas || typeof Chart === "undefined") return;

    new Chart(canvas, {
        type: "pie",
        data: {
            labels: [
                "Total Orders",
                "Accepted",
                "Rejected",
                "Cancelled",
                "Pending",
                "Assigned",
                "Out For Delivery",
                "Delivered"
            ],
            datasets: [{
                data: [
                    window.totalordersCount || 0,
                    window.acceptedCount || 0,
                    window.rejectedCount || 0,
                    window.cancelledCount || 0,
                    window.pendingCount || 0,
                    window.assignedCount || 0,
                    window.out_of_deliveryCount || 0,
                    window.deliveredCount || 0,
                ],
                backgroundColor: [
                    "#7ca5b9",
                    "#b1be78",
                    "#cc9362",
                    "#9a6565",
                    "#ba90b4",
                    "#7a9a91",
                    "#aaa02a",
                    "#3ca74185"
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "bottom",
                    labels: {
                        boxWidth: 14,
                        padding: 15
                    }
                }
            }
        }
    });

});