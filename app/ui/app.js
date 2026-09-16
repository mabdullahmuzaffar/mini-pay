document.addEventListener("DOMContentLoaded", () => {
    // Check API System Status
    fetch("/health")
        .then(res => res.json())
        .then(data => {
            const badge = document.getElementById("health-badge");
            if (data.status === "ok" && data.database === "ok") {
                badge.innerText = "API Healthy";
                badge.className = "badge healthy";
            } else {
                badge.innerText = "API Degraded";
                badge.className = "badge degraded";
            }
        })
        .catch(() => {
            const badge = document.getElementById("health-badge");
            badge.innerText = "Connection Severed";
            badge.className = "badge degraded";
        });

    // Reference Search Action
    document.getElementById("search-button").addEventListener("click", () => {
        const ref = document.getElementById("search-input").value;
        const resDiv = document.getElementById("search-result");
        const errDiv = document.getElementById("search-error");
        
        resDiv.hidden = true;
        errDiv.hidden = true;

        if (!ref) return;

        fetch(`/api/payments/search/transactions?ref=${encodeURIComponent(ref)}`)
            .then(async res => {
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || "Query operation faulted");
                resDiv.innerText = JSON.stringify(data, null, 2);
                resDiv.hidden = false;
            })
            .catch(err => {
                errDiv.innerText = err.message;
                errDiv.hidden = false;
            });
    });

    // Submit Payment Action
    document.getElementById("pay-button").addEventListener("click", () => {
        const customer_ref = document.getElementById("pay-customer").value;
        const amount = document.getElementById("pay-amount").value;
        const transaction_ref = document.getElementById("pay-ref").value;
        const apiKey = document.getElementById("pay-key").value;

        const resDiv = document.getElementById("pay-result");
        const errDiv = document.getElementById("pay-error");
        
        resDiv.hidden = true;
        errDiv.hidden = true;

        fetch("/api/payments", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-API-Key": apiKey
            },
            body: JSON.stringify({ customer_ref, amount, transaction_ref })
        })
        .then(async res => {
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "Transaction processing rejected");
            resDiv.innerText = `Success! Status Code: ${res.status}\n` + JSON.stringify(data, null, 2);
            resDiv.hidden = false;
        })
        .catch(err => {
            errDiv.innerText = err.message;
            errDiv.hidden = false;
        });
    });
});
